from io import BytesIO
import requests
from fastapi import Depends, APIRouter, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session, Load
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import model
import time
import os
import json
from datetime import datetime
import pytz as tz
from azure.storage.blob import BlobServiceClient
import sys

sys.path.append("..")
from logModule import applicationlogging, email_sender
from session import engine
from session import Session as SessionLocal
from FROps.azure_fr import get_fr_data
from FROps.preprocessing import fr_preprocessing
from FROps.postprocessing import postpro
from FROps.sharepoint_util import getfile_as_base64, uploadutility_file_to_blob
from session import engine
from auth import AuthHandler
from session import SQLALCHEMY_DATABASE_URL
from session.notificationsession import client as mqtt

model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)

router = APIRouter(
    prefix="/apiv1.1/ocr",
    tags=["Live OCR"],
    # dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


docLabelMap = {'InvoiceTotal': 'totalAmount',
               'InvoiceId': 'docheaderID', 'InvoiceDate': 'documentDate'}


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


def runStatus_2(request, db):
    while True:
        yield {
            "event": "update",
            "retry": 3000,
            "data": str(time.time())
        }
        time.sleep(10)

        # break


@router.post("/status/saveutility")
async def saveutility(request: Request, db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        filepath = req_body['filepath']
        filename = req_body['filename']
        resp = requests.get(filepath)
        file_content = BytesIO(resp.content).getvalue()
        message = uploadutility_file_to_blob(filename, file_content, db)
        return {"message": message}
    except Exception as e:
        print(e)
        return {"message": "exception"}


@router.get('/status/stream_2')
async def runStatus_1(request: Request, db: Session = Depends(get_db)):
    event_generator = runStatus_2(request, db)
    return EventSourceResponse(event_generator)


status_stream_delay = 1  # second
status_stream_retry_timeout = 30000  # milisecond


@router.get('/status/stream')
async def runStatus(eventSourceObj: str, request: Request, bg_task: BackgroundTasks,
                    db: Session = Depends(get_db)):
    eventSourceObj = json.loads(eventSourceObj)
    file_path = eventSourceObj['file_path']
    vendorAccountID = eventSourceObj['vendorAccountID']
    poNumber = eventSourceObj['poNumber']
    VendoruserID = eventSourceObj['VendoruserID']
    filename = eventSourceObj['filename']
    filetype = eventSourceObj['filetype']
    source = eventSourceObj['source']
    sender = eventSourceObj['sender']
    configs = getOcrParameters(1, db)
    metadata = getMetaData(vendorAccountID, db)
    entityID = eventSourceObj['entityID']
    modelData, modelDetails = getModelData(vendorAccountID, db)
    if modelData is None:
        subject = f'Model Not Trained For {filename}!'
        body = f"""
        <html>
            <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                <strong>Error Summary</strong>: <i>Model not Trained</i>
                <div style="margin-top: 2%;"></div>
                <table border="1" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <th>Description</th>
                        <th>Sender</th>
                        <th>Date & Time</th>
                    </tr>
                    <tr>
                        <td>Model not onboarded to system</td>
                        <td>{sender}</td>
                        <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        email_sender.send_mail("serinaplus.dev@datasemantics.co", sender, subject, body)
        gen = nomodelfound()
        return EventSourceResponse(gen)
    print(f"got Model {modelData.modelID}, model Name {modelData.modelName}")
    ruledata = getRuleData(modelData.idDocumentModel, db)
    folder_name = modelData.folderPath
    id_check = modelData.idDocumentModel
    containername = configs.ContainerName
    connection_str = configs.ConnectionString
    entityBody = db.query(model.EntityBody).filter(model.EntityBody.EntityID == entityID).first()
    entityBodyID = entityBody.idEntityBody
    file_size_accepted = 50
    accepted_file_type = metadata.InvoiceFormat.split(",")
    date_format = metadata.DateFormat
    endpoint = configs.Endpoint
    apim_key = configs.Key1
    inv_model_id = modelData.modelID
    API_version = configs.ApiVersion
    ts = str(time.time())
    if inv_model_id is None:
        ############ start of notification trigger #############
        try:
            vendor = db.query(model.Vendor.VendorName).filter(
                model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
            # filter based on role if added
            role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                    notificationTypeID=2).scalar()
            # getting recipients for sending notification
            recepients = db.query(model.AccessPermission.userID).filter(
                model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
            recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                  model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                model.User.isActive == 1).filter(model.UserAccess.UserID == model.User.idUser).filter(
                model.UserAccess.EntityID == entityID, model.UserAccess.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            try:
                isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                        model.NotificationCategoryRecipient.notificationrecipient).filter(
                    model.NotificationCategoryRecipient.entityID == entityID,
                    model.NotificationCategoryRecipient.notificationTypeID == 2).one()
            except Exception as e:
                pass
            cc_email_ids = []
            if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                    isdefaultrep.notificationrecipient["to_addr"]) > 0:
                email_ids.extend([(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]

            cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
            details = {"user_id": None, "trigger_code": 7009, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"subject": "Invoice Model Issue", "recipients": email_ids,
                                              "Vendor_Name": vendor,
                                              "modelID": inv_model_id, "recipients": email_ids, "cc": cc_email_ids}}
            bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print(e)
    blob_fld_name = str(folder_name.split('/')[0]) + '/temp'
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=connection_str, container_name=containername)
    container_client = blob_service_client.get_container_client(containername)
    file_path_on_azure = os.path.join(blob_fld_name, str(
        ts.replace(".", "_") + '_' + filename.split('/')[-1]))
    file_path_on_azure = file_path_on_azure.replace("\\", "/")
    resp = requests.get(file_path)
    data = BytesIO(resp.content)
    blob_client = container_client.upload_blob(name=file_path_on_azure, data=data)
    generatorObj = {
        'request': request,
        'filepath': file_path,
        'accepted_file_type': accepted_file_type,
        'file_size_accepted': file_size_accepted,
        'apim_key': apim_key,
        'API_version': API_version,
        'endpoint': endpoint,
        'inv_model_id': inv_model_id,
        'entityID': entityID,
        'entityBodyID': entityBodyID,
        'vendorAccountID': vendorAccountID,
        'poNumber': poNumber,
        'modelDetails': modelDetails,
        'date_format': date_format,
        'file_path_on_azure': file_path_on_azure,
        'VendoruserID': VendoruserID,
        'ruleID': ruledata.ruleID,
        'filetype': filetype,
        'filename': filename,
        'db': db,
        'source': source,
        'sender': sender
    }
    event_generator = live_model_fn_1(generatorObj, bg_task)
    return EventSourceResponse(event_generator)


def nomodelfound():
    current_status = {"percentage": 0, "status": "Model not Found!"}
    yield {
        "event": "end",
        "data": json.dumps(current_status)
    }


def getModelData(vendorAccountID, db):
    modelDetails = []
    modelData = db.query(model.DocumentModel).filter(model.DocumentModel.idVendorAccount == vendorAccountID).order_by(
        model.DocumentModel.UpdatedOn).all()
    reqModel = None
    for m in modelData:
        if m.modelID is not None and m.modelID != "":
            reqModel = m
            modelDetails.append({'IdDocumentModel': m.idDocumentModel, 'modelName': m.modelName})
    return reqModel, modelDetails


def getEntityData(vendorAccountID, db):
    entitydata = db.query(model.VendorAccount).options(
        Load(model.VendorAccount).load_only("entityID", "entityBodyID", "vendorID")).filter(
        model.VendorAccount.idVendorAccount == vendorAccountID).first()
    return entitydata


def getMetaData(vendorAccountID, db):
    metadata = db.query(model.FRMetaData).join(model.DocumentModel,
                                               model.FRMetaData.idInvoiceModel == model.DocumentModel.idDocumentModel).filter(
        model.DocumentModel.idVendorAccount == vendorAccountID).first()
    return metadata


def getRuleData(idDocumentModel, db):
    ruledata = db.query(model.FRMetaData).filter(model.FRMetaData.idInvoiceModel == idDocumentModel).first()
    return ruledata


def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "OCR.py getOcrParameters", str(e))
        return Response(status_code=500, headers={"DB Error": "Failed to get OCR parameters"})


def live_model_fn_1(generatorObj, bg_task):
    request = generatorObj['request']
    file_path = generatorObj['filepath']
    accepted_file_type = generatorObj['accepted_file_type']
    file_size_accepted = generatorObj['file_size_accepted']
    apim_key = generatorObj['apim_key']
    API_version = generatorObj['API_version']
    endpoint = generatorObj['endpoint']
    inv_model_id = generatorObj['inv_model_id']
    entityID = generatorObj['entityID']
    entityBodyID = generatorObj['entityBodyID']
    vendorAccountID = generatorObj['vendorAccountID']
    poNumber = generatorObj['poNumber']
    modelDetails = generatorObj['modelDetails']
    date_format = generatorObj['date_format']
    file_path_on_azure = generatorObj['file_path_on_azure']
    userID = generatorObj['VendoruserID']
    ruledata = generatorObj['ruleID']
    filetype = generatorObj['filetype']
    filename = generatorObj['filename']
    sender = generatorObj['sender']
    db = generatorObj['db']
    source = generatorObj['source']
    fr_data = {}
    fr_preprocessing_status, fr_preprocessing_msg, input_data, ui_status = fr_preprocessing(vendorAccountID, entityID,
                                                                                            file_path,
                                                                                            accepted_file_type,
                                                                                            file_size_accepted,
                                                                                            filename, bg_task, db)
    if fr_preprocessing_status == 1:
        current_status = {"percentage": 25, "status": "Pre-Processing ⏳"}
        yield {
            "event": "update",
            "retry": status_stream_retry_timeout,
            "data": json.dumps(current_status)
        }
        valid_file = False
        if filetype == 'image/jpg' or filetype == 'image/jpeg' or filetype == 'image/png' or filetype == 'application/pdf':
            valid_file = True

        if valid_file == True:
            live_model_status = 0
            live_model_msg = "Please upload jpg or pdf file"
        model_type = 'custom'
        cst_model_status, cst_model_msg, cst_data, cst_status, isComposed, template = get_fr_data(input_data, filetype,
                                                                                                  apim_key,
                                                                                                  API_version,
                                                                                                  endpoint,
                                                                                                  model_type,
                                                                                                  inv_model_id)

        if isComposed == False:
            modelID = modelDetails[-1]['IdDocumentModel']
        else:
            modeldict = next(x for x in modelDetails if x["modelName"].lower() == template.lower())
            modelID = modeldict['IdDocumentModel']
        subject = f'Rove Hotel Dev:  Model Captured for {filename}!'
        body = f"""
        <html>
            <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                <strong>Summary</strong>: <i>Model Details</i>
                <div style="margin-top: 2%;"></div>
                <table border="1" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <th>Description</th>
                        <th>Sender</th>
                        <th>Composed</th>
                        <th>Id Document Model</th>
                        <th>Template</th>
                        <th>Date & Time</th>
                    </tr>
                    <tr>
                        <td>Model capture details</td>
                        <td>{sender}</td>
                        <td>{'yes' if isComposed else 'no'}</td>
                        <td>{modelID}</td>
                        <td>{template}</td>
                        <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        email_sender.send_mail("serinaplus.dev@datasemantics.co", "serina.dev@datasemantics.co", subject, body)
        time.sleep(1)
        model_type = 'prebuilt'
        pre_model_status, pre_model_msg, pre_data, pre_status = get_fr_data(input_data, filetype, apim_key,
                                                                            API_version,
                                                                            endpoint,
                                                                            model_type, inv_model_id)
        # TODO: Adding the No. of Pages Processed

        no_pages_processed = len(input_data)
        print("cst_status: ", cst_status, "pre_status: ", pre_status, "modelID:", modelID)
        if (cst_status == 'succeeded') and (pre_status == 'succeeded'):
            current_status = {"percentage": 50, "status": "Processing Model ⚡"}
            # '{"percentage": 50, "status": "Processing Model \\u26a1"}'
            yield {
                "event": "update",
                "retry": status_stream_retry_timeout,
                "data": json.dumps(current_status)
            }
            fr_data, postprocess_msg, postprocess_status = postpro(
                cst_data, pre_data, date_format, modelID, SQLALCHEMY_DATABASE_URL, entityID, vendorAccountID, bg_task,
                filename, db, sender)
            if postprocess_status == 1:
                blobPath = file_path_on_azure
                invoice_ID = push_frdata(fr_data, modelID, file_path, entityID, entityBodyID, vendorAccountID, poNumber,
                                         blobPath, userID, ruledata, no_pages_processed, source, sender, filename,
                                         filetype,
                                         bg_task, db)
                live_model_status = 1
                live_model_msg = 'Data extracted'
                current_status = {"percentage": 75,
                                  "status": "Post-Processing ⌛"}
                yield {
                    "event": "update",
                    "retry": status_stream_retry_timeout,
                    "data": json.dumps(current_status)
                }
                time.sleep(1)
                current_status = {"percentage": 100,
                                  "status": "OCR completed ✔"}
                yield {
                    "event": "update",
                    "retry": status_stream_retry_timeout,
                    "data": current_status
                }  # , "InvoiceID": invoice_ID, "fr_data": fr_data,

                ############ start of notification trigger #############
                # getting recipients for sending notification
                try:
                    # filter based on role if added
                    role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                            notificationTypeID=2).scalar()
                    # getting recipients for sending notification
                    recepients = db.query(model.AccessPermission.userID).filter(
                        model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                    recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                          model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                        model.User.isActive == 1).filter(model.UserAccess.UserID == model.User.idUser).filter(
                        model.UserAccess.EntityID == entityID, model.UserAccess.isActive == 1).all()
                    user_ids, *email = zip(*list(recepients))
                    # just format update
                    # email_ids = list(zip(email[0], email[1], email[2]))
                    cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                    details = {"user_id": user_ids, "trigger_code": 8009, "cust_id": cust_id, "inv_id": invoice_ID,
                               "additional_details": {"subject": "Invoice Upload",
                                                      "recipients": [(sender, "Serina", "User")]}}
                    bg_task.add_task(meta_data_publisher, details)
                except Exception as e:
                    print(e)
                ############ End of notification trigger #############
                current_status = {"live_model_status": live_model_status, "live_model_msg": live_model_msg,
                                  "InvoiceID": invoice_ID}
                # '{"live_model_status":'+live_model_status +' , "live_model_msg": '+live_model_msg+', "InvoiceID": '+invoice_ID+'}'
                time.sleep(.5)
                yield {
                    "event": "end",
                    "data": json.dumps(current_status)
                }

            else:
                live_model_status = 0
                live_model_msg = postprocess_status
                current_status = {"percentage": 75, "status": postprocess_msg}
                yield {
                    "event": "update",
                    "retry": status_stream_retry_timeout,
                    "data": json.dumps(current_status)
                }
        else:
            current_status = {
                "percentage": 50, "status": "prebuilt: " + pre_model_msg + " custom: " + cst_model_msg}
            yield {
                "event": "end",
                "data": json.dumps(current_status)
            }
            if cst_status != 'succeeded':
                live_model_status = 0
                live_model_msg = cst_model_msg
            elif pre_status != 'succeeded':
                live_model_status = 0
                live_model_msg = pre_model_msg
            elif pre_status == cst_status != 'succeeded':
                live_model_status = 0
                live_model_msg = "Custom model: " + cst_model_msg + \
                                 ". Prebuilt Model: " + pre_model_msg
            else:
                live_model_status = 0
                live_model_msg = 'Azure FR api issue'
                ############ start of notification trigger #############
                # getting recipients for sending notification

                # form recognizer api failure
                try:
                    recepients = db.query(model.AccessPermission.userID).filter_by(
                        permissionDefID=1).distinct()
                    recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                          model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                        model.User.isActive == 1).all()
                    user_ids, *email = zip(*list(recepients))
                    cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                    # just format update
                    email_ids = list(zip(email[0], email[1], email[2]))
                    details = {"user_id": None, "trigger_code": 7016, "cust_id": cust_id, "inv_id": None,
                               "additional_details": {"subject": "3rd Party API Failure",
                                                      "recipients": email_ids,
                                                      "​ endpoint_name": "Form Recognizer API v3"}}
                    bg_task.add_task(meta_data_publisher, details)
                except Exception as e:
                    print(e)
                ############ End of notification trigger #############
    else:
        ############ start of notification trigger #############
        # getting recipients for sending notification
        try:
            vendor = db.query(model.Vendor.VendorName).filter(
                model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
            recepients = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID, isActive=1).distinct()
            recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                  model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                model.User.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
            # invoice upload failure
            if sender:
                details = {"user_id": user_ids, "trigger_code": 7014, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "Invoice Upload Failure",
                                                  "recipients": [(sender, "Serina", "User")],
                                                  "Vendor_Name": vendor if vendor else "", "source": source}}
                bg_task.add_task(meta_data_publisher, details)
        except Exception as e:
            print(e)
        ############ End of notification trigger #############
        live_model_status = 0
        live_model_msg = fr_preprocessing_msg
        current_status = {"percentage": 25, "status": fr_preprocessing_msg}

        yield {
            "event": "end",
            "data": json.dumps(current_status)
        }


def live_model_fn(request, file_path, accepted_file_type, file_size_accepted, apim_key, API_version, endpoint,
                  inv_model_id, db):
    # data_p = "{'percentage': 25, 'status': 'Pre-Processing \\u23f3'}"
    time.sleep(3)
    yield {
        "event": "update",
        "retry": status_stream_retry_timeout,
        "data": json.dumps({'percentage': 25, 'status': 'Pre-Processing ⏳'})
    }

    time.sleep(2)
    yield {
        "event": "update",
        "retry": status_stream_retry_timeout,
        "data": json.dumps({'percentage': 50, 'status': "Model Processing ⚡"})
    }
    time.sleep(3)
    yield {
        "event": "update",
        "retry": status_stream_retry_timeout,
        "data": json.dumps({"percentage": 75, "status": "Post-Processing ⌛"})
    }
    time.sleep(3)
    yield {
        "event": "update",
        "retry": status_stream_retry_timeout,
        "data": json.dumps({"percentage": 100, "status": "OCR completed ✔"})
    }

    data_9548 = {'header': [{'tag': 'InvoiceDate', 'data': {'value': '12-12-2020', 'prebuilt_confidence': '0.995',
                                                            'custom_confidence': '0.995'}, 'status': 1},
                            {'tag': 'InvoiceTotal',
                             'data': {'value': '96.29', 'prebuilt_confidence': '0.995', 'custom_confidence': '0.995'},
                             'status': 1}, {'tag': 'InvoiceId',
                                            'data': {'value': 'M20 : 59548', 'prebuilt_confidence': '0.988',
                                                     'custom_confidence': '0.995'}, 'status': 1},
                            {'tag': 'PurchaseOrder',
                             'data': {'value': '045593', 'prebuilt_confidence': '', 'custom_confidence': '0.995'},
                             'status': 1}], 'tab': [[{'tag': 'Description', 'data': 'FRESH HERB MINT-61404009'}, {
        'tag': 'Unit', 'data': 'Kg'}, {'tag': 'Quantity', 'data': '1.00'}, {'tag': 'UnitPrice', 'data': '4.95'},
                                                     {'tag': 'Amount', 'data': '4.95'}],
                                                    [{'tag': 'Description', 'data': 'FRESH HERB CORRIANDER-61404002'},
                                                     {'tag': 'Unit', 'data': 'Kg'}, {'tag': 'Quantity', 'data': '1.00'},
                                                     {'tag': 'UnitPrice', 'data': '5.50'},
                                                     {'tag': 'Amount', 'data': '5.50'}], [{'tag': 'Description',
                                                                                           'data': 'VEG-FRESH TOMATO MEDIUM LOCAL/ME (KG)-70003819'},
                                                                                          {'tag': 'Unit', 'data': 'Kg'},
                                                                                          {'tag': 'Quantity',
                                                                                           'data': '25.00'},
                                                                                          {'tag': 'UnitPrice',
                                                                                           'data': '3.25'},
                                                                                          {'tag': 'Amount',
                                                                                           'data': '81.25'}]],
                 'overall_status': 1}
    data_9497 = {"header": [{"tag": "InvoiceId", "data": {"value": "M20 : 59497", "prebuilt_confidence": "0.99",
                                                          "custom_confidence": "0.995"}, "status": 1},
                            {"tag": "InvoiceTotal",
                             "data": {"value": "849.71", "prebuilt_confidence": "0.995", "custom_confidence": "0.995"},
                             "status": 1}, {"tag": "InvoiceDate",
                                            "data": {"value": "12-12-2020", "prebuilt_confidence": "0.995",
                                                     "custom_confidence": "0.995"}, "status": 1},
                            {"tag": "PurchaseOrder",
                             "data": {"value": "045555", "prebuilt_confidence": "", "custom_confidence": "0.995"},
                             "status": 1}], "tab": [
        [{"tag": "Description", "data": "FRESH HERBS THYME CYPRUS-G1404043"}, {"tag": "Unit", "data": "Kg"},
         {"tag": "Quantity", "data": "1.00"}, {"tag": "UnitPrice", "data": "34.50"},
         {"tag": "Amount", "data": "34.50"}],
        [{"tag": "Description", "data": "FRESH HERBS CHIVES FRANCE-61404032"}, {"tag": "Unit", "data": "Kg"},
         {"tag": "Quantity", "data": "1.00"}, {"tag": "UnitPrice", "data": "52.50"},
         {"tag": "Amount", "data": "52.50"}], [{"tag": "Description", "data": "FRESH HERBS BASIL-61404023"}, {
            "tag": "Unit", "data": "Kg"}, {"tag": "Quantity", "data": "3.00"}, {"tag": "UnitPrice", "data": "46.50"},
                                               {"tag": "Amount", "data": "139.50"}],
        [{"tag": "Description", "data": "FRESH FRUIT LEMON-61403110"}, {"tag": "Unit", "data": "Kg"},
         {"tag": "Quantity", "data": "5.00"}, {"tag": "UnitPrice", "data": "4.50"}, {"tag": "Amount", "data": "22.50"}],
        [{"tag": "Description", "data": "FRESH VEG CAPSICUM RED-61406117"}, {"tag": "Unit", "data": "Kg"},
         {"tag": "Quantity", "data": "20.00"}, {"tag": "UnitPrice", "data": "10.00"},
         {"tag": "Amount", "data": "200.00"}],
        [{"tag": "Description", "data": "FRESH VEG LETTUCE BABY GEM SPAIN HOLLAND-61406286"},
         {"tag": "Unit", "data": "Kg"}, {"tag": "Quantity", "data": "10.00"}, {"tag": "UnitPrice", "data": "25.00"},
         {"tag": "Amount", "data": "250.00"}],
        [{"tag": "Description", "data": "FRESH VEG PUMPKIN BUTTERNUT AUS-61406470"}, {"tag": "Unit", "data": "Kg"},
         {"tag": "Quantity", "data": "15.00"}, {"tag": "UnitPrice", "data": "7.35"},
         {"tag": "Amount", "data": "110.25"}]], "overall_status": 1}
    # fl = file_path.split("/")[-1].split(" ").split(".")[0]
    fl = file_path.split("/")[-1].split(" ")[-1].split(".")[0]
    print("------------------", fl)
    time.sleep(1)
    # if fl == '9548':
    #     invoiceID = push_frdata(data_9548, 38, file_path, db)
    #     yield {
    #         "event": "end",
    #         "data": json.dumps({"InvoiceID": invoiceID})
    #     }
    # elif fl == '9497':
    #     invoiceID = push_frdata(data_9497, 38, file_path, db)
    #     yield {
    #         "event": "end",
    #         "data": json.dumps({"InvoiceID": invoiceID})
    #     }
    # else:
    #     yield {
    #         "event": "end",
    #         "data": "Server Busy!, Please try after sometime."
    #     }


def push_frdata(data, modelID, filepath, entityID, entityBodyID, vendorAccountID, poNumber, blobPath, userID, ruledata,
                no_pages_processed, source, sender, filename, filetype, bg_task, db):
    # create Invoice record

    current_ime = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
    if source == 'Mail' and poNumber == "":
        try:
            poNumber = list(filter(lambda d: d['tag'] == 'PurchaseOrder', data['header']))[0]['data']['value']
        except Exception as e:
            ############ start of notification trigger #############
            # getting recipients for sending notification
            try:
                vendor = db.query(model.Vendor.VendorName).filter(
                    model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                    model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                details = {"user_id": None, "trigger_code": 7026, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "PO Number Empty{MAIL source}",
                                                  "recipients": [(sender, "Serina", "User")],
                                                  "Vendor_Name": vendor}}
                bg_task.add_task(meta_data_publisher, details)
            except Exception as e:
                print(e)
            ############ End of notification trigger #############
            applicationlogging.logException("ROVE HOTEL DEV", "OCR.py No PO found, Mail Source", str(e))
            poNumber = ''
    if source == 'SharePoint' and poNumber == "":
        try:
            poNumber = list(filter(lambda d: d['tag'] == 'PurchaseOrder', data['header']))[0]['data']['value']
        except Exception as e:
            ############ start of notification trigger #############
            # getting recipients for sending notification
            try:
                vendor = db.query(model.Vendor.VendorName).filter(
                    model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                    model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                recepients = db.query(model.UserAccess.UserID).filter(
                    model.UserAccess.EntityID == entityID).filter_by(isActive=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                details = {"user_id": None, "trigger_code": 7026, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "PO Number Empty{SHAREPOINT source}",
                                                  "recipients": [(sender, "Serina", "User")],
                                                  "Vendor_Name": vendor}}
                bg_task.add_task(meta_data_publisher, details)
            except Exception as e:
                print(e)
            ############ End of notification trigger #############
            applicationlogging.logException("ROVE HOTEL DEV", "OCR.py No PO found, Sharepoint Source", str(e))
            poNumber = ''
    if source == 'Web' and poNumber == "":
        try:
            poNumber = list(filter(lambda d: d['tag'] == 'PurchaseOrder', data['header']))[0]['data']['value']
        except Exception as e:
            ############ start of notification trigger #############
            # getting recipients for sending notification
            try:
                vendor = db.query(model.Vendor.VendorName).filter(
                    model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                    model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                details = {"user_id": None, "trigger_code": 7026, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "PO Number Empty{WEB source}",
                                                  "recipients": [(sender, "Serina", "User")],
                                                  "Vendor_Name": vendor}}
                bg_task.add_task(meta_data_publisher, details)
            except Exception as e:
                print(e)
            ############ End of notification trigger #############
            applicationlogging.logException("ROVE HOTEL DEV", "OCR.py No PO found, Web Source", str(e))
            poNumber = ''
    resp = requests.get(filepath)
    file_content = BytesIO(resp.content).getvalue()
    ref_url = getfile_as_base64(filename, filetype, file_content)
    invoice_data = {"idDocumentType": 3, "documentModelID": modelID, "entityID": entityID, "entityBodyID": entityBodyID,
                    "documentStatusID": 0,
                    "vendorAccountID": vendorAccountID, "docPath": blobPath,
                    "documentTotalPages": no_pages_processed, "ruleID": ruledata, "CreatedOn": current_ime,
                    "sourcetype": source, "ref_url": ref_url, "sender": sender}
    # print("invoice_data: ", invoice_data)
    db_data = model.Document(**invoice_data)
    db.add(db_data)
    db.commit()
    invoiceID = db_data.idDocument
    print("Invoice ID:", invoiceID)
    user_details = db.query(model.User.firstName,model.User.lastName).filter(model.User.idUser == userID).first()
    user_name = user_details[0]+" "+user_details[1]
    update_docHistory(invoiceID, userID,0,f"Invoice Uploaded By {user_name}", db)

    # parse tag labels data and push into ivoice data table
    error_labels = parse_labels(data['header'], db, invoiceID, modelID, poNumber, blobPath, sender)
    # parse line item data and push into invoice line itemtable
    error_line_items = parse_tabel(data['tab'], db, invoiceID, modelID)
    if len(error_labels if error_labels else [] + error_line_items if error_line_items else []):
        ############ start of notification trigger #############
        # getting recipients for sending notification
        # filter based on role if added
        try:
            role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                    notificationTypeID=2).scalar()
            # getting recipients for sending notification
            recepients = db.query(model.AccessPermission.userID).filter(
                model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
            recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                  model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                model.User.isActive == 1).filter(model.UserAccess.UserID == model.User.idUser).filter(
                model.UserAccess.EntityID == entityID, model.UserAccess.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            cc_email_ids = []
            try:
                isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                        model.NotificationCategoryRecipient.notificationrecipient).filter(
                    model.NotificationCategoryRecipient.entityID == entityID,
                    model.NotificationCategoryRecipient.notificationTypeID == 2).one()
            except Exception as e:
                pass
            if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                    isdefaultrep.notificationrecipient["to_addr"]) > 0:
                email_ids.extend([(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]
            cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
            details = {"user_id": user_ids, "trigger_code": 7003, "cust_id": cust_id, "inv_id": invoiceID,
                       "additional_details": {"subject": "Label Error",
                                              "keylabel": str(error_labels + error_line_items),
                                              "recipients": email_ids, "cc": cc_email_ids}}
            bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print(e)

    # update document history table
    return invoiceID


def parse_labels(label_data, db, invoiceID, modelID, poNumber, blobPath, sender):
    try:
        error_labels_tag_ids = []
        doc_header = {}
        for label in label_data:
            db_data = {}
            db_data['documentTagDefID'] = get_labelId(
                db, label['tag'], modelID)
            db_data['documentID'] = invoiceID
            db_data['Value'] = label['data']['value']
            db_data['IsUpdated'] = 0
            if label['status'] == 1:
                db_data['isError'] = 0
            else:
                error_labels_tag_ids.append(label['tag'])
                db_data['isError'] = 1
            db_data['ErrorDesc'] = label['status_message']
            if label['boundingBox']:
                db_data['Xcord'] = label['boundingBox']['x']
                db_data['Ycord'] = label['boundingBox']['y']
                db_data['Width'] = label['boundingBox']['w']
                db_data['Height'] = label['boundingBox']['h']
            db.add(model.DocumentData(**db_data))
            if label['tag'] in docLabelMap.keys():
                doc_header[docLabelMap[label['tag']]] = label['data']['value']
        db.commit()
        doc_header['PODocumentID'] = poNumber
        doc_header['docPath'] = blobPath
        print(doc_header)
        update_doc(doc_header, invoiceID, db, sender)
        return error_labels_tag_ids
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "OCR.py parse_labels", str(e))
        return {"DB error": "Error while inserting document data"}


def update_doc(data, invoiceID, db, sender):
    try:
        db.query(model.Document).filter(model.Document.idDocument == invoiceID).update(data)
        db.commit()
    except Exception as e:
        if "Incorrect datetime value" in str(e):
            subject = f'Cannot update Invoice Date to DB!'
            body = f"""
            <html>
                <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                    <strong>Error Summary</strong>: <i>Invoice Date update error</i>
                    <div style="margin-top: 2%;"></div>
                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <th>Description</th>
                            <th>Sender</th>
                            <th>Date & Time</th>
                        </tr>
                        <tr>
                            <td>Invoice Date {data['documentDate']} is not Valid</td>
                            <td>{sender}</td>
                            <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            email_sender.send_mail("serinaplus.dev@datasemantics.co", sender, subject, body)
            del data['documentDate']
            db.query(model.Document).filter(model.Document.idDocument == invoiceID).update(data)
            db.commit()
        if "Data truncated for column 'totalAmount'" in str(e):
            subject = f'Cannot update Invoice Amount to DB!'
            body = f"""
            <html>
                <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                    <strong>Error Summary</strong>: <i>Invoice Amount update error</i>
                    <div style="margin-top: 2%;"></div>
                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <th>Description</th>
                            <th>Sender</th>
                            <th>Date & Time</th>
                        </tr>
                        <tr>
                            <td>Invoice Amount {data['totalAmount']} is not Valid</td>
                            <td>{sender}</td>
                            <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            email_sender.send_mail("serinaplus.dev@datasemantics.co", sender, subject, body)
            del data['totalAmount']
            db.query(model.Document).filter(model.Document.idDocument == invoiceID).update(data)
            db.commit()
        if "Data too long for column 'docheaderID'" in str(e):
            subject = f'Cannot update Invoice ID to DB!'
            body = f"""
            <html>
                <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                    <strong>Error Summary</strong>: <i>Invoice ID update error</i>
                    <div style="margin-top: 2%;"></div>
                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <th>Description</th>
                            <th>Sender</th>
                            <th>Date & Time</th>
                        </tr>
                        <tr>
                            <td>Invoice ID {data['docheaderID']} is not Valid</td>
                            <td>{sender}</td>
                            <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            email_sender.send_mail("serinaplus.dev@datasemantics.co", sender, subject, body)
            del data['docheaderID']
            db.query(model.Document).filter(model.Document.idDocument == invoiceID).update(data)
            db.commit()
        if "Data too long for column 'PODocumentID'" in str(e):
            subject = f'Cannot update PODocumentID to DB!'
            body = f"""
            <html>
                <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                    <strong>Error Summary</strong>: <i>PODocumentID update error</i>
                    <div style="margin-top: 2%;"></div>
                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <th>Description</th>
                            <th>Sender</th>
                            <th>Date & Time</th>
                        </tr>
                        <tr>
                            <td>PO {data['PODocumentID']} is not Valid</td>
                            <td>{sender}</td>
                            <td>{datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            email_sender.send_mail("serinaplus.dev@datasemantics.co", sender, subject, body)
            del data['PODocumentID']
            db.query(model.Document).filter(model.Document.idDocument == invoiceID).update(data)
            db.commit()
        applicationlogging.logException("ROVE HOTEL DEV", "OCR.py update_doc", str(e))
        return {"DB error": "Server error", "Desc": "Error while updating invoice"}


def parse_tabel(tabel_data, db, invoiceID, modelID):
    error_labels_tag_ids = []
    for row in tabel_data:
        for col in row:
            db_data = {}
            db_data['documentID'] = invoiceID
            db_data['Value'] = col['data']
            db_data['lineItemtagID'] = get_lineitemTagId(
                db, col['tag'], modelID)
            if 'status' in col:
                if col['status'] == 1:
                    db_data['isError'] = 0
                else:
                    error_labels_tag_ids.append(col['tag'])
                    db_data['isError'] = 1
                db_data['ErrorDesc'] = col['status_message']
            if col['boundingBox']:
                db_data['Xcord'] = col['boundingBox']['x']
                db_data['Ycord'] = col['boundingBox']['y']
                db_data['Width'] = col['boundingBox']['w']
                db_data['Height'] = col['boundingBox']['h']
            db_data['itemCode'] = col['row_count']
            print(db_data)
            db.add(model.DocumentLineItems(**db_data))
    db.commit()
    return error_labels_tag_ids


def get_lineitemTagId(db, item, modelID):
    # print("Tab :", item)
    result = db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.TagName ==
                                                         item,
                                                         model.DocumentLineItemTags.idDocumentModel == modelID).first()
    if result is not None:
        return result.idDocumentLineItemTags


def get_labelId(db, item, modelID):
    print("Item: ", item)
    result = db.query(model.DocumentTagDef).filter(model.DocumentTagDef.TagLabel ==
                                                   item, model.DocumentTagDef.idDocumentModel == modelID).first()
    if result is not None:
        return result.idDocumentTagDef


def update_docHistory(documentID, userID, documentstatus,documentdesc, db):
    try:
        docHistory = {}
        docHistory['documentID'] = documentID
        docHistory['userID'] = userID
        docHistory['documentStatusID'] = documentstatus
        docHistory['documentdescription'] = documentdesc
        docHistory['CreatedOn'] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        db.add(model.DocumentHistoryLogs(**docHistory))
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "OCR.py update_docHistory", str(e))
        return {"DB error": "Error while inserting document history"}
