from io import BytesIO
from typing import Optional
from schemas import InvoiceSchema as schema
import model
from sqlalchemy.orm import Session, Load
from auth import AuthHandler
from fastapi import Depends, APIRouter, UploadFile, File, Response
import os
import shutil
import sys
sys.path.append("..")
from logModule import applicationlogging
from crud import VendorPortalCrud as crud
from schemas import InvoiceSchema as schema
import model
from session import Session as SessionLocal
from session import engine
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import  generate_blob_sas,ContainerSasPermissions
from datetime  import datetime,timedelta
model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/VendorPortal",
    tags=["Vendor Portal"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/getponumbers/{vendorAccountID}")
async def get_po_numbers(vendorAccountID: int, ent_id: Optional[int] = None, u_id: Optional[int] = None, db: Session = Depends(get_db)):
    """

    """
    return await crud.read_po_numbers(u_id, vendorAccountID, ent_id, db)


@router.post("/addlabel/{invoicemodelID}")
async def add_label(invoicemodelID: int, labelDef: schema.TagDef, db: Session = Depends(get_db)):
    """
    API to add a new label definition to a document model
    """
    return await crud.add_label(invoicemodelID, labelDef, db)


@router.post("/addlineitem/{invoicemodelID}")
async def add_lineitem_tag(invoicemodelID: int, lineitemDef: schema.LineItemDef, db: Session = Depends(get_db)):
    """
    API to add a new line item definition to a document model
    """
    return await crud.add_label(invoicemodelID, lineitemDef, db)


@router.post("/uploadfile/{vendorAccountID}")
async def upload_file(vendorAccountID: int, file: UploadFile = File(...),db: Session = Depends(get_db)):
    content = await file.read()
    configs = getOcrParameters(
        1, db)
    print(vendorAccountID)
    filetype = file.content_type
    filename = file.filename
    containername = configs.ContainerName
    connection_str = configs.ConnectionString
    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    account_key = connection_str.split("AccountKey=")[1].split(";EndpointSuffix")[0]
    
    container_client = blob_service_client.get_container_client(containername)
    blob_client = container_client.upload_blob(name="Uploadeddocs/"+filename, data=BytesIO(content),overwrite=True)
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=containername,
        blob_name="Uploadeddocs/"+filename,
        account_key=account_key,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1),
        content_type=filetype
    )
    filepath = f"https://{blob_service_client.account_name}.blob.core.windows.net/{containername}/Uploadeddocs/{filename}?{sas_token}"
    # file_location = f"Uploaded_docs/{file.filename}"
    # with open(file_location, "wb+") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    return {"filepath": filepath,"filename":filename,"filetype":filetype}

def getOcrParameters(customerID, db):
    try:
        configs = db.query(model.FRConfiguration).filter(
            model.FRConfiguration.idCustomer == customerID).first()
        return configs
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","VendorPortal.py getOcrParameters",str(e))
        return Response(status_code=500, headers={"DB Error": "Failed to get OCR parameters"})
