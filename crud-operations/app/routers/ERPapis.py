import requests
import json
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, BackgroundTasks
from auth import AuthHandler
from session import Session as SessionLocal
from session import engine
import sys
sys.path.append("..")
from logModule import applicationlogging
import model
from sqlalchemy.orm import Session, load_only, Load


# model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Invoice",
    tags=["invoice"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def gettoken():
    client_id = "9f75db6c-2c6e-4ac1-a26c-73d5799b3ca6"
    client_secret = "r1IL.3~7wlbG1yaV3c4OoA_X~ly_h4.j2f"
    res='https://ehgerpint.sandbox.operations.dynamics.com/'
    # scope = "appstore::apps:readwrite"
    grant_type = "client_credentials"
    data = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": res
    }
    amazon_auth_url = "https://login.microsoftonline.com/emaarproperties.onmicrosoft.com/oauth2/token"
    auth_response = requests.post(amazon_auth_url, data=data)

    # Read token from auth response
    auth_response_json = auth_response.json()
    auth_token = auth_response_json["access_token"]
    auth_token_header_value = "Bearer %s" % auth_token
    headers = {"Authorization": auth_token_header_value}
    return headers

check_statusurl="https://ehgerpint.sandbox.operations.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/checkInvoice"
@router.get("/InvoiceStatus/{inv_id}")
async def read_status(inv_id: int, db: Session = Depends(get_db)):
    ent_id=db.query(model.Document.entityID).filter(model.Document.idDocument == inv_id).distinct().one()
    dataareaid=db.query(model.Entity.EntityCode).filter(model.Entity.idEntity == ent_id[0]).distinct().one()
    invoice_id=db.query(model.Document.docheaderID).filter(model.Document.idDocument == inv_id).distinct().one()
    vendoracc_id=db.query(model.Document.vendorAccountID).filter(model.Document.idDocument == inv_id).distinct().one()
    if vendoracc_id[0] is None:
        servacc_id=db.query(model.Document.supplierAccountID).filter(model.Document.idDocument == inv_id).distinct().one()
        serv_id=db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == servacc_id[0]).distinct().one()
        vendcode_id=db.query(model.ServiceProvider.ServiceProviderCode).filter(model.ServiceProvider.idServiceProvider == serv_id[0]).distinct().one()
        invoice_id=invoice_id[0] +'-1'  
    else:
        vend_id=db.query(model.VendorAccount.vendorID).filter(model.VendorAccount.idVendorAccount == vendoracc_id[0]).distinct().one()
        vendcode_id=db.query(model.Vendor.VendorCode).filter(model.Vendor.idVendor == vend_id[0]).distinct().one()
        invoice_id=invoice_id[0]
    status_checkdata={"dataArea":dataareaid[0],"vendAccount":vendcode_id[0],"invoicenum":invoice_id}
    applicationlogging.logException("ROVE HOTEL DEV","ERPapis.py read_status",json.dumps(status_checkdata))
    headers = gettoken()
    status_response = requests.post(check_statusurl, json=status_checkdata,headers=headers)
    status_response_json = status_response.json()
    print(f"status response {status_response_json}")
    status_response_json = json.loads(status_response_json)
    return status_response_json


#for checking payment status
check_payment_statusurl="https://ehgerpint.sandbox.operations.dynamics.com/api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/paymentstatus"
@router.get("/InvoicePaymentStatus/{inv_id}")
async def read_payment_status(inv_id: int, db: Session = Depends(get_db)):
    ent_id=db.query(model.Document.entityID).filter(model.Document.idDocument == inv_id).distinct().one()
    dataareaid=db.query(model.Entity.EntityCode).filter(model.Entity.idEntity == ent_id[0]).distinct().one()
    invoice_id=db.query(model.Document.docheaderID).filter(model.Document.idDocument == inv_id).distinct().one()
    vendoracc_id=db.query(model.Document.vendorAccountID).filter(model.Document.idDocument == inv_id).distinct().one()
    if vendoracc_id[0] is None:
        servacc_id=db.query(model.Document.supplierAccountID).filter(model.Document.idDocument == inv_id).distinct().one()
        serv_id=db.query(model.ServiceAccount.serviceProviderID).filter(model.ServiceAccount.idServiceAccount == servacc_id[0]).distinct().one()
        vendcode_id=db.query(model.ServiceProvider.ServiceProviderCode).filter(model.ServiceProvider.idServiceProvider == serv_id[0]).distinct().one()
        invoice_id=invoice_id[0] +'-1'  
    else:
        vend_id=db.query(model.VendorAccount.vendorID).filter(model.VendorAccount.idVendorAccount == vendoracc_id[0]).distinct().one()
        vendcode_id=db.query(model.Vendor.VendorCode).filter(model.Vendor.idVendor == vend_id[0]).distinct().one()
        invoice_id=invoice_id[0]
    payment_status_checkdata={"dataArea":dataareaid[0],"vendAccount":vendcode_id[0],"invoicenum":invoice_id}
    applicationlogging.logException("ROVE HOTEL DEV","ERPapis.py read_payment_status",json.dumps(payment_status_checkdata))
    headers = gettoken()
    status_response = requests.post(check_payment_statusurl, json=payment_status_checkdata,headers=headers)
    status_response_json = status_response.json()
    print(f"status response {status_response_json}")
    status_response_json = json.loads(status_response_json)
    return status_response_json
