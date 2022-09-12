from fastapi.applications import FastAPI
from fastapi.responses import Response
from sqlalchemy.sql import select, update, delete, func
from sqlalchemy import and_, or_, not_, exc
import json
from random import randrange
from datetime import datetime
import pytz as tz
from sqlalchemy.orm import join, load_only, Load
from fastapi import status, HTTPException
import traceback
import sys
import os
from logModule import applicationlogging

sys.path.append("..")
import model as models
from session.notificationsession import client as mqtt

az_function_name = os.getenv("ScheduleFlowName", "dev_sflow_invoker")
az_function_schedule_variable = os.getenv("ScheduleFlowVariable", "DevScheduleTime")
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


async def new_amount_approval(u_id, maxamount, db):
    """
    This function creates a new amount approval in db. It contains 3 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param maxamount: It is a function parameters that is of integer type, it provides the maximum amount a user can approve.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # subquery to get access permission id from db
        sub_query = db.query(models.AccessPermission.permissionDefID).filter_by(userID=u_id).distinct()
        # query to get the user permission for the user from db
        main_query = db.query(models.AccessPermissionDef.Permissions).filter(
            models.AccessPermissionDef.idAccessPermissionDef.in_(sub_query)).scalar()
        # get the user permission and check if user can create or not by checking if its not null
        if not main_query:
            return Response(status_code=400, headers={"ClientError": "Permission Denied"})
        n_aal = dict(maxamount)
        temp = {}
        temp["userID"] = n_aal.pop("applied_uid")
        # supplying dict as a keyword args to the AmountApproval Model for Saving to db
        n_aal = models.AmountApproveLevel(MaxAmount=n_aal.pop("MaxAmount"))
        db.add(n_aal)
        db.commit()
        result = n_aal.datadict()
        # updating access permission with amount approval id
        result1 = db.query(models.AccessPermission).filter_by(**temp).update(
            {"approvalLevel": result["idAmountApproveLevel"]})
        db.commit()
        if result1 == 1:
            return {"result": result}
        return {"result": "failed"}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def update_amount_approval(u_id, aal_id, maxamount, db):
    """
    This function updates an existing amount approval in db. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param aal_id: It is a function parameters that is of integer type, it provides the amount approval Id.
    :param maxamount: It is a function parameters that is of integer type, it provides the maximum amount a user can approve.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # have to check if u_id is a admin with permission
        # subquery to get access permission id from db
        sub_query = db.query(models.AccessPermission.permissionDefID).filter_by(userID=u_id).distinct()
        # query to get the user permission for the user from db
        main_query = db.query(models.AccessPermissionDef.Permissions).filter(
            models.AccessPermissionDef.idAccessPermissionDef.in_(sub_query)).scalar()
        # get the user permission and check if user can create or not by checking if its not null
        if not main_query:
            return Response(status_code=400, headers={"ClientError": "Permission Denied"})
        # supplying dict as a keyword args to the AmountApproval Model for Saving to db
        stmt = update(models.AmountApproveLevel).where(
            models.AmountApproveLevel.idAmountApproveLevel == aal_id).values(dict(maxamount))
        result = db.execute(stmt)
        db.commit()
        # check if any rows where updated
        AmountApproveLevel = {"idAmountApproveLevel": aal_id, "MaxAmount": maxamount.MaxAmount}
        return {"result": AmountApproveLevel}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


# might be used in future with extra mod
async def read_amount_approval(u_id, aal_id, db):
    """
    This function reads existing amount approval in the db. It contains 3 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param aal_id: It is a query optional parameters that is of integer type, it provides the amount approval Id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # have to check if u_id is a admin with permission
        stmt = select([models.AmountApproveLevel])
        # check if amount approval level is provided
        if aal_id:
            # append filter condition
            stmt = stmt.where(models.AmountApproveLevel.idAmountApproveLevel == aal_id)
        result = db.execute(stmt).fetchall()
        return {"result": result}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def update_access_permission(u_id, apd_id, u_apd, bg_task, db):
    """
    This function updates an existing access permission. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param apd_id: It is a function parameters that is of integer type, it provides the amount approval Id.
    :param u_apd: It is a function parameters that is of Pydantic type, it provides AccessPermission information.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # have to check if u_id is a admin with permission
        u_apd = dict(u_apd)
        max_amount = u_apd.pop("max_amount")
        # check if priority already available
        priority = db.query(models.AccessPermissionDef.Priority).filter_by(Priority=u_apd["Priority"],
                                                                           isActive=1).filter(
            models.AccessPermissionDef.idAccessPermissionDef != apd_id).all()
        if len(priority) > 0:
            return Response(status_code=400, headers={"Error": "Check Priority"})
        # making sure vendor roles are not allowed to trigger schedule
        isUserRole = db.query(models.AccessPermissionDef.isUserRole).filter_by(
            idAccessPermissionDef=apd_id).scalar()
        if not isUserRole:
            u_apd["allowBatchTrigger"] = 0
            u_apd["allowServiceTrigger"] = 0
        if max_amount and u_apd["AccessPermissionTypeId"] == 4:
            max_amount = models.AmountApproveLevel(MaxAmount=max_amount)
            db.add(max_amount)
            db.flush()
            u_apd["amountApprovalID"] = max_amount.idAmountApproveLevel
        else:
            u_apd["amountApprovalID"] = None
        u_apd["UpdatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # update
        db.query(models.AccessPermissionDef).filter_by(idAccessPermissionDef=apd_id).update(u_apd)
        db.commit()
        try:
            ############ start of notification trigger #############
            # getting recipients for sending notification
            recepients = db.query(models.User.idUser, models.User.email, models.User.firstName,
                                  models.User.lastName).filter(models.User.idUser.in_([u_id])).filter(
                models.User.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
            details = {"user_id": user_ids, "trigger_code": 8007, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"subject": "Access Update", "recipients": email_ids}}
            # bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print("notification exception", e)
        return {"result": "updated"}
    except exc.IntegrityError as e:
        # foreign key error , value not found in primary table
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        db.rollback()
        print(traceback.print_exc())
        return traceback.format_exc()
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


# might need mod later
async def read_user_access(u_id, au_id, skip, limit, db):
    """
    This function reads an existing customer invoice access in the db. It contains 3 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param ua_id: It is a query optional parameters that is of integer type, it provides the invoice access Id which is optional.
    :param skip: It is a function parameters that is of integer type, it provides the offset value.
    :param limit: It is a function parameters that is of integer type, it provides the limit value.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # permission check function has to be created and checked
        # selecting only required columns in query
        # .filter(models.UserAccess.EntityID == models.Entity.idEntity, models.UserAccess.EntityBodyID == models.EntityBody.idEntityBody, models.UserAccess.DepartmentID == models.Department.idDepartment)
        query = db.query(models.UserAccess, models.Entity, models.EntityBody, models.Department).join(models.Entity,
                                                                                                      models.Entity.idEntity == models.UserAccess.EntityID,
                                                                                                      isouter=True).join(
            models.EntityBody,
            models.EntityBody.idEntityBody == models.UserAccess.EntityBodyID, isouter=True).join(models.Department,
                                                                                                 models.Department.idDepartment == models.UserAccess.DepartmentID,
                                                                                                 isouter=True).options(
            Load(models.UserAccess).load_only("UserID", "CreatedBy"), Load(models.Entity).load_only("EntityName"),
            Load(models.EntityBody).load_only("EntityBodyName"),
            Load(models.Department).load_only("DepartmentName")).filter(models.UserAccess.isActive == 1)
        # checking if entity body id was provided
        if au_id:
            # selecting by applied user id
            try:
                result = query.filter(models.UserAccess.UserID == au_id).all()
                return {"result": result}
            except Exception as e:
                return Response(status_code=400, headers={"ClientError": f"{e} Vendor user access id does not exist"})
        else:
            result = query.offset(skip).limit(limit).all()
            return {"result": result}
    except exc.IntegrityError as e:
        db.rollback()
        return Response(status_code=400, headers={"ClientError": "one or more values does not exist"})
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": f"{e} Server error"})


def setdochistorylog(dochist, db):
    try:
        if dochist["documentStatusID"]:
            db.query(models.Document).filter_by(idDocument=dochist["documentID"]).update(
                {"documentStatusID": dochist["documentStatusID"]})
        else:
            dochist["documentStatusID"] = 1
        dochist["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        dochist = models.DocumentHistoryLogs(**dochist)
        db.add(dochist)
        db.commit()
        return 1
    except Exception as e:
        print(traceback.print_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


def setapprovallevel(u_id, inv_id, MaxAmount, user_accessdef_id, db):
    dochist = {}
    dochist["userID"] = u_id
    dochist["documentID"] = inv_id
    dochist["userAmount"] = MaxAmount
    current_status = db.query(models.Document.documentStatusID).filter_by(idDocument=inv_id).scalar()
    dochist["documentStatusID"] = current_status
    dochist["documentfinstatus"] = 0
    # add query to extract amount from invdata its temporary for now/replace [fin_approve with actual amount]
    # update it to final approval based on condition
    inv_amount = db.query(models.Document.totalAmount).filter(
        models.Document.idDocument == inv_id).scalar()
    # get priority and roles to handle exception
    user_priority = db.query(models.AccessPermissionDef.Priority).filter_by(
        idAccessPermissionDef=user_accessdef_id).scalar()
    # get the roles with higher priority
    accessdef_ids = db.query(models.AccessPermissionDef.Priority).filter_by(
        AccessPermissionTypeId=4).filter(models.AccessPermissionDef.Priority > user_priority).all()
    if float(inv_amount) <= float(MaxAmount):
        # check if the role flag is enabled
        cmp_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        role_flag = db.query(models.GeneralConfig.isRoleBased).filter_by(customerID=cmp_id).scalar()
        if not role_flag:
            dochist["documentfinstatus"] = 1
            dochist["documentStatusID"] = 3
        else:
            # if no grater role available then approve
            if len(accessdef_ids) < 1:
                dochist["documentfinstatus"] = 1
                dochist["documentStatusID"] = 3
    else:
        # if amount > then max amount and no roles available next to approve, return 0 flag to handle exception
        if len(accessdef_ids) < 1:
            return 0
        else:
            # partially approved
            setdochistorylog(dochist, db)
            return 2
    setdochistorylog(dochist, db)
    return 1


# to set status at different approval level
async def financial_approval_level(u_id, inv_id, bg_task, db):
    """
    This function creates a new amount approval in db. It contains 3 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param inv_id: It is a function parameters that provides the invoice id.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the result data in dictionary type.
    """
    try:
        # get the access def id for the user
        accessdef_id = db.query(models.AccessPermission.permissionDefID).filter_by(userID=u_id).scalar()
        # get the amount approval id from the role
        amt_ap_id = db.query(models.AccessPermissionDef.amountApprovalID).filter_by(
            idAccessPermissionDef=accessdef_id).scalar()
        # check if role can approve
        if amt_ap_id:
            # get the amount user can approve
            max_amount = db.query(models.AmountApproveLevel.MaxAmount).filter_by(
                idAmountApproveLevel=amt_ap_id).scalar()
            # check if the invoice has been completely approved
            doc_fin_stat = db.query(models.DocumentHistoryLogs.documentfinstatus).filter_by(documentID=inv_id,
                                                                                            documentfinstatus=1).scalar()
            if doc_fin_stat:
                return Response(status_code=400,
                                headers={"Error": "permission denied, Invoice already financially approved"})
            # check if the same amount is approved before
            approvedby = db.query(models.DocumentHistoryLogs.userID,
                                  models.DocumentHistoryLogs.documentfinstatus).filter_by(
                documentID=inv_id, documentfinstatus=0, userAmount=max_amount).all()
            if len(approvedby) > 0:
                return Response(status_code=400,
                                headers={"Error": "permission denied, Invoice already approved with same amount"})
        flag = setapprovallevel(u_id, inv_id, max_amount, accessdef_id, db)
        try:
            ############ start of notification trigger #############
            cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
            # only financial users
            acc_def_id = db.query(models.AccessPermissionDef.idAccessPermissionDef).filter_by(
                AccessPermissionTypeId=4).distinct()
            recepients1 = db.query(models.AccessPermission.userID).filter(
                models.AccessPermission.permissionDefID == acc_def_id).distinct()
            recepients2 = db.query(models.AccessPermission.userID).filter(
                models.AccessPermission.permissionDefID == 1).distinct()
            recepients = db.query(models.User.idUser, models.User.email, models.User.firstName,
                                  models.User.lastName).filter(models.User.idUser.in_(recepients1)).filter(
                models.User.idUser.in_(recepients2)).filter(
                models.User.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just formatting
            email_ids = list(zip(email[0], email[1], email[2]))
            userdetails = db.query(models.User).options(load_only("firstName", "lastName", "email")).filter_by(
                idUser=u_id).one()
        except Exception as e:
            print("notification exception", e)
        if flag == 1:
            try:
                details = {"user_id": user_ids, "trigger_code": 8002, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {"subject": "Partial Approval", "recipients": email_ids,
                                                  "ffirstName": userdetails.firstName,
                                                  "llastName": userdetails.lastName}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
            return {"result": "Amount approved"}
        elif flag == 2:
            try:
                details = {"user_id": user_ids, "trigger_code": 8018, "cust_id": cust_id, "inv_id": inv_id,
                           "additional_details": {"subject": "Complete Approval", "recipients": email_ids,
                                                  "ffirstName": userdetails.firstName,
                                                  "llastName": userdetails.lastName}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
            return {"result": "Amount approved Partially"}
        else:
            return Response(status_code=400,
                            headers={"details": "Request Admin to increase the max amount limit"})
    except Exception as e:
        print(traceback.print_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def apply_access_permission(u_id, a_ap, bg_task, db):
    """

    :param u_id:
    :param a_ap:
    :param db:
    :return:
    """
    try:
        # create access permission to apply the permission def
        temp = {}
        a_ap = dict(a_ap)
        a_ap["userID"] = a_ap.pop("applied_uid")
        temp["userID"] = a_ap["userID"]
        existing_permission_id = db.query(models.AccessPermission.idAccessPermission).filter_by(**temp).scalar()
        a_ap["permissionDefID"] = a_ap.pop("appied_permission_def_id")
        if existing_permission_id:
            db.query(models.AccessPermission).filter_by(**temp).update(a_ap)
        else:
            a_ap["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
            a_ap = models.AccessPermission(**a_ap)
            db.add(a_ap)
        db.commit()
        try:
            ############ start of notification trigger #############
            # getting recipients for sending notification
            recepients = db.query(models.User.idUser, models.User.email, models.User.firstName,
                                  models.User.lastName).filter(models.User.idUser.in_([u_id])).filter(
                models.User.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            cust_id = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
            details = {"user_id": user_ids, "trigger_code": 8007, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"subject": "Access Update", "recipients": email_ids}}
            # bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print("notification exception", e)
        return {"result": "success"}
    except Exception as e:
        traceback.print_exc()
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def read_roles_permission(u_id, db, utype):
    """

    :param u_id:
    :param db:
    :param utype:
    :return:
    """
    try:
        result = db.query(models.AccessPermissionDef).options(
            load_only("NameOfRole", "Priority", "AccessPermissionTypeId", "isDefault"))
        if utype == "vendor":
            result = result.filter_by(isUserRole=0).filter_by(isActive=1).all()
        else:
            result = result.filter_by(isUserRole=1).filter_by(isActive=1).all()
        return {"roles": result}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def read_roles_permission_info(u_id, apd_id, db):
    """

    :param u_id:
    :param apd_id:
    :param db:
    :return:
    """
    try:
        result = db.query(models.AccessPermissionDef, models.AmountApproveLevel).filter_by(
            idAccessPermissionDef=apd_id).options(
            Load(models.AccessPermissionDef).load_only("User", "Priority", "Permissions", "AccessPermissionTypeId",
                                                       "NewInvoice", "isDashboard", "allowBatchTrigger",
                                                       "allowServiceTrigger",
                                                       "isUserRole", "isConfigPortal", "is_epa", "is_gpa", "is_vspa",
                                                       "is_spa")).join(models.AmountApproveLevel,
                                                                       models.AccessPermissionDef.amountApprovalID == models.AmountApproveLevel.idAmountApproveLevel,
                                                                       isouter=True).one()
        return {"roleinfo": result}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def delete_role_permission(u_id, apd_id, bg_task, db):
    """

    :param u_id:
    :param apd_id:
    :param db:
    :return:
    """
    try:
        result = db.query(models.AccessPermission.idAccessPermission).filter_by(permissionDefID=apd_id).all()
        for row in result:
            if row[0]:
                return Response(status_code=400, headers={"ClientError": "Cannot delete after assigning permission"})
        result = db.query(models.AccessPermissionDef).filter_by(idAccessPermissionDef=apd_id).update({"isActive": 0})
        db.commit()
        if result == 1:
            try:
                ############ start of notification trigger #############
                role_name = db.query(models.AccessPermissionDef.NameOfRole).filter_by(
                    idAccessPermissionDef=apd_id).scalar()
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
                details = {"user_id": user_ids, "trigger_code": 8025, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "Role Delete", "recipients": email_ids,
                                                  "role_name": role_name}}
                # bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
            return {"result": "success"}
        return {"result": "failed"}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def new_access_permission(u_id, n_ap, bg_task, db, utype):
    """

    :param u_id:
    :param n_ap:
    :param db:
    :param utype:
    :return:
    """
    try:
        n_ap = dict(n_ap)
        max_amount = n_ap.pop("max_amount")
        # check if priority already available
        priority = db.query(models.AccessPermissionDef.Priority).filter_by(Priority=n_ap["Priority"],
                                                                           isActive=1).scalar()
        if priority:
            return Response(status_code=400, headers={"Error": "Check Priority"})
        if max_amount and n_ap["AccessPermissionTypeId"] == 4:
            max_amount = models.AmountApproveLevel(MaxAmount=max_amount)
            db.add(max_amount)
            db.flush()
            n_ap["amountApprovalID"] = max_amount.idAmountApproveLevel
        if utype == "vendor":
            n_ap["isUserRole"] = 0
            n_ap["allowBatchTrigger"] = 0
            n_ap["allowServiceTrigger"] = 0
        n_ap["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        n_ap["UpdatedOn"] = n_ap["CreatedOn"]
        n_ap = models.AccessPermissionDef(**n_ap)
        db.add(n_ap)
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
            details = {"user_id": user_ids, "trigger_code": 8024, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"subject": "Role Added", "recipients": email_ids,
                                              "role_name": n_ap.NameOfRole}}
            # bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print("notification exception", e)
        return {"result": n_ap.datadict()}
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def update_service_schedule(u_id, schedule_update, bg_task, db):
    """

    :param u_id:
    :param schedule_update:
    :param db:
    :return:
    """
    try:
        schedule_update = dict(schedule_update)
        ser_schedule_conf = db.query(models.GeneralConfig.serviceBatchConf).filter_by(idgeneralconfig=1).scalar()
        ser_schedule_conf["schedule"] = schedule_update["schedule"]
        ser_schedule_conf["isTriggerActive"] = schedule_update["isTriggerActive"]
        ser_schedule_conf["isScheduleActive"] = schedule_update["isScheduleActive"]
        UpdatedOn = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        updatedBy = u_id
        db.query(models.GeneralConfig).filter_by(idgeneralconfig=1).update(
            {"serviceBatchConf": ser_schedule_conf, "UpdatedOn": UpdatedOn, "updatedBy": updatedBy})
        db.commit()
        try:
            import os
            from azure.cli.core import get_default_cli as azcliclient
            azcliclient().invoke(
                ["login", "--output", "none", "--service-principal", "-u", "a7d7f024-8082-4aad-9a4b-71de6d684218", "-p",
                 "kM27Q~TS7WQ4F8xSDdap2uAVN4UiOJpp9Yvkx", "--tenant",
                 "86fb359e-1360-4ab3-b90d-2a68e8c007b9"])
            azcliclient().invoke(
                ["functionapp", "config", "appsettings", "set", "--name", "serinaplus-func", "--resource-group",
                 "SERINAPLUS", "--settings", f"{az_function_schedule_variable}={schedule_update['schedule']}",
                 "--output", "none"])
            if not schedule_update['isScheduleActive']:
                azcliclient().invoke(["functionapp", "config", "appsettings", "set", "--name", "serinaplus-func",
                                      "--resource-group", "SERINAPLUS", "--settings",
                                      f"AzureWebJobs.{az_function_name}.Disabled=true", "--output", "none"])
            else:
                azcliclient().invoke(["functionapp", "config", "appsettings", "set", "--name", "serinaplus-func",
                                      "--resource-group", "SERINAPLUS", "--settings",
                                      f"AzureWebJobs.{az_function_name}.Disabled=false", "--output", "none"])
            azcliclient().invoke(["logout", "--output", "none"])
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
                details = {"user_id": user_ids, "trigger_code": 8008, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "Service Schedule Update", "recipients": email_ids}}
                # bg_task.add_task(meta_data_publisher, details)
                ########### End of notification trigger #############
            except Exception as e:
                print("notification exception", e)
        except Exception as e:
            print(traceback.format_exc())
            return Response(status_code=400, headers={"Error": "Azure Error"})
        return {"result": "successful"}
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def read_service_schedule(u_id, db):
    """

    :param u_id:
    :param db:
    :return:
    """
    try:
        cid = db.query(models.User.customerID).filter_by(idUser=u_id).scalar()
        data = db.query(models.GeneralConfig.serviceBatchConf).filter_by(customerID=cid).scalar()
        data.pop("isRunning")
        data.pop("scheduleUrl")
        return {"result": data}
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()
