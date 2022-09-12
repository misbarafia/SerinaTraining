import traceback
import uuid
from io import BytesIO
import requests
from sqlalchemy.orm import Session, load_only, Load
import tempfile
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from sqlalchemy import func,case
from cryptography.fernet import Fernet
from fastapi.responses import Response, FileResponse, StreamingResponse
from datetime import datetime
from logModule import applicationlogging
import sys
import json
import os
import pytz as tz

sys.path.append("..")
import model
import schemas
from session.notificationsession import client as mqtt

container_name = os.getenv("agi_cost_path", "agicostallocdev")
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


# Background task publisher
def meta_data_scheduler(msg):
    try:
        mqtt.publish("service_batch_queue", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


async def new_service(u_id, n_ser, db):
    """
    This function creates a new Service provider. It contains 3 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param n_ser: It is function parameter that is of a Pydantic class object, It takes member data for creation of new Service provider.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        n_ser = dict(n_ser)
        # have to make it dynamic to void duplicate error
        n_ser["createdBy"] = u_id
        n_ser["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # supplying dict as a keyword args to the Service Model
        n_ser = model.ServiceProvider(**n_ser)
        db.add(n_ser)
        db.commit()
        resp = {"result": "saved to db", "record": n_ser}
        return resp
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid User ID"})
    finally:
        db.close()


def new_service_account(u_id, s_id, n_ser_acc, db):
    """
    This function creates a new Service provider. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param s_id: It is a function parameter that is of integer type, it provides the Service provider id.
    :param n_ser_acc: It is function parameter that is of a Pydantic class object, It takes member data for creation of new Service account.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        n_ser_acc = dict(n_ser_acc)
        # have to make it dynamic to void duplicate error
        # n_ser_acc["idSupplierAccount"] = 1
        # have to check if corresponds to the user id
        n_ser_acc["serviceProviderID"] = s_id
        n_ser_acc["createdBy"] = u_id
        n_ser_acc["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # supplying dict as a keyword args to the ServiceAccount Model
        db_model = model.ServiceAccount(**n_ser_acc)
        db.add(db_model)
        db.commit()
        n_ser_acc["idServiceAccount"] = db_model.idServiceAccount
        return n_ser_acc
    except Exception as e:
        print(e)
        db.rollback()
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid ID passed"})
    finally:
        db.close()


def new_service_schedule(u_id, sa_id, n_sup_sch, db):
    """
    This function creates a new Supply Schedule. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sa_id: It is a function parameters that is of integer type, it provides the Service account id.
    :param n_sup_sch: It is function parameter that is of a Pydantic class object, It takes member data for creation of new Supplier Schedule.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        n_sup_sch = dict(n_sup_sch)
        n_sup_sch["serviceAccountID"] = sa_id
        n_sup_sch["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # supplying dict as a keyword args to the ServiceSchedule Model
        db_model = model.ServiceProviderSchedule(**n_sup_sch)
        db.add(db_model)
        db.commit()
        return n_sup_sch
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid ID passed"})
    finally:
        db.close()


def new_account_cost_allocation(u_id, sa_id, n_acc_cos_aln, db):
    """
    This function creates a new Account Cost Allocation. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sa_id: It is a function parameters that is of integer type, it provides the Service account id.
    :param n_acc_cos_aln: It is function parameter that is of a Pydantic class object, It takes member data for creation of new AccountCostAllocation.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # looping through list
        percentage = 0.0
        validation_skip = False
        for row in n_acc_cos_aln:
            row = dict(row)
            if row["isActive_Alloc"]:
                validation_skip = True
            row["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
            row["UpdatedOn"] = row["CreatedOn"]
            row["accountID"] = sa_id
            percentage += float(row["elementFactor"])
            row = model.AccountCostAllocation(**row)
            db.add(row)
        if int(percentage) == 100 and validation_skip == False:
            db.commit()
            return {"result": "updated"}
        elif validation_skip == True:
            db.commit()
            return {"result": "updated"}
        else:
            return Response(status_code=400, headers={"ClientError": "Account cost allocation is not valid"})
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


def new_account_credentials(u_id, sa_id, n_acc_cred, db):
    """
    This function creates a new Account Cost Allocation. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sa_id: It is a function parameters that is of integer type, it provides the Service account id.
    :param n_acc_cred: It is function parameter that is of a Pydantic class object, It takes member data for creation of new credentials.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        n_acc_cred = dict(n_acc_cred)
        # have to make it dynamic to void duplicate error
        # have to check if it corresponds to the user id and service account id
        n_acc_cred["serviceProviderAccountID"] = sa_id
        n_acc_cred["userID"] = None
        n_acc_cred["crentialTypeId"] = 4
        fernet = Fernet("g-FLG74U9o68MN4YOVTt-w8QuB6fgi2p2omd6qOZtUs=")
        encMessage = fernet.encrypt(n_acc_cred["LogSecret"].encode())
        n_acc_cred["LogSecret"] = encMessage.decode("utf-8")
        n_acc_cred["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # supplying dict as a keyword args to the AccountCostAllocation Model
        db_model = model.Credentials(**n_acc_cred)
        db.add(db_model)
        db.commit()
        return n_acc_cred
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid ID passed"})
    finally:
        db.close()


def update_sp(s_id, u_ser, db):
    """
    This function updates the Supply Schedule of a given id. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param s_id: It is a function parameters that is of integer type, it provides the service Id.
    :param u_ser: It is Body parameter that is of a Pydantic class object, It takes member data for updating of new Service.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # have to check if it corresponds to the user id and s_id
        u_ser = dict(u_ser)
        # u_ser["createdBy"] = u_id
        for item_key in u_ser.copy():
            # pop out elements that are not having any value
            if not u_ser[item_key]:
                u_ser.pop(item_key)
        # creating a sql stmt for update
        db.query(model.ServiceProvider).filter(model.ServiceProvider.idServiceProvider == s_id).update(u_ser)
        db.commit()
        return {"result": "Updated", "record": u_ser}
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid ID passed"})
    finally:
        db.close()


def update_sp_account(u_id, sa_id, u_sp_acc, db):
    """
    This function updates the Account Cost Allocation of a given id. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sa_id: It is a function parameters that is of integer type, it provides the serviceaccount id.
    :param u_sp_acc: It is function parameter that is of a Pydantic class object, It takes member data for updating of new account.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # have to check if it corresponds to the user id and sa_id
        u_sp_acc = dict(u_sp_acc)
        db.query(model.ServiceAccount).filter(model.ServiceAccount.idServiceAccount == sa_id).update(u_sp_acc)
        db.commit()
        return u_sp_acc
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid ID passed"})
    finally:
        db.close()


def update_account_cost_allocation(u_id, ca_id, u_acc_cos_aln, db):
    """
    This function updates the Account Cost Allocation of a given id. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param ca_id: It is a function parameters that is of integer type, it provides the cost allocation id.
    :param u_acc_cos_aln: It is function parameter that is of a Pydantic class object, It takes member data for updating of new AccountCostAllocation.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        created_on = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        # looping through list
        percentage = 0.0
        validation_skip = False
        for row in u_acc_cos_aln:
            row = dict(row)
            if row["isActive_Alloc"]:
                validation_skip = True
            # if existing row
            if row["idAccountCostAllocation"]:
                row["UpdatedOn"] = created_on
                percentage += float(row["elementFactor"])
                db.query(model.AccountCostAllocation).filter_by(
                    idAccountCostAllocation=row["idAccountCostAllocation"]).update(row)
            else:
                row.pop("idAccountCostAllocation")
                row["CreatedOn"] = created_on
                row["accountID"] = ca_id
                percentage += float(row["elementFactor"])
                row = model.AccountCostAllocation(**row)
                db.add(row)
        if int(percentage) == 100 and validation_skip == False:
            db.commit()
            return {"result": "updated"}
        elif validation_skip == True:
            db.commit()
            return {"result": "updated"}
        else:
            return Response(status_code=400, headers={"ClientError": "Account cost allocation is not valid"})
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


def update_credentials(u_id, acc_id, u_acc_cred, db):
    """
    This function updates the Account Cost Allocation of a given id. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param ca_id: It is a function parameters that is of integer type, it provides the cost allocation id.
    :param u_acc_cos_aln: It is function parameter that is of a Pydantic class object, It takes member data for updating of new AccountCostAllocation.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # have to check if it corresponds to the user id and ca_id
        u_acc_cred = dict(u_acc_cred)
        fernet = Fernet("g-FLG74U9o68MN4YOVTt-w8QuB6fgi2p2omd6qOZtUs=")
        encMessage = fernet.encrypt(u_acc_cred["LogSecret"].encode())
        # check if the password is same before update
        passwd = db.query(model.Credentials.LogSecret).filter(
            model.Credentials.serviceProviderAccountID == acc_id).filter(model.Credentials.crentialTypeId == 4).scalar()
        if u_acc_cred["LogSecret"] != passwd:
            u_acc_cred["LogSecret"] = encMessage.decode("utf-8")
        else:
            # don't update password if matching
            u_acc_cred.pop("LogSecret")
        db.query(model.Credentials).filter(
            model.Credentials.serviceProviderAccountID == acc_id).filter(model.Credentials.crentialTypeId == 4).update(
            u_acc_cred)
        db.commit()
        return u_acc_cred
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


def update_supply_schedule(u_id, sc_id, u_sp_sch, db):
    """
    This function updates the Supply Schedule of a given id. It contains 4 parameters.
    :param u_id: It is a function parameters that is of integer type, it provides the user Id.
    :param sc_id: It is a function parameters that is of integer type, it provides the supplier schedule Id.
    :param u_sup_sch: It is function parameter that is of a Pydantic class object, It takes member data for updating of new Supplier Schedule.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return a result of dictionary type.
    """
    try:
        # have to check if it corresponds to the user id and sc_id
        u_sp_sch = dict(u_sp_sch)
        db.query(model.ServiceProviderSchedule).filter(model.ServiceProviderSchedule.serviceAccountID == sc_id).update(
            u_sp_sch)
        db.commit()
        return u_sp_sch
    except Exception as e:
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def readserviceprovider(u_id, db):
    """
     This function read service provider list. It contains 1 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        # get active entites of the user
        ent_ids = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1)
        return db.query(model.ServiceProvider, model.Entity).options(
            Load(model.ServiceProvider).load_only("ServiceProviderName", "ServiceProviderCode", "LocationCode"),
            Load(model.Entity).load_only("EntityName")).filter(model.ServiceProvider.entityID.in_(ent_ids)).filter(
            model.ServiceProvider.entityID == model.Entity.idEntity).all()
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readspbyuid(u_id, sp_type, db, off_limit, api_filter):
    """
     This function read a Service Provider. It contains 1 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        # case statement for onboarding status
        onboarding_status = case(
            [
                (model.DocumentModel.modelStatus.in_((2, 3, 4, 5)), "Onboarded"),
                (model.DocumentModel.idDocumentModel.is_(None), "Not-Onboarded")
            ]
            , else_='Not-Onboarded'
        ).label("OnboardedStatus")
        sub_query1 = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        ven_id = db.query(model.ServiceAccount.serviceProviderID).filter(
            model.ServiceAccount.entityID.in_(sub_query1)).distinct()
        data = db.query(model.ServiceProvider, model.Entity, onboarding_status).options(
            Load(model.ServiceProvider).load_only("ServiceProviderName", "ServiceProviderCode"),
            Load(model.Entity).load_only("EntityName")).filter(
            model.ServiceProvider.entityID == model.Entity.idEntity).join(model.ServiceAccount,
            model.ServiceProvider.idServiceProvider == model.ServiceAccount.serviceProviderID).join(model.DocumentModel,
                                                                        model.DocumentModel.idServiceAccount == model.ServiceAccount.idServiceAccount,
                                                                        isouter=True).filter(
            model.ServiceProvider.idServiceProvider.in_(ven_id))
        for key, val in api_filter.items():
            if key == "ent_id" and val:
                data = data.filter(model.Entity.idEntity == val)
            if key == "ven_code" and val:
                data = data.filter(model.ServiceProvider.ServiceProviderName.like(f"%{val}%"))
            if key == "onb_status" and val:
                if val == "Onboarded":
                    data = data.filter(model.DocumentModel.modelStatus.in_((2, 3, 4, 5)))
                if val == "Not-Onboarded":
                    data = data.filter((model.DocumentModel.idDocumentModel.is_(
                        None) | model.DocumentModel.modelStatus.not_in((2, 3, 4, 5))))
        off_val = (off_limit[0] - 1) * off_limit[1]
        if off_val < 0:
            return Response(status_code=403, headers={"ClientError": "please provide right offset value"})
        return data.limit(off_limit[1]).offset(off_val).distinct().all()
    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV", "ServiceProviderCrud.py readspbyuid", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})

async def readserviceproviderbyid(db: Session, sp_id: int):
    """
     This function read a service provider details. It contains 2 parameter.
    :param sp_ID: It is a function parameters that is of integer type, it provides the service provider Id.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        return db.query(model.ServiceProvider).filter(model.ServiceProvider.idServiceProvider == sp_id).all()
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readserviceprovideraccount(u_id, sp_id, db):
    """
     This function read a service provider account. It contains 2 parameter.
    :param sp_id: It is a function parameters that is of integer type, it provides the service provider Id.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        sub_query = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        data = db.query(model.ServiceAccount, model.Entity, model.Credentials).filter(
            model.ServiceAccount.serviceProviderID == sp_id).filter(
            model.ServiceAccount.entityID == model.Entity.idEntity).filter(
            model.ServiceAccount.idServiceAccount == model.Credentials.serviceProviderAccountID).filter(
            model.ServiceAccount.entityID.in_(sub_query)).all()
        # may be required later
        # .join(model.EntityBody,
        #             model.ServiceAccount.entityBodyID == model.EntityBody.idEntityBody, isouter=True)
        # .options(
        #     Load(model.Entity).load_only("idEntity", "EntityName"),
        #     Load(model.Credentials).load_only("idEntity", "EntityName"))
        for row in data:
            acc_cost_allo = db.query(model.AccountCostAllocation, model.Department).filter(
                model.AccountCostAllocation.accountID == row[0].idServiceAccount).join(model.Department,
                                                                                       model.AccountCostAllocation.departmentID == model.Department.idDepartment,
                                                                                       isouter=True).all()
            try:
                acc_schedule_dates = db.query(model.ServiceProviderSchedule).options(
                    load_only("ScheduleDateTime")).filter(
                    model.ServiceProviderSchedule.serviceAccountID == row[0].idServiceAccount).one()
                setattr(row[0], "account_cost", acc_cost_allo)
                setattr(row[0], "account_schedule", acc_schedule_dates)
            except Exception as e:
                setattr(row[0], "account_cost", [])
                setattr(row[0], "account_schedule", [])
        return data
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def trigger_service_batch(u_id, tbody, bg_task, db):
    try:
        CreatedOn = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        cid = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
        trigger_data = db.query(model.GeneralConfig.serviceBatchConf).filter(
            model.GeneralConfig.customerID == cid).scalar()
        unique_id = str(uuid.uuid4())
        if trigger_data["isTriggerActive"] == 1 and trigger_data["isRunning"] == 0:
            tbody = dict(tbody)
            tbody["user_id"] = u_id
            tbody["uniq_id"] = unique_id
            req_data = requests.post(url=trigger_data["scheduleUrl"], json=tbody)
            if req_data.status_code == 202:
                trigger_data["isRunning"] = 1
                batch_hist = {"started_by": u_id, "entityID": tbody["entity_ids"][0], "status": "Started Running",
                              "uniqueID": unique_id, "started_on": CreatedOn}
                db.add(model.BatchTriggerHistory(**batch_hist))
                db.query(model.GeneralConfig).filter(model.GeneralConfig.customerID == cid).update(
                    {"serviceBatchConf": trigger_data})
                db.commit()
                try:
                    ############ start of notification trigger #############
                    # getting recipients for sending notification
                    # filter based on role if added
                    role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(notificationTypeID=4,
                                                                                            updated_by=1).distinct().scalar()
                    # getting recipients for sending notification
                    recepients = db.query(model.AccessPermission.userID).filter(
                        model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                    recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                          model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                        model.User.isActive == 1).all()
                    user_ids, *email = zip(*list(recepients))
                    # just format update
                    email_ids = list(zip(email[0], email[1], email[2]))
                    cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                    details = {"user_id": None, "trigger_code": 8000, "cust_id": cust_id, "inv_id": None,
                               "additional_details": {"subject": "Batch Process Start", "created_on": CreatedOn,
                                                      "recipients": email_ids}}
                    bg_task.add_task(meta_data_publisher, details)
                    ############ End of notification trigger #############
                except Exception as e:
                    print("notification exception", e)
                return {"result": "trigger call successful"}
            else:
                return Response(status_code=400,
                                headers={"error": "Please contact the Serina Team"})
        elif trigger_data["isTriggerActive"] == 1 and trigger_data["isRunning"] == 1:
            tbody = dict(tbody)
            tbody["user_id"] = u_id
            tbody["uniq_id"] = unique_id
            bg_task.add_task(meta_data_scheduler, tbody)
            batch_hist = {"started_by": u_id, "entityID": tbody["entity_ids"][0], "status": "Batch Queued",
                          "uniqueID": unique_id, "started_on": CreatedOn}
            db.add(model.BatchTriggerHistory(**batch_hist))
            db.commit()
            return {"result": "Batch Process has been Queued"}
        elif trigger_data["isTriggerActive "] == 0:
            return {"result": "request the Admin to enable the trigger"}
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def read_sbatch_history(u_id, db):
    try:
        ent_ids = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        data = db.query(model.BatchTriggerHistory, model.Entity.EntityName,
                        func.concat(model.User.firstName, " ", model.User.lastName).label("startedby")).options(
            Load(model.BatchTriggerHistory).load_only("status", "started_on", "compeleted_on")).filter(
            model.BatchTriggerHistory.batchProcessType == 1).filter(
            model.BatchTriggerHistory.entityID == model.Entity.idEntity).filter(
            model.BatchTriggerHistory.started_by == model.User.idUser).filter(
            model.BatchTriggerHistory.entityID.in_(ent_ids)).all()
        return {"result": data}
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})


async def upload_cost_allocation(u_id, file, db):
    try:
        local_file_name = datetime.now(tz_region).strftime("%b-%Y")
        local_file_name = f"Etisalat {local_file_name}.xlsx"
        con_str = db.query(model.FRConfiguration.ConnectionString).filter_by(idFrConfigurations=1).scalar()
        blob_service_client = BlobServiceClient.from_connection_string(con_str)
        blob_client = blob_service_client.get_blob_client(container=container_name,
                                                          blob=local_file_name)
        data = await file.read()
        try:
            blob_client.upload_blob(data)
        except Exception as e:
            blob_client.delete_blob()
            blob_client.upload_blob(data)
        upload_date = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        cost_alloc = model.AgiCostAlloc(
            **{"filename": local_file_name, "uploaded_by": u_id, "uploadeddate": upload_date})
        db.add(cost_alloc)
        db.commit()
        return {"result": "file uploaded"}
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})


def remove_file(path: str) -> None:
    os.unlink(path)


async def download_cost_allocation(u_id, filename, bg_task, db):
    try:
        con_str = db.query(model.FRConfiguration.ConnectionString).filter_by(idFrConfigurations=1).scalar()
        blob_service_client = BlobServiceClient.from_connection_string(con_str)
        blob_client = blob_service_client.get_blob_client(container=container_name,
                                                          blob=filename)
        data = blob_client.download_blob().readall()
        data = BytesIO(data)
        # fd, path = tempfile.mkstemp(suffix='.xlsx')
        # with os.fdopen(fd, 'wb') as f:
        #     f.write(data)
        # bg_task.add_task(remove_file, path)
        return StreamingResponse(data, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # return FileResponse(path, filename=filename,
        #                     media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})


async def read_cost_allocation(u_id, db):
    try:
        data = db.query(model.AgiCostAlloc, model.User).options(
            Load(model.AgiCostAlloc).load_only("filename", "uploadeddate"),
            Load(model.User).load_only("firstName", "lastName")).filter(
            model.AgiCostAlloc.uploaded_by == model.User.idUser).order_by(
            model.AgiCostAlloc.idagicostallocation.desc()).limit(12).all()
        return {"result": data}
    except Exception as e:
        print(traceback.format_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
