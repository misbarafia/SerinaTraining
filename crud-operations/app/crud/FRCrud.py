import traceback
from fastapi.responses import Response
from datetime import datetime
import pytz as tz
from sqlalchemy import or_
import pandas as pd
import sys
import os
sys.path.append("..")
from logModule import applicationlogging,email_sender
import model
from schemas import FRSchema as schema
from session import SQLALCHEMY_DATABASE_URL,DB,engine
from sqlalchemy.orm import join, load_only, Load
# FRMetaData
import time


tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


async def getFRConfig(userID, db):
    """
    This function gets the form recognizer configurations set for the user, contains following parameters
    - userID: unique identifier for a particular user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        customer_id = db.query(model.User.customerID).filter_by(idUser=userID).scalar()
        return db.query(model.FRConfiguration).filter(model.FRConfiguration.idCustomer == customer_id).first()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py getFRConfig",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


async def updateFRConfig(userID, frConfig, db):
    """
    This function gets the form recognizer configurations set for the user, contains following parameters
    - userID: unique identifier for a particular user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        frConfig = dict(frConfig)
        # pop out elements that are not having any value
        for item_key in frConfig.copy():
            if not frConfig[item_key]:
                frConfig.pop(item_key)

        db.query(model.FRConfiguration).filter(
            model.FRConfiguration.idCustomer == userID).update(frConfig)
        db.commit()
        return {"result": "Updated", "records": frConfig}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py updateFRConfig",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})

def check_same_vendors_different_entities(vendoraccountId,modelname,db):
    try:
        account = db.query(model.VendorAccount.Account).filter(model.VendorAccount.idVendorAccount == vendoraccountId).first()
        vendorcode = account[0]
        vendors = db.query(model.VendorAccount.idVendorAccount).filter(model.VendorAccount.Account == vendorcode).all()
        count = 0
        for v in vendors:
            if v[0] != vendoraccountId:
                checkmodel = db.query(model.DocumentModel).filter(model.DocumentModel.idVendorAccount == v[0],model.DocumentModel.modelName == modelname).first()
                if checkmodel is None:
                    count = count + 1
        vendor = db.query(model.Vendor.VendorName).filter(model.Vendor.VendorCode == vendorcode).first()
        vendorName = vendor[0]
        if count >= 1:
            return {"message":"exists","vendor":vendorName,"count":count-1}
        else:
            return {"message":"not exists","vendor":vendorName,"count":count}
    except Exception as e:
        print(e)
        return {"message":"exception"}

def check_same_sp_different_entities(serviceaccountID,modelname,db):
    try:
        account = db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == serviceaccountID).first()
        spid = account[0]
        serviceprovider = db.query(model.ServiceProvider.ServiceProviderCode).filter(model.ServiceProvider.idServiceProvider == spid).first()
        vendorcode = serviceprovider[0]
        sps = db.query(model.ServiceProvider.idServiceProvider).filter(model.ServiceProvider.ServiceProviderCode == vendorcode).all()
        count = 0
        for v in sps:
            if v[0] != spid:
                checkmodel = db.query(model.DocumentModel).filter(model.DocumentModel.serviceproviderID == v[0],model.DocumentModel.modelName == modelname).first()
                if checkmodel is None:
                    count = count + 1
        sp = db.query(model.ServiceProvider.ServiceProviderName).filter(model.ServiceProvider.idServiceProvider == spid).first()
        ServiceProviderName = sp[0]
        if count >= 1:
            return {"message":"exists","sp":ServiceProviderName,"count":count-1}
        else:
            return {"message":"not exists","sp":ServiceProviderName,"count":count}
    except Exception as e:
        print(e)
        return {"message":"exception"}

def copymodels(vendoraccountId,modelname,db):
    try:
        account = db.query(model.VendorAccount.Account).filter(model.VendorAccount.idVendorAccount == vendoraccountId).first()
        vendorcode = account[0]
        vendors = db.query(model.VendorAccount.idVendorAccount).filter(model.VendorAccount.Account == vendorcode).all()
        docmodelqr = "SELECT * FROM "+DB+".documentmodel WHERE idVendorAccount="+str(vendoraccountId)+" and modelName = '"+modelname+"';"
        docmodel = pd.read_sql(docmodelqr, SQLALCHEMY_DATABASE_URL)
        inputmodel = {}
        for d in docmodel.head():
            inputmodel[d] = docmodel[d][0]
        model_id = inputmodel['idDocumentModel']
        frmetadataqr = "SELECT * FROM "+DB+".frmetadata WHERE idInvoiceModel="+str(model_id)+""
        frmetadatares = pd.read_sql(frmetadataqr, SQLALCHEMY_DATABASE_URL)
        frmetadata = {}
        for f in frmetadatares.head():
            frmetadata[f] = frmetadatares[f][0]
        del frmetadata['idFrMetaData']
        del inputmodel['idDocumentModel']
        allmodelid = []
        for v in vendors:
            if v[0] != vendoraccountId:
                iddocqr = db.query(model.DocumentModel.idDocumentModel).filter(model.DocumentModel.idVendorAccount == v[0],model.DocumentModel.modelName == modelname).first()
                if iddocqr is None:
                    inputmodel['idVendorAccount'] = v[0]
                    inputmodel["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                    inputmodel["UpdatedOn"] = inputmodel["CreatedOn"]
                    invoiceModelDB = model.DocumentModel(**inputmodel)
                    db.add(invoiceModelDB)
                    db.commit()
                    print(v[0])
                    iddocqr = db.query(model.DocumentModel.idDocumentModel).filter(model.DocumentModel.idVendorAccount == v[0],model.DocumentModel.modelName == modelname).first()    
                    allmodelid.append(iddocqr[0])
        print(f"frmetadata {allmodelid}")
        for m in allmodelid:
            frmetadata['idInvoiceModel'] = m
            frmetaDataDB = model.FRMetaData(**frmetadata)
            db.add(frmetaDataDB)
            db.commit()
            print(m)
        documenttagdefqr = "SELECT * FROM "+DB+".documenttagdef WHERE idDocumentModel="+str(model_id)+""
        documenttagdefres = pd.read_sql(documenttagdefqr, SQLALCHEMY_DATABASE_URL)
        documenttagdef = []
        for i in range(len(documenttagdefres)):
            obj = {}
            for f in documenttagdefres.head():
                if f != "idDocumentTagDef":
                    obj[f] = documenttagdefres[f][i]
            documenttagdef.append(obj)
        print(f"header tag {documenttagdef}")
        for m in allmodelid:
            checktag = db.query(model.DocumentTagDef).filter(model.DocumentTagDef.idDocumentModel == m).first()
            if checktag is None:
                for d in documenttagdef:
                    d['idDocumentModel'] = m
                    documenttagdefDB = model.DocumentTagDef(**d)
                    db.add(documenttagdefDB)
                    db.commit()
        documentlinedefqr = "SELECT * FROM "+DB+".documentlineitemtags WHERE idDocumentModel="+str(model_id)+""
        documentlinedefres = pd.read_sql(documentlinedefqr, SQLALCHEMY_DATABASE_URL)
        documentlinedef = []
        for i in range(len(documentlinedefres)):
            obj = {}
            for f in documentlinedefres.head():
                if f != "idDocumentLineItemTags":
                    obj[f] = documentlinedefres[f][i]
            documentlinedef.append(obj)
        print(f"line tag {documentlinedef}")
        for m in allmodelid:
            checktag = db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.idDocumentModel == m).first()
            if checktag is None:
                for d in documentlinedef:
                    d['idDocumentModel'] = m
                    documentlinedefDB = model.DocumentLineItemTags(**d)
                    db.add(documentlinedefDB)
                    db.commit()
        return {"message":"success"}
    except Exception as e:
        print(traceback.format_exc())
        return {"message":"exception"}

def copymodelsSP(serviceaccountId,modelname,db):
    try:
        account = db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == serviceaccountId).first()
        spid = account[0]
        serviceprovider = db.query(model.ServiceProvider.ServiceProviderCode).filter(model.ServiceProvider.idServiceProvider == spid).first()
        vendorcode = serviceprovider[0]
        sps = db.query(model.ServiceProvider.idServiceProvider).filter(model.ServiceProvider.ServiceProviderCode == vendorcode).all()
        docmodelqr = "SELECT * FROM "+DB+".documentmodel WHERE serviceproviderID="+str(spid)+" and modelName = '"+modelname+"';"
        docmodel = pd.read_sql(docmodelqr, SQLALCHEMY_DATABASE_URL)
        inputmodel = {}
        for d in docmodel.head():
            inputmodel[d] = docmodel[d][0]
        model_id = inputmodel['idDocumentModel']
        frmetadataqr = "SELECT * FROM "+DB+".frmetadata WHERE idInvoiceModel="+str(model_id)+""
        frmetadatares = pd.read_sql(frmetadataqr, SQLALCHEMY_DATABASE_URL)
        frmetadata = {}
        for f in frmetadatares.head():
            frmetadata[f] = frmetadatares[f][0]
        del frmetadata['idFrMetaData']
        del inputmodel['idDocumentModel']
        allmodelid = []
        for v in sps:
            if v[0] != spid:
                iddocqr = db.query(model.DocumentModel.idDocumentModel).filter(model.DocumentModel.serviceproviderID == v[0],model.DocumentModel.modelName == modelname).first()
                saccounts = db.query(model.ServiceAccount.idServiceAccount).filter(model.ServiceAccount.serviceProviderID == v[0]).first()
                seraccount = saccounts[0]
                if iddocqr is None:
                    inputmodel['idServiceAccount'] = seraccount
                    inputmodel['serviceproviderID'] = v[0]
                    inputmodel["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                    inputmodel["UpdatedOn"] = inputmodel["CreatedOn"]
                    invoiceModelDB = model.DocumentModel(**inputmodel)
                    db.add(invoiceModelDB)
                    db.commit()
                    print(v[0])
                    iddocqr = db.query(model.DocumentModel.idDocumentModel).filter(model.DocumentModel.serviceproviderID == v[0],model.DocumentModel.modelName == modelname).first()    
                    allmodelid.append(iddocqr[0])
        print(f"frmetadata {allmodelid}")
        for m in allmodelid:
            frmetadata['idInvoiceModel'] = m
            frmetaDataDB = model.FRMetaData(**frmetadata)
            db.add(frmetaDataDB)
            db.commit()
            print(m)
        documenttagdefqr = "SELECT * FROM "+DB+".documenttagdef WHERE idDocumentModel="+str(model_id)+""
        documenttagdefres = pd.read_sql(documenttagdefqr, SQLALCHEMY_DATABASE_URL)
        documenttagdef = []
        for i in range(len(documenttagdefres)):
            obj = {}
            for f in documenttagdefres.head():
                if f != "idDocumentTagDef":
                    obj[f] = documenttagdefres[f][i]
            documenttagdef.append(obj)
        print(f"header tag {documenttagdef}")
        for m in allmodelid:
            checktag = db.query(model.DocumentTagDef).filter(model.DocumentTagDef.idDocumentModel == m).first()
            if checktag is None:
                for d in documenttagdef:
                    d['idDocumentModel'] = m
                    documenttagdefDB = model.DocumentTagDef(**d)
                    db.add(documenttagdefDB)
                    db.commit()
        documentlinedefqr = "SELECT * FROM "+DB+".documentlineitemtags WHERE idDocumentModel="+str(model_id)+""
        documentlinedefres = pd.read_sql(documentlinedefqr, SQLALCHEMY_DATABASE_URL)
        documentlinedef = []
        for i in range(len(documentlinedefres)):
            obj = {}
            for f in documentlinedefres.head():
                if f != "idDocumentLineItemTags":
                    obj[f] = documentlinedefres[f][i]
            documentlinedef.append(obj)
        print(f"line tag {documentlinedef}")
        for m in allmodelid:
            checktag = db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.idDocumentModel == m).first()
            if checktag is None:
                for d in documentlinedef:
                    d['idDocumentModel'] = m
                    documentlinedefDB = model.DocumentLineItemTags(**d)
                    db.add(documentlinedefDB)
                    db.commit()
        return {"message":"success"}
    except Exception as e:
        print(traceback.format_exc())
        return {"message":"exception"}

async def updateMetadata(documentId, frmetadata, db):
    try:
        frmetadata = dict(frmetadata)
        print(f"frmetadata {frmetadata}")
        meta = db.query(model.FRMetaData).filter(model.FRMetaData.idInvoiceModel == documentId).first()
        if meta is not None:
            db.query(model.FRMetaData).filter(model.FRMetaData.FolderPath == frmetadata["FolderPath"]).update(frmetadata)
        else:
            frmetadata["idInvoiceModel"] = documentId
            db.add(model.FRMetaData(**frmetadata))
        db.commit()
        return {"result": "Updated", "records": frmetadata}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py updateMetadata",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid DocumentId"})
        
def createInvoiceModel(userID, invoiceModel, db):
    """
    This function creates a new invoice model, contains following parameters
    :param userID: unique identifier for a particular user
    :param invoiceModel: It is function parameter that is of a Pydantic class object, It takes member data for creation of new Vendor.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        ts = str(time.time())
        fld_name = ts.replace(".", "_")+'/train'
        
        user_details = db.query(model.User.firstName,model.User.lastName).filter(model.User.idUser == userID).first()
        user_name = user_details[0]+" "+user_details[1]
        # Add user authentication
        invoiceModel = dict(invoiceModel)
        invoiceModel['folderPath'] = fld_name
        # Assigning current date to date fields
        invoiceModel["CreatedOn"] = datetime.now(tz_region).strftime(
            "%Y-%m-%d %H:%M:%S")
        invoiceModel["UpdatedOn"] = invoiceModel["CreatedOn"]
        # create sqlalchemy model, push and commit to db
        invoiceModelDB = model.DocumentModel(**invoiceModel)
        db.add(invoiceModelDB)
        db.commit()
        if invoiceModel['idVendorAccount']:
            vendorId = db.query(model.VendorAccount.vendorID).filter(model.VendorAccount.idVendorAccount == invoiceModel['idVendorAccount']).first()[0]
            vendor = db.query(model.Vendor.VendorName).filter(model.Vendor.idVendor == vendorId).first()[0]
        elif invoiceModel['idServiceAccount']:
            vendorId = db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == invoiceModel['idServiceAccount']).first()[0]
            vendor = db.query(model.ServiceProvider.ServiceProviderName).filter(model.ServiceProvider.idServiceProvider == vendorId).first()[0]
        body = f"""
        <html>
            <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                <strong>Error Summary</strong>: <i>New Model Template Created</i>
                <div style="margin-top: 2%;"></div>
                <table border="1" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <th>Description</th>
                        <th>Vendor</th>
                        <th>Created By</th>
                        <th>Template Name</th>
                        <th>Date & Time</th>
                    </tr>
                    <tr>
                        <td>New Model Template has been created!</td>
                        <td>{vendor}</td>
                        <td>{user_name}</td>
                        <td>{invoiceModel['modelName']}</td>
                        <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        applicationlogging.logException("ROVE HOTEL DEV",f"Model Template created by {user_name} for vendor {vendor}, Model name: {invoiceModel['modelName']}","")
        email_sender.send_mail("serinaplus.dev@datasemantics.co","serina.dev@datasemantics.co","Rove Hotel Dev - New Model Template Created!",body)
        # return the updated record
        return {"result": "Updated", "records": invoiceModel}
    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py createInvoiceModel",traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def updateInvoiceModel(modelID, invoiceModel, db):
    """
    This function updates a new invoice model, contains following parameters
    :param modelID: unique identifier for a particular model
    :param invoiceModel: It is function parameter that is of a Pydantic class object, It takes member data for creation of new Vendor.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # Add user authentication
        invoiceModel = dict(invoiceModel)
        # pop out elements that are not having any value
        for item_key in invoiceModel.copy():
            if not invoiceModel[item_key]:
                invoiceModel.pop(item_key)

        db.query(model.DocumentModel).filter(
            model.DocumentModel.idDocumentModel == modelID).update(invoiceModel)
        db.commit()
        # return the updated record
        return {"result": "Updated", "records": invoiceModel}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py updateInvoiceModel",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def getmodellist(vendorID, db):
    """
    This function gets the form recognizer configurations set for the user, contains following parameters
    - userID: unique identifier for a particular user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        # subquery to get access permission id from db
        sub_query = db.query(model.VendorAccount.idVendorAccount).filter(
            model.VendorAccount.vendorID == vendorID).distinct()
        # query to get the user permission for the user from db
        main_query = db.query(model.DocumentModel).filter(
            model.DocumentModel.idVendorAccount.in_(sub_query)).all()
        # get the user permission and check if user can create or not by checking if its not null
        if not main_query:
            return Response(status_code=404, headers={"Not Found": "No vendor account model found"})
        return main_query
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py getmodellist",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})

def getmodellistsp(serviceProviderID, db):
    """
    This function gets the form recognizer configurations set for the user, contains following parameters
    - userID: unique identifier for a particular user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It return a result of dictionary type.
    """
    try:
        # subquery to get access permission id from db
        sub_query = db.query(model.ServiceAccount.idServiceAccount).filter(
            model.ServiceAccount.serviceProviderID == serviceProviderID).distinct()
        # query to get the user permission for the user from db
        main_query = db.query(model.DocumentModel).filter(
            model.DocumentModel.idServiceAccount.in_(sub_query)).all()
        # get the user permission and check if user can create or not by checking if its not null
        if not main_query:
            return Response(status_code=404, headers={"Not Found": "No service provider account model found"})
        return main_query
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py getmodellistsp",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


async def readvendor(db):
    """
     This function read a Vendor. It contains 1 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        return db.query(model.Vendor).filter(or_(model.Vendor.idVendor <= 5,  model.Vendor.idVendor == 2916)).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py readvendor",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readvendoraccount(db, v_id: int):
    """
     This function read Vendor account details. It contains 2 parameter.
    :param v_ID: It is a function parameters that is of integer type, it provides the vendor Id.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        return db.query(model.VendorAccount).filter(model.VendorAccount.vendorID == v_id).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py readvendoraccount",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})

async def readspaccount(db, s_id: int):
    """
     This function read Vendor account details. It contains 2 parameter.
    :param v_ID: It is a function parameters that is of integer type, it provides the vendor Id.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        return db.query(model.ServiceAccount).filter(model.ServiceAccount.serviceProviderID == s_id).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py readspaccount",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def addOCRLog(logData, db):
    """
    This functions creates a new log in OCRlogs table based on an OCR run on a document
    - logData: pydantic class object of the log data obtained from the OCR run 
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    """
    try:
        logData = dict(logData)
        logData["editedOn"] = datetime.now(tz_region).strftime(
            "%Y-%m-%d %H:%M:%S")
        db.add(model.OCRLogs(**logData))
        db.commit()
        return {"result": "Updated", "records": logData}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py addOCRLog",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while adding log"})


async def addItemMapping(mapData, db):
    """
    This functions creates a new user defined item mapping 
    - mapData: pydantic class object of the item mapping
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    """
    try:
        mapData = dict(mapData)
        mapData["createdOn"] = datetime.now(tz_region).strftime(
            "%Y-%m-%d %H:%M:%S")
        db.add(model.UserItemMapping(**mapData))
        db.commit()
        return {"result": "Updated", "records": mapData}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py addItemMapping",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while adding item mapping"})


async def addfrMetadata(m_id:int,r_id:int,n_fr_mdata, db):
    """
    This functions creates a new user defined item mapping 
    - frmData: pydantic class object of the fr meta data
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    """
    try:

        frmData = dict(n_fr_mdata)
        frmData["idInvoiceModel"] = m_id
        frmData["ruleID"] = r_id
        db.add(model.FRMetaData(**frmData))
        db.commit()
        return {"result": "Inserted", "records": frmData}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py addfrMetadata",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while adding FR meta data"})

async def getMetaData(documentId:int,db):
    return db.query(model.FRMetaData).filter(model.FRMetaData.idInvoiceModel == documentId).first()

async def getTrainTestRes(modelId:int,db):
    return db.query(model.DocumentModel).options(load_only("training_result","test_result")).filter(model.DocumentModel.idDocumentModel == modelId).first()

async def getActualAccuracy(tp:str,nm:str,db):
    try:
        if tp == "vendor":
            accuracy_data = db.query(model.Document,model.DocumentTagDef,model.Vendor,model.DocumentData,model.VendorAccount).options(Load(model.DocumentTagDef).load_only("TagLabel"),Load(model.Vendor).load_only("VendorName"),Load(model.DocumentData).load_only("Value","IsUpdated","isError","ErrorDesc"),Load(model.Document).load_only("idDocument"),Load(model.VendorAccount).load_only("idVendorAccount")).join(model.DocumentData,model.DocumentData.documentID == model.Document.idDocument).join(model.DocumentTagDef,model.DocumentTagDef.idDocumentTagDef == model.DocumentData.documentTagDefID).join(model.VendorAccount,model.VendorAccount.idVendorAccount == model.Document.vendorAccountID).join(model.Vendor,model.Vendor.idVendor == model.VendorAccount.vendorID).filter(model.Vendor.VendorName == nm,model.Document.idDocumentType == 3).all()
        else:
            accuracy_data = db.query(model.Document,model.DocumentTagDef,model.ServiceProvider,model.DocumentData,model.ServiceAccount).options(Load(model.DocumentTagDef).load_only("TagLabel"),Load(model.ServiceProvider).load_only("ServiceProviderName"),Load(model.DocumentData).load_only("Value","IsUpdated","isError","ErrorDesc"),Load(model.Document).load_only("idDocument"),Load(model.ServiceAccount).load_only("idServiceAccount")).join(model.DocumentData,model.DocumentData.documentID == model.Document.idDocument).join(model.DocumentTagDef,model.DocumentTagDef.idDocumentTagDef == model.DocumentData.documentTagDefID).join(model.ServiceAccount,model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID).join(model.ServiceProvider,model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID).filter(model.ServiceProvider.ServiceProviderName == nm,model.Document.idDocumentType == 3).all()
        final_dict = {}
        documents = []
        for a in accuracy_data:
            documentid = a.Document.idDocument
            if documentid not in documents:
                documents.append(a.Document.idDocument)
            key = a.DocumentTagDef.TagLabel
            iserror = a.DocumentData.isError
            isupdated = a.DocumentData.IsUpdated
            if key not in final_dict.keys():
                final_dict[key] = {"miss": 0,"match":0}
            else:
                if iserror == 1 or isupdated == 1:
                    final_dict[key]["miss"] += 1
                else:
                    final_dict[key]["match"] += 1
        final_dict["DocumentCount"] = len(documents)
        return final_dict
    except Exception as e:
        print(e)
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py getActualAccuracy",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while reading data"})

async def getall_tags(tagtype,db):
    try:
        header_tags=db.query(model.DefaultFields).options(load_only("Name","Ismendatory")).filter(model.DefaultFields.Type == "Header",model.DefaultFields.TagType == tagtype).all()
        line_tags=db.query(model.DefaultFields).options(load_only("Name","Ismendatory")).filter(model.DefaultFields.Type == "line",model.DefaultFields.TagType == tagtype).all()
        return {"header": header_tags,"line":line_tags}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py getall_tags",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while reading data"})

async def get_entity_level_taggedInfo():
    try:
        connection = engine.connect()
        df = pd.read_sql("select EntityName as Entity,VendorName as Vendor,mandatoryheadertags as `Mandatory Header Tags`,mandatorylinetags as `Mandatory Line Item Tags`,optionalheadertags as `Optional Header Tags`,optionallinertags as `Optional Line Item Tags` from frmetadata as f, documentmodel as dm, vendoraccount as va, vendor as v, entity as e where f.idInvoiceModel = dm.idDocumentModel and dm.idVendorAccount = va.idVendorAccount and va.vendorID = v.idVendor and v.entityID = e.idEntity",connection)
        df.to_excel("VendorsTaggedInfo.xlsx",index=False)
        return "VendorsTaggedInfo.xlsx"
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py get_entity_level_taggedInfo",str(e))
        df = pd.DataFrame()
        df.to_excel("VendorsTaggedInfo.xlsx",index=False)
        return "VendorsTaggedInfo.xlsx"
# async def create_tags(Default_fields,db):
#     try:
#         df_fields = dict(Default_fields)
#         existingnames=db.query(model.DefaultFields.Name).filter(model.DefaultFields.Type == df_fields['Type']).all()
#         field_name=(df_fields['Name'],)
#         if field_name in existingnames:
#             res="Not Inserted"
#         else:
#             db.add(model.DefaultFields(**df_fields))
#             db.commit()
#             res="Inserted"
#         return {"result": res, "records": df_fields}

    # except Exception as e:
    #     print(e)
    #     return Response(status_code=500, headers={"Error": "Server error", "Desc": "Error while reading data"})


async def readdocumentrules(db):
    """
     This function read document rules list. It contains 1 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        return db.query(model.Rule).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py readdocumentrules",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})

async def readnewdocrules(db):
    """
     This function read new document rules list for agi. It contains 1 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        return db.query(model.AGIRule).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","FRCrud.py readnewdocrules",str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})

