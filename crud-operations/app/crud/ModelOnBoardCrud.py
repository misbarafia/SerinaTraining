# from sqlalchemy.orm import
from sqlalchemy.sql.base import Executable
from fastapi.responses import Response
from datetime import datetime
import pytz as tz
import json
import os
import sys
sys.path.append("..")
from logModule import email_sender
import model
from schemas import InvoiceSchema as schema
from logModule import applicationlogging

tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


def ParseInvoiceData(modelID, userId, invoiceData, db):
    """
    This function parse the data from recogniser into db format
    - invoiceData: Form recogniser output JSON data
    - return: It return a result of dictionary type.
    """
    try:
        user_details = db.query(model.User.firstName,model.User.lastName).filter(model.User.idUser == userId).first()
        user_name = user_details[0]+" "+user_details[1]
        modeldetails = db.query(model.DocumentModel.folderPath,model.DocumentModel.training_result).filter(model.DocumentModel.idDocumentModel == modelID).first()
        folderpath = modeldetails[0]
        trainingresut = modeldetails[1]
        invoiceData = dict(invoiceData)
        # parsing account id
        # if invoiceData['VendorAccount']:
        #     vendorAccID = db.query(model.VendorAccount.idVendorAccount).filter(
        #         model.VendorAccount.Account == invoiceData["VendorAccount"]).first()[0]
        #     modelData["idVendorAccount"] = vendorAccID
        # else:
        #     serviceAccID = db.query(model.ServiceAccount.idServiceAccount).filter(
        #         model.ServiceAccount.Account == invoiceData["ServiceAccount"]).first()[0]
        #     modelData["idServiceAccount"] = serviceAccID
        #  parse form recogniser model ID
        # modelData["modelID"] = invoiceData["ModelID"]
        # create Model
        # invoiceModel_rsp, modelID = createInvoiceModel(modelData, db)
        # delete any exisiting tag definitions
        #cleanupTags(modelID, db)
        # Add tags
        if len(invoiceData['TestResult'].keys()) > 0:
            db.query(model.DocumentModel).filter(
                model.DocumentModel.folderPath == folderpath).update({'modelID':invoiceData['ModelID'],'training_result':trainingresut,'test_result':json.dumps(invoiceData['TestResult'])})
        else:
            db.query(model.DocumentModel).filter(
                model.DocumentModel.folderPath == folderpath).update({'modelID':invoiceData['ModelID'],'training_result':trainingresut})
        db.commit()
        all_models = db.query(model.DocumentModel.idDocumentModel).filter(model.DocumentModel.folderPath == folderpath).all()
        tag_rsp = addTagDefinition(all_models, invoiceData["labels"],db)
        # Add line item tags
        lineItem_rsp = addLineItemTag(
            all_models, invoiceData["line_tables"],db)
        if "VendorAccount" in invoiceData:
            vendorId = db.query(model.VendorAccount.vendorID).filter(model.VendorAccount.idVendorAccount == invoiceData['VendorAccount']).first()[0]
            vendor = db.query(model.Vendor.VendorName).filter(model.Vendor.idVendor == vendorId).first()[0]
        else:
            vendorId = db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == invoiceData['ServiceAccount']).first()[0]
            vendor = db.query(model.ServiceProvider.ServiceProviderName).filter(model.ServiceProvider.idServiceProvider == vendorId).first()[0]
        body = f"""
        <html>
                <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                    <strong>Error Summary</strong>: <i>Model Onboarded</i>
                    <div style="margin-top: 2%;"></div>
                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <th>Description</th>
                            <th>Vendor/Service Provider</th>
                            <th>Onboarded By</th>
                            <th>Model Id</th>
                            <th>Date & Time</th>
                        </tr>
                        <tr>
                            <td>New Model Onboarded/ Existing Model Updated</td>
                            <td>{vendor}</td>
                            <td>{user_name}</td>
                            <td>{invoiceData['ModelID']}</td>
                            <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                </body>
            </html>
        """
        applicationlogging.logException("ROVE HOTEL DEV",f"Model Onboarded by {user_name} for vendor/Service Provider {vendor}, Model id: {invoiceData['ModelID']}","")
        email_sender.send_mail("serinaplus.dev@datasemantics.co","serina.dev@datasemantics.co","ROVE HOTEL DEV - New Model Onboarded!",body)
        return {"result": "Updated", "records": {"Labels": tag_rsp, "LineItems": lineItem_rsp}}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while parsing data"})


def cleanupTags(modelID, db):
    # delete any exisiting tag definitions
    db.query(model.DocumentTagDef).filter_by(idDocumentModel=modelID).delete()
    # delete any exisiting tag definitions
    db.query(model.DocumentLineItemTags).filter_by(
        idDocumentModel=modelID).delete()
    db.commit()


def createInvoiceModel(invoiceModel, db):
    """
    This function creates a new invoice model, contains following parameters
    - userID: unique identifier for a particular user
    - invoiceModel: It is function parameter that is of a Pydantic class object, It takes member data for creation of new Vendor.
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        # Add user authentication
        # invoiceModel = dict(invoiceModel)
        # Assigning current date to date fields
        invoiceModel["CreatedOn"] = datetime.now(tz_region).strftime(
            "%Y-%m-%d %H:%M:%S")
        invoiceModel["UpdatedOn"] = invoiceModel["CreatedOn"]
        # create sqlalchemy model, push and commit to db
        invoiceModelDB = model.DocumentModel(**invoiceModel)
        db.add(invoiceModelDB)
        db.commit()
        modelID = invoiceModelDB.idDocumentModel
        # return the updated record
        return invoiceModel, modelID
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error While creating model"})


def addTagDefinition(models, tags, db):
    """
    This function creates a new set of tag definitions, contains following parameters
    - modelID: unique identifier for a particular model created in the DB
    - tags: It is function parameter that is list of a Pydantic class object, It takes member data for creation of new tag definition.
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        createdTime = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # looping through the tagdef to insert recrod one by one
        for m in models:
            all_headertags = []
            for item in tags:
                item = dict(item)
                tagdef = parseLabelValue(item['value'])
                # Add created on, UpdatedOn and model7 ID to each tag definition records
                tagdef["TagLabel"] = item['label']
                all_headertags.append(item['label'])
                tagdef["CreatedOn"] = createdTime
                tagdef["UpdatedOn"] = createdTime
                tagdef["idDocumentModel"] = m[0]
                if len(db.query(model.DocumentTagDef).filter(model.DocumentTagDef.idDocumentModel == m[0],model.DocumentTagDef.TagLabel == item['label']).all()) > 0:
                    db.query(model.DocumentTagDef).filter(model.DocumentTagDef.idDocumentModel == m[0],model.DocumentTagDef.TagLabel == item['label']).update(tagdef)
                else:
                    db.add(model.DocumentTagDef(**tagdef))
            all_tags = db.query(model.DocumentTagDef).filter(model.DocumentTagDef.idDocumentModel == m[0]).all()
            print(all_headertags)
            for tag in all_tags:
                if tag.TagLabel not in all_headertags:
                    db.query(model.DocumentTagDef).filter_by(idDocumentModel=m[0],TagLabel=tag.TagLabel).delete()  
            db.commit()
        return tags
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while adding tag definitions"})


def addLineItemTag(models, lineItemTag, db):
    """
    This function creates a new set of line item tag definitions, contains following parameters
    - modelID: unique identifier for a particular model created in the DB
    - lineItemTag: It is function parameter that is list of a Pydantic class object, It takes member data for creation of new line item tag definition.
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        all_lineitemtags = []
        for m in models:
            for item in lineItemTag['tab_1']:
                item = dict(item)
                if item['row'] != "0":
                    continue
                lineItemDef = parseTabelValue(item['value'])
                all_lineitemtags.append(lineItemDef['TagName'])
                lineItemDef["idDocumentModel"] = m[0]
                if len(db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.idDocumentModel == m[0],model.DocumentLineItemTags.TagName == lineItemDef['TagName']).all()) > 0:
                    db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.idDocumentModel == m[0],model.DocumentLineItemTags.TagName == lineItemDef['TagName']).update(lineItemDef)
                else:
                    db.add(model.DocumentLineItemTags(**lineItemDef))
            all_linetags = db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.idDocumentModel == m[0]).all()
            for tag in all_linetags:
                if tag.TagName not in all_lineitemtags:
                    db.query(model.DocumentLineItemTags).filter_by(idDocumentModel=m[0],TagName=tag.TagName).delete()
            db.commit()
        return lineItemTag
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while adding tag definitions"})


def updateLabels(documentId,labelVal,db):
    try:
        db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == documentId).update({'labels':labelVal})
        db.commit()
        return "success"
    except Exception as e:
        return "exception"

def get_fr_training_result_by_vid(db,modeltype,Id):
    if modeltype == 'vendor':
        return db.query(model.DocumentModel).filter(model.DocumentModel.idVendorAccount == Id, model.DocumentModel.training_result != None).all()
    else:
        return db.query(model.DocumentModel).filter(model.DocumentModel.idServiceAccount == Id, model.DocumentModel.training_result != None).all()
def get_composed_training_result_by_vid(db,modeltype,Id):
    if modeltype == 'vendor':
        return db.query(model.DocumentModelComposed).filter(model.DocumentModelComposed.vendorAccountId == Id, model.DocumentModelComposed.training_result != None).all()
    else:
        return db.query(model.DocumentModelComposed).filter(model.DocumentModelComposed.serviceAccountId == Id, model.DocumentModelComposed.training_result != None).all()

def getFields(documentId,db):
    return db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == documentId).all()[0].fields

def getSavedLabels(documentId,db):
    return db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == documentId).all()[0].labels

def get_fr_training_result(db,documentId):
    result = db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == documentId).all()[0].training_result
    if result is not None:
        return result
    else:
        return []

def updateFields(documentId,fieldsVal,db):
    try:
        db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == documentId).update({'fields':fieldsVal})
        db.commit()
        return "success"
    except Exception as e:
        return "exception"

def createOrUpdateComposeModel(composeObj,db):
    try:
        add = "add"
        composeObj = dict(composeObj)   
        db.add(model.DocumentModelComposed(**composeObj))
        db.commit()
        return f"success {add}"
    except Exception as e:
        return "exception"

def updateTrainingResult(documentId,result,db):
    try:
        db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == documentId).update({'training_result':result})
        db.commit()
        return "success"
    except Exception as e:
        return "exception"

def parseLabelValue(labelValue):
    """
    This function parses the list of values in form-recogniser data into single bounding box and value
    - labelValue : list of values provided by form recogniser
    - return: It returns the label page number and bounding boxes.
    """
    try:
        # extract page list and bounding box list from label value
        dict_list = []
        boundingbox_list = []
        for item in labelValue:
            item = dict(item)
            dict_list.append(item)
            boundingbox_list.append(dict(item['boundingBoxes']))
        # parse page numbers
        pagelist = [item['page'] for item in dict_list]
        # removing any duplicate page numbers
        pagelist = list(set(pagelist))
        # convert page numbers to comma seprated string
        pages = ','.join([str(item) for item in pagelist])
        # find max and min of x cordinates
        xmax = max(float(item['x']) for item in boundingbox_list or [{'x':0}])
        xmin = min(float(item['x']) for item in boundingbox_list or [{'x':0}])
        # find max and min of y cordinates
        ymax = max(float(item['y']) for item in boundingbox_list or [{'y':0}])
        ymin = min(float(item['y']) for item in boundingbox_list or [{'y':0}])
        # find height and width of last bounding box
        addheight = boundingbox_list[len(boundingbox_list)-1]['h'] if len(boundingbox_list) > 0 else 0
        addwidth = boundingbox_list[len(boundingbox_list)-1]['w'] if len(boundingbox_list) > 0 else 0
        # find total height and width
        width = str(int(float(xmax)) - int(float(xmin)) + int(float(addwidth)))
        height = str(int(float(ymax)) - int(float(ymin)) +
                     int(float(addheight)))
        # create return dict with parsed values
        tagdef = {"Xcord": xmin, "Ycord": ymin,
                  "Width": width, "Height": height, "Pages": pages}
        return tagdef
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while parsing label value"})


def parseTabelValue(labelValue):
    """
    This function parses the list of line item column names in form-recogniser data into single bounding box and value
    - labelValue : list of values provided by form recogniser
    - return: It returns the label TagName and bounding boxes.
    """
    for item in labelValue:
        if 'boundingBoxes' in item:
            if 'x' in item['boundingBoxes'] and 'y' in item['boundingBoxes'] and 'w' in item['boundingBoxes'] and 'h' in item['boundingBoxes']:
                lineItemDef = {"Xcord": item['boundingBoxes']['x'], "Ycord": item['boundingBoxes']['y'],
                            "Width": item['boundingBoxes']['w'], "Height": item['boundingBoxes']['h'],
                            "TagName": item['text']}
            else:
                lineItemDef = {"Xcord": 0, "Ycord": 0,
                            "Width": 0, "Height": 0,
                            "TagName": ""}
        else:
            lineItemDef = {"Xcord": 0, "Ycord": 0,
                            "Width": 0, "Height": 0,
                            "TagName": ""}

    return lineItemDef
