from email.policy import strict
from numpy import size
from fastapi import Depends,status, APIRouter, Request, Response
import sys,jwt,model,traceback,json,requests
sys.path.append("..")
from auth import AuthHandler
from logModule import applicationlogging
from sqlalchemy.orm import Session,load_only, Load
from session import Session as SessionLocal
from azure.storage.blob import BlobServiceClient
# model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/sharepoint",
    tags=["Sharepoint"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","sharepoint.py getOcrParameters",str(e))
        return Response(status_code=500, headers={"DB Error": "Failed to get OCR parameters"})


@router.get("/getsharepointconfig", status_code=status.HTTP_200_OK)
async def getsharepointconfig(db: Session = Depends(get_db)):
    try:
        tenant_id = '86fb359e-1360-4ab3-b90d-2a68e8c007b9'
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        body = {
            "grant_type":"client_credentials",
            "client_id":"44e503fe-f768-46f8-99bf-803d4a2cf62d",
            "scope":"https://vault.azure.net/.default",
            "client_secret":"uXB7Q~yxwdwfzrDX8GgkqlLdxMK3O0iQU_ZDJ"
        }
        headers = {
            'Content-Type':'application/x-www-form-urlencoded'
        }
        token_resp = requests.post(token_url,data=body,headers=headers)
        access_token = token_resp.json()['access_token']
        keyvault_url = 'https://rove-vault.vault.azure.net/'
        secret_name = 'roveclient'
        vault_url = f"{keyvault_url}/secrets/{secret_name}?api-version=7.2"
        configresp = requests.get(vault_url,headers={"Authorization":f"Bearer {access_token}"})
        if configresp.status_code == 200:
            config = configresp.json()['value']
            config = jwt.decode(config,auth_handler.secret,algorithms=['HS256'])
            message = 'success'
        else:
            message = 'Fail to get Sharepoint config'
            config = {}
        secret_name = 'rovehotels'
        vault_url = f"{keyvault_url}/secrets/{secret_name}?api-version=7.2"
        synresp = requests.get(vault_url,headers={"Authorization":f"Bearer {access_token}"})
        if synresp.status_code == 200:
            conf = synresp.json()['value']
            conf = jwt.decode(conf,auth_handler.secret,algorithms=['HS256'])
            print(conf)
            result = {"serina-endpoint":conf["serina-endpoint"],"model":conf["model"],"fr-version":conf["fr-version"],"fr-key":conf["fr-key"],"synonyms":createsynonym_config(db)}
            message = 'success'
        else:
            message = 'Fail to get Synonyms'
            result = {}
        return {"message":message,"config":config,"frconfig":result}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","sharepoint.py /getsharepointconfig",str(e))
        return {"message":f"exception {e}","config":{},"frconfig":{}}

@router.post("/savesharepointconfig", status_code=status.HTTP_200_OK)
async def savesharepointconfig(request:Request,db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        client_id = req_body['client_id']
        client_secret = req_body['client_secret']
        folder = req_body['folder']
        site_url = req_body['site_url']
        service_url = req_body['service_url']
        tenant_id = '86fb359e-1360-4ab3-b90d-2a68e8c007b9'
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        body = {
            "grant_type":"client_credentials",
            "client_id":"44e503fe-f768-46f8-99bf-803d4a2cf62d",
            "scope":"https://vault.azure.net/.default",
            "client_secret":"uXB7Q~yxwdwfzrDX8GgkqlLdxMK3O0iQU_ZDJ"
        }
        token_resp = requests.post(token_url,data=body,headers={'Content-Type':'application/x-www-form-urlencoded'})
        access_token = token_resp.json()['access_token']
        keyvault_url = 'https://rove-vault.vault.azure.net/'
        secret_name = 'roveclient'
        vault_url = f"{keyvault_url}/secrets/{secret_name}?api-version=7.2"
        configresp = requests.get(vault_url,headers={"Authorization":f"Bearer {access_token}"})
        if configresp.status_code == 200:
            config = configresp.json()['value']
            final_dict = jwt.decode(config,auth_handler.secret,algorithms=['HS256'])
            final_dict["client_id"] = client_id
            final_dict["client_secret"] = client_secret
            final_dict["folder"] = folder
            final_dict["site_url"] = site_url
            final_dict["service_url"] = service_url
        else:
            final_dict = {
                "client_id":client_id,
                "client_secret":client_secret,
                "folder":folder,
                "site_url":site_url,
                "service_url":service_url
            }
        encoded_dict = jwt.encode(final_dict,auth_handler.secret,algorithm='HS256')
        set_body = {
            "value": encoded_dict
        }
        setresp = requests.put(vault_url,data=json.dumps(set_body),headers={"Content-Type":"application/json","Authorization":f"Bearer {access_token}"})
        return {"message":"success","details":"secret created"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","sharepoint.py /savesharepointconfig",str(e))
        return {"message":f"exception","details":e}

def createsynonym_config(db):
    try:
        Synonyms = db.query(model.Vendor).filter(model.Vendor.Synonyms.isnot(None)).all()
        obj = {}
        for s in Synonyms:
            obj[s.VendorName] = json.loads(s.Synonyms,strict=False)
        return obj
    except Exception as e:
        return {}




