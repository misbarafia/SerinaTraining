from email.policy import strict
import imp
from numpy import size
from fastapi import Depends,status, APIRouter, Request, Response
import sys,jwt,model,traceback,json,requests
sys.path.append("..")
from logModule import applicationlogging
from auth import AuthHandler
from sqlalchemy.orm import Session,load_only, Load
from session import Session as SessionLocal
from crud import customerCrud as crd
from typing import Optional
from azure.storage.blob import BlobServiceClient
# model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/emailconfig",
    tags=["EmailListener"],
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
        applicationlogging.logException("ROVE HOTEL DEV","maillistener.py getOCRParametes",str(e))
        return Response(status_code=500, headers={"DB Error": "Failed to get OCR parameters"})

def getuserdetails(username, db):
    """
    ### Function to fetch the details of the user performing log in
    :param username: It is a string parameter for providing username
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the user data
    """
    try:
        data = db.query(model.User, model.Credentials, model.AccessPermission.idAccessPermission,
                        model.AccessPermissionDef, model.AmountApproveLevel).options(
            Load(model.User).load_only("firstName", "lastName", "isActive"),
            Load(model.AccessPermissionDef).load_only("NameOfRole", "Priority", "User", "Permissions", "isUserRole",
                                                      "AccessPermissionTypeId", "allowBatchTrigger",
                                                      "allowServiceTrigger", "NewInvoice"),
            Load(model.Credentials).load_only("LogSecret", "crentialTypeId")).filter(
            model.User.idUser == model.Credentials.userID).filter(
            model.Credentials.crentialTypeId.in_((1, 2))).filter(model.Credentials.LogName == username).join(
            model.AccessPermission, model.AccessPermission.userID == model.User.idUser, isouter=True).join(
            model.AccessPermissionDef,
            model.AccessPermissionDef.idAccessPermissionDef == model.AccessPermission.permissionDefID).join(
            model.AmountApproveLevel,
            model.AmountApproveLevel.idAmountApproveLevel == model.AccessPermissionDef.amountApprovalID, isouter=True)
        return data.all()
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","maillistener.py getuserdetails",str(e))
        print(traceback.print_exc())
    finally:
        db.close()

@router.get("/getemailconfig/{userId}", status_code=status.HTTP_200_OK)
async def getemailconfig(userId:str,db: Session = Depends(get_db)):
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
        secret_name = 'rovehotels'
        vault_url = f"{keyvault_url}/secrets/{secret_name}?api-version=7.2"
        configresp = requests.get(vault_url,headers={"Authorization":f"Bearer {access_token}"})
        if configresp.status_code == 200:
            config = configresp.json()['value']
            config = jwt.decode(config,auth_handler.secret,algorithms=['HS256'])
            message = 'success'
        else:
            message = 'KeyVault Access Denied'
            config = {}
        config["synonyms"] = createsynonym_config(db)
        return {"message":message,"config":config}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","maillistener.py getemailconfig",str(e))
        return {"message":f"exception {e}","config":{}}

@router.post("/saveemailconfig", status_code=status.HTTP_200_OK)
async def saveemailconfig(request:Request,db: Session = Depends(get_db)):
    try:
        req_body = await request.json()
        username = req_body['username']
        password = req_body['password']
        folder = req_body['folder']
        loginuser = req_body['loginuser']
        loginpass = req_body['loginpass']
        host = req_body['host']
        acceptedDomains = req_body['acceptedDomains']
        acceptedEmails = req_body['acceptedEmails']
        userdetails = getuserdetails(loginuser, db)
        if not auth_handler.verify_password(loginpass,userdetails[0][1].LogSecret):
            return {"message": f"Invalid username and/or password"}
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
        secret_name = 'rovehotels'
        vault_url = f"{keyvault_url}/secrets/{secret_name}?api-version=7.2"
        configresp = requests.get(vault_url,headers={"Authorization":f"Bearer {access_token}"})
        if configresp.status_code == 200:
            config = configresp.json()['value']
            final_dict = jwt.decode(config,auth_handler.secret,algorithms=['HS256'])
            final_dict["username"] = username
            final_dict["password"] = password
            final_dict["folder"] = folder
            final_dict["host"] = host
            final_dict["loginuser"] = loginuser
            final_dict["loginpass"] = loginpass
            final_dict['acceptedDomains'] = acceptedDomains
            final_dict['acceptedEmails'] = acceptedEmails
        else:
            configs = getOcrParameters(1,db)
            connection_str = configs.ConnectionString
            containername = configs.ContainerName
            blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_str)
            account_key = connection_str.split("AccountKey=")[1].split(";EndpointSuffix")[0]
            final_dict = {
                "username":username,
                "password":password,
                "host":host,
                "folder":folder,
                "acceptedEmails":acceptedEmails,
                "acceptedDomains":acceptedDomains,
                "accepted_attachments":["application/pdf","image/png","image/jpg","image/jpeg"],
                "bulk_attachments":["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
                "connectStr":connection_str,
                "containerName":containername,
                "accountname":blob_service_client.account_name,
                "accountkey":account_key,
                "host-endpoint":"https://serina-qa.centralindia.cloudapp.azure.com/apiv1.1",
                "accepted_headers":"document url",
                "loginuser":loginuser,
                "loginpass":loginpass,
                "bulk_upload_url":"http://20.204.220.145",
                "serina-endpoint":configs.Endpoint,
                "model":"prebuilt-invoice",
                "fr-version":"api-version=2021-09-30-preview",
                "fr-key":configs.Key1
            }
        encoded_dict = jwt.encode(final_dict,auth_handler.secret,algorithm='HS256')
        set_body = {
            "value": encoded_dict
        }
        setresp = requests.put(vault_url,data=json.dumps(set_body),headers={"Content-Type":"application/json","Authorization":f"Bearer {access_token}"})
        mes = "secret created"
        return {"message":"success","details":mes}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","maillistener.py saveemailconfig",str(e))
        return {"message":f"exception","details":e}

@router.get("/getvendoraccount/{vendorname}", status_code=status.HTTP_200_OK)
async def getvendoraccount(vendorname:str,entityID: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        vendordetails = db.query(model.Vendor).filter(model.Vendor.VendorName == vendorname).first()
        if entityID:
            vendordetails = db.query(model.Vendor).filter(model.Vendor.VendorName == vendorname,model.Vendor.entityID == entityID).first()
        vendorId = vendordetails.idVendor if vendordetails else "0"
        if vendorId != "0":
            return await crd.readvendoraccount(1,vendorId,db)
        else:
            return {"message":"Vendor ID missing"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","maillistener /getvendoraccount",str(e))
        return {"message":"exception, Check Log details"}

def createsynonym_config(db):
    try:
        Synonyms = db.query(model.Vendor).filter(model.Vendor.Synonyms.isnot(None)).all()
        obj = {}
        for s in Synonyms:
            obj[s.VendorName] = json.loads(s.Synonyms,strict=False)
        return obj
    except Exception as e:
        print(e)
        return {}


