from numpy import size
from fastapi import Depends,status, APIRouter, Request, Response
import sys,jwt,model,traceback,json,requests
sys.path.append("..")
from dependency import dependencies
from logModule import applicationlogging
from auth import AuthHandler
from typing import Optional
from sqlalchemy.orm import Session,load_only, Load
from session import Session as SessionLocal
from azure.storage.blob import BlobServiceClient
from crud import dashboardCrud as crud
# model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/invcountbyvendor/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getinvcountbyvendor(u_id: int,documenttype: int,vendor: Optional[str] = None,entity: Optional[int] = None,source: Optional[str] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),
                                 db: Session = Depends(get_db)):
    try:
        data = crud.getinvcountbyvendor(u_id,documenttype,usertype,vendor,entity,source,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /invcountbyvendor",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/rejectedinvcountbyvendor/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getrejinvcountbyvendor(u_id: int,documenttype: int,vendor: Optional[str] = None,entity: Optional[int] = None,source: Optional[str] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),
                                 db: Session = Depends(get_db)):
    try:
        data = crud.getrejectedinvcountbyvendor(u_id,documenttype,usertype,vendor,entity,source,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /invcountbyvendor",str(e))
        return {"message":f"exception {e}","data":[]}


@router.get("/invcountbysource/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getinvcountbysource(u_id:int,documenttype:int,vendor: Optional[str] = None,entity: Optional[int] = None,source: Optional[str] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getinvcountbysource(u_id,documenttype,usertype,vendor,entity,source,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /invcountbysource",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/pendinginvbyamount/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getpendinginvbyamount(u_id:int,documenttype:int,vendor: Optional[str] = None,entity: Optional[int] = None,source: Optional[str] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getpendinginvbyamount(u_id,documenttype,usertype,vendor,entity,source,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /pendinginvbyamount",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/ageingreport/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getageingreport(u_id:int,documenttype:int,vendor: Optional[str] = None,entity: Optional[int] = None,source: Optional[str] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.ageingreport(u_id,documenttype,usertype,vendor,entity,source,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /ageingreport",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/vendorbasedsummary/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getvendorsummary(u_id:int,documenttype:int,vendor: Optional[str] = None,entity: Optional[int] = None,source: Optional[str] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getvendorsummary(u_id,documenttype,usertype,vendor,entity,source,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /vendorbasedsummary",str(e))
        return {"message":f"exception {e}","data":{}}


@router.get("/exceptionsummary/{u_id}/{documenttype}",status_code=status.HTTP_200_OK)
async def getvendorsummary(u_id:int,documenttype:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getexceptionsummary(u_id,documenttype,usertype,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /exceptionsummary",str(e))
        return {"message":f"exception {e}","data":{}}

@router.get("/servpendingbyamount/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getpendingservbyamount(u_id:int,documenttype:int,serviceprovider: Optional[str] = None,entity: Optional[int] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getpendingservbyamount(u_id,documenttype,usertype,serviceprovider,entity,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /servpendingbyamount",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/servprocessedbyamount/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getprocessedservbyamount(u_id:int,documenttype:int,serviceprovider: Optional[str] = None,entity: Optional[int] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getprocessedservbyamount(u_id,documenttype,usertype,serviceprovider,entity,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /servpendingbyamount",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/overallserv/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getoverallserv(u_id:int,documenttype:int,serviceprovider: Optional[str] = None,entity: Optional[int] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getoverallserv(u_id,documenttype,usertype,serviceprovider,entity,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /servpendingbyamount",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/overallservbyprovider/{u_id}/{documenttype}", status_code=status.HTTP_200_OK)
async def getoverallservbyprovider(u_id:int,documenttype:int,serviceprovider: Optional[str] = None,entity: Optional[int] = None,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getoverallservbyprovider(u_id,documenttype,usertype,serviceprovider,entity,date,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /servpendingbyamount",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/emailexceptions",status_code=status.HTTP_200_OK)
async def getemailexceptions(date: Optional[str] = None,exceptiontype: Optional[str] = None):
    try:
        data = crud.getemailexceptions(date,exceptiontype)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /emailexceptions",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/getinvoicesforvendor/{u_id}", status_code=status.HTTP_200_OK)
async def getinvoicespervendor(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getinvoicesforvendor(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getinvoicesforvendor",str(e))
        return {"message":f"exception {e}","data":[]}


@router.get("/getunderProcessInvforvendor/{u_id}", status_code=status.HTTP_200_OK)
async def getprocessinginvvendor(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getprocessinginvvendor(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getunderProcessInvforvendor",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/getInvoicedforVendor/{u_id}", status_code=status.HTTP_200_OK)
async def getInvoiced(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getInvoiced(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getInvoicedforVendor",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/getAgeingforVendor/{u_id}", status_code=status.HTTP_200_OK)
async def getAgeingforVendor(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getageingforvendor(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getAgeingforVendor",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/getmostOrderedItems/{u_id}", status_code=status.HTTP_200_OK)
async def getmostOrderedItems(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getmostordereditems(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getmostOrderedItems",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/getCollectionsforVendor/{u_id}", status_code=status.HTTP_200_OK)
async def getCollections(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getCollections(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getCollectionsforVendor",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/getRejectedforVendor/{u_id}", status_code=status.HTTP_200_OK)
async def getRejected(u_id:int,date: Optional[str] = None,usertype: int = Depends(dependencies.check_usertype),db: Session = Depends(get_db)):
    try:
        data = crud.getRejected(u_id,date,usertype,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /getRejectedforVendor",str(e))
        return {"message":f"exception {e}","data":[]}

@router.get("/onboardedVendorsByMonth/{uid}",status_code=status.HTTP_200_OK)
async def getonboarded(uid:int,month: Optional[int]=None,db: Session = Depends(get_db)):
    try:
        data = crud.getOnboardedByMonth(uid,month,db)
        return {"message":"success","data":data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV","dashboard.py /onboardedVendorsByMonth",str(e))
        return {"message":f"exception {e}","data":[]}


