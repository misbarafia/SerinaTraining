# from sqlalchemy.orm import
from fastapi.responses import Response, StreamingResponse
from fastapi import File
from datetime import datetime, timedelta
from io import BytesIO
import pytz as tz
import pandas as pd
from sqlalchemy import func, case, or_, and_
import traceback, base64
import json
from sqlalchemy.sql.elements import Null
from sqlalchemy.orm import join, load_only, Load, aliased
import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import sys

sys.path.append("..")
from auth import AuthHandler
import model as models
from logModule import applicationlogging
import model
from dependency import dependencies
from session.notificationsession import client as mqtt

tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


# dict to store doc type
invtype = {"PO": 1, "GRN": 2, "Invoice": 3, "Receipt": 4}

# dict of tab type
model_col = {"INV": 1, "PO": 2, "ARC": 3, "VEN": 4, "SER": 5, "INVS": 6}

status = ["System Check In - Progress", "Processing Document", "Finance Approval Completed", "Need To Review",
          "Edit in Progress", "Awaiting Edit Approval", "Sent to ERP", "Payment Cleared",
          "Payment Partially Paid", "Invoice Rejected", "Payment Rejected", "PO Open", "PO Closed", "Posted In ERP"]

# substatus = [(7, "Invoice Meta Issue"), (8, "PO Item Check"), (9, "Invoice Amount Issue"),
#              (10, "Invoice Successfully Processed"), (11, "Invoice Manually"), (14, "Invoice Item Missing"),
#              (15, "PO QTY MISMATCHED"), (16, "Unit Price Mismatch"), (17, "GRN QTY Mismatched"),
#              (18, "Item Matched"), (19, "PO Item Missing"), (20, "GRN Item Check"), (21, "PO QTY Check"),
#              (22, "GRN QTY CHeck"), (27, "Mismatch Values"), (28, "Batch Exception"), (32, "ERP Exception")]

substatus = [(32, "ERP Exception"), (35, "Ready for GRN creation "), (37, "GRN successfully created in ERP"),
             (39, "GRN Created in Serina")]

# Sql case statement for re placing number with string status

doc_status = case(
    [
        (model.Document.documentsubstatusID == value[0], value[1])
        for value in substatus
    ] + [
        (model.Document.documentStatusID == value[0] + 1, value[1])
        for value in enumerate(status)
    ]
    , else_=''
).label("docstatus")

approval_type = case(
    [
        (model.DocumentSubStatus.idDocumentSubstatus == 4, "Batch Approval"),
        (model.DocumentSubStatus.idDocumentSubstatus == 6, "Manual Approval")
    ], else_='Batch Approval'
).label("Approvaltype")


# async def getInvoiceTypes(userID, typeID, skip, limit, db):
#     """
#     This function gets the types of invoices, contains following parameters
#     :param userID: unique identifier for a particular user
#     :param typeID: unique identifier for a particular Invoice type
#     :param skip: to set an offset value
#     :param limit: limits the number of records pulled from the db
#     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     :return: It return a result of dict type.
#     """
#     try:
#         # Add user authentication
#         if typeID:
#             # Query db to filter idDocumentType with type details
#             return db.query(model.idDocumentType).filter(model.idDocumentType.idDocumentType == typeID).first()
#         else:
#             # Query db to fetch all DocumentTypes
#             return db.query(model.idDocumentType).offset(skip).limit(limit).all()
#     except Exception as e:
#         print(e)
#         return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def createInvoiceModel(userID, documentModel, db):
    """
    This function creates a new invoice model, contains following parameters
    :param userID: unique identifier for a particular user
    :param invoiceModel: It is function parameter that is of a Pydantic type object, It takes member data for creation of new Vendor.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # Add user authentication
        DocumentModel = dict(documentModel)
        # Assigning current date to date fields
        DocumentModel["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        DocumentModel["UpdatedOn"] = DocumentModel["CreatedOn"]
        # create sqlalchemy model, push and commit to db
        DocumentModelDB = model.DocumentModel(**DocumentModel)
        db.add(DocumentModelDB)
        db.flush()
        # return the updated record
        return DocumentModel
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py createInvoiceModel", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})


def addTagDefinition(userID, tags, db):
    """
    This function creates a new set of tag definitions, contains following parameters
    :param userID: unique identifier for a particular user
    :param tags: It is function parameter that is list of a Pydantic type object, It takes member data for creation of new tag definition.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - It return a result of dict type.
    """
    try:
        tags = dict(tags)
        createdTime = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # Find the modelID which was just created session.query(func.max(Table.column))
        model_id = db.query(func.max(model.DocumentModel.idDocumentModel)).one()[0]
        # looping through the tagdef to insert recrod one by one
        for item in tags['tagList']:
            item = dict(item)
            # Add created on, UpdatedOn and model ID to each tag definition records
            item["CreatedOn"] = createdTime
            item["UpdatedOn"] = createdTime
            item["idDocumentModel"] = model_id
            tagsDB = model.DocumentTagDef(**item)
            db.add(tagsDB)
        db.commit()
        return tags
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py addTagDefinition", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})


def createInvoice(userID, document, db):
    """
    This function creates a new invoice with meta data of an uploaded invoice, contains following parameters
    :param userID: unique identifier for a particular user
    :param document: It is function parameter that is list of a Pydantic type object, It takes member data for creation
    of new invoice.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # Add user authentication
        document = dict(document)
        # Assigning status, current date to date fields
        document["documentStatusID"] = 1  # submitted
        document["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # create sqlalchemy model, push and commit to db
        documentDB = model.Document(**document)
        db.add(documentDB)
        db.commit()
        document["documentID"] = documentDB.idDocument
        # print(invoiceDB.idDocument)
        # return the updated record
        return document
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py createInvoice", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def createInvoiceData(userID, documentID, documentData, db):
    """
    This function creates a new invoice data with captured values of an invoice, contains following parameters
    :param userID: unique identifier for a particular user
    :param documentID : unique identifier for the invoice to which data is associated to.
    :param documentData: It is function parameter that is list of a Pydantic type object, It takes member data for
    creation of new invoice data.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # Add user authentication
        documentData = dict(documentData)
        createdTime = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # Assigning invoice ID and current date to fields
        for item in documentData['dataList']:
            item = dict(item)
            item["documentID"] = documentID
            item["CreatedOn"] = createdTime
            tagsDB = model.DocumentData(**item)
            db.add(tagsDB)
        # create sqlalchemy model, push and commit to db
        db.commit()
        # return the updated record
        return documentData
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py createInvoiceData", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def createInvoiceTableDef(userID, documentID, documentTableDef, db):
    """
    This function creates a new invoice table definition, contains following parameters
    :param userID: unique identifier for a particular user
    :param documentID: unique identifier for the invoice to which data is associated to.
    :param documentTableDef: It is function parameter that is list of a Pydantic type object, It takes member data for
    creation of new invoice table definition.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # Add user authentication
        documentTableDef = dict(documentTableDef)
        # Assigning document ID, userID and current date to corresponding fields
        documentTableDef["updatedBy"] = userID
        documentTableDef["documentID"] = documentID
        documentTableDef["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        documentTableDef["UpdatedOn"] = documentTableDef["CreatedOn"]
        # create sqlalchemy model, push and commit to db
        documentTableDefDB = model.DocumentTableDef(**documentTableDef)
        db.add(documentTableDefDB)
        db.commit()
        # return the updated record
        return documentTableDef
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py createInvoiceTableDef", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def createInvoiceLineItems(userID, documentID, documentLineItems, db):
    """
    This function creates a invoice line item, contains following parameters
    :param userID: unique identifier for a particular user
    :param documentID : unique identifier for the invoice to which data is associated to.
    :param invoiceLineItems: It is function parameter that is list of a Pydantic type object, It takes member data for creation of new invoice line item definition.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # Add user authentication
        documentLineItems = dict(documentLineItems)
        # Add Document ID field to each record in the list
        for item in documentLineItems['lineItemList']:
            item = dict(item)
            item["documentID"] = documentID
            documentLineItemsDB = model.DocumentLineItems(**item)
            db.add(documentLineItemsDB)
        # commit changes to db
        db.commit()
        # return recrods added
        return documentLineItems
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py createInvoiceLineItems", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


def createInvoiceUpdate(userID, documentDataID, documentLineItemID, documentUpdate, db):
    """
    This function creates a record of update in invoice data, contains following parameters
    :param userID: unique identifier for a particular user
    :param documentDataID : unique identifier for the invoice tag data.
    :param documentLineItemID : unique identifier for the invoice line item tag data.
    :param documentUpdate: It is function parameter that is list of a Pydantic type object, It takes member data for
    updating the status of an invoice.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # Add user authentication
        documentUpdate = dict(documentUpdate)
        # filter((User.email == email) | (User.name == name))
        documentUpdate["updatedBy"] = userID
        documentUpdate["UpdatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # Check and update data ID or line item ID
        if documentDataID:
            documentUpdate["documentDataID"] = documentDataID
        elif documentLineItemID:
            documentUpdate["documentLineItemID"] = documentLineItemID
        # create db object and push
        documentUpdateDB = model.DocumentUpdates(**documentUpdate)
        db.add(documentUpdateDB)
        db.commit()
        return documentUpdate
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py createInvoiceUpdate", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


# def updateInvoiceStage(userID, documentDataID, documentStage, db):
#     """
#     This function updates the stage of the invoice, contains following parameters
#     :userID: unique identifier for a particular user
#     :documentDataID : unique identifier for the invoice tag data.
#     :db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     :return: It return a result of dict type.
#     """
#     try:
#         # Add user authentication
#         documentStage = dict(documentStage)
#         db.query(model.DocumentData).filter(
#             model.DocumentData.idDocumentData == documentDataID).update(documentStage)
#         db.commit()
#         return {"result": "Updated", "records": documentStage}
#     except Exception as e:
#         print(e)
#         return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


# def updateInvoiceTableDef(userID, documentID, documentTableDef, db):
#     """
#     This function updates the table definition in an invoice, contains following parameters
#     :userID: unique identifier for a particular user
#     :documentID : unique identifier for the invoice to which data is associated to.
#     :invoiceTableDef: It is function parameter that is list of a Pydantic type object, It takes member data for updation of an invoice table definition.
#     :db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     :return: It return a result of dict type.
#     """
#     try:
#         # Add user authentication
#         documentTableDef = dict(documentTableDef)
#         # Add updated date and updated by user ID
#         documentTableDef["updatedBy"] = userID
#         documentTableDef["UpdatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
#         db.query(model.DocumentTableDef).filter(
#             model.DocumentTableDef.documentID == documentID).update(documentTableDef)
#         db.commit()
#         return documentTableDef
#     except Exception as e:
#         print(e)
#         return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


# def updateInvoiceLineItemTags(userID, documentID, lineitemTags, db):
#     """
#     This function updates the line item definition in an document, contains following parameters
#     :userID: unique identifier for a particular user
#     :documentID : unique identifier for the invoice to which data is associated to.
#     :lineitemTags: It is function parameter that is list of a Pydantic type object, It takes member data for updating a line item definition.
#     :db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     :return: It return a result of dict type.
#     """
#     try:
#         # Add user authentication
#         lineitemTags = dict(lineitemTags)
#         # Add updated date and updated by user ID
#         lineitemTags["documentID"] = documentID
#         db.query(model.DocumentLineItems).filter(
#             model.DocumentLineItems.documentID == documentID).update(lineitemTags)
#         db.commit()
#         return lineitemTags
#     except Exception as e:
#         print(e)
#         return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})


####################################################################################################


async def read_doc_po_list(u_id, sp_id, ven_id, usertype, db, off_limit, uni_api_filter):
    """
    This function reads the invoice list, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id : It is a function parameter that is of integer type, it provides the Service provider id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        offset, limit = off_limit
        offset = (offset - 1) * limit
        if offset < 0:
            return Response(status_code=403, headers={"ClientError": "please provide right offset value"})
        # sub query to get only user accessible entities
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id).distinct()
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        # get total po count:
        po_count = db.query(func.count(model.Document.idDocument)).filter(model.Document.idDocumentType == 1).filter(
            user_type_filter[usertype]).scalar()
        # base query to fetch invoice data
        data = db.query(model.Document, doc_status, model.Entity, model.EntityBody,
                        model.VendorAccount, model.Vendor).filter(
            user_type_filter[usertype])
        # filters for query parameters
        if sp_id:
            sub_query = db.query(model.ServiceAccount.idServiceAccount).filter_by(
                serviceProviderID=sp_id)
            data = data.filter(model.Document.supplierAccountID.in_(sub_query))
        if ven_id:
            sub_query = db.query(model.VendorAccount.idVendorAccount).filter_by(
                vendorID=ven_id)
            data = data.filter(model.Document.vendorAccountID.in_(sub_query))
        # podata filters
        podata = data.filter(model.Document.idDocumentType == 1)

        podata = podata.options(
            Load(model.Document).load_only("docheaderID", "documentDate", "totalAmount",
                                           "documentStatusID"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName", "Address"),
            Load(model.Vendor).load_only("VendorName"), Load(model.VendorAccount).load_only("Account")).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).join(model.Vendor,
                               model.Vendor.idVendor == model.VendorAccount.vendorID,
                               isouter=True)
        if uni_api_filter:
            podata = podata.filter((model.Document.docheaderID.like(
                f"%{uni_api_filter}%") | model.Document.documentDate.like(
                f"%{uni_api_filter}%") | model.Document.totalAmount.like(
                f"%{uni_api_filter}%") | model.Entity.EntityName.like(
                f"%{uni_api_filter}%") | model.EntityBody.EntityBodyName.like(
                f"%{uni_api_filter}%") | model.EntityBody.Address.like(
                f"%{uni_api_filter}%") | model.Vendor.VendorName.like(
                f"%{uni_api_filter}%") | model.VendorAccount.Account.like(f"%{uni_api_filter}%")))
        return {"ok": {"podata": podata.offset(offset).limit(
            limit).all(), "total_po": po_count}}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_po_list", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


async def read_doc_inv_list(u_id, sp_id, ven_id, usertype, inv_type, db):
    """
    This function reads document invoice list, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
    :param ven_id: It is a function parameters that is of integer type, it provides the vendor Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        # sub query to get only user accessable entities
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id).distinct()
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        # base query to fetch invoice data
        inv_choice = {"ser": (
            model.ServiceProvider, model.ServiceAccount, Load(model.ServiceProvider).load_only("ServiceProviderName"),
            Load(model.ServiceAccount).load_only("Account")), "ven": (
            model.VendorAccount, model.Vendor, Load(model.Vendor).load_only("VendorName", "Address"),
            Load(model.VendorAccount).load_only("Account"))}
        data = db.query(model.Document, doc_status, model.Entity,
                        model.EntityBody, inv_choice[inv_type][0],
                        inv_choice[inv_type][1]).filter(user_type_filter[usertype]).filter(
            model.Document.documentStatusID != 14).filter(model.Document.documentStatusID != 10)
        # filters for query parameters
        if sp_id:
            sub_query = db.query(model.ServiceAccount.idServiceAccount).filter_by(
                serviceProviderID=sp_id)
            data = data.filter(model.Document.supplierAccountID.in_(sub_query))
        if ven_id:
            sub_query = db.query(model.VendorAccount.idVendorAccount).filter_by(
                vendorID=ven_id)
            data = data.filter(model.Document.vendorAccountID.in_(sub_query))
        # podata filters
        documentdata = data.filter(model.Document.idDocumentType == 3, model.Document.documentStatusID != 0)
        # Fetching Document data
        Documentdata = documentdata.options(
            Load(model.Document).load_only("docheaderID", "PODocumentID", "documentDate", "totalAmount",
                                           "documentStatusID", "sourcetype", "CreatedOn", "documentsubstatusID","sender"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName"),
            inv_choice[inv_type][2], inv_choice[inv_type][3]).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True)
        if inv_type == "ser":
            Documentdata = Documentdata.join(model.ServiceAccount,
                                             model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
                                             isouter=True).join(
                model.ServiceProvider,
                model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
                isouter=True).filter(model.Document.supplierAccountID.isnot(None))
        else:
            Documentdata = Documentdata.join(
                model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
                isouter=True).join(model.Vendor,
                                   model.Vendor.idVendor == model.VendorAccount.vendorID,
                                   isouter=True).filter(model.Document.vendorAccountID.isnot(None))
        Documentdata = Documentdata.order_by(model.Document.CreatedOn.desc()).all()
        return {"ok": {"Documentdata": Documentdata}}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_inv_list", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


async def read_doc_inv_arc_list(u_id, sp_id, ven_id, usertype, inv_type, db):
    """
    This function reads document invoice list, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
    :param ven_id: It is a function parameters that is of integer type, it provides the vendor Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        # sub query to get only user accessable entities
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id).distinct()
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        # base query to fetch invoice data
        inv_choice = {"ser": (
            model.ServiceProvider, model.ServiceAccount, Load(model.ServiceProvider).load_only("ServiceProviderName"),
            Load(model.ServiceAccount).load_only("Account")), "ven": (
            model.VendorAccount, model.Vendor, Load(model.Vendor).load_only("VendorName", "Address"),
            Load(model.VendorAccount).load_only("Account"))}
        data = db.query(model.Document, doc_status, model.Entity,
                        model.EntityBody, inv_choice[inv_type][0],
                        inv_choice[inv_type][1]).filter(user_type_filter[usertype]).filter(
            model.Document.documentStatusID == 14)
        # filters for query parameters
        if sp_id:
            sub_query = db.query(model.ServiceAccount.idServiceAccount).filter_by(
                serviceProviderID=sp_id)
            data = data.filter(model.Document.supplierAccountID.in_(sub_query))
        if ven_id:
            sub_query = db.query(model.VendorAccount.idVendorAccount).filter_by(
                vendorID=ven_id)
            data = data.filter(model.Document.vendorAccountID.in_(sub_query))
        # podata filters
        documentdata = data.filter(model.Document.idDocumentType == 3, model.Document.documentStatusID != 0)
        # Fetching Document data
        Documentdata = documentdata.options(
            Load(model.Document).load_only("docheaderID", "PODocumentID", "documentDate", "totalAmount",
                                           "documentStatusID", "sourcetype", "CreatedOn", "documentsubstatusID"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName"),
            inv_choice[inv_type][2], inv_choice[inv_type][3]).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True)
        if inv_type == "ser":
            Documentdata = Documentdata.join(model.ServiceAccount,
                                             model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
                                             isouter=True).join(
                model.ServiceProvider,
                model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
                isouter=True).filter(model.Document.supplierAccountID.isnot(None))
        else:
            Documentdata = Documentdata.join(
                model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
                isouter=True).join(model.Vendor,
                                   model.Vendor.idVendor == model.VendorAccount.vendorID,
                                   isouter=True).filter(model.Document.vendorAccountID.isnot(None))
        Documentdata = Documentdata.order_by(model.Document.CreatedOn.desc()).all()
        return {"ok": {"Documentdata": Documentdata}}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_inv_list", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


async def read_doc_inv_rejected_list(u_id, sp_id, ven_id, usertype, inv_type, db):
    """
    This function reads document invoice list, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
    :param ven_id: It is a function parameters that is of integer type, it provides the vendor Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        # sub query to get only user accessable entities
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id,
                                                                                   isActive=1).distinct()
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        # base query to fetch invoice data
        inv_choice = {"ser": (
            model.ServiceProvider, model.ServiceAccount, Load(model.ServiceProvider).load_only("ServiceProviderName"),
            Load(model.ServiceAccount).load_only("Account")), "ven": (
            model.VendorAccount, model.Vendor, Load(model.Vendor).load_only("VendorName", "Address"),
            Load(model.VendorAccount).load_only("Account"))}
        data = db.query(model.Document, model.DocumentHistoryLogs,
                        func.max(model.DocumentHistoryLogs.iddocumenthistorylog), doc_status, model.Entity,
                        model.EntityBody, inv_choice[inv_type][0],
                        inv_choice[inv_type][1]).filter(user_type_filter[usertype]).filter(
            model.Document.documentStatusID == 10).filter(
            model.Document.idDocument == model.DocumentHistoryLogs.documentID).filter(
            model.DocumentHistoryLogs.documentStatusID == 10).filter(model.DocumentHistoryLogs.documentID)
        # filters for query parameters
        if sp_id:
            sub_query = db.query(model.ServiceAccount.idServiceAccount).filter_by(
                serviceProviderID=sp_id)
            data = data.filter(model.Document.supplierAccountID.in_(sub_query))
        if ven_id:
            sub_query = db.query(model.VendorAccount.idVendorAccount).filter_by(
                vendorID=ven_id)
            data = data.filter(model.Document.vendorAccountID.in_(sub_query))
        # podata filters
        documentdata = data.filter(model.Document.idDocumentType == 3, model.Document.documentStatusID != 0)
        # Fetching Document data
        Documentdata = documentdata.options(
            Load(model.Document).load_only("docheaderID", "PODocumentID", "documentDate", "totalAmount",
                                           "documentStatusID", "sourcetype", "CreatedOn", "documentsubstatusID","sender"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName"),
            inv_choice[inv_type][2], inv_choice[inv_type][3]).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True)
        if inv_type == "ser":
            Documentdata = Documentdata.join(model.ServiceAccount,
                                             model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
                                             isouter=True).join(
                model.ServiceProvider,
                model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
                isouter=True).filter(model.Document.supplierAccountID.isnot(None))
        else:
            Documentdata = Documentdata.join(
                model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
                isouter=True).join(model.Vendor,
                                   model.Vendor.idVendor == model.VendorAccount.vendorID,
                                   isouter=True).filter(model.Document.vendorAccountID.isnot(None))
        Documentdata = Documentdata.order_by(model.DocumentHistoryLogs.CreatedOn.desc()).group_by(
            model.DocumentHistoryLogs.iddocumenthistorylog).all()
        return {"ok": {"Documentdata": Documentdata}}

    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_inv_list", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


async def read_doc_grn_exception_list(u_id, usertype, db):
    try:
        # sub query to get only user accessible entities
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id,
                                                                                   isActive=1).distinct()
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        # base query to fetch invoice data
        # base query to fetch invoice data
        data = db.query(model.Document, doc_status, model.Entity,
                        model.EntityBody, model.VendorAccount,
                        model.Vendor, model.GrnReupload).filter(user_type_filter[usertype]).filter(
            model.Document.documentStatusID == 10)
        # grn exception invoice filter
        documentdata = data.filter(model.Document.idDocumentType == 3, model.Document.documentsubstatusID == 41)
        # Fetching Document data
        Documentdata = documentdata.options(
            Load(model.Document).load_only("docheaderID", "PODocumentID", "documentDate", "totalAmount",
                                           "documentStatusID", "sourcetype", "CreatedOn", "documentsubstatusID"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName"), Load(model.Vendor).load_only("VendorName", "Address"),
            Load(model.VendorAccount).load_only("Account"),
            Load(model.GrnReupload).load_only("grnreuploadID", "GRNNumber", "RejectDescription")).filter(
            model.Document.idDocument == model.GrnReupload.documentIDInvoice)
        # joins between tables
        Documentdata = Documentdata.join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).join(model.Vendor,
                               model.Vendor.idVendor == model.VendorAccount.vendorID,
                               isouter=True).filter(model.Document.vendorAccountID.isnot(None))
        # ordering the data based on created on date
        Documentdata = Documentdata.order_by(model.Document.CreatedOn.desc()).all()
        return {"ok": {"Documentdata": Documentdata}}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_inv_list", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})


async def read_doc_grn_list(u_id, ven_id, usertype, db, off_limit, uni_api_filter):
    """

    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
    :param ven_id: It is a function parameters that is of integer type, it provides the vendor Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        offset, limit = off_limit
        offset = (offset - 1) * limit
        if offset < 0:
            return Response(status_code=403, headers={"ClientError": "please provide right offset value"})
        # sub query to get only user accessable entities
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id).distinct()
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        # get grn total count
        grn_count = db.query(func.count(model.Document.idDocument)).filter(model.Document.idDocumentType == 2,
                                                                           model.Document.documentStatusID != 0).filter(
            user_type_filter[usertype]).scalar()
        # base query to fetch invoice data
        grndata = db.query(model.Document).filter(user_type_filter[usertype]).options(
            load_only("docheaderID", "documentDate", "totalAmount", "PODocumentID")).filter(
            model.Document.idDocumentType == 2).filter(model.Document.documentStatusID != 0)
        if uni_api_filter:
            grndata = grndata.filter((model.Document.docheaderID.like(
                f"%{uni_api_filter}%") | model.Document.documentDate.like(
                f"%{uni_api_filter}%") | model.Document.totalAmount.like(
                f"%{uni_api_filter}%") | model.Document.PODocumentID.like(
                f"%{uni_api_filter}%")))
        return {"grndata": grndata.limit(
            limit).offset(offset).all(), "grn_total": grn_count}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_grn_list", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


# time being
async def read_invoice_list_for_vendor(u_id, sp_id, ven_id, inv_type, db):
    """
    This function reads the invoice list, contains following parameters
    :u_id: It is a function parameters that is of integer type, it provides the user Id.
    :sp_id : It is a function parameter that is of integer type, it provides the Service provider id.
    :db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        sub_query1 = db.query(model.VendorUser.vendorID).filter_by(idVendorUser=u_id).distinct()
        sub_query2 = db.query(model.VendorAccount.idVendorAccount).filter_by(vendorID=sub_query1).distinct()
        data = db.query(model.Document, model.Entity, model.EntityBody, model.ServiceProvider, model.ServiceAccount,
                        model.VendorAccount, model.Vendor).filter(
            model.Document.vendorAccountID.in_(sub_query2))
        # filters for query parameters
        if sp_id:
            sub_query = db.query(model.ServiceAccount.idServiceAccount).filter_by(
                serviceProviderID=sp_id)
            data = data.filter(model.Document.supplierAccountID.in_(sub_query))
        if ven_id:
            sub_query = db.query(model.VendorAccount.idVendorAccount).filter_by(
                vendorID=ven_id)
            data = data.filter(model.Document.vendorAccountID.in_(sub_query))
        # podata filters
        podata = data.filter(model.Document.idDocumentType == 1)
        invoicedata = data.filter(model.Document.idDocumentType == 3)
        podata = podata.options(
            Load(model.Document).load_only("docheaderID", "documentDate", "totalAmount"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName", "Address"),
            Load(model.ServiceProvider).load_only("ServiceProviderName"),
            Load(model.ServiceAccount).load_only("idServiceAccount"),
            Load(model.Vendor).load_only("VendorName"), Load(model.VendorAccount).load_only("Account")).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True).join(
            model.ServiceAccount,
            model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
            isouter=True).join(
            model.ServiceProvider, model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
            isouter=True).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).join(model.Vendor,
                               model.Vendor.idVendor == model.VendorAccount.vendorID,
                               isouter=True).all()
        # Fetching invoice data
        invoicedata = invoicedata.options(
            Load(model.Document).load_only("idDocument", "idDocumentType", "docheaderID",
                                           "documentStatusID", "CreatedOn"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName", "Address"),
            Load(model.ServiceProvider).load_only("ServiceProviderName"),
            Load(model.ServiceAccount).load_only("idServiceAccount"),
            Load(model.Vendor).load_only("VendorName"), Load(model.VendorAccount).load_only("Account")).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True).join(
            model.ServiceAccount,
            model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
            isouter=True).join(
            model.ServiceProvider, model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
            isouter=True).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).join(model.Vendor,
                               model.Vendor.idVendor == model.VendorAccount.vendorID,
                               isouter=True).all()
        return {"ok": {"invoicedata": invoicedata}, "podata": podata}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_list_for_vendor", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


async def read_doc_grn_list_for_vendor(u_id, sp_id, ven_id, db):
    """

    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
    :param ven_id: It is a function parameters that is of integer type, it provides the vendor Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        sub_query1 = db.query(model.VendorUser.vendorID).filter_by(idVendorUser=u_id).distinct()
        sub_query2 = db.query(model.VendorAccount.idVendorAccount).filter_by(
            vendorID=sub_query1.scalar_subquery()).distinct()
        grndata = db.query(model.Document).options(
            load_only("docheaderID", "documentDate", "totalAmount", "CreatedOn")).filter(
            model.Document.vendorAccountID.in_(sub_query2)).filter(model.Document.idDocumentType == 2).all()
        return {"grndata": grndata}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_grn_list_for_vendor", str(e))
        return Response(status_code=500, headers={"codeError": f"Server Error{str(traceback.format_exc())}"})
    finally:
        db.close()


async def read_invoice_data(u_id, inv_id, db):
    """
    This function reads the invoice list, contains following parameters
    :u_id: It is a function parameters that is of integer type, it provides the user Id.
    :inv_id : It is a function parameter that is of integer type, it provides the invoice id.
    :db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        servicedata = ""
        vendordata = ""
        # getting invoice data for later operation
        invdat = db.query(model.Document).options(
            load_only("docPath", "supplierAccountID", "vendorAccountID")).filter_by(
            idDocument=inv_id).one()

        # provide service provider details
        if invdat.supplierAccountID:
            servicedata = db.query(model.ServiceProvider, model.ServiceAccount).options(
                Load(model.ServiceProvider).load_only("ServiceProviderName", "ServiceProviderCode",
                                                      "LocationCode", "City", "Country"),
                Load(model.ServiceAccount).load_only("Account", "Email", "MeterNumber")).filter(
                model.ServiceAccount.idServiceAccount == invdat.supplierAccountID).join(model.ServiceAccount,
                                                                                        model.ServiceAccount.serviceProviderID == model.ServiceProvider.idServiceProvider,
                                                                                        isouter=True).all()

        # provide vendor details
        if invdat.vendorAccountID:
            vendordata = db.query(model.Vendor, model.VendorAccount).options(
                Load(model.Vendor).load_only("VendorName", "VendorCode", "Email", "Contact", "TradeLicense",
                                             "VATLicense",
                                             "TLExpiryDate", "VLExpiryDate", "TRNNumber"),
                Load(model.VendorAccount).load_only("AccountType", "Account")).filter(
                model.VendorAccount.idVendorAccount == invdat.vendorAccountID).join(model.VendorAccount,
                                                                                    model.VendorAccount.vendorID == model.Vendor.idVendor,
                                                                                    isouter=True).all()
        # provide header deatils of invoce
        headerdata = db.query(model.DocumentData, model.DocumentTagDef, model.DocumentUpdates).options(
            Load(model.DocumentData).load_only("Value", "isError", "ErrorDesc", "IsUpdated", "Xcord", "Ycord", "Width",
                                               "Height"),
            Load(model.DocumentTagDef).load_only("TagLabel"),
            Load(model.DocumentUpdates).load_only("OldValue", "UpdatedOn")).filter(
            model.DocumentData.documentTagDefID == model.DocumentTagDef.idDocumentTagDef,
            model.DocumentData.documentID == inv_id).join(
            model.DocumentUpdates,
            model.DocumentUpdates.documentDataID == model.DocumentData.idDocumentData,
            isouter=True).filter(
            or_(model.DocumentData.IsUpdated == 0, model.DocumentUpdates.IsActive == 1))
        headerdata = headerdata.all()
        # provide linedetails of invoice, add this later , "isError", "IsUpdated"
        # to get the unique line item tags
        subquery = db.query(model.DocumentLineItems.lineItemtagID).filter_by(documentID=inv_id).distinct()
        # get all the related line tags description
        doclinetags = db.query(model.DocumentLineItemTags).options(load_only("TagName")).filter(
            model.DocumentLineItemTags.idDocumentLineItemTags.in_(subquery)).all()
        # form a line item structure
        for row in doclinetags:
            linedata = db.query(model.DocumentLineItems, model.DocumentUpdates).options(
                Load(model.DocumentLineItems).load_only("Value", "IsUpdated", "isError",
                                                        "ErrorDesc", "Xcord", "Ycord", "Width",
                                                        "Height","itemCode"),
                Load(model.DocumentUpdates).load_only("OldValue", "UpdatedOn")).filter(
                model.DocumentLineItems.lineItemtagID == row.idDocumentLineItemTags,
                model.DocumentLineItems.documentID == inv_id).join(
                model.DocumentUpdates,
                model.DocumentUpdates.documentLineItemID == model.DocumentLineItems.idDocumentLineItems,
                isouter=True).filter(
                or_(model.DocumentLineItems.IsUpdated == 0, model.DocumentUpdates.IsActive == 1)).all()
            row.linedata = linedata
        return {"ok": {"vendordata": vendordata, "servicedata": servicedata, "headerdata": headerdata,
                       "linedata": doclinetags}}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_data", str(e))
        return Response(status_code=500, headers={"codeError": "Server Error"})
    finally:
        db.close()


async def read_invoice_file(u_id, inv_id, db):
    try:
        content_type = "application/pdf"
        # getting invoice data for later operation
        invdat = db.query(model.Document).options(
            load_only("docPath", "supplierAccountID", "vendorAccountID")).filter_by(
            idDocument=inv_id).one()
        # check if file path is present and give base64 coded image url
        if invdat.docPath:
            try:
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                fr_data = db.query(model.FRConfiguration).options(
                    load_only("ConnectionString", "ContainerName", "ServiceContainerName")).filter_by(
                    idCustomer=cust_id).one()
                # Create the BlobServiceClient object which will be used to create a container client
                blob_service_client = BlobServiceClient.from_connection_string(fr_data.ConnectionString)
                if invdat.supplierAccountID:
                    blob_client = blob_service_client.get_blob_client(container=fr_data.ContainerName,
                                                                      blob=invdat.docPath)
                if invdat.vendorAccountID:
                    blob_client = blob_service_client.get_blob_client(container=fr_data.ContainerName,
                                                                      blob=invdat.docPath)

                # invdat.docPath = str(list(blob_client.download_blob().readall()))
                try:
                    filetype = os.path.splitext(invdat.docPath)[1]
                    if filetype == ".png":
                        content_type = "image/png"
                    elif filetype == ".jpg" or filetype == ".jpeg":
                        content_type = "image/jpg"
                    else:
                        content_type = "application/pdf"
                except:
                    pass
                invdat.docPath = base64.b64encode(blob_client.download_blob().readall())
            except:
                invdat.docPath = ""

        return {"result": {"filepath": invdat.docPath, "content_type": content_type}}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_file", str(e))
        return Response(status_code=500, headers={"codeError": "Server Error"})


async def read_po_data(u_id, inv_id, db):
    try:
        poheaderdata = db.query(model.DocumentData, model.DocumentTagDef).options(
            Load(model.DocumentData).load_only("Value", "isError", "ErrorDesc", "IsUpdated", "Xcord", "Ycord", "Width",
                                               "Height"),
            Load(model.DocumentTagDef).load_only("TagLabel")).filter(
            model.DocumentData.documentTagDefID == model.DocumentTagDef.idDocumentTagDef,
            model.DocumentData.documentID == inv_id).filter(model.Document.idDocumentType == 1)

        vendordata = db.query(model.Vendor).options(load_only("VendorName", "VendorCode")).filter(
            model.Document.idDocument == inv_id,
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount).filter(
            model.VendorAccount.vendorID == model.Vendor.idVendor).filter(
            model.Document.idDocumentType == 1)
        vendoraccountdata = db.query(model.VendorAccount).options(load_only("AccountType", "Account")).filter(
            model.Document.idDocument == inv_id,
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount).filter(
            model.Document.idDocumentType == 1)

        return {"result": {"headerdata": poheaderdata.all(), "vendordata": vendordata.all()},
                "vendoraccountdata": vendoraccountdata.all()}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_po_data", str(e))
        return Response(status_code=500, headers={"codeError": "Server Error"})
    finally:
        db.close()


async def update_invoice_data(u_id, inv_id, inv_data, db):
    """
    This function update the invoice line item data, contains following parameters
    :u_id: It is a function parameters that is of integer type, it provides the user Id.
    :inv_id : It is a function parameter that is of integer type, it provides the invoice id.
    :param inv_data: It is Body parameter that is of a Pydantic type object, It takes member data for updating of new invoice line item.
    :db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # avoid data updates by other users if in lock
        user_id = db.query(model.Document.lock_user_id).filter_by(idDocument=inv_id).scalar()
        if user_id != u_id:
            return Response(status_code=403, headers={"ClientError": "get Lock on invoice to update"})
        dt = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        for row in inv_data:
            try:
                # check to see if the document id and document data are related
                if row.documentDataID:
                    db.query(model.DocumentData).filter_by(documentID=inv_id, idDocumentData=row.documentDataID)
                else:
                    db.query(model.DocumentLineItems).filter_by(documentID=inv_id,
                                                                idDocumentLineItems=row.documentLineItemID)
            except Exception as e:
                applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py update_invoice_data", str(e))
                return Response(status_code=403, headers={"ClientError": "invoice and value mismatch"})
            # to check if the document update already has a any rows present in it
            inv_up_id = db.query(model.DocumentUpdates.idDocumentUpdates).filter_by(
                documentDataID=row.documentDataID).all()
            if len(inv_up_id) > 0:
                # if present set active status to false for old row
                if row.documentDataID:
                    db.query(model.DocumentUpdates).filter_by(documentDataID=row.documentDataID, IsActive=1).update(
                        {"IsActive": 0})
                else:
                    db.query(model.DocumentUpdates).filter_by(documentLineItemID=row.documentLineItemID,
                                                              IsActive=1).update({"IsActive": 0})
            data = dict(row)
            data["IsActive"] = 1
            data["updatedBy"] = u_id
            data["UpdatedOn"] = dt
            data = model.DocumentUpdates(**data)
            if row.documentDataID:
                doc_table_match = {"InvoiceTotal": "totalAmount", "InvoiceDate": "documentDate",
                                   "InvoiceId": "docheaderID", "PurchaseOrder": "PODocumentID"}
                tag_def_inv_id = db.query(model.DocumentData.documentTagDefID, model.DocumentData.documentID).filter_by(
                    idDocumentData=row.documentDataID).one()
                label = db.query(model.DocumentTagDef.TagLabel).filter_by(
                    idDocumentTagDef=tag_def_inv_id.documentTagDefID).scalar()
                # to update the document if header data is updated
                if label in doc_table_match.keys():
                    db.query(model.Document).filter_by(idDocument=tag_def_inv_id.documentID).update(
                        {doc_table_match[label]: data.NewValue})
                db.query(model.DocumentData).filter_by(idDocumentData=row.documentDataID).update(
                    {"IsUpdated": 1, "Value": data.NewValue})
            else:
                db.query(model.DocumentLineItems).filter_by(idDocumentLineItems=row.documentLineItemID).update(
                    {"IsUpdated": 1, "Value": data.NewValue})
            db.add(data)
        # last updated time stamp
        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"UpdatedOn": datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")})
        db.commit()
        return {"result": "success"}
    except Exception as ex:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py update_invoice_data", str(ex))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close


async def update_column_pos(u_id, tabtype, col_data, bg_task, db):
    """
    This function update column position of the tab, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param tabtype: It is a function parameters that is of string type, it provides the type of tab.
    :param col_data: It is a function parameters that is of Pydantic type, It provides column data for updating column
    position.
    :param db:It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        UpdatedOn = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        for items in col_data:
            items = dict(items)
            items["UpdatedOn"] = UpdatedOn
            items["documentColumnPos"] = items.pop("ColumnPos")
            result = db.query(model.DocumentColumnPos).filter_by(idDocumentColumn=items.pop("idtabColumn")).filter_by(
                userID=u_id).filter_by(tabtype=model_col[tabtype]).update(items)
        db.commit()
        try:
            ############ start of notification trigger #############
            cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
            user_details = db.query(model.User).options(load_only("email", "firstName", "lastName")).filter_by(
                idUser=u_id).one()
            details = {"user_id": None, "trigger_code": 8006, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {
                           "recipients": [(user_details.email, user_details.firstName, user_details.lastName)],
                           "subject": "User Details Update"}}
            # bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print("no users")
        return {"result": "updated"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py update_column_pos", str(e))
        return Response(status_code=403, headers={f"{traceback.format_exc()}clientError": "update failed"})
    finally:
        db.close


async def reset_column_pos(u_id, tabtype, bg_task, db):
    """
    This function resets the column position of tab with preset values, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param tabtype: It is a function parameters that is of string type, it provides the type of tab.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:

        result = db.execute(f"call resetusercolpos({u_id}, {model_col[tabtype]},  @res_result)")
        db.commit()
        try:
            ############ start of notification trigger #############
            cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
            user_details = db.query(model.User).options(load_only("email", "firstName", "lastName")).filter_by(
                idUser=u_id).one()
            details = {"user_id": None, "trigger_code": 8006, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {
                           "recipients": [(user_details.email, user_details.firstName, user_details.lastName)],
                           "subject": "User Details Update"}}
            # bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print("no users")
        return {"result": "updated"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py reset_column_pos", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def read_column_pos(u_id, tabtype, db):
    """
    This function reads the column position of a given tab type, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param tabtype: It is a function parameters that is of string type, it provides the type of tab.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        column_data = db.query(model.DocumentColumnPos, model.ColumnPosDef).filter_by().options(
            Load(model.DocumentColumnPos).load_only("documentColumnPos", "isActive"),
            Load(model.ColumnPosDef).load_only("columnName", "columnDescription", "dbColumnname")).filter(
            model.DocumentColumnPos.columnNameDefID == model.ColumnPosDef.idColumn,
            model.DocumentColumnPos.userID == u_id, model.DocumentColumnPos.tabtype == model_col[tabtype]).all()
        return {"col_data": column_data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_column_pos", str(e))
        return Response(status_code=500, headers={"Error": f"Server Error {traceback.format_exc()}"})
    finally:
        db.close


async def get_role_priority(u_id, db):
    try:
        sub_query = db.query(model.AccessPermission.permissionDefID).filter_by(userID=u_id)
        # return priority
        return db.query(model.AccessPermissionDef.Priority).filter_by(
            idAccessPermissionDef=sub_query.scalar_subquery()).scalar()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py get_role_priority", str(e))
        return 0


async def read_vendor_invoice_list_edited(u_id, db):
    """
    This function reads the invoice list for the edited tab, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # sub query to get only user accessable entities
        sub_query_ent = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        # review invoices
        invoices = db.query(model.Document, model.VendorAccount, model.Vendor, model.DocumentHistoryLogs).options(
            Load(model.Document).load_only("idDocument", "docheaderID", "vendorAccountID",
                                           "documentDate",
                                           "totalAmount", "UpdatedOn"),
            Load(model.VendorAccount).load_only("Account"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.Vendor).load_only("VendorName")).filter(model.Document.documentStatusID == 4,
                                                               model.Document.idDocumentType == 3).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).filter(model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.DocumentHistoryLogs.documentStatusID == 4).filter(
            model.DocumentHistoryLogs.documentID == model.Document.idDocument).filter(
            model.Document.vendorAccountID.isnot(None)).filter(model.Document.documentsubstatusID.is_(None)).all()

        # in progress invoices
        stat_id = 5
        # sub query to get log id for specific status and last record
        sub_query = db.query(
            func.min(model.DocumentHistoryLogs.iddocumenthistorylog).label("iddocumenthistorylog")).filter(
            model.DocumentHistoryLogs.documentStatusID == stat_id).group_by(
            model.DocumentHistoryLogs.documentID)
        # to get in progress data
        # get documents from user of lower roles and hide documents of higher roles
        logs_list = db.query(model.DocumentHistoryLogs).options(load_only("userID", "documentID")).filter_by(
            documentStatusID=stat_id).all()
        doc_id_in_prog_list = []
        current_user_priority = await get_role_priority(u_id, db)
        for row in logs_list:
            user_priority = await get_role_priority(row.userID, db)
            # priority comparison
            if user_priority <= current_user_priority:
                doc_id_in_prog_list.append(row.documentID)
        inprogress = db.query(model.Document, model.VendorAccount, model.Vendor, model.DocumentHistoryLogs,
                              func.concat(model.User.firstName, " ", func.ifnull(model.User.lastName, "")).label(
                                  "assigned_to")).options(
            Load(model.Document).load_only("idDocument", "docheaderID", "supplierAccountID", "vendorAccountID",
                                           "documentDate",
                                           "totalAmount", "UpdatedOn"),
            Load(model.VendorAccount).load_only("Account"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.Vendor).load_only("VendorName")).filter(
            model.Document.documentStatusID == stat_id, model.Document.idDocumentType == 3).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).filter(model.DocumentHistoryLogs.documentID == model.Document.idDocument).filter(
            model.User.idUser == model.DocumentHistoryLogs.userID).filter(
            model.DocumentHistoryLogs.iddocumenthistorylog.in_(sub_query)).filter(
            model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
            model.Document.entityID.in_(sub_query_ent),
            model.Document.idDocument.in_(tuple(doc_id_in_prog_list))).filter(
            model.Document.vendorAccountID.isnot(None)).filter(model.Document.documentsubstatusID.is_(None)).all()

        # approval needed invoices
        stat_id = 6
        sub_query = db.query(
            func.max(model.DocumentHistoryLogs.iddocumenthistorylog).label("iddocumenthistorylog")).filter(
            model.DocumentHistoryLogs.documentStatusID == stat_id).group_by(
            model.DocumentHistoryLogs.documentID)
        tobeapproved = db.query(model.Document, model.VendorAccount, model.Vendor, model.DocumentHistoryLogs,
                                func.concat(model.User.firstName, " ", func.ifnull(model.User.lastName, "")).label(
                                    "edited_by")).options(
            Load(model.Document).load_only("idDocument", "docheaderID", "supplierAccountID", "vendorAccountID",
                                           "documentDate",
                                           "totalAmount", "UpdatedOn"),
            Load(model.VendorAccount).load_only("Account"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.Vendor).load_only("VendorName")).filter(model.Document.documentStatusID == stat_id,
                                                               model.Document.idDocumentType == 3).join(
            model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
            isouter=True).filter(model.DocumentHistoryLogs.documentID == model.Document.idDocument).filter(
            model.User.idUser == model.DocumentHistoryLogs.userID).filter(
            model.DocumentHistoryLogs.iddocumenthistorylog.in_(sub_query)).filter(
            model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.Document.vendorAccountID.isnot(None)).filter(model.Document.documentsubstatusID.is_(None)).all()
        return {"invoices": invoices, "inprogress": inprogress, "tobeapproved": tobeapproved}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_vendor_invoice_list_edited", str(e))
        return Response(status_code=500, headers={"Error": f"{e}Server Error"})
    finally:
        db.close


async def read_service_invoice_list_edited(u_id, db):
    """
    This function reads the invoice list for the edited tab, contains following parameters
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # sub query to get only user accessable entities
        sub_query_ent = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        # review invoices
        invoices = db.query(model.Document, model.ServiceAccount, model.ServiceProvider, model.ServiceAccount,
                            model.DocumentHistoryLogs).options(
            Load(model.Document).load_only("idDocument", "docheaderID", "supplierAccountID", "documentDate",
                                           "totalAmount", "UpdatedOn"),
            Load(model.ServiceAccount).load_only("Account"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.ServiceProvider).load_only("ServiceProviderName")).filter(model.Document.documentStatusID == 4,
                                                                                 model.Document.documentsubstatusID == 29,
                                                                                 model.Document.idDocumentType == 3).join(
            model.ServiceAccount, model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
            isouter=True).filter(
            model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.DocumentHistoryLogs.documentStatusID == 4).filter(
            model.DocumentHistoryLogs.documentID == model.Document.idDocument).filter(
            model.Document.supplierAccountID.isnot(None)).all()

        # in progress invoices
        stat_id = 5
        # sub query to get log id for specific status and last record
        sub_query = db.query(
            func.max(model.DocumentHistoryLogs.iddocumenthistorylog).label("iddocumenthistorylog")).filter(
            model.DocumentHistoryLogs.documentStatusID == stat_id).group_by(
            model.DocumentHistoryLogs.documentID)
        # to get in progress data
        # get documents from user of lower roles and hide documents of higher roles
        logs_list = db.query(model.DocumentHistoryLogs).options(load_only("userID", "documentID")).filter_by(
            documentStatusID=stat_id).all()
        doc_id_in_prog_list = []
        current_user_priority = await get_role_priority(u_id, db)
        for row in logs_list:
            user_priority = await get_role_priority(row.userID, db)
            # priority comparison
            if user_priority <= current_user_priority:
                doc_id_in_prog_list.append(row.documentID)
        inprogress = db.query(model.Document, model.ServiceAccount, model.ServiceProvider, model.DocumentHistoryLogs,
                              func.concat(model.User.firstName, " ", func.ifnull(model.User.lastName, "")).label(
                                  "assigned_to")).options(
            Load(model.Document).load_only("idDocument", "docheaderID", "supplierAccountID", "documentDate",
                                           "totalAmount", "UpdatedOn"),
            Load(model.ServiceAccount).load_only("Account"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.ServiceProvider).load_only("ServiceProviderName")).filter(
            model.Document.documentStatusID == stat_id, model.Document.idDocumentType == 3).join(
            model.ServiceAccount, model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
            isouter=True).filter(model.DocumentHistoryLogs.documentID == model.Document.idDocument).filter(
            model.User.idUser == model.DocumentHistoryLogs.userID).filter(
            model.DocumentHistoryLogs.iddocumenthistorylog.in_(sub_query)).filter(
            model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID).filter(
            model.Document.entityID.in_(sub_query_ent),
            model.Document.idDocument.in_(tuple(doc_id_in_prog_list))).filter(
            model.Document.supplierAccountID.isnot(None)).all()

        # approval needed invoices
        stat_id = 6
        sub_query = db.query(
            func.max(model.DocumentHistoryLogs.iddocumenthistorylog).label("iddocumenthistorylog")).filter(
            model.DocumentHistoryLogs.documentStatusID == stat_id).group_by(
            model.DocumentHistoryLogs.documentID)
        tobeapproved = db.query(model.Document, model.ServiceAccount, model.ServiceProvider, model.DocumentHistoryLogs,
                                func.concat(model.User.firstName, " ", func.ifnull(model.User.lastName, "")).label(
                                    "edited_by")).options(
            Load(model.Document).load_only("idDocument", "docheaderID", "supplierAccountID", "documentDate",
                                           "totalAmount", "UpdatedOn"),
            Load(model.ServiceAccount).load_only("Account"),
            Load(model.DocumentHistoryLogs).load_only("documentdescription"),
            Load(model.ServiceProvider).load_only("ServiceProviderName")).filter(
            model.Document.documentStatusID == stat_id,
            model.Document.idDocumentType == 3).join(
            model.ServiceAccount, model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
            isouter=True).filter(model.DocumentHistoryLogs.documentID == model.Document.idDocument).filter(
            model.User.idUser == model.DocumentHistoryLogs.userID).filter(
            model.DocumentHistoryLogs.iddocumenthistorylog.in_(sub_query)).filter(
            model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.Document.supplierAccountID.isnot(None)).all()
        return {"invoices": invoices, "inprogress": inprogress, "tobeapproved": tobeapproved}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_service_invoice_list_edited", str(e))
        return Response(status_code=500, headers={"Error": f"{e}Server Error"})
    finally:
        db.close


async def action_center_invoice(u_id, usertype, doc_types, data_type, db, user_ids=None, inv_cat=None):
    """
    This function reads the invoice for action center tab, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param doc_types: It is a function parameters that is of tuple type, it provides the status types of document needed to be
    read.
    :param data_type: It is a function parameter that is of string type, it identifies the data which is being returned.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :param user_ids: It is a optional function parameter, to filter based on document ids, default value None.
    :return: It return a result of dict type.
    """
    try:
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id).distinct()
        # filter dictionary to get service or vendor invoice
        inv_catg = {"ser": (model.ServiceProvider, model.ServiceAccount, "ServiceProviderName"),
                    "ven": (model.Vendor, model.VendorAccount, "VendorName")}
        sub_query_desc = db.query(
            func.max(model.DocumentHistoryLogs.iddocumenthistorylog).label("iddocumenthistorylog")).filter(
            model.DocumentHistoryLogs.documentStatusID.in_(doc_types)).group_by(
            model.DocumentHistoryLogs.documentID)
        # create case statement
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}

        data = db.query(model.Document, doc_status, model.Entity, model.EntityBody,
                        inv_catg[inv_cat][0], inv_catg[inv_cat][1], model.User,
                        model.DocumentHistoryLogs.documentdescription, approval_type, model.Rule).filter(
            user_type_filter[usertype]).filter(model.Document.documentStatusID.in_(doc_types)).filter(
            model.DocumentHistoryLogs.iddocumenthistorylog.in_(sub_query_desc))

        # check if document ids filter has to be applied
        if user_ids != 1 and user_ids:
            # pass
            # filter already approved docs
            remove_doc_ids = db.query(model.DocumentHistoryLogs.documentID).filter(
                (model.DocumentHistoryLogs.documentfinstatus.in_((0, 1))), model.DocumentHistoryLogs.userID == u_id)
            # return remove_doc_ids
            docidsprevuser = db.query(model.DocumentHistoryLogs.documentID).filter(
                model.DocumentHistoryLogs.userID.in_(user_ids)).filter(
                model.DocumentHistoryLogs.documentfinstatus == 0).distinct()
            data = data.filter(model.DocumentHistoryLogs.documentID.in_(docidsprevuser)).filter(
                model.Document.idDocument.not_in(remove_doc_ids))
        # done to get invoices for least priority users
        elif user_ids == 1:
            remove_doc_ids = db.query(model.DocumentHistoryLogs.documentID).filter_by(userID=u_id,
                                                                                      documentStatusID=2
                                                                                      ).filter(
                model.DocumentHistoryLogs.documentfinstatus == 0)
            data = data.filter(model.Document.idDocument.not_in(remove_doc_ids))

        # have to add invoice number ,po number and amount
        data = data.options(
            Load(model.Document).load_only("docheaderID", "documentStatusID", "UpdatedOn", "documentDate",
                                           "totalAmount"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName", "Address"),
            Load(model.User).load_only("firstName", "lastName"),
            Load(inv_catg[inv_cat][0]).load_only(inv_catg[inv_cat][2]),
            Load(inv_catg[inv_cat][1]).load_only("Account"), Load(model.Rule).load_only("Name")).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True)
        if inv_cat == "ven":
            data = data.join(model.VendorAccount, model.VendorAccount.idVendorAccount == model.Document.vendorAccountID,
                             isouter=True).join(model.Vendor, model.Vendor.idVendor == model.VendorAccount.vendorID,
                                                isouter=True).filter(model.Document.vendorAccountID.isnot(None))
        if inv_cat == "ser":
            data = data.join(model.ServiceAccount,
                             model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID,
                             isouter=True).join(model.ServiceProvider,
                                                model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
                                                isouter=True).filter(model.Document.supplierAccountID.isnot(None))
        data = data.join(model.DocumentHistoryLogs, model.DocumentHistoryLogs.documentID == model.Document.idDocument,
                         isouter=True).join(model.User, model.User.idUser == model.DocumentHistoryLogs.userID,
                                            isouter=True).join(model.DocumentSubStatus,
                                                               model.Document.documentsubstatusID == model.DocumentSubStatus.idDocumentSubstatus,
                                                               isouter=True).join(model.Rule,
                                                                                  model.Document.ruleID == model.Rule.Name,
                                                                                  isouter=True).all()

        return {data_type: data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py action_center_invoice", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def read_invoice_list_approved(u_id, usertype, inv_cat, db):
    """
    This function reads invoice list for approved tab, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        if usertype != 1:
            return Response(status_code=403, headers={"Error": "Unknown user type"})
        # select all user ids whose priority is less then the current user
        current_user_priority = await get_role_priority(u_id, db)
        # get one level lower priority
        low_one_priority = db.query(model.AccessPermissionDef.Priority).filter(
            model.AccessPermission.permissionDefID == model.AccessPermissionDef.idAccessPermissionDef).filter(
            model.AccessPermissionDef.Priority < current_user_priority).filter(
            model.AccessPermissionDef.amountApprovalID.isnot(None)).limit(1).distinct().scalar()
        user_ids = db.query(model.AccessPermission.userID).filter(
            model.AccessPermission.permissionDefID == model.AccessPermissionDef.idAccessPermissionDef).filter(
            model.AccessPermissionDef.Priority == low_one_priority).filter(
            model.AccessPermissionDef.amountApprovalID.isnot(None)).all()
        if len(user_ids) == 0:
            user_ids = 1
        else:
            user_ids = tuple(x[0] for x in user_ids)
        return await action_center_invoice(u_id, usertype, (2,), "approved", db, user_ids=user_ids, inv_cat=inv_cat)
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_list_approved", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def setdochistorylog(u_id, inv_id, stat_id, dochist, db):
    """
    This function saves the status of the invoice thus preserving its history , contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param stat_id:
    :param dochist:  It is a function parameters that is of dict type, it provides the description and amount which are
    optional.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of 1 integer type.
    """
    # return dochist["documentdescription"]
    if dochist["documentdescription"] is None or "documentdescription" not in dochist.keys():
        user_name = db.query(model.User.firstName, model.User.lastName).filter_by(idUser=u_id).one()
        description = {
            1: f"Edit approved by user {user_name[0] if user_name[0] else ''} {user_name[1] if user_name[1] else ''}",
            5: f"Invoice assigned to id {user_name[0] if user_name[0] else ''} {user_name[1] if user_name[1] else ''}",
            6: f"Invoice edited by user id {user_name[0] if user_name[0] else ''} {user_name[1] if user_name[1] else ''}"}
        dochist["documentdescription"] = description[stat_id]
    try:
        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"UpdatedOn": datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"), "documentStatusID": stat_id})
        dochist["documentID"] = inv_id
        dochist["documentStatusID"] = stat_id
        dochist["userID"] = u_id
        dochist["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        dochist = model.DocumentHistoryLogs(**dochist)
        db.add(dochist)
        db.commit()
        return 1
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py setdochistorylog", str(e))
        return None
    finally:
        db.close()


async def assign_invoice_to_user(u_id, inv_id, bg_task, db):
    """
    This function assigns the invoice to the user, and moves it to in progress queue , contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        dochist = {"documentdescription": None}
        if await setdochistorylog(u_id, inv_id, 5, dochist, db):
            try:
                ############ start of notification trigger #############
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                user_details = db.query(model.User).options(load_only("email", "firstName", "lastName")).filter_by(
                    idUser=u_id).one()
                details = {"user_id": [u_id], "trigger_code": 8020, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {
                               "recipients": [(user_details.email, user_details.firstName, user_details.lastName)],
                               "subject": "Invoice Assignment", "ffirstName": user_details.firstName,
                               "llastName": user_details.lastName}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("no users")
            return {"result": "updated"}
        return {"result": "failed"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py assign_invoice_to_user", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def submit_invoice(u_id, inv_id, dochist, bg_task, db):
    """
    This function moves the invoice to approved queue once the invoice is edited, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param dochist: It is a function parameters that is of dict type, it provides the description and amount which are
    optional.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # simple db operation to update the status of invoice to edit approve
        if await setdochistorylog(u_id, inv_id, 6, dochist, db):
            try:
                ############ start of notification trigger #############
                entityID = db.query(model.Document.entityID).filter_by(idDocument=inv_id).scalar()
                recepients = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID, isActive=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                user_details = db.query(model.User).options(load_only("email", "firstName", "lastName")).filter_by(
                    idUser=u_id).one()
                details = {"user_id": user_ids, "trigger_code": 8003, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {
                               "recipients": email_ids,
                               "subject": "Invoice Acceptation", "ffirstName": user_details.firstName,
                               "llastName": user_details.lastName}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("no users")
            return {"result": "updated"}
        return {"result": "failed"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py submit_invoice", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def approve_invoice(u_id, inv_id, dochist, bg_task, db):
    """
    This function is used to approve the edited invoice, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param dochist: It is a function parameters that is of dict type, it provides the description and amount which are
    optional.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        if await setdochistorylog(u_id, inv_id, 1, dochist, db):
            try:
                ############ start of notification trigger #############
                entityID = db.query(model.Document.entityID).filter_by(idDocument=inv_id).scalar()
                recepients = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID, isActive=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                details = {"user_id": user_ids, "trigger_code": 8021, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {"subject": "Invoice Edit Approval", "recipients": email_ids}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("no users")
            return {"result": "invoice approved"}
        return {"result": "invoice approve failed"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py approve_invoice", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def read_invoice_list_vendor(u_id, ven_id, db):
    """
    This function is used to read invoice list for a Vendor, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param ven_id: It is a function parameters that is of integer type, it provides the vendor Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # offset, limit = off_limit
        # off_val = (offset - 1) * limit
        # if off_val < 0:
        #     return Response(status_code=403, headers={"ClientError": "please provide right offset value"})
        sub_query1 = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        sub_query2 = db.query(model.VendorAccount.idVendorAccount).filter_by(vendorID=ven_id).distinct()
        data = db.query(model.Document, doc_status, model.Entity, model.EntityBody,
                        model.VendorAccount, model.Vendor).filter(
            model.Document.entityID.in_(sub_query1)).filter(model.Document.vendorAccountID.in_(sub_query2)).filter(
            model.Document.idDocumentType == 3).filter(model.Document.documentStatusID != 0)
        # have to add invoice number ,po number and amount
        data = data.options(
            Load(model.Document).load_only("docheaderID", "PODocumentID", "documentStatusID", "UpdatedOn",
                                           "documentDate",
                                           "totalAmount"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName", "Address"),
            Load(model.Vendor).load_only("VendorName"), Load(model.VendorAccount).load_only("Account")).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True).join(
            model.VendorAccount,
            model.VendorAccount.idVendorAccount == model.Document.vendorAccountID, isouter=True).join(model.Vendor,
                                                                                                      model.Vendor.idVendor == model.VendorAccount.vendorID,
                                                                                                      isouter=True)
        # .limit(
        # limit).offset(offset).all()
        return {"data": data.all()}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_list_vendor", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close


async def read_invoice_list_serviceprovider(u_id, sp_id, db):
    """
    This function is used to read invoice list for a service provider, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # offset, limit = off_limit
        # off_val = (offset - 1) * limit
        # if off_val < 0:
        #     return Response(status_code=403, headers={"ClientError": "please provide right offset value"})
        # sub query one, to get distinct entity it
        sub_query1 = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        # sub query two, to get the distinct service account id[db unique key]
        sub_query2 = db.query(model.ServiceAccount.idServiceAccount).filter_by(serviceProviderID=sp_id).distinct()
        data = db.query(model.Document, model.Entity, model.EntityBody,
                        model.ServiceAccount, model.ServiceProvider, doc_status).filter(
            model.Document.entityID.in_(sub_query1)).filter(model.Document.supplierAccountID.in_(sub_query2)).filter(
            model.Document.idDocumentType == 3)
        # have to add invoice number ,po number and amount
        data = data.options(
            Load(model.Document).load_only("docheaderID", "documentStatusID", "UpdatedOn", "documentDate",
                                           "totalAmount"),
            Load(model.Entity).load_only("EntityName"),
            Load(model.EntityBody).load_only("EntityBodyName", "Address"),
            Load(model.ServiceProvider).load_only("ServiceProviderName"),
            Load(model.ServiceAccount).load_only("Account")).join(
            model.Entity,
            model.Entity.idEntity == model.Document.entityID, isouter=True).join(model.EntityBody,
                                                                                 model.EntityBody.idEntityBody == model.Document.entityBodyID,
                                                                                 isouter=True).join(
            model.ServiceAccount,
            model.ServiceAccount.idServiceAccount == model.Document.supplierAccountID, isouter=True).join(
            model.ServiceProvider,
            model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID,
            isouter=True)
        # .limit(limit).offset(offset)
        return {"data": data.all()}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_list_serviceprovider", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close


async def read_invoice_grn_ready(u_id, db):
    try:

        # sub query one, to get distinct entity it
        ent_ids = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1)
        data = db.query(model.Document, model.Vendor).options(
            Load(model.Document).load_only("docheaderID", "CreatedOn", "PODocumentID", "totalAmount"),
            Load(model.Vendor).load_only("VendorName")).filter(
            model.Document.entityID.in_(ent_ids), model.Document.idDocumentType == 3,
            model.Document.vendorAccountID.is_not(None), model.Document.documentStatusID == 4,
                                                  model.Document.documentsubstatusID == 35).filter(
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount,
            model.VendorAccount.vendorID == model.Vendor.idVendor).all()
        return {"result": data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_list_serviceprovider", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})


async def read_invoice_grn_ready_data(u_id, inv_id, db):
    try:
        ent_ids = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1)
        # getting invoice data for later operation
        invdat = db.query(model.Document).options(
            load_only("vendorAccountID", "PODocumentID", "docheaderID")).filter_by(
            idDocument=inv_id).filter(model.Document.entityID.in_(ent_ids)).one()
        po_doc_id = db.query(model.Document.idDocument).filter_by(docheaderID=invdat.PODocumentID).scalar()
        grn_id = db.query(model.Document.idDocument).filter(model.Document.idDocumentType == 2,
                                                            model.Document.docheaderID == f"GRN-{invdat.docheaderID}").scalar()
        # provide vendor details
        if invdat.vendorAccountID:
            vendordata = db.query(model.Vendor, model.VendorAccount).options(
                Load(model.Vendor).load_only("VendorName", "VendorCode", "Email", "Contact", "TradeLicense",
                                             "VATLicense",
                                             "TLExpiryDate", "VLExpiryDate", "TRNNumber"),
                Load(model.VendorAccount).load_only("AccountType", "Account")).filter(
                model.VendorAccount.idVendorAccount == invdat.vendorAccountID).join(model.VendorAccount,
                                                                                    model.VendorAccount.vendorID == model.Vendor.idVendor,
                                                                                    isouter=True).all()
            # provide header deatils of invoce
            headerdata = db.query(model.DocumentData, model.DocumentTagDef).options(
                Load(model.DocumentData).load_only("Value"),
                Load(model.DocumentTagDef).load_only("TagLabel")).filter(
                model.DocumentData.documentTagDefID == model.DocumentTagDef.idDocumentTagDef,
                model.DocumentData.documentID == inv_id)
            headerdata = headerdata.all()
            # provide linedetails of invoice, add this later , "isError", "IsUpdated"
            # to get the unique line item tags
            subquery = db.query(model.DocumentLineItems.lineItemtagID).filter_by(documentID=inv_id).distinct()
            # get all the related line tags description
            doclinetags = db.query(model.DocumentLineItemTags).options(load_only("TagName")).filter(
                model.DocumentLineItemTags.idDocumentLineItemTags.in_(subquery),
                model.DocumentLineItemTags.TagName.in_(("Description", "Quantity", "UnitPrice", "AmountExcTax"))).all()
            # get po line item description
            po_mod_id = db.query(model.Document.idDocument, model.Document.documentModelID).filter(
                model.Document.docheaderID == invdat.PODocumentID, model.Document.idDocumentType == 1).one()
            line_tag_id = db.query(model.DocumentLineItemTags.idDocumentLineItemTags).filter(
                model.DocumentLineItemTags.TagName == 'Name',
                model.DocumentLineItemTags.idDocumentModel == po_mod_id.documentModelID).scalar()
            po_desciption_items = db.query(model.DocumentLineItems.Value,
                                           model.DocumentLineItems.itemCode).filter(
                model.DocumentLineItems.documentID == po_mod_id.idDocument,
                model.DocumentLineItems.lineItemtagID == line_tag_id).all()
            po_desc_dict = {}
            for row in po_desciption_items:
                po_desc_dict[row.itemCode] = row.Value
            # po_item_codes = list(po_desc_dict.keys())
            # form a line item structure
            for idx, row in enumerate(doclinetags):
                grn_linedata = None
                linedata = db.query(model.DocumentLineItems).options(
                    load_only("Value", "invoice_itemcode", "ErrorDesc")).filter(
                    model.DocumentLineItems.lineItemtagID == row.idDocumentLineItemTags,
                    model.DocumentLineItems.documentID == inv_id)
                if row.TagName == "Description":
                    linedata = linedata.filter(model.DocumentLineItems.invoice_itemcode.in_(list(po_desc_dict.keys())))
                    row.linedata = linedata.all()
                    for line_row in row.linedata:
                        line_row.POValue = po_desc_dict[line_row.invoice_itemcode]
                        is_mapped = db.query(model.ItemUserMap.batcherrortype).filter_by(
                            mappedinvoiceitemcode=line_row.invoice_itemcode, documentID=inv_id).scalar()
                        if is_mapped:
                            line_row.is_mapped = 1
                        else:
                            line_row.is_mapped = 0
                else:
                    row.linedata = linedata.all()
                itemcodes = []
                for item_code in linedata:
                    if item_code.invoice_itemcode not in itemcodes:
                        itemcodes.append(item_code.invoice_itemcode)
                    del item_code.invoice_itemcode
                    item_code.ErrorDesc = ""
                if row.TagName == "Quantity":
                    # get pending po quantity data
                    po_qty_details = db.query(model.DocumentLineItemTags.TagName, model.DocumentLineItems.Value).filter(
                        model.DocumentLineItemTags.TagName.in_(("PurchQty", "RemainInventPhysical"))).filter(
                        model.DocumentLineItems.documentID == po_doc_id).filter(
                        model.DocumentLineItems.itemCode.in_(itemcodes)).join(
                        model.DocumentLineItemTags,
                        model.DocumentLineItems.lineItemtagID == model.DocumentLineItemTags.idDocumentLineItemTags,
                        isouter=True).all()
                    row.podata = po_qty_details
                if grn_id:
                    grn_linedata = db.query(model.DocumentLineItems).options(
                        load_only("Value", "ErrorDesc")).filter(
                        model.DocumentLineItems.lineItemtagID == row.idDocumentLineItemTags,
                        model.DocumentLineItems.documentID == grn_id).all()
                else:
                    grn_linedata = row.linedata
                row.grndata = grn_linedata
            return {"ok": {"vendordata": vendordata, "headerdata": headerdata,
                           "linedata": doclinetags, }}
        return {"ok": "no data"}
    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_grn_data", str(e))
        return Response(status_code=500, headers={"codeError": "Server Error"})
    finally:
        db.close()


async def save_invoice_grn_data(u_id, inv_id, save_type, grn_data, bg_task, db):
    try:
        ent_ids = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1)
        # getting invoice data for later operation
        inv_meta_data = db.query(model.Document).filter_by(
            idDocument=inv_id).filter(model.Document.entityID.in_(ent_ids)).one()
        invoice_id = f"GRN-{inv_meta_data.docheaderID}"
        grn_exists = db.query(model.Document.idDocument).filter(
            model.Document.docheaderID == invoice_id,
            model.Document.idDocumentType == 2).scalar()
        beyond_threshold = 0
        if grn_exists:
            for row in grn_data:
                row = dict(row)
                if "old_value" in row.keys():
                    old_value = row.pop("old_value")
                    try:
                        old_value = float(old_value)
                    except Exception as e:
                        old_value = None
                if "is_quantity" in row.keys() and row.pop("is_quantity") and old_value is not None:
                    model_id = db.query(model.Document.documentModelID).filter_by(idDocument=inv_id).scalar_subquery()
                    qty_threshold = db.query(model.FRMetaData.QtyTol_percent).filter_by(
                        idInvoiceModel=model_id).scalar()
                    limit_quantity_max = old_value + (old_value / (100 / float(qty_threshold)))
                    limit_quantity_min = old_value - (old_value / (100 / float(qty_threshold)))
                    grn_tty = float(row["Value"])
                    if grn_tty > limit_quantity_max or grn_tty < limit_quantity_min:
                        beyond_threshold = 1
                        # return Response(status_code=403,
                        #                 headers={"ClientError": "invoice quantity beyond threshold"})
                row["UpdatedDate"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                db.query(model.DocumentLineItems).filter_by(documentID=grn_exists,
                                                            idDocumentLineItems=row.pop("idDocumentLineItems")).update(
                    row)
            db.commit()
        else:
            crt_time = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
            new_grn_doc = {"idDocumentType": 2, "documentModelID": inv_meta_data.documentModelID,
                           "entityID": inv_meta_data.entityID, "entityBodyID": inv_meta_data.entityBodyID,
                           "vendorAccountID": inv_meta_data.vendorAccountID,
                           "docheaderID": f"GRN-{inv_meta_data.docheaderID}",
                           "PODocumentID": inv_meta_data.PODocumentID, "documentStatusID": 0,
                           "CreatedOn": crt_time, "UpdatedOn": crt_time}
            new_grn_doc = model.Document(**new_grn_doc)
            db.add(new_grn_doc)
            db.flush()
            header_data = db.query(model.DocumentData).filter_by(documentID=inv_id).all()
            for row in header_data:
                grn_header = {"documentID": new_grn_doc.idDocument, "documentTagDefID": row.documentTagDefID,
                              "Value": row.Value, "CreatedOn": crt_time}
                grn_header = model.DocumentData(**grn_header)
                db.add(grn_header)
            for row in grn_data:
                row = dict(row)
                inv_lineItem = db.query(model.DocumentLineItems.lineItemtagID,
                                        model.DocumentLineItems.invoice_itemcode).filter_by(
                    idDocumentLineItems=row["idDocumentLineItems"], documentID=inv_id).one()
                if "old_value" in row.keys():
                    old_value = row.pop("old_value")
                    try:
                        old_value = float(old_value)
                    except Exception as e:
                        old_value = None
                if "is_quantity" in row.keys() and row.pop("is_quantity") and old_value is not None:
                    model_id = db.query(model.Document.documentModelID).filter_by(idDocument=inv_id).scalar_subquery()
                    qty_threshold = db.query(model.FRMetaData.QtyTol_percent).filter_by(
                        idInvoiceModel=model_id).scalar()
                    limit_quantity_max = old_value + (old_value / (100 / float(qty_threshold)))
                    limit_quantity_min = old_value - (old_value / (100 / float(qty_threshold)))
                    grn_tty = float(row["Value"])
                    if grn_tty > limit_quantity_max or grn_tty < limit_quantity_min:
                        beyond_threshold = 1
                        # return Response(status_code=403,
                        #                 headers={"ClientError": "invoice quantity beyond threshold"})
                grn_line = {"documentID": new_grn_doc.idDocument, "lineItemtagID": inv_lineItem.lineItemtagID,
                            "invoice_itemcode": inv_lineItem.invoice_itemcode, "Value": row["Value"],
                            "CreatedDate": crt_time, "ErrorDesc": row["ErrorDesc"]}
                grn_line = model.DocumentLineItems(**grn_line)
                db.add(grn_line)
            db.commit()
            grn_exists = new_grn_doc.idDocument
        if save_type and grn_exists:
            rejectdatetime = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
            description = "GRN Saving or Creation"
            erp_doc_status = 20
            inv_doc_status = (4, 39)
            if beyond_threshold:
                description = "Auto Reject due to GRN QTY Mismatch"
                erp_doc_status = 21
                inv_doc_status = (10, 41)
                grn_reupload = {"InvoiceId": inv_meta_data.docheaderID, "POnumber": inv_meta_data.PODocumentID,
                                "RejectDescription": description, "GRNNumber": invoice_id,
                                "RejectDateTime": rejectdatetime, "RejectStatus": 1,
                                "documentIDInvoice": inv_meta_data.idDocument,
                                "documentIDgrn": grn_exists, "entityID": inv_meta_data.entityID}
                grn_reupload = model.GrnReupload(**grn_reupload)
                db.add(grn_reupload)
            db.query(model.Document).filter_by(idDocument=inv_id).update(
                {"documentStatusID": inv_doc_status[0], "documentsubstatusID": inv_doc_status[1]})
            db.query(model.Document).filter_by(idDocument=grn_exists).update(
                {"documentStatusID": erp_doc_status})
            document_history = {"documentID": inv_id, "documentdescription": description, "userID": u_id,
                                "documentStatusID": inv_doc_status[0], "documentSubStatusID": inv_doc_status[1],
                                "CreatedOn": rejectdatetime}
            document_history = model.DocumentHistoryLogs(**document_history)
            db.add(document_history)
            try:
                ############ start of notification trigger #############
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                # get vendor account id
                ven_acc_id = db.query(model.Document.vendorAccountID).filter(
                    model.Document.idDocument == inv_id).scalar_subquery()
                # get all ven user ids for that ven account access
                ven_uids = db.query(model.VendorUserAccess.vendorUserID).filter(
                    model.VendorUserAccess.vendorAccountID == ven_acc_id, model.VendorUserAccess.isActive == 1)
                # get user details to send mail
                recepients = db.query(models.User.idUser, models.User.email, models.User.firstName,
                                      models.User.lastName).filter(models.User.idUser.in_(ven_uids)).filter(
                    models.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                # get data for test comments to be displayed
                # get item code to get specific row from table
                item_codes = db.query(model.DocumentLineItems.invoice_itemcode).filter(
                    model.DocumentLineItems.ErrorDesc != '').filter(
                    model.DocumentLineItems.documentID == grn_exists).distinct()
                linedata = db.query(model.DocumentLineItems, model.DocumentLineItemTags).options(
                    Load(model.DocumentLineItems).load_only("Value", "ErrorDesc"),
                    Load(model.DocumentLineItemTags).load_only("TagName")).filter(
                    model.DocumentLineItems.lineItemtagID == model.DocumentLineItemTags.idDocumentLineItemTags,
                    model.DocumentLineItems.documentID == grn_exists).filter(
                    model.DocumentLineItems.invoice_itemcode.in_(item_codes)).filter(
                    model.DocumentLineItemTags.TagName.in_(("Description", "Quantity")))
                linedata = linedata.all()
                table_row = {}
                for rowvalue, row_tagname in linedata:
                    if row_tagname.TagName in table_row.keys():
                        table_row[row_tagname.TagName].append(rowvalue.Value)
                        if row_tagname.TagName == "Quantity":
                            table_row["Comments"].append(rowvalue.ErrorDesc)
                    else:
                        table_row[row_tagname.TagName] = [rowvalue.Value]
                        if row_tagname.TagName == "Quantity":
                            table_row["Comments"] = [rowvalue.ErrorDesc]
                table_val = [x for x in table_row.values()]
                trigger_code = 8031
                details = {"user_id": None, "trigger_code": trigger_code, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {
                               "recipients": email_ids,
                               "subject": "Grn Creation", "table_head": list(table_row.keys())}}
                if beyond_threshold:
                    trigger_code = 8032
                    details["additional_details"]["table_data"] = list(zip(table_val[0], table_val[1], table_val[2]))
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("no users")
            db.commit()
            if beyond_threshold:
                return {"result": ["GRN Created, but invoice is rejected due to Quantity Mismatch", 2]}
            return {"result": ["GRN Created Successfully", 1]}
        return {"result": ["GRN Saved", 0]}
    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py reject_invoice_it", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})


async def reject_invoice_it(u_id, inv_id, dochist, bg_task, db):
    """
    This function is used to reject invoice doc to In progress queue, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param dochist: It is a function parameters that is of dict type, it provides the description and amount which are
    optional.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        if await setdochistorylog(u_id, inv_id, 5, dochist, db):
            try:
                ############ start of notification trigger #############
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                prev_u_id = db.query(model.DocumentHistoryLogs.userID).filter(documentID=inv_id).order_by(
                    model.DocumentHistoryLogs.iddocumenthistorylog.desc()).limit(1).scalar()
                user_details = db.query(model.User).options(load_only("email", "firstName", "lastName")).filter_by(
                    idUser=prev_u_id).one()
                reject_user_details = db.query(model.User).options(load_only("firstName", "lastName")).filter_by(
                    idUser=u_id).one()
                details = {"user_id": [prev_u_id], "trigger_code": 8022, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {
                               "recipients": [(user_details.email, user_details.firstName, user_details.lastName)],
                               "subject": "Invoice IT Rejection", "ffirstName": reject_user_details.firstName,
                               "llastName": reject_user_details.lastName}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("no users")
            return {"result": "rejected to it"}
        return {"result": "rejected to it failed"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py reject_invoice_it", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def reject_invoice_ven(u_id, inv_id, dochist, bg_task, db):
    """
    This function is used to reject invoice doc to In vendor portal review queue, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param dochist: It is a function parameters that is of dict type, it provides the description and amount which are
    optional.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        comment = dochist["documentdescription"]
        if await setdochistorylog(u_id, inv_id, 10, dochist, db):
            try:
                ############ start of notification trigger #############
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                entityID = db.query(model.Document.entityID).filter_by(idDocument=inv_id).scalar()
                sender = db.query(model.Document.sender).filter_by(idDocument=inv_id).scalar()
                recepients1 = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID, isActive=1).distinct()
                ven_acc_id = db.query(model.Document.vendorAccountID).filter_by(idDocument=inv_id).scalar()
                recepients2 = db.query(model.VendorUserAccess.vendorUserID).filter_by(isActive=1,
                                                                                      vendorAccountID=ven_acc_id).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter(
                    (model.User.idUser.in_(recepients1) | model.User.idUser.in_(recepients2))).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                if sender:
                    email_ids.append((sender, "Serina", "User"))
                user_details = db.query(model.User).options(load_only("email", "firstName", "lastName")).filter_by(
                    idUser=u_id).one()
                details = {"user_id": user_ids, "trigger_code": 8023, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {
                               "recipients": email_ids,
                               "subject": "Invoice Vendor Rejection", "ffirstName": user_details.firstName,
                               "llastName": user_details.lastName, "comment": comment}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("No users")
            return {"result": "rejected to Vendor"}
        return {"result": "rejected to Vendor failed"}
    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py reject_invoice_ven", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def read_invoice_payment_status(u_id, usertype, db):
    """
    This function is used to read payment status for invoice, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dict type.
    """
    try:
        # sub query to get the enitity access, later entity body can be added
        # if user type is customer
        if usertype == 1:
            sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        else:
            sub_query = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id).distinct()
        # create case statement
        user_type_filter = {1: model.Document.entityID.in_(sub_query), 2: model.Document.vendorAccountID.in_(sub_query)}
        payment_case = case(
            [
                (model.Document.documentStatusID == 7, "Payment Pending"),
                (model.Document.documentStatusID == 8, "Payment Cleared")
            ]
        ).label("documentPaymentStatus")
        # apply the filter to get invoice which are financially approved and payments completed
        data = db.query(model.Document.docheaderID, model.Document.documentStatusID, model.Document.PODocumentID,
                        model.Document.documentDate, model.Document.totalAmount, model.Entity.EntityName).filter(

            user_type_filter[usertype]

        ).join(model.Entity, model.Entity.idEntity == model.Document.entityID, isouter=True).filter(

            model.Document.idDocumentType == 3, model.Document.documentStatusID.in_((7, 14)))
        return {"data": data.all()}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_payment_status", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def read_vendor_rejected_invoices(u_id, usertype, db):
    """
    This function is used to read payment status for invoice, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        return await action_center_invoice(u_id, usertype, (10, 11), "rejected", db, inv_cat="ven")
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_vendor_rejected_invoices", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def read_pending_invoices(u_id, usertype, db):
    """
    This function is used to read pending invoice for vendor portal, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        return await action_center_invoice(u_id, usertype, (1, 2, 3, 4, 5, 6, 7), "pending", db, inv_cat="ven")
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_pending_invoices", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def read_vendor_approved_invoices(u_id, usertype, db):
    """
    This function is used to read invoices financially approved by the customer , contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param usertype: It is a function parameters that is of integer type, it provides the user type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        return await action_center_invoice(u_id, usertype, (8,), "approved", db, inv_cat="ven")
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_vendor_approved_invoices", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close


async def read_invoice_status_history(u_id, inv_id, db):
    """
    This function is used to read invoice history logs, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        doc_status_hist = case(
            [
                (and_(model.DocumentHistoryLogs.documentStatusID == 4, model.DocumentHistoryLogs.documentSubStatusID == 29),model.DocumentHistoryLogs.documentdescription),
                (model.DocumentHistoryLogs.documentStatusID == 0, "Invoice Uploaded"),
                (model.DocumentHistoryLogs.documentStatusID == 2, "Document Processed Successfully"),
                (model.DocumentHistoryLogs.documentStatusID == 3, "Finance Approval Completed"),
                (model.DocumentHistoryLogs.documentSubStatusID == 35, "Ready For GRN Creation"),
                (model.DocumentHistoryLogs.documentSubStatusID == 39, "GRN Created in Serina"),
                (model.DocumentHistoryLogs.documentSubStatusID == 37, "GRN Created in ERP"),
                (and_(model.DocumentHistoryLogs.documentSubStatusID == 3,model.DocumentHistoryLogs.documentStatusID == None), "OCR Error Corrected"),
                (and_(model.DocumentHistoryLogs.documentSubStatusID == 3,model.DocumentHistoryLogs.documentStatusID == 1), "Invoice Submitted for Batch"),
                (model.DocumentHistoryLogs.documentStatusID == 5, "Edit in Progress"),
                (model.DocumentHistoryLogs.documentStatusID == 6, "Awaiting Edit Approval"),
                (model.DocumentHistoryLogs.documentStatusID == 7, "Sent to ERP"),
                (model.DocumentHistoryLogs.documentStatusID == 8, "Payment Cleared"),
                (model.DocumentHistoryLogs.documentStatusID == 9, "Payment Partially Paid"),
                (model.DocumentHistoryLogs.documentStatusID == 10, "Invoice Rejected"),
                (model.DocumentHistoryLogs.documentStatusID == 11, "Payment Rejected"),
                (model.DocumentHistoryLogs.documentStatusID == 12, "PO Open"),
                (model.DocumentHistoryLogs.documentStatusID == 13, "PO Closed"),
                (model.DocumentHistoryLogs.documentStatusID == 14, "Posted In ERP"),
                (model.DocumentHistoryLogs.documentStatusID == 16, "Invoice Upload"),
                (model.DocumentHistoryLogs.documentStatusID == 17, "Edit Rule"),
                (model.DocumentHistoryLogs.documentStatusID == 18, "Approved Rule"),
                (model.DocumentHistoryLogs.documentStatusID == 19, "ERP Updated"),
                (model.DocumentHistoryLogs.documentStatusID == 21, "GRN Invoice Rejected")
            ]
        ).label("dochistorystatus")
        doc_fin_status = case(
            [
                (model.DocumentHistoryLogs.documentfinstatus == 0, "Partially Approved"),
                (model.DocumentHistoryLogs.documentfinstatus == 1, "Completely Approved")
            ], else_='UNKNOWN'
        ).label("documentFinancialStatus")
        return db.query(model.DocumentHistoryLogs, model.User.firstName, model.User.lastName,
                        model.Document.docheaderID, doc_status_hist,
                        doc_fin_status).options(load_only("documentdescription", "userAmount", "CreatedOn")).filter(
            model.DocumentHistoryLogs.documentID == model.Document.idDocument).join(model.User,
                                                                                    model.DocumentHistoryLogs.userID == model.User.idUser,
                                                                                    isouter=True).filter(
            model.Document.idDocument == inv_id).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_invoice_status_history", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close

async def read_doc_data(inv_id,db):
    data = db.query(model.Document.entityID,model.Document.vendorAccountID,model.Document.supplierAccountID,model.Document.documentDate,model.Document.PODocumentID).filter(model.Document.idDocument == inv_id).first()
    entityID = data[0]
    vendoraccountId = data[1]
    supplierAccountId = data[2]
    inv_date = data[3]
    po = data[4]
    grndata = db.query(model.Document.docheaderID).filter(model.Document.PODocumentID == po,model.Document.idDocumentType == 2).first()
    grn = grndata[0] if grndata is not None else ""
    if vendoraccountId is not None:
        vendordata = db.query(model.VendorAccount.vendorID).filter(model.VendorAccount.idVendorAccount == vendoraccountId).first()
        vendor = db.query(model.Vendor.VendorName).filter(model.Vendor.idVendor == vendordata[0]).first()
    if supplierAccountId is not None:
        spdata = db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == supplierAccountId).first()
        vendor = db.query(model.ServiceProvider.ServiceProviderName).filter(model.ServiceProvider.idServiceProvider == spdata[0]).first()
    entity = db.query(model.Entity.EntityName).filter(model.Entity.idEntity == entityID).first()
    return {'Entity':entity[0],'Vendor':vendor[0],'InvoiceDate': inv_date.strftime("%Y-%m-%d %H:%M:%S") if inv_date is not None else "",'PO': po if po is not None else "",'GRN':grn if grn is not None else ""}

async def read_doc_history(inv_id, db):
    """
    This function is used to read invoice history logs, contains following parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that is of integer type, it provides the invoice Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of list type.
    """
    try:
        doc_status_hist = case(
            [
                (and_(model.DocumentHistoryLogs.documentStatusID == 4, model.DocumentHistoryLogs.documentSubStatusID == 29),model.DocumentHistoryLogs.documentdescription),
                (model.DocumentHistoryLogs.documentStatusID == 0, "Invoice Uploaded"),
                (model.DocumentHistoryLogs.documentStatusID == 2, "Document Processed Successfully"),
                (model.DocumentHistoryLogs.documentStatusID == 3, "Finance Approval Completed"),
                (model.DocumentHistoryLogs.documentSubStatusID == 39, "GRN Created in Serina"),
                (model.DocumentHistoryLogs.documentSubStatusID == 37, "GRN Created in ERP"),
                (and_(model.DocumentHistoryLogs.documentSubStatusID == 3,model.DocumentHistoryLogs.documentStatusID == None), "OCR Error Corrected"),
                (and_(model.DocumentHistoryLogs.documentSubStatusID == 3,model.DocumentHistoryLogs.documentStatusID == 1), "Invoice Submitted for Batch"),
                (model.DocumentHistoryLogs.documentStatusID == 10, "Invoice Rejected"),
                (model.DocumentHistoryLogs.documentStatusID == 14, "Posted In ERP")
            ]
        ).label("dochistorystatus")
        doc_fin_status = case(
            [
                (model.DocumentHistoryLogs.documentfinstatus == 0, "Partially Approved"),
                (model.DocumentHistoryLogs.documentfinstatus == 1, "Completely Approved")
            ], else_='UNKNOWN'
        ).label("documentFinancialStatus")
        return db.query(model.DocumentHistoryLogs, model.User.firstName, model.User.lastName,
                        model.Document.docheaderID, doc_status_hist,
                        doc_fin_status).options(load_only("documentdescription", "userAmount", "CreatedOn")).filter(
            model.DocumentHistoryLogs.documentID == model.Document.idDocument).join(model.User,
                                                                                    model.DocumentHistoryLogs.userID == model.User.idUser,
                                                                                    isouter=True).filter(
            model.Document.idDocument == inv_id).all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "InvoiceCrud.py read_doc_history", str(e))
        return Response(status_code=500, headers={"Error": "Server Error"})
    finally:
        db.close

def upload_master_execl_db(u_id, data, db):
    try:
        uploaded_on = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        id = db.query(model.ItemMapUploadHistory.iditemmappinguploadhistory).order_by(
            model.ItemMapUploadHistory.iditemmappinguploadhistory.desc()).limit(1).scalar()
        if id:
            local_file_name = f"itemupload{id + 1}.xlsx"
        else:
            local_file_name = f"itemupload1.xlsx"

        con_details = db.query(model.FRConfiguration.ConnectionString, model.FRConfiguration.ContainerName).filter_by(
            idFrConfigurations=1).one()
        blob_service_client = BlobServiceClient.from_connection_string(con_details.ConnectionString)
        blob_client = blob_service_client.get_blob_client(container=con_details.ContainerName,
                                                          blob=f"itemmasterexcel/{local_file_name}")
        blob_client.upload_blob(data, overwrite=True)
        item_history = {"status": "File Uploaded", "uploaded_file": f"itemmasterexcel/{local_file_name}",
                        "uploaded_datetime": uploaded_on, "uploaded_by": u_id}
        item_history = model.ItemMapUploadHistory(**item_history)
        db.add(item_history)
        db.commit()
        print('pushed file')
    except Exception as e:
        print(traceback.format_exc())


async def upload_mater_item_mapping(u_id, file, bg_task, db):
    try:
        if "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" == file.content_type:
            data = await file.read()
            bg_task.add_task(upload_master_execl_db, u_id, data, db)
        else:
            return Response(status_code=403, headers={"ClientError": "provide excel file with .xlsx extension"})
        return {"result": "uploaded"}
    except Exception as e:
        return {"result": "upload failed"}


async def read_item_master_status(u_id, db):
    try:
        meta_excel_status = db.query(model.ItemMapUploadHistory, model.User).options(
            Load(model.User).load_only("firstName", "lastName")).filter(
            model.ItemMapUploadHistory.uploaded_by == model.User.idUser).order_by(
            model.ItemMapUploadHistory.iditemmappinguploadhistory.desc()).limit(5).all()
        return {"result": meta_excel_status}
    except Exception as e:
        pass


async def download_item_master_error(u_id, item_history_id, db):
    try:
        error_excel = db.query(model.ItemMapUploadHistory.error_file).filter_by(
            iditemmappinguploadhistory=item_history_id).scalar()

        if error_excel:
            con_details = db.query(model.FRConfiguration.ConnectionString,
                                   model.FRConfiguration.ContainerName).filter_by(
                idFrConfigurations=1).one()
            blob_service_client = BlobServiceClient.from_connection_string(con_details.ConnectionString)
            blob_client = blob_service_client.get_blob_client(container=con_details.ContainerName,
                                                              blob=error_excel)
            data = blob_client.download_blob().readall()
            data = BytesIO(data)
            return StreamingResponse(data,
                                     media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            return Response(status_code=403, headers={"ClientError": "no records"})
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})


async def read_document_lock_statu(u_id, inv_id, db):
    try:
        current_datetime = datetime.utcnow()
        lock_info = db.query(model.Document, model.User).options(
            Load(model.Document).load_only("lock_status", "lock_date_time"),
            Load(model.User).load_only("firstName", "lastName")).filter(
            model.Document.idDocument == inv_id).join(model.User, model.User.idUser == model.Document.lock_user_id,
                                                      isouter=True).one()
        if lock_info[0].lock_date_time:
            lock_datetime = lock_info[0].lock_date_time
            if lock_datetime < current_datetime:
                db.query(model.Document).filter_by(idDocument=inv_id).update(
                    {"lock_status": 0, "lock_date_time": None, "lock_user_id": None})
                db.commit()
                lock_info[0].lock_status = 0
                lock_info[0].lock_date_time = ""
        return {"result": lock_info}
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})


async def update_document_lock_statu(u_id, inv_id, session_datetime, db):
    try:
        lock_uid = db.query(model.Document.lock_user_id).filter(
            model.Document.idDocument == inv_id).scalar()
        session_datetime = dict(session_datetime)
        if lock_uid and lock_uid != u_id:
            return Response(status_code=403, headers={"ClientError": "check lock status before updating"})
        else:
            if session_datetime["session_status"]:
                session_time = datetime.utcnow()
                session_time = session_time + timedelta(minutes=5)
                session_time = session_time.strftime("%Y-%m-%d %H:%M:%S")
                db.query(model.Document).filter_by(idDocument=inv_id).update(
                    {"lock_status": 1, "lock_date_time": session_time, "lock_user_id": u_id})
            else:
                session_time = ""
                db.query(model.Document).filter_by(idDocument=inv_id).update(
                    {"lock_status": 0, "lock_date_time": None, "lock_user_id": None})
            db.commit()
            return {"result": "updated", "session_end_time": session_time}
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})

async def deletelineitem(docid,itemcode,db):
    try:
        allids = db.query(model.DocumentLineItems.idDocumentLineItems).filter(model.DocumentLineItems.documentID == docid,model.DocumentLineItems.itemCode == itemcode).all()
        for a in allids:
            db.query(model.DocumentUpdates).filter(model.DocumentUpdates.documentLineItemID == a[0]).delete()
            db.commit()
        db.query(model.DocumentLineItems).filter(model.DocumentLineItems.documentID == docid,model.DocumentLineItems.itemCode == itemcode).delete()
        db.commit()
        return {"status": "deleted","data":{"docid":docid,"itemcode":itemcode}}
    except Exception as e:
        print(traceback.format_exc())
        Response(status_code=500, headers={"Error": "Server error"})

async def checklineitemcode(docid,itemcode,db):
    try:
        check = db.query(model.DocumentLineItems).filter(model.DocumentLineItems.documentID == docid,model.DocumentLineItems.itemCode == itemcode).first()
        if check is None:
            return {"status":"not exists"}
        else:
            return {"status":"exists"}
    except Exception as e:
        print(traceback.format_exc())
        Response(status_code=500, headers={"Error": "Server error"})

async def addLineItem(docinput,db):
    try:
        inp = dict(docinput)
        lineitemtags = db.query(model.DocumentLineItems.lineItemtagID).filter(model.DocumentLineItems.documentID == inp['documentID']).all()
        ids = list(set([l[0] for l in lineitemtags]))
        for i in ids:
            datatoadd = {'lineItemtagID':i,'documentID':inp['documentID'],'itemCode':inp['itemCode'],'UpdatedDate':datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"),'CreatedDate':datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}
            db.add(model.DocumentLineItems(**datatoadd))
            db.commit()
        return {"status":"added","data":inp}
    except Exception as e:
        print(traceback.format_exc())
        Response(status_code=500, headers={"Error": "Server error"})

async def read_item_master_items(u_id, ven_acc_id, db):
    try:
        ent_ids = db.query(model.UserAccess.EntityID).filter_by(isActive=1, UserID=u_id)
        ven_ids = db.query(model.Vendor.idVendor).filter_by(idVendor=ven_acc_id).filter(
            model.Vendor.entityID.in_(ent_ids))
        ven_accs = db.query(model.VendorAccount.idVendorAccount).filter(model.VendorAccount.vendorID.in_(ven_ids))
        item_map_data = db.query(model.ItemMetaData, model.ItemUserMap).options(
            Load(model.ItemMetaData).load_only("itemcode", "description"),
            Load(model.ItemUserMap).load_only("mappedinvoitemdescription")).filter(
            model.ItemMetaData.iditemmetadata == model.ItemUserMap.itemmetadataid).filter(
            model.ItemUserMap.vendoraccountID.in_(ven_accs))
        return {"result": item_map_data.all()}
    except Exception as e:
        print(traceback.format_exc())
        Response(status_code=500, headers={"Error": "Server error"})
