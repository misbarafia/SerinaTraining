
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.runtime.http.request_options import RequestOptions
import os,requests,jwt,sys
from azure.storage.blob import BlobServiceClient
sys.path.append("..")
from auth import AuthHandler
import model
import base64,json
from logModule import applicationlogging
auth_handler = AuthHandler()
def upload_file_to_sharepoint(file_name,file_content,folder,source):
    try:
        message,site_url,client_id,client_secret = sharepoint_creds()
        if message == "success":
            list_title = "AP Invoice Dev/"+folder
            if source == 'SharePoint':
                list_title = "AP Invoice Dev/Archived Dev"
                return site_url+"/"+list_title+"/"+file_name
            ctx = ClientContext(site_url).with_credentials(ClientCredential(client_id,client_secret))
            
            target_folder = ctx.web.get_folder_by_server_relative_url(list_title)
            target_folder.upload_file(file_name, file_content).execute_query()
            return site_url+"/"+list_title+"/"+file_name
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","sharepoint_util.py upload_file",str(e))
        return "exception"

def uploadutility_file_to_blob(file_name,file_content,db):
    try:
        configs = getOcrParameters(1, db)
        containername = configs.ContainerName
        connection_str = configs.ConnectionString
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_str, container_name=containername)
        container_client = blob_service_client.get_container_client(containername)
        file_path = "DU Bills/"+file_name
        container_client.upload_blob(name=file_path, data=file_content)
        return "success"
    except Exception as e:
        print(e)
        return "exception"

def getfile_as_base64(file_name,file_type,file_content):
    try:
        base64_str = base64.b64encode(file_content)
        attachment_dict = {"filename":file_name,"filetype":file_type,"content":base64_str.decode("utf-8")}
        return json.dumps(attachment_dict)
    except Exception as e:
        print(e)
        return "exception"

def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(
            model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","VendorPortal.py getOcrParameters",str(e))
        return {}

def uploadutility_file(file_name,file_content):
    try:
        list_title = "Shared Documents/Utility Bills"
        ctx = ClientContext("https://dsglobal.sharepoint.com/sites/SerinaDev").with_credentials(ClientCredential("1f81940b-2b54-4d5e-8b95-bc87436ec928","igVPhM+0DmmprpI3XCD2VgMLfOYoG+iBof8Qt/9U9Bk="))
        target_folder = ctx.web.get_folder_by_server_relative_url(list_title)
        target_folder.upload_file(file_name, file_content).execute_query()
        return "success"
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","sharepoint_util.py upload_utility_file",str(e))
        return "exception"
        
def sharepoint_creds():
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
        config = {"client_id":"","client_secret":""}
    return message,config['site_url'],config["client_id"],config["client_secret"]