from fastapi import Depends, FastAPI
from fastapi import APIRouter, Depends, Body, status,HTTPException,File, UploadFile
from auth import AuthHandler
from sqlalchemy.orm import Session
from session import Session as SessionLocal
from crud import SPbulkuploadCrud as crud
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/SP",
    tags=["SP"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# @router.post("/UploadData")
# async def readexcel(file: UploadFile = File(...)):
#     return await crud.uploadspdata(file)

@router.post("/BulkUploadData")
async def UploadData(file: UploadFile = File(...),db: Session = Depends(get_db)):
    res= await crud.bulkuploaddata(file,db)
    return {"Result": res}

@router.post("/Downloadstemplate")
async def downloadsptemplate(temp:str):

   return await crud.downloadtemplate(temp)

@router.post("/DownloadRejectedRecords")
async def RejectedRecords(): 
    return await crud.BulkuploaddataRejectedRecords()