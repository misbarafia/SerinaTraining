from fastapi.applications import FastAPI
from fastapi.responses import Response
from sqlalchemy.sql import func
from sqlalchemy import exc
import json
import pytz as tz
from datetime import datetime
from sqlalchemy.orm import join, load_only, Load
from fastapi import status, HTTPException
import traceback
import sys
import os

sys.path.append("..")
from auth import AuthHandler
import model as models
from session.notificationsession import client as mqtt

endpoint_site = os.getenv('Endpoint_Site', default="https://rovedev.serinaplus.com/")
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


# creating function to push data in customer table.
async def new_customer(n_customer, db):
    """
    This function creates a new Customer in the db. It contains 2 parameters.
    :param n_customer: It is a function parameters that is of Pydantic type, it provides Customer details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # permission check function has to be created and checked
        n_cust = models.Customer(CustomerName=n_customer.CustomerName,
                                 CreatedOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
        db.add(n_cust)
        # notifying changes to the db but not committing since next stage it will be committed
        db.flush()
        # returning the customer details with custom function from models to avoid all columns
        return n_cust.datadict()
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error"})


# creating function to push data in user table.
async def new_user(u_id, n_usr, db):
    """
    This function creates a new User in the db. It contains 3 parameters.
    :param u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param n_usr: It is a function parameters that is of Pydantic type, it provides User details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # permission check function has to be created and checked
        createdon = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # pop the user access
        n_usr = n_usr.dict()
        n_usr["isCustomerUser"] = 1
        user_access = n_usr.pop("userentityaccess")
        role_id = n_usr.pop("role_id")
        n_usr["created_by"] = u_id
        # get company id
        c_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        n_usr = models.User(**n_usr, customerID=c_id, CreatedOn=createdon)
        db.add(n_usr)
        db.flush()
        # common info
        basedata = {"UserID": n_usr.idUser,
                    "CreatedBy": u_id,
                    "CreatedOn": createdon,
                    "UpdatedOn": createdon}
        # saving the access permission
        user_access = [models.UserAccess(**row, **basedata) for row in user_access]
        db.add_all(user_access)
        # notifying changes to the db but not committing since next stage it will be committed
        db.flush()
        db.add(models.AccessPermission(permissionDefID=role_id, userID=n_usr.idUser, CreatedOn=createdon))
        db.flush()
        # returning the customer details with custom function from models to avoid all columns

        return n_usr.datadict(), 1
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(traceback.print_exc())
        db.rollback()
        return Response(status_code=500, headers={"Error": f"Server error"})


async def new_user_credentials(u_id, n_acc_cred, email, user_type, userdetails, bg_task, db):
    """
    This function creates a new Account Cost Allocation. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param n_acc_cred: It is function parameter that is of a Pydantic class object, It takes member data for creation of new credentials.
    :param email: It is function parameter that is of a string type, provides email id of new user.
    :param user_type: It is function parameter that is of a integer type, provides the type of user.
    :param userdetails: It is function parameter that is of a dict type, provides the newly created user details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        n_acc_cred = dict(n_acc_cred)
        auth_handler = AuthHandler()
        n_acc_cred["LogSecret"] = auth_handler.get_password_hash(n_acc_cred["LogSecret"])
        n_acc_cred["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        n_acc_cred["crentialTypeId"] = user_type
        # supplying dict as a keyword args to the AccountCostAllocation Model
        db_model = models.Credentials(**n_acc_cred)
        db.add(db_model)
        userdetails["username"] = n_acc_cred["LogName"]
        # commit the newly created user
        db.commit()
        # prepare notification
        try:
            ############ start of notification trigger #############
            cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
            details = {"user_id": [u_id], "trigger_code": 8011, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {
                           "recipients": [(email, userdetails["firstName"], userdetails["lastName"])],
                           "subject": "verification mail",
                           "endpoint_url": f"{endpoint_site}/#/registration-page/activationLink/",
                           "user_details": userdetails}}
            bg_task.add_task(meta_data_publisher, details)
        except Exception as e:
            print("notification exception", e)
        ############ End of notification trigger #############
        return {"result": "success"}
    except Exception as e:
        print(traceback.print_exc())
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{traceback.format_exc()}Server error"})
    finally:
        db.close()


async def update_customer(c_id, u_cust, db):
    """
    This function updates a existing Customer in the db. It contains 3 parameters.
    :param c_id: It is a function parameters that is of integer type, it provides the customer Id.
    :param u_cust: It is a function parameters that is of Pydantic type, it provides Customer details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # permission check function has to be created and checked
        # result provides an integer value 0 or 1 depending on if the updating was successful
        result = db.query(models.Customer).filter(models.Customer.idCustomer == c_id).update(u_cust.dict())
        # notifying changes to the db but not committing since next stage it will be committed
        db.flush()
        return result
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error"})


def update_user(u_id, bg_task, uu_id, u_user, u_useraccess, db):
    """
    This function updates a existing User in the db. It contains 3 parameters.
    :param uu_id: It is a function parameters that is of integer type, it provides the update user Id.
    :param u_user: It is a function parameters that is of Pydantic type, it provides User details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    print("just checking")
    try:
        # permission check function has to be created and checked
        # getting the user id from customer id in the User table
        ############ start of notification trigger #############
        cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        user_id = db.query(models.User.idUser).filter_by(idUser=uu_id).scalar()
        # checking if the user id is present
        if user_id:
            # result provides an integer value 0 or 1 depending on if the updating was successful
            if u_user:
                u_user = {k: v for k, v in u_user.dict().items() if v}
                db.query(models.User).filter_by(idUser=user_id).update(u_user)
            # updating user access if any enity , entity body access was provided along with department
            if u_useraccess:
                entity_names = {"deleted entities": [], "new entities": []}
                for access in u_useraccess:
                    # if access id for the user is provided , then mark it for delete
                    if access.idUserAccess:
                        entity_name = db.query(models.Entity.EntityName).filter_by(idEntity=access.EntityID).scalar()
                        entity_names["deleted entities"].append(entity_name)
                        db.query(models.UserAccess).filter_by(UserID=uu_id, idUserAccess=access.idUserAccess).update(
                            {"isActive": 0})
                    else:
                        # else check if the row with the values are present already and update it as active
                        del access.idUserAccess
                        result = db.query(models.UserAccess.idUserAccess).filter_by(UserID=uu_id,
                                                                                    **dict(access)).scalar()
                        # return result
                        if result:
                            entity_name = db.query(models.Entity.EntityName).filter_by(
                                idEntity=access.EntityID).scalar()
                            entity_names["new entities"].append(entity_name)
                            db.query(models.UserAccess).filter_by(UserID=uu_id, **dict(access)).update({"isActive": 1})
                        # check if the update was success else no record is present , create a new record
                        else:
                            entity_name = db.query(models.Entity.EntityName).filter_by(
                                idEntity=access.EntityID).scalar()
                            entity_names["new entities"].append(entity_name)
                            access = access.dict()
                            access["UserID"] = uu_id
                            access["CreatedBy"] = u_id
                            access["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                            access["UpdatedOn"] = access["CreatedOn"]
                            access = models.UserAccess(**access)
                            db.add(access)
                entity_names = str(entity_names)
                try:
                    details = {"user_id": None, "trigger_code": 8007, "cust_id": cust_id, "inv_id": None,
                               "additional_details": {
                                   "recipients": [(u_user["email"], u_user["firstName"], u_user["lastName"])],
                                   "subject": "User Access Update",
                                   "entity_list": entity_names[1:len(entity_names) - 1]}}
                    # bg_task.add_task(meta_data_publisher, details)
                except Exception as e:
                    print("notification exception", e)
            db.commit()
            try:
                details = {"user_id": None, "trigger_code": 8006, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {
                               "recipients": [(u_user["email"], u_user["firstName"], u_user["lastName"])],
                               "subject": "User Details Update"}}
                # bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
            return {"result": "Updated"}
        else:
            db.rollback()
            return Response(status_code=400, headers={"ClientError": "User id not active"})
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400,
                        headers={"ClientError": f"{str(traceback.format_exc())}one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{str(traceback.format_exc())} Server error"})


def update_usr_credentials(uu_id, u_acc_cred, db):
    """
    This function updates the Account Cost Allocation of a given id. It contains 4 parameters.
    :param uu_id: It is a function parameters that is of integer type, it provides the user Id which has to be updated.
    :param u_acc_cred: It is function parameter that is of a Pydantic class object, It takes member data for updating of new AccountCostAllocation.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # have to check if it corresponds to the user id and ca_id
        auth_handler = AuthHandler()
        # creating a new hashed password to update old password
        u_acc_cred["LogSecret"] = auth_handler.get_password_hash(u_acc_cred["LogSecret"])
        db.query(models.Credentials).filter(
            models.Credentials.userID == uu_id).update(u_acc_cred)
        db.commit()
        return u_acc_cred
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid ID passed"})
    finally:
        db.close()


async def read_entity_dept(u_id, en_id, skip, limit, db):
    """
    This function creates is for reading entity and its related department details. It contains 5 parameters.
    :param u_id: u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param en_id: It is a path parameters that is of integer type which is optional, it provides the entity Id.
    :param skip: It is a path parameters that is of integer type, it provides the offset value.
    :param limit: It is a path parameters that is of integer type, it provides the limit value.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # permission check function has to be created and checked
        # display entity only from access permission provided
        ent_id = db.query(models.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1)
        # selecting only required columns in query
        query = db.query(models.Entity).options(
            load_only("idEntity", "customerID", "EntityName", "sourceSystemType", "EntityAddress", "City", "Country",
                      "entityTypeID",
                      "EntityCode"))
        # checking if entity id was provided
        if en_id:
            ent_result = query.filter(models.Entity.idEntity.in_(ent_id.filter_by(EntityID=en_id).distinct())).one()
            # loading department result for the entity
            dpt_result = db.query(models.Department).options(
                load_only("idDepartment", "entityBodyID", "DepartmentName")).filter_by(
                entityID=ent_result.idEntity).all()
            # storing the department to entity department variable
            ent_result.department = dpt_result
            return ent_result
        else:
            is_super_admin = db.query(models.User.created_by).filter_by(idUser=u_id).scalar()
            if is_super_admin is not None:
                # selecting entity based on offset and limit
                ent_result = query.filter(models.Entity.idEntity.in_(ent_id.distinct())).offset(skip).limit(limit).all()
            else:
                ent_result = query.limit(limit).all()
            # looping through results
            for row in ent_result:
                dpt_result = db.query(models.Department).options(
                    load_only("idDepartment", "entityID", "entityBodyID", "DepartmentName")).filter_by(
                    entityID=row.idEntity).all()
                # storing the department to entity department variable
                row.department = dpt_result
            return ent_result
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error"})


async def update_entity_dept(u_id, u_ent_dept, db):
    """
    This function is for updating entity and its related department details. It contains 3 parameters.
    :param u_id: u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param u_ent_dept: It is a function parameters that is of Pydantic type, it provides Entity and department details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # dept_id = db.query(models.Department.idDepartment).filter_by(
        #     idDepartment=u_ent_dept.Department.idDepartment).scalar()
        # permission check function has to be created and checked
        # variable with value of 0 to store result of the update status
        r_dpt, r_ent = 0, 0
        # checking if department details is present
        if u_ent_dept.Department:
            u_dpt = dict(u_ent_dept.Department)
            # using copy to avoid dict error
            for item_key in u_dpt.copy():
                # pop out elements that are not having any value
                if not u_dpt[item_key]:
                    u_dpt.pop(item_key)
            # performing update
            r_dpt = db.query(models.Department).filter_by(idDepartment=u_dpt["idDepartment"]).update(
                u_dpt)
            # notifying changes to the db but not committing since next stage it will be committed
            db.flush()
        if u_ent_dept.Entity:
            u_ent = dict(u_ent_dept.Entity)
            for item_key in u_ent.copy():
                # pop out elements that are not having any value
                if not u_ent[item_key]:
                    u_ent.pop(item_key)
            r_ent = db.query(models.Entity).filter_by(idEntity=u_ent["idEntity"]).update(
                u_ent)
            # notifying changes to the db but not committing since next stage it will be committed
            db.flush()
        if u_ent_dept.Department or u_ent_dept.Entity:
            if r_dpt or r_ent == 1:
                # performing commit if both are updated
                db.commit()
                return {"result": "Updated"}
            else:
                db.rollback()
                return Response(status_code=400, headers={"ClientError": "Updated Failed"})
        return Response(status_code=422, headers={"ClientError": "Body Improper"})
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error"})


async def read_entity_body_dept(u_id, enb_id, skip, limit, db):
    """
    This function is for reading entity body and its related department details. It contains 5 parameters.
    :param u_id: u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param enb_id: It is a path parameters that is of integer type which is optional, it provides the entity body Id.
    :param skip: It is a path parameters that is of integer type, it provides the offset value.
    :param limit: It is a path parameters that is of integer type, it provides the limit value.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # permission check function has to be created and checked
        # selecting only required columns in query
        query = db.query(models.EntityBody).options(
            load_only("idEntityBody", "EntityBodyName", "EntityCode", "Address", "LocationCode", "City", "Country",
                      "EntityID", "entityBodyTypeID"))
        # checking if entity body id was provided
        if enb_id:
            # selecting by entity body id
            entb_result = db.query(models.EntityBody).filter(models.EntityBody.EntityID == enb_id).all()
            # fetching department and entity body details
            for row in entb_result:
                dpt_result = db.query(models.Department).options(
                    load_only("idDepartment", "entityBodyID", "DepartmentName")).filter_by(
                    entityBodyID=row.idEntityBody).all()
                row.department = dpt_result
            return entb_result
        else:
            # fetching all department and entity body details
            entb_result = query.offset(skip).limit(limit).all()
            for row in entb_result:
                dpt_result = db.query(models.Department).options(
                    load_only("idDepartment", "entityBodyID", "DepartmentName")).filter_by(
                    entityBodyID=row.idEntityBody).all()
                row.department = dpt_result
            return entb_result
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error"})


async def update_entity_body_dept(u_id, u_entb_dept, db):
    """
    This function is for updating entity body and its related department details. It contains 3 parameters.
    :param u_id: u_id: It is a path parameters that is of integer type, it provides the user Id.
    :param u_entb_dept: It is a function parameters that is of Pydantic type, it provides entity bosy and department details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # dept_id = db.query(models.Department.idDepartment).filter_by(
        #     idDepartment=u_ent_dept.Department.idDepartment).scalar()
        r_dpt, r_entb = 0, 0
        # checking if department details given for update
        if u_entb_dept.Department:
            u_dpt = dict(u_entb_dept.Department)
            for item_key in u_dpt.copy():
                # pop out elements that are not having any value
                if not u_dpt[item_key]:
                    u_dpt.pop(item_key)
            r_dpt = db.query(models.Department).filter_by(idDepartment=u_dpt["idDepartment"]).update(
                u_dpt)
            db.flush()
        if u_entb_dept.EntityBody:
            u_entb = dict(u_entb_dept.EntityBody)
            for item_key in u_entb.copy():
                # pop out elements that are not having any value
                if not u_entb[item_key]:
                    u_entb.pop(item_key)
            r_entb = db.query(models.EntityBody).filter_by(idEntityBody=u_entb["idEntityBody"]).update(
                u_entb)
            # notifying changes to the db but not committing since next stage it will be committed
            db.flush()
        if u_entb_dept.Department or u_entb_dept.EntityBody:
            if r_dpt or r_entb == 1:
                # committing changes if both are updated
                db.commit()
                return {"result": "Updated"}
            else:
                db.rollback()
                return Response(status_code=400, headers={"ClientError": "Updated Failed"})
        return Response(status_code=422, headers={"ClientError": "Body Improper"})
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error"})


async def ReadCustomerUser(db, u_id: int):
    """
     This function read customer user list. It contains 2 parameter.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It returns the result data in list type.
     """
    try:
        c_id = db.query(models.User.customerID).filter_by(idUser=u_id)
        # each user profile data
        pfdata = db.query(models.AccessPermission, models.AccessPermissionDef, models.AmountApproveLevel,
                          models.User).filter(models.AccessPermissionDef.isUserRole == 1).filter(
            models.AccessPermission.permissionDefID == models.AccessPermissionDef.idAccessPermissionDef).join(
            models.AmountApproveLevel,
            models.AccessPermissionDef.amountApprovalID == models.AmountApproveLevel.idAmountApproveLevel,
            isouter=True).filter(models.AccessPermission.userID == models.User.idUser).filter(
            models.User.customerID == c_id.scalar_subquery())
        is_admin = db.query(models.User.created_by).filter_by(idUser=u_id).scalar()
        if is_admin:
            pfdata = pfdata.filter((
                                           models.User.created_by == u_id) | (models.User.idUser == u_id)).all()
        else:
            pfdata = pfdata.all()
        for pfrow in pfdata:
            count = 0
            # each users entity site count
            acdata = db.query(models.UserAccess.EntityID, models.UserAccess.EntityBodyID).filter_by(
                UserID=pfrow.AccessPermission.userID).filter_by(isActive=1).all()
            for acent, acentb in acdata:
                # if specific entity body is given count only that
                if acentb:
                    count += 1
                else:
                    # count by entity if no entity body provided , since overall entity permission
                    count += int(db.query(func.count(models.EntityBody.idEntityBody)).filter(
                        models.EntityBody.EntityID == acent).scalar())
            setattr(pfrow[3], "entity_site_count", count)
        return pfdata
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readVendorNames(u_id, ent_id, ven_name,off_limit, db):
    """
    This function reads Vendor names. It contains 2 parameter.
    :param user_id: It is a function parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in list type.
    """
    offset, limit = off_limit
    if offset < 0:
        return Response(status_code=403, headers={"ClientError": "please provide right offset value"})
    try:
        if ent_id:
            # only if the entity id is present in user access table
            ent_ids = db.query(models.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1,
                                                                     EntityID=ent_id).distinct()
        else:
            ent_ids = db.query(models.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        vendor = db.query(models.Vendor).options(load_only("VendorName")).filter(
            models.Vendor.entityID.in_(ent_ids))
        if ven_name:
            vendor = vendor.filter(models.Vendor.VendorName.like(f"%{ven_name}%"))
        if limit:
            vendor = vendor.limit(limit)
        if offset:
            offset = (offset - 1) * limit
            vendor = vendor.offset(offset)
        return {"vendorlist": vendor.all()}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def readVendorEntityCodes(u_id, ven_code, db):
    """
    This function reads Vendor names. It contains 2 parameter.
    :param user_id: It is a function parameters that is of integer type, it provides the user Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in list type.
    """
    try:
        ent_ids = db.query(models.Vendor.entityID).filter_by(VendorCode=ven_code).distinct()
        ent_ids = db.query(models.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).filter(
            models.UserAccess.EntityID.in_(ent_ids)).distinct()
        ent_details = db.query(models.Entity).options(load_only("EntityName")).filter(
            models.Entity.idEntity.in_(ent_ids)).distinct().all()
        return {"ent_details": ent_details}

    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def readUserName(name, db):
    """
    this function is used to validate if userlog name has already been used by someone else
    :param name: It is a function parameters that is of string type, it provides the user login name.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dict type.[None if name is not present]
    """
    try:
        LogName = db.query(models.Credentials.LogName).filter_by(LogName=name).scalar()
        return {"LogName": LogName}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def newVendorAdminUserName(u_id, ven_user, ven_user_type, db):
    """
    This function creates new Vendor users. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param ven_user: It is a function parameter of Pydantic class, it provides the new Vendor user details.
    :param ven_user_type: It provides the type of vendor user that is being creating.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data of dict type.
    """
    try:
        # permission check function has to be created and checked
        createdon = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # pop the user access
        n_usr = ven_user.dict()
        n_usr["created_by"] = u_id
        user_access = n_usr.pop("uservendoraccess")
        role_id = n_usr.pop("role_id")
        # get company id
        c_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        n_usr = models.User(**n_usr, customerID=c_id, CreatedOn=createdon)
        db.add(n_usr)
        db.flush()
        # common info
        basedata = {"vendorUserID": n_usr.idUser,
                    "CreatedBy": u_id,
                    "CreatedOn": createdon,
                    "UpdatedOn": createdon}
        # removing duplicate key
        [row.pop("vendorUserID") for row in user_access]
        # saving the access permission
        user_access = user_access[0]
        entity_ids = user_access.pop("entityID")
        ven_ids = db.query(models.Vendor.idVendor).filter_by(VendorCode=user_access["vendorCode"]).filter(
            models.Vendor.entityID.in_(entity_ids))
        accounts = db.query(models.VendorAccount.idVendorAccount, models.VendorAccount.vendorID,
                            models.Vendor.entityID).filter(
            models.VendorAccount.vendorID.in_(ven_ids), models.VendorAccount.vendorID == models.Vendor.idVendor).all()
        user_access = [{"vendorAccountID": val[0], "vendorID": val[1], "entityID": val[2]} for val in accounts]
        user_access = [models.VendorUserAccess(**row, **basedata) for row in user_access]
        db.add_all(user_access)
        # notifying changes to the db but not committing since next stage it will be committed
        db.flush()
        db.add(models.AccessPermission(permissionDefID=role_id, userID=n_usr.idUser, CreatedOn=createdon))
        db.flush()
        # returning the customer details with custom function from models to avoid all columns
        return n_usr.datadict(), ven_user_type
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(traceback.print_exc())
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{traceback.format_exc()}Server error"})


async def read_vendor_user(db, u_id):
    """
    This function reads vendor admin users. It contains 2 parameters.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :return:It returns the result data of list type.
    """
    try:
        ctby_id = db.query(models.User.created_by).filter_by(idUser=u_id).scalar()
        vendor_admin_data = db.query(models.AccessPermissionDef,
                                     models.User).options(
            Load(models.User).load_only("firstName", "lastName", "isActive"),
            Load(models.AccessPermissionDef).load_only("NameOfRole")).filter(
            models.User.idUser == models.AccessPermission.userID,
            models.AccessPermission.permissionDefID == models.AccessPermissionDef.idAccessPermissionDef).filter(
            models.User.isCustomerUser == 0).filter(
            models.AccessPermissionDef.idAccessPermissionDef == 7)
        # each user profile data
        if ctby_id:
            vendor_admin_data = vendor_admin_data.filter(models.User.created_by == u_id).all()
        else:
            vendor_admin_data = vendor_admin_data.all()
        for row in vendor_admin_data:
            ven_id = db.query(models.VendorUserAccess.vendorID).filter_by(vendorUserID=row[1].idUser,
                                                                          isActive=1).limit(1).scalar()
            vendor_name = db.query(models.Vendor.VendorName).filter_by(idVendor=ven_id).scalar()
            setattr(row[1], "vendor_name", vendor_name)
        return vendor_admin_data
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def deactivate_user_account(db, bg_task, u_id, d_u_id):
    """
    This function deactivates a user account of existing user. It contains 3 parameters.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param d_u_id: It is a function parameters that is of integer type, it provides the user Id that has to be
    deactivated.
    :return: It returns the result data of dict type.
    """
    try:
        cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        userdetails = db.query(models.User).options(load_only("firstName", "lastName", "email")).filter_by(
            idUser=d_u_id).one()
        userdetails = userdetails.__dict__
        userdetails.pop('_sa_instance_state')
        # check the user permission before it can deactivate other users(pending)
        isactive = db.query(models.User.isActive).filter_by(idUser=d_u_id).scalar()
        # check if the account is active or not
        if isactive:
            if isactive == 1:
                db.query(models.User).filter_by(idUser=d_u_id).update({"isActive": 0})
                db.commit()
                try:
                    ############ start of notification trigger #############
                    details = {"user_id": None, "trigger_code": 8005, "cust_id": cust_id, "inv_id": None,
                               "additional_details": {
                                   "recipients": [
                                       (userdetails["email"], userdetails["firstName"], userdetails["lastName"])],
                                   "subject": "account deactivation",
                                   "user_details": userdetails}}
                    # bg_task.add_task(meta_data_publisher, details)
                    ############ End of notification trigger #############
                except Exception as e:
                    print("notification exception", e)
                return {"result": "account deactivated"}
        elif isactive == 0:
            try:
                ############ start of notification trigger #############
                userdetails["username"] = db.query(models.Credentials.LogName).filter_by(userID=d_u_id).filter(
                    models.Credentials.crentialTypeId.in_((1, 2))).scalar()
                details = {"user_id": [u_id], "trigger_code": 8011, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {
                               "recipients": [
                                   (userdetails["email"], userdetails["firstName"], userdetails["lastName"])],
                               "subject": "Account Activation",
                               "endpoint_url": f"{endpoint_site}/#/registration-page/activationLink/",
                               "user_details": userdetails}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
            return {"result": "account activation mail sent"}

    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


def update_vendor_user(u_id, uu_id, u_user, uservendoraccess, bg_task, db):
    """
    This function updates a existing User in the db. It contains 3 parameters.
    :param uu_id: It is a function parameters that is of integer type, it provides the update user Id.
    :param u_user: It is a function parameters that is of Pydantic type, it provides User details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data of dict type.
    """
    try:
        # uu_id = 7290
        # permission check function has to be created and checked
        # getting the user id from customer id in the User table
        user_id = db.query(models.User.idUser).filter_by(idUser=uu_id).scalar()
        # checking if the user id is present
        if user_id:
            # result provides an integer value 0 or 1 depending on if the updating was successful
            if u_user:
                u_user = {k: v for k, v in u_user.dict().items() if v}
                db.query(models.User).filter_by(idUser=user_id).update(u_user)
            # updating user access if any vendor id, vendor account access was provided along with department
            if uservendoraccess:
                for access in uservendoraccess:
                    # if access id for the user is provided , then mark it for delete
                    if access.idVendorUserAccess:
                        db.query(models.VendorUserAccess).filter_by(vendorUserID=uu_id,
                                                                    idVendorUserAccess=access.idVendorUserAccess).update(
                            {"isActive": 0})
                    else:
                        # else check if the row with the values are present already and update it as active
                        del access.idVendorUserAccess
                        result = db.query(models.VendorUserAccess.idVendorUserAccess).filter_by(vendorUserID=uu_id,
                                                                                                **dict(access)).scalar()
                        # if result update to activate
                        if result:
                            db.query(models.VendorUserAccess).filter_by(vendorUserID=uu_id, **dict(access)).update(
                                {"isActive": 1})
                        # check if the update was success else no record is present , create a new record
                        else:
                            access = access.dict()
                            access["vendorUserID"] = uu_id
                            access["CreatedBy"] = u_id
                            access["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                            access["UpdatedOn"] = access["CreatedOn"]
                            access = models.VendorUserAccess(**access)
                            db.add(access)
            db.commit()
            try:
                ############ start of notification trigger #############
                cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
                details = {"user_id": [u_id], "trigger_code": 8006, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {
                               "recipients": [(u_user["email"], u_user["firstName"], u_user["lastName"])],
                               "subject": "User Details Update"}}
                # bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
            return {"result": "Updated"}
        else:
            db.rollback()
            return Response(status_code=400, headers={"ClientError": "User id not active"})
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400,
                        headers={"ClientError": f"{str(traceback.format_exc())}one or more values does not exist"})
    except Exception as e:
        print(traceback.print_exc())
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{str(traceback.format_exc())} Server error"})


async def update_rolebased_gen_config(u_id, isenabled, bg_task, db):
    try:
        cmp_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        db.query(models.GeneralConfig).filter_by(customerID=cmp_id).update({"isRoleBased": isenabled})
        db.commit()
        try:
            ############ start of notification trigger #############
            # getting recipients for sending notification
            recepients = db.query(models.AccessPermission.userID).filter(
                models.AccessPermission.permissionDefID == 1).distinct()
            recepients = db.query(models.User.idUser, models.User.email, models.User.firstName,
                                  models.User.lastName).filter(models.User.idUser.in_(recepients)).filter(
                models.User.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
            details = {"user_id": None, "trigger_code": 8008, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"subject": "Settings Update", "recipients": email_ids}}
            bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print("notification exception", e)
        return {"result": "updated"}
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400,
                        headers={"ClientError": f"{str(traceback.format_exc())}one or more values does not exist"})
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{str(traceback.format_exc())} Server error"})
    finally:
        db.close()


async def read_gen_setting(u_id, db):
    try:
        cmp_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        result = db.query(models.GeneralConfig).filter_by(customerID=cmp_id).one()
        return {"data": result}
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400,
                        headers={"ClientError": f"{str(traceback.format_exc())}one or more values does not exist"})
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{str(traceback.format_exc())} Server error"})
    finally:
        db.close()


async def readvendoraccount(u_id, v_id, db):
    """
     This function read Vendor account details. It contains 2 parameter.
     :param u_id: It is a function parameters that is of integer type, it provides the vendor user Id.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        ven_accs = db.query(models.VendorAccount).options(load_only('Account')).filter_by(
            vendorID=v_id).all()
        return {"result": ven_accs}
    except Exception as e:
        print(f"{traceback.format_exc()}")
        return Response(status_code=500, headers={"Error": "Server error"})


async def update_portal_pass(u_id, new_pass, db):
    """

    """
    try:
        new_pass = dict(new_pass)
        auth_handler = AuthHandler()
        # check old password matches the existing password
        hashed_db_pass = db.query(models.Credentials.LogSecret).filter(models.Credentials.userID == u_id,
                                                                       models.Credentials.crentialTypeId.in_(
                                                                           (1, 2))).scalar()
        if hashed_db_pass:
            pass_bool = auth_handler.verify_password(new_pass["old_pass"], hashed_db_pass)
            if pass_bool:
                pass_obj = {}
                pass_obj["LogSecret"] = auth_handler.get_password_hash(new_pass["new_pass"])
                pass_obj["UpdatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                db.query(models.Credentials).filter(models.Credentials.userID == u_id,
                                                    models.Credentials.crentialTypeId.in_((1, 2))).update(pass_obj)
                db.commit()
                return {"result": "password updated"}
            else:
                return Response(status_code=400,
                                headers={"ClientError": "old password does not match"})
        else:
            return Response(status_code=400,
                            headers={"ClientError": "User not found"})
    except Exception as e:
        print(f"{traceback.format_exc()}")
        return Response(status_code=500, headers={"Error": "Server error"})
