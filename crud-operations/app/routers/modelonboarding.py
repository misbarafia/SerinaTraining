from fastapi import Depends, status, APIRouter, Request, UploadFile, File, Response
from sqlalchemy.orm import Session
import json,requests,os,base64
from io import BytesIO
from pdf2image import convert_from_bytes
from azure.storage.blob import (
    BlobServiceClient,generate_blob_sas,ContainerSasPermissions,generate_container_sas
)
import sys
sys.path.append("..")
from datetime import datetime,timedelta
from crud import ModelOnBoardCrud as crud
from FROps import form_recognizer as fr,util as ut
from schemas import InvoiceSchema as schema
import model
from session import Session as SessionLocal
from session import engine
from logModule import applicationlogging
model.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/apiv1.1/ModelOnBoard",
    tags=["Model On-Boarding"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/newModel/{modelID}/{userId}", status_code=status.HTTP_200_OK, response_model=schema.Response)
async def onboard_invoice_model(request: Request, userId: int, modelID: int,db: Session = Depends(get_db)):
    """
    <b>API route to onboard a new invoice template Form Recognizer output.</b>
    - userID : Unique indetifier used to indentify a user
    - invoiceTemplate: The Form Recognizer output, passed as API body
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.

    <b> CRUD Ops</b>
    1. Create Model from Invoice template data
    2. Add associated tag definitions of model from the template data to db
    3. Add associated line item fields into line item definition table
    """
    invoiceTemplate = await request.json()
    return crud.ParseInvoiceData(modelID, userId, invoiceTemplate, db)


# @router.get("/get_fr_connection/{frp_id}")
# async def get_conn(frp_id:int,db: Session = Depends(get_db)):
#     try:
#         fr_conn = crud.get_connection_by_id(db=db,frp_id=frp_id)
#         return {"message":"success","conn":fr_conn}
#     except Exception as e:
#         return {"message":"exception","conn":""}

# @router.get("/get_fr_connection_by_project/{pid}")
# async def get_conn(pid:int,db: Session = Depends(get_db)):
#     try:
#         fr_conn = crud.get_connection_by_id_by_project(db=db,pid=pid)
#         return {"message":"success","conn":fr_conn}
#     except Exception as e:
#         print(e)
#         return {"message":"exception","conn":""}


# @router.get("/get_projects/{pid}/{user_id}")
# async def get_project(pid:int,user_id:str,db: Session = Depends(get_db)):
#     try:
#         projects = crud.get_fr_projects(db,user_id,pid)
#         return {"message":"success","projects":list(projects)}
#     except Exception as e:
#         return {"message":f"exception {e}","projects":[]}

# @router.put("/update_connection/{user_id}/{pid}")
# async def update_connection(request:Request,user_id:str,pid:int,db: Session = Depends(get_db)):
#     try:
#         connection = request.headers.get('storage_token')
#         status = crud.update_fr_project_connection(db=db,user_id=user_id,pid=pid,conn=connection)
#         return {"message":status}
#     except Exception as e:
#         print(e)
#         return {"message":"exception"}
        
@router.get("/get_tagging_info/{documentId}")
async def get_tagging_details(request:Request,documentId:int,db: Session = Depends(get_db)):
    try:
        folder_path = request.headers.get("path")
        connection_string = request.headers.get("connection_string")
        if connection_string == None:
            connection_string = os.environ['Azure_conn_str']
        print(f"connstr {connection_string}")    
        container = request.headers.get("container")
        savelabels = "{}"
        blob_client_service = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_client_service.get_container_client(container)
        list_of_blobs = container_client.list_blobs(name_starts_with=folder_path)
        file_list = []
        fields = crud.getFields(documentId,db)
        if fields == None:
            fields = '{"fields":[]}'
        fields = json.loads(fields)
        fieldexist = False
        acceptedext = ['.pdf','.png','.jpeg','.jpg']
        for b in list_of_blobs:
            if b.name.endswith("fields.json"):
                blob = blob_client_service.get_blob_client(container,b.name).download_blob().readall()
                fields = json.loads(blob)
            if os.path.splitext(b.name)[1] in acceptedext:
                bdata = blob_client_service.get_blob_client(container,b.name).download_blob().readall()
                #bdata = blob_client_service.get_blob_to_bytes(container,b.name)
                obj = {}
                filename = b.name.split("/")[-1]
                if os.path.splitext(b.name)[1] == '.pdf':
                    images = convert_from_bytes(bdata,dpi=92,poppler_path='/usr/bin')
                    for i in images:
                        im_bytes = BytesIO()
                        i.save(im_bytes, format='JPEG')
                        b64 = base64.b64encode(im_bytes.getvalue()).decode('utf-8')
                        obj[filename] = 'data:image/jpeg;base64,'+str(b64)
                        break
                else:
                    b64 = base64.b64encode(BytesIO(bdata).getvalue()).decode('utf-8')
                    obj[filename] = 'data:image/jpeg;base64,'+str(b64)
                file_list.append(obj)
        if len(fields['fields']) > 0:
            fieldexist = True
        return {"message":"success","file_list":file_list,"fields":fields,"fieldexist":fieldexist,"savedlabels":savelabels}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /get_tagging_info",str(e))
        return {"message":f"exception {e}","file_list":[],"fields":{},"fieldexist":False,"savedlabels":"{}"}

@router.get("/get_labels_info/{filename}")
async def get_tagging_details(request:Request,filename:str,db: Session = Depends(get_db)):
    try:
        folder_path = request.headers.get('folderpath')
        configs = getOcrParameters(1,db)
        containername = configs.ContainerName
        connection_string = configs.ConnectionString
        blob_client_service = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_client_service.get_container_client(containername)
        list_of_blobs = container_client.list_blobs(name_starts_with=folder_path)
        labels = {}
        for b in list_of_blobs:
            if b.name.endswith(filename+".labels.json"):
                try:
                    blob = blob_client_service.get_blob_client(containername,b.name).download_blob().readall()
                    labels = {'blob':blob,'labelexist':True}
                except:
                    labels = {'blob':{},'labelexist':False}
        return {"message":"success","labels":labels}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /get_labels_info",str(e))
        return {"message":f"exception {e}","labels":{}}
        
@router.post("/save_labels_file")
async def save_labels_file(request:Request,db: Session = Depends(get_db)):
    try:
        body = await request.json()
        container = body["container"]
        filename = body["filename"]
        connstr = body['connstr']
        labeljson = body["labelJson"]
        savejson = body["saveJson"]
        idDocumentModel = body['documentId']
        #crud.updateLabels(idDocumentModel,savejson,db)
        blob_name = filename+'.labels.json'
        json_string = json.dumps(labeljson)
        blob_client_service = BlobServiceClient.from_connection_string(connstr)
        bloblient = blob_client_service.get_blob_client(container,blob=blob_name)
        bloblient.upload_blob(json_string,overwrite=True)
        return {"message":"success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /save_labels_file",str(e))
        return {"message":f"exception {e}"}

@router.post("/save_fields_file")
async def save_fields_file(request:Request,db: Session = Depends(get_db)):
    try:
        body = await request.json()
        fields = body['fields']
        documentId = body['documentId']
        connstr = body['connstr']
        folderpath = body['folderpath']
        container = body['container']
        crud.updateFields(documentId,json.dumps(fields),db)
        blob_name = folderpath+'/'+'fields.json'
        json_string = json.dumps(fields)
        blob_client_service = BlobServiceClient.from_connection_string(connstr)
        blobclient = blob_client_service.get_blob_client(container,blob=blob_name)
        blobclient.upload_blob(json_string,overwrite=True)
        return {"message":"success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /save_fields_file",str(e))
        return {"message":f"exception {e}"}

@router.post("/reset_tagging")
async def reset(request:Request,db: Session = Depends(get_db)):  
    try:
        reqbody = await request.json()
        model_id = reqbody['model_id']
        folderpath = reqbody['folderpath']
        configs = getOcrParameters(1, db)
        containername = configs.ContainerName
        connection_str = configs.ConnectionString
        blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        container_client = blob_service_client.get_container_client(containername)
        list_of_blobs = container_client.list_blobs(name_starts_with=folderpath)
        for b in list_of_blobs:
            if b.name.endswith("labels.json"):
                container_client.delete_blob(blob=b.name)
        db.query(model.DocumentModel).filter(model.DocumentModel.idDocumentModel == model_id).update({'labels':None})
        db.commit()
        return {"message":"success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /reset_tagging",str(e))
        return {"message":f"exception {e}"}

@router.get("/get_analyze_result/{container}")
async def get_result(request:Request,container:str,db: Session = Depends(get_db)):
    try:
        filename = request.headers.get('filename')
        connstr = request.headers.get('connstr')
        frconfigs = getOcrParameters(1,db)
        fr_endpoint = frconfigs.Endpoint
        fr_key = frconfigs.Key1
        storage = request.headers.get('account')
        account_key = connstr.split("AccountKey=")[1].split(";EndpointSuffix")[0]
        ext = os.path.splitext(filename)[1]
        content_type = ''
        if ext == ".jpg":
            content_type = 'image/jpg'
        elif ext == '.jpeg':
            content_type = 'image/jpeg'
        elif ext == '.png':
            content_type = 'image/png'
        else:
            content_type = 'application/pdf'
        
        token = generate_blob_sas(
            account_name=storage,
            container_name=container,
            blob_name=filename,
            account_key=account_key,
            permission=ContainerSasPermissions(read=True,write=True,list=True,delete=True),
            start=datetime.utcnow() - timedelta(hours=3),
            expiry=datetime.utcnow() + timedelta(hours=3),
            content_type=content_type
        )
        file_url = 'https://'+storage+'.blob.core.windows.net/'+container+'/'+filename+'?'+token
        url = f"{fr_endpoint}formrecognizer/v2.1/layout/analyze"
        headers = {
            'Content-Type':'application/json',
            'Ocp-Apim-Subscription-Key':fr_key
        }
        blob_client_service = BlobServiceClient.from_connection_string(connstr)
        blob_client = blob_client_service.get_blob_client(container,blob=filename+'.ocr.json')
        if blob_client.exists():
            bdata = blob_client.download_blob().readall()
            json_result = json.loads(bdata)    
        else:
            body = json.dumps({'source':file_url})
            json_result = fr.analyzeForm(url=url,headers=headers,body=body)
            #json_result = util.correctAngle(json_result)
            json_string = json.dumps(json_result)
            blob_client.upload_blob(json_string,overwrite=True)
        return {"message":"success","json_result":json_result,"file_url":file_url,"content_type":content_type}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /get_analyze_result",str(e))
        return {"message":f"exception {e}","json_result":{},"file_url":"","content_type":""}

@router.post("/test_analyze_result/{modelid}")
async def get_test_result(request:Request,modelid:str,file: UploadFile = File(...),db: Session = Depends(get_db)):
    try:
        frconfigs = getOcrParameters(1,db)
        fr_endpoint = frconfigs.Endpoint
        fr_key = frconfigs.Key1
        url = f"{fr_endpoint}formrecognizer/v2.1/custom/models/{modelid}/analyze?includeTextDetails=true"
        metadata, f, valid_file = await ut.get_file(file,900)
        if not valid_file:
            return {'message':'File is invalid'}   
        acceptedfiletype = ['application/pdf','image/jpg','image/png','image/jpeg']
        contenttype = "application/pdf"
        if metadata[0] in acceptedfiletype:
            contenttype = metadata[0] 
        fileurl = ""
        if contenttype != "application/pdf":
            b64 = base64.b64encode(f.getvalue()).decode('utf-8')
            fileurl = 'data:image/jpeg;base64,'+str(b64)
        headers = {
            'Content-Type':contenttype,
            'Ocp-Apim-Subscription-Key':fr_key
        }
        body = f.getvalue()
        json_result = fr.analyzeForm(url=url,headers=headers,body=body)
        json_result = ut.correctAngle(json_result)
        return {"message":"success","json_result":json_result,"content_type":contenttype,"url":fileurl}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /test_analyze_result",str(e))
        return {"message":f"exception {e}","json_result":{},"content_type":"","url":""}


@router.get("/get_training_result/{documentmodelId}")
async def get_training_res(documentmodelId:int,db: Session = Depends(get_db)):
    try:
        training_res = crud.get_fr_training_result(db,documentmodelId)
        return {"message":"success","result":[training_res]}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /get_training_result",str(e))
        return {"message":f"exception {e}","result":[]}

@router.get("/check_model_status/{modelId}")
async def check_model(modelId: str,db: Session = Depends(get_db)):
    try:
        frconfigs = getOcrParameters(1,db)
        fr_endpoint = frconfigs.Endpoint
        fr_key = frconfigs.Key1
        url = f"{fr_endpoint}formrecognizer/v2.1/custom/models/{modelId}?includeKeys=False"
        headers = {
            'Content-Type':'application/json',
            'Ocp-Apim-Subscription-Key':fr_key
        }
        get_resp = requests.get(url,headers=headers)
        if get_resp.status_code == 200:
            return get_resp.json()
        else:
            return {"message":"exception"}
    except Exception as e:
        print(e)
        return {"message":"exception"}


@router.get("/get_training_result_vendor/{modeltype}/{vendorId}")
async def get_training_res(vendorId:int,modeltype:str,db: Session = Depends(get_db)):
    try:
        training_res = crud.get_fr_training_result_by_vid(db,modeltype,vendorId)
        res = crud.get_composed_training_result_by_vid(db,modeltype,vendorId)
        for r in res:
            training_res.append(r)
        return {"message":"success","result":training_res}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /get_training_result_vendor",str(e))
        return {"message":f"exception {e}","result":[]}

@router.post("/create_training_result")
async def create_result(request:Request,db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        fr_result = req_body['fr_result']
        docid = req_body['docid']
        create_result = crud.updateTrainingResult(docid,fr_result,db)
        return {"message":create_result}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /create_training_result",str(e))
        return {"message":"exception"}

@router.post("/create_compose_result")
async def create_result(request:Request,db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        create_result = crud.createOrUpdateComposeModel(req_body,db)
        return {"message":create_result}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /create_compose_result",str(e))
        return {"message":"exception"}

@router.post("/compose_model")
async def compose_model(request:Request,db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        modelIds = req_body['modelIds']
        modelName = req_body['modelName']
        frconfigs = getOcrParameters(1,db)
        fr_endpoint = frconfigs.Endpoint
        fr_key = frconfigs.Key1
        compose_url = f"{fr_endpoint}formrecognizer/v2.1/custom/models/compose"
        headers = {
            'Content-Type':'application/json',
            'Ocp-Apim-Subscription-Key':fr_key
        }
        body = {
            "modelIds":modelIds,
            "modelName":modelName
        }
        post_resp = requests.post(compose_url,data=json.dumps(body),headers=headers)
        get_url = post_resp.headers["location"]
        json_resp = fr.getModelResponse(get_url=get_url,headers=headers)
        return {"message":"success","result":json_resp}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /compose_model",str(e))
        return {"message":f"exception {e}","result":{}}

@router.post("/train-model")
async def train_model(request:Request,db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        frconfigs = getOcrParameters(1,db)
        fr_endpoint = frconfigs.Endpoint
        fr_key = frconfigs.Key1
        connstr = req_body['connstr']
        account_key = connstr.split("AccountKey=")[1].split(";EndpointSuffix")[0]
        blob_client_service = BlobServiceClient.from_connection_string(connstr)
        folder_path = req_body['folderpath']
        container = req_body['container']
        storage = req_body['account']
        container_client = blob_client_service.get_container_client(container)
        list_of_blobs = container_client.list_blobs(name_starts_with=folder_path)
        blob_list = []
        for b in list_of_blobs:
            if b.name != "fields.json":
                blob_list.append(b.name)
        acceptedext = ['.pdf','.png','.jpeg','.jpg']
        file_counter = 0
        error_list = []
        for b in blob_list:
            if os.path.splitext(b)[1] in acceptedext:
                file_counter += 1
                if b+".labels.json" not in blob_list:
                    error_list.append({'file':b,'message':'File missing labels.json file'})
                if b+".ocr.json" not in blob_list:
                    error_list.append({'file':b,'message':'File missing ocr.json file'})
        if len(error_list) > 0:
            return {"errorlist":error_list}
        if file_counter < 5:
            return {"error":"Training files should be more than 5"}
        include_subfolders = False
        modelName = req_body['modelName']
        training_url = f"{fr_endpoint}formrecognizer/v2.1/custom/models"
        token = generate_container_sas(storage, container, account_key=account_key, permission=ContainerSasPermissions(read=True,write=True,delete=True,list=True), expiry=datetime.utcnow() + timedelta(hours=1), start=datetime.utcnow() - timedelta(hours=1))
        connection_url = f"https://{storage}.blob.core.windows.net/{container}?"+token
        headers = {
            'Content-Type':'application/json',
            'Ocp-Apim-Subscription-Key':fr_key
        }
        body = {
            "source": connection_url,
            "sourceFilter": {
            "prefix": folder_path,
            "includeSubFolders": include_subfolders
         },
        "useLabelFile": True,
        "modelName":modelName
        }
        post_resp = requests.post(training_url,data=json.dumps(body),headers=headers)
        get_url = post_resp.headers["location"]
        json_resp = fr.getModelResponse(get_url=get_url,headers=headers)
        return {"message":json_resp['message'],"result":json_resp['result']}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py /train-model",str(e))
        return {"message":f"exception {e}","result":{},"post_resp":post_resp.text}
# @app.post("/startOnBoard")
# async def extract_text(image: UploadFile = File(...)):

def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(
            model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","modelonboarding.py getOcrParameters",str(e))
        return Response(status_code=500, headers={"DB Error": "Failed to get OCR parameters"})
