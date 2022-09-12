from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, BackgroundTasks
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import File, UploadFile
from typing import List
import sys
from Utilities import operationalunits

sys.path.append("..")
from crud import ServiceProviderCrud as crud
from schemas import ServiceProviderSchema as schemas
import model
from dependency import dependencies
from session import Session as SessionLocal
from session import engine
from auth import AuthHandler

model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/ServiceProvider",
    tags=["ServiceProvider"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


## Non PO Service Provider

@router.post("/newServiceProvider/{u_id}", status_code=status.HTTP_201_CREATED)
async def new_service_provider(u_id: int, bg_task: BackgroundTasks, n_ser: schemas.ServiceProvider,
                               db: Session = Depends(get_db)):
    """
    ###This function creates an api route for new service provider. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param n_ser: It is Body parameter that is of a Pydantic class object, It takes member data for creation of new Service provider.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await crud.new_service(u_id, n_ser, db)


@router.post("/newSPAccount/{u_id}/serviceId/{s_id}", status_code=status.HTTP_201_CREATED)
def new_service_provider_account(u_id: int, bg_task: BackgroundTasks, s_id: int, n_sp_acc: schemas.ServiceAccount,
                                 n_sp_sched: schemas.ServiceProviderSchedule,
                                 n_cred: schemas.Credentials,
                                 n_sp_cst: Optional[List[schemas.AccountCostAllocation]] = None,
                                 db: Session = Depends(get_db)):
    """
    ###API to create a new service provider account, the API executes 3 crud operation
    1. Creates a new service account
    2. Creates a new service schedule
    3. creates a new cost allocation
    4. Create a credentials
    """
    resp_sp_acc = crud.new_service_account(u_id, s_id, n_sp_acc, db)
    if type(resp_sp_acc) != dict:
        # return error msg
        return resp_sp_acc
    resp_sp_sched = crud.new_service_schedule(u_id, resp_sp_acc["idServiceAccount"], n_sp_sched, db)
    if type(resp_sp_sched) != dict:
        return resp_sp_sched
    if n_sp_cst is not None and len(n_sp_cst) > 0:
        resp_sp_cst_alloc = crud.new_account_cost_allocation(u_id, resp_sp_acc["idServiceAccount"], n_sp_cst, db)
        if type(resp_sp_cst_alloc) != dict:
            return resp_sp_cst_alloc
    resp_sp_cred = crud.new_account_credentials(u_id, resp_sp_acc["idServiceAccount"], n_cred, db)
    if type(resp_sp_cred) != dict:
        return resp_sp_cred
    return {"Result": "Created"}


@router.post("/updateServiceProvider/{s_id}", status_code=status.HTTP_200_OK)
def update_service_provider(s_id: int, bg_task: BackgroundTasks, u_ser: schemas.ServiceProvider,
                            db: Session = Depends(get_db)):
    """
    ###API to update the data of an existing Service Provider, inputs service provider, name, city, location
    :param s_id:
    :param u_ser:
    :param db:
    :return:
    """
    return crud.update_sp(s_id, u_ser, db)


@router.post("/updateSPAccount/{u_id}/idServiceAccount/{sa_id}", status_code=status.HTTP_200_OK)
def update_sp_account(u_id: int, bg_task: BackgroundTasks, sa_id: int, u_sp_acc: schemas.ServiceAccount,
                      u_sp_sch: schemas.ServiceProviderSchedule, u_cred: schemas.Credentials,
                      u_sp_cst_aloc: Optional[List[schemas.UAccountCostAllocation]] = None,
                      db: Session = Depends(get_db)):
    """
    API route to update a service provider account
    """
    resp_sp_account = crud.update_sp_account(u_id, sa_id, u_sp_acc, db)
    if type(resp_sp_account) != dict:
        return resp_sp_account
    resp_sp_sch = crud.update_supply_schedule(u_id, sa_id, u_sp_sch, db)
    if type(resp_sp_sch) != dict:
        return resp_sp_sch
    if u_sp_cst_aloc is not None and len(u_sp_cst_aloc) > 0:
        resp_sp_acc_aloc = crud.update_account_cost_allocation(u_id, sa_id, u_sp_cst_aloc, db)
        if type(resp_sp_acc_aloc) != dict:
            return resp_sp_acc_aloc
    resp_sp_cred = crud.update_credentials(u_id, sa_id, u_cred, db)
    if type(resp_sp_cred) != dict:
        resp_sp_cred
    return {"Result": "Updated"}


# Displaying service providers list
@router.get("/serviceproviderlist/{u_id}", status_code=status.HTTP_200_OK)
async def read_serviceprovider(u_id: int, db: Session = Depends(get_db)):
    return await crud.readserviceprovider(u_id, db)

@router.get("/serviceproviderlist1/{u_id}", status_code=status.HTTP_200_OK)
async def read_sp(u_id: int,ent_id: Optional[int] = None, ven_code: Optional[str] = None,
                      onb_status: Optional[str] = None, offset: int = 1, limit: int = 10,
                      sp_type: Optional[str] = None, db: Session = Depends(get_db)):
    return await crud.readspbyuid(u_id,sp_type, db,(offset, limit),
                                      {"ent_id": ent_id, "ven_code": ven_code, "onb_status": onb_status})


# Displaying service provider all details
@router.get("/serviceprovider/{sp_id}")
async def read_serviceproviderbyid(sp_id: int, db: Session = Depends(get_db)):
    db_user = crud.readserviceproviderbyid(db, sp_id=sp_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await db_user


# {u_id}/idServiceProvider/
# Displaying service provider account details
@router.get("/serviceprovideraccount/{u_id}/idService/{sp_id}")
async def read_serviceprovideraccount(u_id: int, sp_id: int, db: Session = Depends(get_db)):
    return await crud.readserviceprovideraccount(u_id, sp_id, db)


@router.post("/triggerServiceBatch/{u_id}", status_code=status.HTTP_202_ACCEPTED,
             dependencies=[Depends(dependencies.check_if_service_trigger)])
async def trigger_service_batch(u_id: int, tbody: schemas.TriggerBody, bg_task: BackgroundTasks,
                                db: Session = Depends(get_db)):
    """
    This function creates an api route for triggering service schedule. It contains 2 parameters.
    :param u_id:
    :param db:
    :return:
    """
    return await crud.trigger_service_batch(u_id, tbody, bg_task, db)


# Displaying BatchProcessDetails for Service Provider
@router.get("/ServiceBatchHistory/{u_id}")
async def read_sbatch_history(u_id: int, db: Session = Depends(get_db)):
    return await crud.read_sbatch_history(u_id, db)


# Upload Cost allocation file for users single entity
@router.post("/ServiceCostAllocationFileUpload/{u_id}")
async def upload_cost_allocation_file(u_id: int, file: UploadFile = File(...),
                                      db: Session = Depends(get_db)):
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(400, detail="Invalid document type")
    return await crud.upload_cost_allocation(u_id, file, db)


# Download Cost allocation file for users single entity
@router.get("/ServiceCostAllocationFileDownload/{u_id}/fileName/{filename}")
async def download_cost_allocation_file(u_id: int, filename: str, bg_task: BackgroundTasks,
                                        db: Session = Depends(get_db)):
    return await crud.download_cost_allocation(u_id, filename, bg_task, db)


# readCost allocation files for users single entity
@router.get("/ServiceCostAllocationFileHistory/{u_id}")
async def read_cost_allocation_file(u_id: int,
                                    db: Session = Depends(get_db)):
    return await crud.read_cost_allocation(u_id, db)

@router.get("/getoperationalUnits")
def read_opunits():
    return operationalunits.getopunits()

@router.post("/addOperationalUnit")
def add_opunit(unit:str):
    return operationalunits.addunit(unit)
