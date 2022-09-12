from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request, BackgroundTasks
from sqlalchemy.orm import Session, session
from typing import Optional
import sys

sys.path.append("..")
from crud import VendorCrud as crud
from crud import customerCrud
from dependency.dependencies import check_create_user, check_update_vendor_user
from dependency import dependencies
from crud import permissionCrud as per_crud
from schemas import VendorSchema as schema
from schemas import customersm
from schemas import permissionssm
import model
from session import Session as SessionLocal
from session import engine
from auth import AuthHandler

model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Vendor",
    tags=["Vendor"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/updateVendor/{vu_id}/idVendor/{v_id}", status_code=status.HTTP_200_OK)
async def update_vendor_erp(vu_id: int, bg_task: BackgroundTasks, v_id: int,
                            UpdateVendor: schema.UpdateVendor, db: Session = Depends(get_db)):
    """
    This function creates an api route to update Vendor. It contains 4 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param v_id: It is a path parameters that is of integer type, it provides the vendor Id.
    :param UpdateVendor: It is Body parameter that is of a Pydantic class object, It takes member data for updating of Vendor.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag result.
    """
    return await crud.UpdateVendorERP(vu_id, v_id, UpdateVendor, db)


@router.put("/updateVendorAccount/{vu_id}/idVendorAccount/{va_id}", status_code=status.HTTP_200_OK)
async def update_vendor_account_erp(vu_id: int, bg_task: BackgroundTasks, va_id: int,
                                    UpdateVendorAcc: schema.UpdateVendorAccount,
                                    db: Session = Depends(get_db)):
    """
    This function creates an api route to update Vendor Account. It contains 4 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param va_id: It is a path parameters that is of integer type, it provides the vendor account Id.
    :param UpdateVendorAcc: It is Body parameter that is of a Pydantic class object, It takes member data for updating of Vendor account.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag result.
    """
    return await crud.UpdateVendorAccERP(vu_id, va_id, UpdateVendorAcc, db)


@router.post("/newVendor/{vu_id}", status_code=status.HTTP_201_CREATED)
async def create_new_vendor_nonerp(request: Request, vu_id: int, db: Session = Depends(get_db)):
    """
    This function creates an api route to create a new Vendor. It contains 3 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param NewVendor: It is Body parameter that is of a Pydantic class object, It takes member data for creating a new vendor.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the newly created record.
    """
    NewVendor = await request.json()
    return await crud.NewVendor(vu_id, NewVendor, db)


@router.post("/newVendorAccount/{vu_id}/idVendor/{v_id}", status_code=status.HTTP_201_CREATED)
async def create_new_vendoracc_nonerp(request: Request, vu_id: int, v_id: int,
                                      db: Session = Depends(get_db)):
    """
    This function creates an api route to create a new Vendor Account. It contains 4 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param v_id: It is a path parameters that is of integer type, it provides the vendor Id.
    :param NewVendorAcc: It is Body parameter that is of a Pydantic class object, It takes member data for creating a new vendor account.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the newly created record.
    """
    NewVendorAcc = await request.json()
    return await crud.NewVendorAcc(vu_id, v_id, NewVendorAcc, db)


@router.post("/newVendorUser/{vu_id}", status_code=status.HTTP_201_CREATED)
async def create_new_vendoruser_nonerp(vu_id: int, bg_task: BackgroundTasks, n_ven_user: customersm.VendorUser = None,
                                       n_cred: customersm.Credentials = None, db: Session = Depends(get_db)):
    """
    This function creates an api route to create a new Vendor user. It contains 4 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param VendorID: It is a path parameters that is of integer type, it provides the vendor Id.
    :param NewVendorUser: It is Body parameter that is of a Pydantic class object, It takes member data for creating a new vendor user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the newly created record.
    """
    # calling function to create customer user
    n_usr, user_type = await crud.NewVendorUser(vu_id, n_ven_user, 2, db)
    # checking if any of the type is not dict to return error status
    if type(n_usr) != dict:
        return n_usr
    # passing id to user and email
    n_cred.userID = n_usr["idUser"]
    email = n_usr.pop("email")
    userdetails = {"idUser": n_usr.pop("idUser"), "firstName": n_usr.pop("firstName"),
                   "lastName": n_usr.pop("lastName")}
    # calling function to create customer credentials
    return await customerCrud.new_user_credentials(vu_id, n_cred, email, user_type, userdetails, bg_task, db)


@router.put("/updateVendorUser/{vu_id}/idUser/{uu_id}", status_code=status.HTTP_200_OK)
async def update_vendoruser_nonerp(bg_task: BackgroundTasks, vu_id=Depends(check_update_vendor_user), uu_id: int = None,
                                   u_cust: customersm.UVendorUserAndPermissionDetails = None,
                                   db: Session = Depends(get_db)):
    """
    This function creates an api route to update an exisiting Vendor details. It contains 4 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param uu_id: It is a path parameters that is of integer type, it provides the vendor Id that needs to be updated.
    :param u_cust: It is Body parameter that is of a Pydantic class object, It takes member data for updating vendor user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag result.
    """
    return customerCrud.update_vendor_user(vu_id, uu_id, u_cust.User, u_cust.uservendoraccess, db)


@router.get("/changeAccountStatus/{vu_id}")
async def deactivate_user_account(vu_id: int, bg_task: BackgroundTasks, deactivate_uid: int,
                                  db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading customer user. It contains 3 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param deactivate_uid: It is a query parameters that is of integer type, it provides the vendor user Id, for which
    account status has to be changed.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag result.
    """
    return await customerCrud.deactivate_user_account(db, vu_id, deactivate_uid)


@router.get("/readVendorDetails/{vu_id}")
async def read_vendor_user(vu_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor details. It contains 2 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor details associated with the vendor user
    """
    return await crud.read_vendor_details(db, vu_id)


# API to read all vendor list
@router.get("/vendorlist")
async def read_vendor(db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor list. It contains 2 parameters.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: it returns vendor list
    """
    return await crud.readvendor(db)


# API to read all vendor list
@router.get("/vendorlist/{u_id}")
async def read_vendor(u_id: int, ent_id: Optional[int] = None, ven_code: Optional[str] = None,
                      onb_status: Optional[str] = None, offset: int = 1, limit: int = 10,
                      vendor_type: Optional[str] = None, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor list. It contains 2 parameters.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: it returns vendor list
    """
    return await crud.readvendorbyuid(u_id, vendor_type, db, (offset, limit),
                                      {"ent_id": ent_id, "ven_code": ven_code, "onb_status": onb_status})


@router.get("/check_onboarded/{u_id}")
async def check_onboard(u_id: int, db: Session = Depends(get_db)):
    """
    This API will check if the vendor is onboarded or not for each entity. Parameter passed is vendor code
    """
    return await crud.checkonboarded(u_id, db)


# API to read all vendor list
@router.get("/vendorAccountPermissionList/{u_id}")
async def read_vendor_account_permission(u_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor list. It contains 2 parameters.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: it returns vendor list
    """
    return await crud.read_vendor_account_permission(u_id, db)


# API to read particulaar vendor details using unique id
@router.get("/vendordetails/{v_id}")
async def read_vendordetails(v_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor list. It contains 2 parameters.
    :param v_id: It provides a session to interact with the backend Database,that is of Session Object Type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: it returns vendor list
    """
    return await crud.readvendorbyid(db, v_id=v_id)


# API to read all vendor user list
@router.get("/vendorUserList/{vu_id}")
async def read_vendoruser(vu_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor user list. It contains 2 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns non admin vendor user list
    """
    return await crud.read_vendor_user(db, vu_id)


# API to read all vendor account
@router.get("/vendorAccount/{vu_id}")
async def read_vendoraccount(vu_id: int, ent_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a vendor user.
    """
    return await crud.readvendoraccount(vu_id, ent_id, db)


@router.get("/vendorAccountpo/{vu_id}")
async def read_vendoraccount_uploadpo(vu_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a vendor user.
    """
    return await crud.readvendoraccount_uploadpo(db, vu_id)


# To read vendor Sites
@router.get("/vendorSite/{u_id}/idVendor/{v_id}")
async def read_vendorsites(u_id: int, v_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the  user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a vendor user.
    """
    return await crud.readvendorsites(db, u_id, v_id)


# API to read all vendor account
@router.get("/submitVendorInvoice/{vu_id}")
async def submit_invoice_vendor(vu_id: int, re_upload: bool, bg_task: BackgroundTasks, inv_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param vu_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a vendor user.
    """
    return await crud.submit_invoice_vendor(vu_id, inv_id, re_upload, bg_task, db)


# To read unique Vendor Names along with their codes
@router.get("/vendorNameCode/{u_id}")
async def read_vendor_name_codes(u_id: int, offset: int = 0, limit: int = 0, ven_name: str = None,
                                 db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the  user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a vendor user.
    """
    return await crud.read_vendor_name_codes(db, u_id, (offset, limit), ven_name)
