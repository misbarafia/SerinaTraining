from azure.storage.blob import BlobServiceClient
from logModule import applicationlogging
import sys
sys.path.append("..")
import model
def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(
            model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","VendorPortal.py getOcrParameters",str(e))
        return {}

def upload_to_blob(file_name,file_content,db):
    try:
        configs = getOcrParameters(1, db)
        containername = configs.ContainerName
        connection_str = configs.ConnectionString
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_str, container_name=containername)
        container_client = blob_service_client.get_container_client(containername)
        file_path = "JourneyDocs/"+file_name
        container_client.upload_blob(name=file_path, data=file_content, overwrite=True)
        return "success"
    except Exception as e:
        print(e)
        return "exception"