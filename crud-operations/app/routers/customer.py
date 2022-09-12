from fastapi import APIRouter, Depends, Body, status, HTTPException, BackgroundTasks
from typing import Optional
from fastapi.responses import Response
from sqlalchemy.orm import scoped_session
import sys

sys.path.append("..")
from schemas import customersm
from crud import customerCrud, permissionCrud
from dependency.dependencies import check_create_user, check_update_user, check_if_cust_user_and_admin
from session import Session
from auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Customer",
    tags=["Customer"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    """
    This function yields a DB session object if the connection is established with the backend DB, takes
    in  no parameter.
    :return: It returns a DB session Object to the calling function.
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()


# Depends(check_create_user)
@router.post("/newCustomer/{u_id}", status_code=status.HTTP_201_CREATED)
async def new_customer_item(u_id: int, bg_task: BackgroundTasks, n_cust: customersm.User = None,
                            n_cred: customersm.Credentials = None,
                            db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for new Customer creation. It contains 4 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param bg_task
    :param n_cust: It is a body parameters that is of Pydantic type, it provides Customer details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    # calling function to create customer user
    data = await customerCrud.new_user(u_id, n_cust, db)
    if type(data) != tuple:
        return data
    n_usr, user_type = data
    # checking if any of the type is not dict to return error status
    # passing id to user and email
    n_cred.userID = n_usr["idUser"]
    email = n_usr.pop("email")
    userdetails = {"idUser": n_usr.pop("idUser"), "firstName": n_usr.pop("firstName"),
                   "lastName": n_usr.pop("lastName")}
    # calling function to create customer credentials
    return await customerCrud.new_user_credentials(u_id, n_cred, email, user_type, userdetails, bg_task, db)
    # checking if any of the type is not dict to return error status


@router.post("/updateCustomer/{u_id}/idUser/{uu_id}")
async def update_customer_item(bg_task: BackgroundTasks, u_id=Depends(check_update_user), uu_id: int = None,
                               u_cust: customersm.UCustomerAndPermissionDetails = None,
                               db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating of existing Customer details. It contains 4 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param uu_id: It is a path parameters that is of integer type, it provides the update user Id.
    :param u_cust: It is a body parameters that is of Pydantic object type, it provides the customer and user details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    # calling customer update function
    # u_cust_name = await customerCrud.update_customer(c_id, u_cust.Customer, db)
    # calling customer user update function
    # resp_sp_cred = customerCrud.update_usr_credentials(uu_id, up_cred, db)
    # resp_sp_cred = customerCrud.update_usr_access(uu_id, up_cred, db)
    return customerCrud.update_user(u_id, bg_task, uu_id, u_cust.User, u_cust.userentityaccess, db)


@router.get("/readEntity_Dept/{u_id}")
async def read_entity_dept_item(u_id: int, en_id: Optional[int] = None, skip: int = 0, limit: Optional[int] = None,
                                db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading entity and its related department details. It contains 5 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param en_id: It is a path parameters that is of integer type which is optional, it provides the entity Id.
    :param skip: It is a path parameters that is of integer type, it provides the offset value.
    :param limit: It is a path parameters that is of integer type, it provides the limit value.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await customerCrud.read_entity_dept(u_id, en_id, skip, limit, db)


@router.put("/updateEntity_Dept/{u_id}")
async def update_entity_dept_item(u_id: int, bg_task: BackgroundTasks, u_ent_dept: customersm.UEntityDept,
                                  db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating entity and its related department details. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param u_ent_dept: It is a body parameters that is of Pydantic type, it provides Entity and Department details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await customerCrud.update_entity_dept(u_id, u_ent_dept, db)


@router.get("/readEntity_Body_Dept/{u_id}")
async def read_entity_body_dept_item(u_id: int, ent_id: Optional[int] = None, skip: int = 0,
                                     limit: Optional[int] = None, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading entity body and its related department details. It contains 5 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param ent_id: It is a path parameters that is of integer type which is optional, it provides the entity body Id.
    :param skip: It is a path parameters that is of integer type, it provides the offset value.
    :param limit: It is a path parameters that is of integer type, it provides the limit value.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await customerCrud.read_entity_body_dept(u_id, ent_id, skip, limit, db)


@router.put("/updateEntity_Body_Dept/{u_id}")
async def update_entity_body_dept_item(u_id: int, bg_task: BackgroundTasks, u_entb_dept: customersm.UEntityBodyDept,
                                       db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating entity body and its related department details. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param u_entb_dept: It is a body parameters that is of Pydantic type, it provides EntityBody and Department details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await customerCrud.update_entity_body_dept(u_id, u_entb_dept, db)


@router.get("/userList/{u_id}")
async def Read_CustomerUser(u_id: int, db: Session = Depends(get_db)):
    """
    This function creates an api route for Reading customer user. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the list of customer users.
    """
    db_user = customerCrud.ReadCustomerUser(db, u_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await db_user


@router.get("/vendorNameList/{u_id}")
async def getVendorname(u_id: str, offset: Optional[int] = 0, limit: Optional[int] = 0,
                        ent_id: Optional[int] = None, ven_name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    This function creates an api route for Reading Vendor names. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a list of Vendor names .
    """
    return await customerCrud.readVendorNames(u_id, ent_id, ven_name,(offset, limit), db)


@router.get("/vendorEntityCodes/{u_id}")
async def getVendorcode(u_id: str, ven_code: str, db: Session = Depends(get_db)):
    """
    This function creates an api route for Reading Vendor names. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a list of Vendor names .
    """
    return await customerCrud.readVendorEntityCodes(u_id, ven_code, db)


@router.get("/userName")
async def getusername(name: str, db: Session = Depends(get_db)):
    """
    This function creates an api route for validating if a username is available or not. It contains 2 parameters.
    :param name: It is a query parameters that is of string type, it provides the user name.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag [None, name].
    """
    return await customerCrud.readUserName(name, db)


@router.post("/newVendorAdminUser/{u_id}", status_code=status.HTTP_201_CREATED)
async def newvendor(u_id: int, bg_task: BackgroundTasks, n_ven_user: customersm.VendorUser = None,
                    n_cred: customersm.Credentials = None,
                    db: Session = Depends(get_db)):
    """
    This function creates an api route for creating a new Vendor admin user. It contains 4 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param n_ven_user: It is a body parameters that is of Pydantic class, it provides the user details.
    :param n_cred: It is a body parameters that is of Pydantic class, it provides the user credential details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag result.
    """
    # calling function to create customer user
    n_usr, user_type = await customerCrud.newVendorAdminUserName(u_id, n_ven_user, 2, db)
    # return await customerCrud.newVendorAdminUserName(user_id, n_ven_user,1, db)
    # checking if any of the type is not dict to return error status
    if type(n_usr) != dict:
        return n_usr
    # passing id to user and email
    n_cred.userID = n_usr["idUser"]
    email = n_usr.pop("email")
    userdetails = {"idUser": n_usr.pop("idUser"), "firstName": n_usr.pop("firstName"),
                   "lastName": n_usr.pop("lastName")}
    # calling function to create customer credentials
    return await customerCrud.new_user_credentials(u_id, n_cred, email, user_type, userdetails, bg_task, db)


@router.get("/vendorUserlist/{u_id}")
async def read_vendor_user(u_id: int, db: Session = Depends(get_db)):
    """
    This function creates an api route for Reading vendor users. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the vendor user list.
    """
    return await customerCrud.read_vendor_user(db, u_id)


@router.get("/changeUserAccountStatus/{u_id}")
async def deactivate_user_account(u_id: int, bg_task: BackgroundTasks, deactivate_uid: int,
                                  db: Session = Depends(get_db)):
    """
    This function creates an api route for changing the active status of a user account. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param deactivate_uid: It is a query parameters that is of integer type, it provides the user Id which has to be de
    activated or vise versa.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag result.
    """
    return await customerCrud.deactivate_user_account(db, bg_task, u_id, deactivate_uid)


@router.post("/updateVendorUser/{u_id}/idUser/{uu_id}")
async def update_customer_item(bg_task: BackgroundTasks, u_id=Depends(check_update_user), uu_id: int = None,
                               u_cust: customersm.UVendorUserAndPermissionDetails = None,
                               db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating the existing vendor user details. It contains 4 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param uu_id: It is a path parameters that is of integer type, it provides the update user Id.
    :param u_cust: It is a body parameters that is of Pydantic object type, it provides the customer and user details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    # calling customer update function
    # u_cust_name = await customerCrud.update_customer(c_id, u_cust.Customer, db)
    # calling customer user update function
    # resp_sp_cred = customerCrud.update_usr_credentials(uu_id, up_cred, db)
    # resp_sp_cred = customerCrud.update_usr_access(uu_id, up_cred, db)
    return customerCrud.update_vendor_user(u_id, uu_id, u_cust.User, u_cust.uservendoraccess, bg_task, db)


@router.post("/switchRoleBased/{u_id}", dependencies=[Depends(check_if_cust_user_and_admin)])
async def update_customer_item(u_id: int, bg_task: BackgroundTasks, isenabled: bool,
                               db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating the GenSettings. It contains 4 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param isenabled: It is a path parameters that is of boolean type, it provides the status.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await customerCrud.update_rolebased_gen_config(u_id, isenabled, db)


@router.get("/readGenSettings/{u_id}", dependencies=[Depends(check_if_cust_user_and_admin)])
async def read_gen_setting_item(u_id: int, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading the gen settings.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param isenabled: It is a path parameters that is of boolean type, it provides the status.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result status.
    """
    return await customerCrud.read_gen_setting(u_id, db)


@router.get("/vendorAccount/{u_id}/idVendor/{v_id}")
async def read_vendoraccount(u_id: int, v_id: int, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a customer user.
    """
    return await customerCrud.readvendoraccount(u_id, v_id, db)


@router.post("/PortalPasswordUpdate/{u_id}")
async def update_pass(u_id: int, new_pass: customersm.UPassword, db: Session = Depends(get_db)):
    """
    ###This function creates an api route for Reading Vendor accounts. It contains 2 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param new_pass: It is a path parameters that is of integer type, it provides the vendor user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns vendor account for a customer user.
    """
    return await customerCrud.update_portal_pass(u_id, new_pass, db)
