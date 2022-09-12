# from model import Vendor
# some_file.py
import traceback

from fastapi import Depends, FastAPI
# from dependency.dependencies import get_query_token, get_token_header
from fastapi.middleware.cors import CORSMiddleware


# dependencies=[Depends(get_query_token)])
app = FastAPI(title="SERINA", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from routers import serviceprovider, vendor, invoice, permissions, customer, authenticate, FR, OCR, modelonboarding, \
    VendorPortal, SPbulkupload, batchexception, summary, notification, maillistener, sharepoint, dashboardapi, ERPapis

# Define routers in the main
app.include_router(serviceprovider.router)
app.include_router(customer.router)
app.include_router(vendor.router)
app.include_router(invoice.router)
app.include_router(permissions.router)
# app.include_router(service.router)
app.include_router(authenticate.router)
app.include_router(FR.router)
app.include_router(OCR.router)
app.include_router(modelonboarding.router)
app.include_router(VendorPortal.router)
app.include_router(SPbulkupload.router)
app.include_router(summary.router)
app.include_router(batchexception.router)
app.include_router(notification.router)
app.include_router(maillistener.router)
app.include_router(sharepoint.router)
app.include_router(dashboardapi.router)
app.include_router(ERPapis.router)
# from fastapi_utils.tasks import repeat_every
from session.notificationsession import client
from fastapi.middleware.wsgi import WSGIMiddleware

app.mount("/v1", WSGIMiddleware(client))


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
