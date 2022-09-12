from fastapi import APIRouter, Depends, Body, status,BackgroundTasks
from sqlalchemy.orm import scoped_session
# from database import SessionLocal, engine
from typing import Optional
from pydantic import BaseModel
import sys
sys.path.append("..")
from schemas import permissionssm
from crud import permissionCrud
from session import Session
from dependency import dependencies
from auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Permission",
    tags=["Permission"],
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


@router.post("/newAmountApproval/{u_id}", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(dependencies.check_if_user_amount_approval)])
async def new_amount_approval_item(u_id: int, maxamount: permissionssm.Maxamount, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for new amount approval. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param maxamount: It is a body parameters that is of integer type, it provides the maximum amount a user can approve.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.new_amount_approval(u_id, maxamount, db)


@router.post("/newAccessPermissionUser/{u_id}", status_code=status.HTTP_201_CREATED)
async def new_access_permission_item(u_id: int, bg_task: BackgroundTasks,n_ap: permissionssm.AccessPermissionDef,
                                     db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for new access permission for customer user. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param n_ap: It is a body parameters that is of Pydantic type, it provides new AccessPermission information.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.new_access_permission(u_id, n_ap, bg_task, db, "user")


@router.post("/newAccessPermissionVendor/{u_id}", status_code=status.HTTP_201_CREATED)
async def new_access_permission_item(u_id: int, n_ap: permissionssm.AccessPermissionDef,
                                     db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for new access permission Vendor user. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param n_ap: It is a body parameters that is of Pydantic type, it provides new AccessPermission information.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.new_access_permission(u_id, n_ap, db, "vendor")


@router.post("/applyAccessPermission/{u_id}", status_code=status.HTTP_202_ACCEPTED)
async def apply_access_permission_item(u_id: int, bg_task: BackgroundTasks, a_ap: permissionssm.ApplyPermission,
                                       db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for applying new access permission. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param a_ap: It is a body parameters that is of Pydantic type, it provides AccessPermission information.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.apply_access_permission(u_id, a_ap, bg_task, db)


@router.get("/readPermissionRolesUser/{u_id}")
async def read_roles_permission_items(u_id: int, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading roles of user. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.read_roles_permission(u_id, db, "user")


@router.get("/readPermissionRolesVendor/{u_id}")
async def read_roles_permission_items(u_id: int, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading roles of vendor. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.read_roles_permission(u_id, db, "vendor")


@router.get("/readPermissionRoleInfo/{u_id}/accessPermissionDefID/{apd_id}")
async def read_roles_permission_info_items(u_id: int, apd_id: int, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading permission info. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param apd_id: It is a path parameters that is of integer type, it provides the access permission Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.read_roles_permission_info(u_id, apd_id, db)


@router.put("/updateAccessPermission/{u_id}/idAccessPermission/{apd_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_access_permission_item(u_id: int, bg_task: BackgroundTasks,apd_id: int, u_apd: permissionssm.UAccessPermissionDef,
                                        db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating access permission. It contains 4 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param apd_id: It is a path parameters that is of integer type, it provides the access permission Id.
    :param u_apd: It is a body parameters that is of Pydantic type, it provides AccessPermission information.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.update_access_permission(u_id, apd_id, u_apd, bg_task, db)


@router.get("/readUserAccess/{u_id}")
async def read_user_access_item(u_id: int, ua_id: int, skip: int = 0, limit: Optional[int] = None,
                                db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading customer user access. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param ua_id: It is a query optional parameters that is of integer type, it provides the invoice access Id which is optional.
    :param skip: It is a path parameters that is of integer type, it provides the offset value.
    :param limit: It is a path parameters that is of integer type, it provides the limit value.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.read_user_access(u_id, ua_id, skip, limit, db)


@router.get("/financiallapproval/{u_id}/idInvoice/{inv_id}",
            dependencies=[Depends(dependencies.check_finance_approve)])
async def financial_approval_item(u_id: int, bg_task: BackgroundTasks,inv_id: int,
                                  db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for invoice amount approval. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param inv_id: It is path parameter that is of integer type. it provides the invoice id that has to be approved.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.financial_approval_level(u_id, inv_id, bg_task, db)


@router.get("/deletePermissionRole/{u_id}/accessPermissionDefID/{apd_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_role_permission_item(u_id: int, bg_task: BackgroundTasks,apd_id: int, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for deleting the roles. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param apd_id: It is a path parameters that is of integer type, it provides the access permission Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.delete_role_permission(u_id, apd_id, bg_task, db)


@router.post("/updateServiceSchedule/{u_id}", status_code=status.HTTP_202_ACCEPTED,
             dependencies=[Depends(dependencies.check_if_cust_user_and_admin)])
async def update_service_schedule_item(u_id: int, bg_task: BackgroundTasks,schedule_update: permissionssm.UpdateServiceSchedule,
                                       db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for updating service schedule. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.update_service_schedule(u_id, schedule_update, bg_task, db)


@router.get("/readServiceSchedule/{u_id}", status_code=status.HTTP_202_ACCEPTED,
             dependencies=[Depends(dependencies.check_if_cust_user_and_admin)])
async def read_service_schedule_item(u_id: int, db: scoped_session = Depends(get_db)):
    """
    This function creates an api route for reading service schedule. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    return await permissionCrud.read_service_schedule(u_id, db)
