import logging, requests
from opencensus.ext.azure.log_exporter import AzureLogHandler

def logException(env,file,msg):
    try:
        key = enableAppInsights()
        handler = AzureLogHandler(connection_string=key)
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.info(f"{env} - Exception in {file} - {msg}")
        return "success"
    except Exception as e:
        print(e)
        return "exception"

def getInstrumentKey():
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
        secret_name = 'instrumentationkey'
        vault_url = f"{keyvault_url}/secrets/{secret_name}?api-version=7.2"
        configresp = requests.get(vault_url,headers={"Authorization":f"Bearer {access_token}"})
        if configresp.status_code == 200:
            key = configresp.json()['value']
        else:
            key = "InstrumentationKey=763f057b-32b6-4e43-8000-7d03d866d178;IngestionEndpoint=https://southeastasia-1.in.applicationinsights.azure.com/"
        return key
    except Exception as e:
        return "InstrumentationKey=763f057b-32b6-4e43-8000-7d03d866d178;IngestionEndpoint=https://southeastasia-1.in.applicationinsights.azure.com/"
def enableAppInsights():
    key = getInstrumentKey()
    return key