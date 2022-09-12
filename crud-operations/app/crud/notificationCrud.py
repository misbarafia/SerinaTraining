from pyexpat import model
from fastapi.applications import FastAPI
from fastapi.responses import Response
from sqlalchemy.sql import select, update, delete, func
from sqlalchemy import and_, or_, not_, exc
import os
import sys

sys.path.append("..")
from logModule import applicationlogging
from random import randrange
from string import Template
from datetime import datetime, timedelta
import pytz as tz
import model as models
from sqlalchemy.orm import join, load_only, Load
import traceback
import json
from session.notificationsession import client as mqtt


tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


async def get_notifications_recipients(u_id, nty_id, ent_id, db):
    """
    This function fetches default and custom notification templates for a User in the db. It contains 2 parameters.
    :param userID: Unique indetifier used to indentify a user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns notification template lists
    """
    try:
        # getting all the notification type recpients based on entity.
        data = db.query(models.NotificationCategoryRecipient).options(
            load_only("isDefaultRecepients", "entityID", "notificationTypeID", "notificationrecipient")).filter_by(
            notificationTypeID=nty_id, entityID=ent_id).all()
        return {"result" :data}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py get_notifications_template", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def mark_notifications(userID, nt_id, db):
    """
    This function marks the seen notification of a user. it contains 3 parameters.
    :param userID: Unique indetifier used to indentify a user.
    :param nt_id: Unique indetifier used to indentify a notification.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a status dict.
    """
    try:
        filter_dict = {"userID": userID}
        # if specific notification marked otherwise delete all notification
        if nt_id:
            filter_dict["idPullNotification"] = nt_id
        db.query(models.PullNotification).filter_by(**filter_dict).delete()
        db.commit()
        return {"result", "marked"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py mark_notifications", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def reset_notification_template(userID, ntt_id, db):
    """
    This function resets the notification with the default data. It contains 3 parameters.
    :param userID: Unique indetifier used to indentify a user.
    :param ntt_id: Unique indetifier used to indentify a notification template.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a status dict.
    """
    try:
        # resetting notification template to default values, by marking custom template as deleted.
        is_template_present = db.query(models.CustomPullNotificationTemplate).filter_by(
            pullnotificationTemplateID=ntt_id, userID=userID, isDeleted=0).update({"isDeleted": 1})
        if is_template_present == 1:
            db.commit()
            return {"success", "reset"}
        return {"result": "failed"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py reset_notification_template", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def update_notification_recipients(u_id, nty_id, ent_id, ntr_bdy, db):
    """
    This function updates existing or creates a custom notification template if it does not exists. It has 4 paramtrs.
    :param userID: Unique indetifier used to indentify a user.
    :param ntt_id: Unique indetifier used to indentify a notification template.
    :param ntt_bdy: contains notification template body items.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a status dict.
    """
    try:
        ntt_bdy = dict(ntr_bdy)
        isdefault = ntt_bdy.pop("isDefaultRecepients")
        db.query(models.NotificationCategoryRecipient).filter_by(
            notificationTypeID=nty_id, entityID=ent_id).update(
            {"isDefaultRecepients": isdefault, "notificationrecipient": ntt_bdy})
        db.commit()
        return {"success", "updated"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py update_notification_template", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


# async def get_template_tags(userID, db):
#     try:
#         tags = db.query(models.TemplateTags).options(load_only("tag_name", "tag_value", "tag_description")).all()
#         return tags
#     except Exception as e:
#         print(traceback.print_exc())
#         return Response(status_code=500, headers={"Error": "Server error"})
#     finally:
#         db.close()


async def setnotification(userID, ntt_id, values, db):
    """

    :param userID:
    :param ntt_id:
    :param values:
    :param db:
    :return:
    """
    try:
        try:
            # first checking if there is a custom notification template for the user
            cntt_data = db.query(models.CustomPullNotificationTemplate).filter_by(pullnotificationTemplateID=ntt_id,
                                                                                  userID=userID, isDeleted=0).options(
                load_only('templateMessage', 'notificationTypeID', 'notificationPriorityID', 'notification_on_off',
                          'rhythm')).one()
            # check if the user has turned of the notification
            if cntt_data.notification_on_off == 0:
                return False
        except Exception as ex:
            applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py get_notifications_template", str(ex))
            # creating from default template if no custom template exist for user
            cntt_data = db.query(models.PullNotificationTemplate).filter_by(idPullNotificationTemplate=ntt_id).options(
                load_only('templateMessage', 'notificationTypeID', 'notificationPriorityID',
                          'rhythm')).one()
        msg = Template(cntt_data.templateMessage).safe_substitute(values)
        temp = {}
        temp["userID"] = userID
        temp["notificationPriorityID"] = cntt_data.notificationPriorityID
        temp["notificationTypeID"] = cntt_data.notificationTypeID
        temp["notificationMessage"] = msg
        temp["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.now(tz_region)
        now = now + timedelta(minutes=int(cntt_data.rhythm))
        temp["delayby"] = now.strftime("%Y-%m-%d %H:%M:%S")
        notmsg = models.PullNotification(**temp)
        db.add(notmsg)
        db.commit()
        return True
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py setnotification", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


async def getrecepients(u_id, ent_id, db):
    """
    :param userID:
    :param db:
    :return:
    """
    try:
        user_ids = db.query(models.UserAccess.UserID).filter_by(EntityID=ent_id).distinct()
        inv_users = db.query(models.User.email).filter(models.User.idUser.in_(user_ids)).all()
        group_users = db.query(models.AccessPermissionDef).options(load_only("NameOfRole")).all()
        users = {"individual_users": inv_users, "group_users": group_users}
        return users
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "notificationCrud.py getrecepients", str(e))
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()
