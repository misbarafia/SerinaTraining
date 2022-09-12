from fastapi import Depends, status, APIRouter, File, UploadFile, BackgroundTasks, Request, Response
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import List
import shutil
from typing import Optional
import os, json, requests, jwt
import pandas as pd
import time
import tempfile
from tinydb import TinyDB, Query
import sys

sys.path.append("..")
from datetime import datetime
from dependency import dependencies
from schemas import FRSchema as schema
from crud import FRCrud as crud
from FROps import frtrigger_crud as crud_fr
from auth import AuthHandler

auth_handler = AuthHandler()
import model
from session import Session as SessionLocal
from session.session import DB
from session import engine
from session import SQLALCHEMY_DATABASE_URL
from FROps.upload import upload_files_to_azure
from FROps.grnreupload import grn_reuploadINVO
from FROps.reupload import reupload_file_azure
from FROps.model_validate import model_validate_final
from tasks.tasks import checkOCRError
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import generate_blob_sas, ContainerSasPermissions
from io import BytesIO

model.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/apiv1.1/fr",
    tags=["Form Recogniser"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

temp_dir_obj = None


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/getfrconfig/{userID}", status_code=status.HTTP_200_OK)
async def get_fr_config(userID: int, db: Session = Depends(get_db)):
    """
    <b> API route to get Form Recogniser Configuration. It contains following parameters.</b>
    - userID : Unique indetifier used to indentify a user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """
    return await crud.getFRConfig(userID, db)


@router.post("/updatefrconfig/{userID}",
             status_code=status.HTTP_200_OK)
async def update_fr_config(userID: int, frConfig: schema.FrConfig,
                           db: Session = Depends(get_db)):
    """
    <b> API route to update invoice status. It contains following parameters.</b>
    - userID : Unique indetifier used to indentify a user
    - invoiceID : Unique indetifier used to indentify a particular invoice in database
    - invoiceStatus: It is Body parameter that is of a Pydantic class object, creates member data for updating invoice status
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """

    return await crud.updateFRConfig(userID, frConfig, db)


@router.get("/getfrmetadata/{documentId}")
async def get_fr_data(documentId: int, db: Session = Depends(get_db)):
    return await crud.getMetaData(documentId, db)


@router.get("/getTrainTestResults/{modelId}")
async def get_test_data(modelId: int, db: Session = Depends(get_db)):
    return await crud.getTrainTestRes(modelId, db)

@router.get("/getActualAccuracy/{type}/{name}")
async def getAccuracy(type:str,name:str,db: Session = Depends(get_db)):
    return await crud.getActualAccuracy(type,name,db)


@router.get("/getalltags")
async def get_fr_tags(tagtype: Optional[str] = None,db: Session = Depends(get_db)):
    return await crud.getall_tags(tagtype,db)

@router.get("/entityTaggedInfo")
async def get_entity_levelTaggedInfo(tagtype: Optional[str] = None):
    for f in os.listdir():
        if os.path.isfile(f) and f.endswith(".xlsx"):
            os.unlink(f)
    if tagtype == "vendor":
        filename = await crud.get_entity_level_taggedInfo()
    else:
        filename = await crud.get_entity_level_taggedInfo()
    return FileResponse(path=filename, filename=filename, media_type='application/vnd.ms-excel') 


@router.put("/update_metadata/{documentId}")
async def update_metadata(request:Request, documentId: int, db: Session = Depends(get_db)):
    frmetadata = await request.json()
    blb_fldr = frmetadata["FolderPath"]
    mandatoryheadertags = frmetadata["mandatoryheadertags"].split(",")
    mandatorylinetags = frmetadata["mandatorylinetags"].split(",")
    optionallinertags = frmetadata["optionallinertags"].split(",")
    optionalheadertags = frmetadata["optionalheadertags"].split(",")
    if len(optionalheadertags) == 1 and optionalheadertags[0] == '':
        optionalheadertags = []
    if len(optionallinertags) == 1 and optionallinertags[0] == '':
        optionallinertags = []
    vendorname = frmetadata["vendorName"] if 'vendorName' in frmetadata else frmetadata["ServiceProviderName"]  
    if 'vendorName' in frmetadata:
        syn = frmetadata["synonyms"]
        db.execute(f"update vendor set Synonyms = '{json.dumps(syn)}' where VendorName = '{vendorname}'")
        del frmetadata["synonyms"]
        del frmetadata["vendorName"]
    else:
        del frmetadata["ServiceProviderName"]
    configs = getOcrParameters(1, db)
    containername = configs.ContainerName
    connection_str = configs.ConnectionString
    blob_service_client = BlobServiceClient.from_connection_string(
    conn_str=connection_str, container_name=containername)
    container_client = blob_service_client.get_container_client(containername)
    list_of_blobs = container_client.list_blobs(name_starts_with=blb_fldr)
    mandatoryheaderfields = []
    definitions = {}
    lineitemupdates = []
    if len(mandatorylinetags) > 0:
        definitions = {
            "tab_1_object": {"fieldKey": "tab_1_object", "fieldType": "object", "fieldFormat": "not-specified",
                             "itemType": None, "fields": []}}
        for m in mandatorylinetags:
            definitions["tab_1_object"]["fields"].append(
                {"fieldKey": m, "fieldType": "string", "fieldFormat": "not-specified", "itemType": None,
                 "fields": None})
            lineitemupdates.append(m)
        if len(optionallinertags) > 0:
            for m in optionallinertags:
                definitions["tab_1_object"]["fields"].append(
                    {"fieldKey": m, "fieldType": "string", "fieldFormat": "not-specified", "itemType": None,
                     "fields": None})
                lineitemupdates.append(m)
    for b in list_of_blobs:
        if b.name.endswith("labels.json"):
            blob = blob_service_client.get_blob_client(containername, b.name).download_blob().readall()
            labjson = json.loads(blob)
            for l in labjson["labels"]:
                if l['label'].startswith("tab_1") == False:
                    if l['label'] not in mandatoryheadertags and l['label'] not in optionalheadertags:
                        index = next((index for (index, d) in enumerate(labjson["labels"]) if d["label"] == l['label']), None)
                        del labjson["labels"][index]
                else:
                    if l['label'].split("/")[2] not in lineitemupdates:
                        index = next((index for (index, d) in enumerate(labjson["labels"]) if d["label"] == l['label']), None)
                        del labjson["labels"][index]
                        
            bloblient = blob_service_client.get_blob_client(containername,blob=b.name)
            bloblient.upload_blob(json.dumps(labjson),overwrite=True)

    for m in mandatoryheadertags:
        mandatoryheaderfields.append({"fieldKey": m, "fieldType": "string", "fieldFormat": "not-specified"})
    for m in optionalheadertags:
        mandatoryheaderfields.append({"fieldKey": m, "fieldType": "string", "fieldFormat": "not-specified"})
    mandatoryheaderfields.append({"fieldKey":"tab_1","fieldType":"array","fieldFormat":"not-specified","itemType":"tab_1_object","fields":None})
    jso = {"$schema": "https://schema.cognitiveservices.azure.com/formrecognizer/2021-03-01/fields.json", "definitions": definitions, "fields": mandatoryheaderfields}
    data = json.dumps(jso)
    blobclient = blob_service_client.get_blob_client(containername,blob=blb_fldr+"/fields.json")
    blobclient.upload_blob(data=data,overwrite=True)
    return await crud.updateMetadata(documentId,frmetadata,db)

# @router.post("/createtags")
# async def create_fr_tags(Default_fields: schema.DefaultFieldsS,db: Session = Depends(get_db)):
#     return await crud.create_tags(Default_fields,db)

@router.post('/upload_blob')
# min_no: int, max_no: int, file_size_accepted: int, cnt_str: str, cnt_nm: str, local_path: str
def upload_blob(uploadParams: schema.FrUpload):
    local_pth = fr"{uploadParams.local_path}"
    accepted_file_type = ['pdf', 'json', "txt"]
    nl_upload_status, fnl_upload_msg, blob_fld_name = upload_files_to_azure(uploadParams.min_no, uploadParams.max_no,
                                                                            accepted_file_type,
                                                                            uploadParams.file_size_accepted,
                                                                            uploadParams.cnx_str,
                                                                            uploadParams.cont_name, local_pth,
                                                                            uploadParams.folderpath)
    return {"nl_upload_status": nl_upload_status, "fnl_upload_msg": fnl_upload_msg, "blob_fld_name": blob_fld_name}


@router.post('/reupload_blob')
def reupload_blob(uploadParams: schema.FrReUpload):
    # min_no = 5
    # max_no = 50
    # accepted_file_type = "jpg,pdf"
    # file_size_accepted = 50 # MB
    # cnt_str = "DefaultEndpointsProtocol=https;AccountName=testblob0203;AccountKey=h3ro+ZcNm1Y7F2GZz1ESrRbz6kiu5PBKTAmK2iB+KNdlnw8ZaAycjjwrsvO6drtBQHYMR/NlwdOBi1BJKojJLg==;EndpointSuffix=core.windows.net"
    # cnt_nm = "upload1"
    # old_fld_name =

    local_pth = fr"{uploadParams.local_path}"
    accepted_file_type = uploadParams.accepted_file_type.split(",")
    print(uploadParams.old_folder)
    reupload_status, reupload_status_msg, blob_fld_name = reupload_file_azure(
        uploadParams.min_no, uploadParams.max_no, accepted_file_type, uploadParams.file_size_accepted,
        uploadParams.cnx_str, uploadParams.cont_name, local_pth, uploadParams.old_folder, uploadParams.upload_type)
    return {"nl_upload_status": reupload_status, "fnl_upload_msg": reupload_status_msg, "blob_fld_name": blob_fld_name}


@router.post('/model_validate')
def model_validate(validateParas: schema.FrValidate, db: Session = Depends(get_db)):
    # model_path = "C:\Users\yesh\serina\onboard_api_prj\model-a2f612fb-f403-4d25-beda-151dc6197c23.json"
    # req_fields_accuracy = 80.0
    # req_model_accuracy = 78.0
    # mand_fld_list = "invoice_date,invoice_number"
    # cnt_str = "DefaultEndpointsProtocol=https;AccountName=testblob0203;AccountKey=h3ro+ZcNm1Y7F2GZz1ESrRbz6kiu5PBKTAmK2iB+KNdlnw8ZaAycjjwrsvO6drtBQHYMR/NlwdOBi1BJKojJLg==;EndpointSuffix=core.windows.net"
    # cnt_nm = "upload1"

    # mand_fld_list = validateParas.mand_fld_list.split(",")
    # print(mand_fld_list)
    fr_lab_String = "SELECT mandatoryheadertags,mandatorylinetags FROM " + DB + ".frmetadata WHERE idInvoiceModel=" + str(
        validateParas.model_id) + ";"
    fr_lab_df = pd.read_sql(fr_lab_String, SQLALCHEMY_DATABASE_URL)
    mand_fld_list = list(fr_lab_df['mandatoryheadertags'])[0].split(",")
    model_path = json.loads(validateParas.model_path)
    template_metadata = {}
    fr_modelid = validateParas.fr_modelid
    model_validate_final_status, model_validate_final_msg, model_id, file_path, data = model_validate_final(
        model_path, fr_modelid, validateParas.req_fields_accuracy, validateParas.req_model_accuracy, mand_fld_list,
        validateParas.cnx_str, validateParas.cont_name, validateParas.VendorAccount, validateParas.ServiceAccount, template_metadata)
    # update model ID
    # model_update = crud.updateInvoiceModel(
    #     validateParas.model_id, {"modelID": model_id}, db)
    # # store final data to json db
    # jsonDb = TinyDB('db.json')
    # jsonDb.insert({"model_id": model_id, "data": data})

    blob_service_client = BlobServiceClient.from_connection_string(conn_str=validateParas.cnx_str,
                                                                   container_name=validateParas.cont_name)
    container_client = blob_service_client.get_container_client(validateParas.cont_name)
    jso = container_client.get_blob_client('db.json').download_blob().readall()
    jso = json.loads(jso)
    allids = []
    for m in jso:
        allids.append(m['model_id'])
    if model_id not in allids:
        jso.append({"model_id": model_id, "data": data})
    container_client.upload_blob(name='db.json', data=json.dumps(jso), overwrite=True)
    return {"model_validate_status": model_validate_final_status, "model_validate_msg": model_validate_final_msg,
            "model_id": model_id, "model_updates": {"result": "Updated", "records": {"modelID": model_id}},
            "final_data": data}


@router.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"train_docs/{file.filename}"
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filepath": r'%s' % os.getcwd() + "/train_docs/" + file.filename}


@router.post("/uploadfolder")
async def create_upload_files(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        ts = str(time.time())
        dir_path = ts.replace(".", "_")
        configs = getOcrParameters(1, db)
        containername = configs.ContainerName
        connection_str = configs.ConnectionString
        blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        container_client = blob_service_client.get_container_client(containername)
        for file in files:
            content = await file.read()
            file_location = f"{dir_path}/{file.filename}"
            container_client.upload_blob(name=file_location, data=BytesIO(content), overwrite=True)
        return {"filepath": dir_path}
    except Exception as e:
        print(e)
        return {"filepath": ""}


@router.post("/createmodel/{userID}", status_code=status.HTTP_200_OK)
async def create_invoice_model(userID: int, invoiceModel: schema.InvoiceModel,
                               db: Session = Depends(get_db)):
    """
    <b> API route to create a new Invoice model with associated tag definitions. It contains following parameters.</b>
    - userID : Unique indetifier used to indentify a user
    - invoiceModel: It is Body parameter that is of a Pydantic class object, creates member data for creating a new Invoice Model
    - tags: It is Body parameter that is of a Pydantic class object, creates member data for creating a set of tag definitions
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """

    return crud.createInvoiceModel(userID, invoiceModel, db)


@router.get("/checkduplicatevendors/{vendoraccountID}/{modelname}")
async def getduplicates(vendoraccountID: int, modelname: str, db: Session = Depends(get_db)):
    """
    This API checks if a vendor has multiple entities
    """
    status = crud.check_same_vendors_different_entities(vendoraccountID, modelname, db)
    return status

@router.get("/checkduplicatesp/{serviceaccountID}/{modelname}")
async def getduplicates(serviceaccountID: int, modelname: str, db: Session = Depends(get_db)):
    """
    This API checks if a vendor has multiple entities
    """
    status = crud.check_same_sp_different_entities(serviceaccountID, modelname, db)
    return status    




@router.get("/copymodels/{vendoraccountID}/{modelname}")
async def copyallmodels(vendoraccountID: int, modelname: str, db: Session = Depends(get_db)):
    """
    This API will copy the same model for a vendor for all different entities
    """
    status = crud.copymodels(vendoraccountID, modelname, db)
    return status

@router.get("/copymodelsSP/{serviceaccountID}/{modelname}")
async def copyallmodels(serviceaccountID: int, modelname: str, db: Session = Depends(get_db)):
    """
    This API will copy the same model for a vendor for all different entities
    """
    status = crud.copymodelsSP(serviceaccountID, modelname, db)
    return status


@router.get("/get_entities")
async def get_entities(db: Session = Depends(get_db)):
    """
    This api will return the list of Entities
    """
    all_entities = db.query(model.Entity).all()
    return all_entities


@router.get("/get_all_entities/{u_id}")
async def get_all_entities(u_id: int, db: Session = Depends(get_db)):
    """
    This api will return the list of Entities per user entity access
    """
    sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
    all_entities = db.query(model.Entity).filter(model.Entity.idEntity.in_(sub_query)).all()
    return all_entities


@router.put("/update_entity/{eid}")
async def update_ent(eid: int, EntityModel: schema.Entity, db: Session = Depends(get_db)):
    """
    This API will update the Entity values
    """
    try:
        db.query(model.Entity).filter(model.Entity.idEntity == eid).update(dict(EntityModel))
        db.commit()
        return {"message": "success"}
    except Exception as e:
        return {"message": f"exception {e}"}


@router.post("/updatemodel/{modelID}",
             status_code=status.HTTP_200_OK)
async def update_invoicemodel(modelID: int, invoiceModel: schema.InvoiceModel,
                              db: Session = Depends(get_db)):
    """
    <b> API route to update invoice status. It contains following parameters.</b>
    - userID : Unique indetifier used to indentify a user
    - invoiceID : Unique indetifier used to indentify a particular invoice in database
    - invoiceStatus: It is Body parameter that is of a Pydantic class object, creates member data for updating invoice status
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """
    db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == modelID).update(
        {'UpdatedOn': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")})
    db.commit()
    return crud.updateInvoiceModel(modelID, invoiceModel, db)


@router.get("/getmodellist/{vendorID}")
async def get_modellist(vendorID: int, db: Session = Depends(get_db)):
    """
    <b> API route to get Form Recogniser Configuration. It contains following parameters.</b>
    - userID : Unique indetifier used to indentify a user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """
    return crud.getmodellist(vendorID, db)

@router.get("/getmodellistsp/{serviceProviderID}")
async def get_modellistsp(serviceProviderID: int, db: Session = Depends(get_db)):
    """
    <b> API route to get Form Recogniser Configuration. It contains following parameters.</b>
    - userID : Unique indetifier used to indentify a user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """
    return crud.getmodellistsp(serviceProviderID, db)

@router.get("/getfinaldata/{modelID}")
async def get_finaldata(modelID: str, db: Session = Depends(get_db)):
    """
    <b> API route to get post processed final data. It contains following parameters.</b>
    - modelID : Unique indetifier used to indentify a model
    - return: It returns the result status.
    """
    configs = getOcrParameters(1, db)
    containername = configs.ContainerName
    connection_str = configs.ConnectionString
    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    container_client = blob_service_client.get_container_client(containername)
    jso = container_client.get_blob_client('db.json').download_blob().readall()
    jso = json.loads(jso)
    data = list(filter(lambda x: x['model_id'] == modelID, jso))
    print(data)
    data = data[0]['data']
    return {"final_data": data}


# API to read all vedor list


@router.get("/vendorlist", status_code=status.HTTP_200_OK)
async def read_vendor(db: Session = Depends(get_db)):
    return await crud.readvendor(db)


@router.get("/vendoraccount/{v_id}")
async def read_vendoraccount(v_id: int, db: Session = Depends(get_db)):
    db_user = crud.readvendoraccount(db, v_id=v_id)
    # if db_user is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    return await db_user

@router.get("/serviceaccount/{s_id}")
async def read_spaccount(s_id: int, db: Session = Depends(get_db)):
    db_user = crud.readspaccount(db, s_id=s_id)
    # if db_user is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    return await db_user


# API for logging OCR run status


@router.post("/ocrlog")
async def addOCRLog(logData: schema.OCRLogs, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    API route to log OCR run status
    - logData: It is Body parameter that is of a Pydantic class object, creates member data for logging OCR run status
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    """
    response = await crud.addOCRLog(logData, db)
    #  trigger OCR error check task in backround
    background_tasks.add_task(checkOCRError, logData.documentId, db)
    return response


# API for adding new user item mapping


@router.post("/addItemMapping")
async def addItemMapping(mapData: schema.ItemMapping, db: Session = Depends(get_db)):
    """
    API route to add a new user item mapping
    - mapData: It is Body parameter that is of a Pydantic class object, creates member data for new item mapping
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    """
    return await crud.addItemMapping(mapData, db)


@router.post("/addfrmetadata/{m_id}/RuleId/{r_id}", status_code=status.HTTP_201_CREATED)
async def new_fr_meta_data(m_id: int, r_id: int, n_fr_mdata: schema.FrMetaData, db: Session = Depends(get_db)):
    resp_fr_mdata = await crud.addfrMetadata(m_id, r_id, n_fr_mdata, db)
    return {"Result": "Updated", "Records": [resp_fr_mdata]}


# Displaying document rules list
@router.get("/documentrules", status_code=status.HTTP_200_OK)
async def read_docrules(db: Session = Depends(get_db)):
    return await crud.readdocumentrules(db)


# Displaying new doc rules list
@router.get("/documentrulesnew", status_code=status.HTTP_200_OK)
async def read_docrulesnew(db: Session = Depends(get_db)):
    return await crud.readnewdocrules(db)


def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(
            model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"DB Error": "Failed to get OCR parameters"})


# to trigger batch

@router.post("/triggerbatch/{id_doc}")
async def batch_trigger(id_doc: int, re_upload: bool, grnreuploadID:Optional[int]= None,  db: Session = Depends(get_db)):
    if re_upload:
        sub_status_id = db.query(model.Document.documentsubstatusID).filter(
            model.Document.idDocument == id_doc).scalar()
        db.query(model.GrnReupload).filter_by(grnreuploadID=grnreuploadID).update({'reuploadedInvoId': id_doc})
        db.commit()
        if sub_status_id == 45:
            # GRN reupload
            single_doc = grn_reuploadINVO(grnreuploadID)
            return single_doc
    else:
        sub_status_id = db.query(model.Document.documentsubstatusID).filter(
            model.Document.idDocument == id_doc).scalar()
        if sub_status_id != 29:
            single_doc = crud_fr.single_doc_prc(id_doc)
        else:
            single_doc = "no data"

        return single_doc
