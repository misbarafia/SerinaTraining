import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.orm import join, load_only
import paho.mqtt.client as mqtt
from pytz import utc
import jwt
import re
import uuid
from sqlalchemy.orm import Session
from queue import PriorityQueue, Queue
from threading import Thread
import os
import json
import asyncio
from datetime import datetime, timedelta
import jinja2
import model
from session import Session
import nest_asyncio
import Pyro5.api

client = mqtt.Client(client_id=f"serina_system_1001", transport="websockets")
nest_asyncio.apply()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

broker_site = os.getenv('Broker_Site', default='rovedev.centralindia.cloudapp.azure.com')



def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()


# notification queue
waited_notification = []
mail_safe_queue = Queue(maxsize=0)
executed_notification = {}

# thread and process pool executors
executors = {
    'default': ThreadPoolExecutor(4),
    # 'processpool': ProcessPoolExecutor(2)
}

# job conf
job_defaults = {
    'coalesce': False,
    'max_instances': 1,
    'misfire_grace_time': 600,
}

# Scheduler instance
scheduler = BackgroundScheduler(executors=executors,
                                job_defaults=job_defaults, timezone=utc, daemonic=False)
# starting scheduler
scheduler.start()


# job event listener
def job_status_listener(event):
    if event.job_id in executed_notification.keys():
        executed_notification.pop(event.job_id)
        print(f'job id {event.job_id} executed and removed from execution queue with {event.exception} exception')
    if event.exception:
        print(event.traceback)


# job event listener
scheduler.add_listener(job_status_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

# template loader

templateLoader = jinja2.FileSystemLoader(searchpath="./html_templates")
templateEnv = jinja2.Environment(loader=templateLoader)


# to get invoice values
def invoice_meta_data(inv_id, db):
    try:
        values = db.query(model.Document).options(load_only("docheaderID", "documentDate", "PODocumentID")).filter_by(
            idDocument=inv_id).one()
        return {"docheaderID": values.docheaderID if values.docheaderID else "",
                "documentDate": values.documentDate if values.documentDate else "",
                "PODocumentID": values.PODocumentID if values.PODocumentID else ""}
    except Exception as e:
        pass


# to get model id meta data:
# def model_meta_data(inv_id, db):

# to get Vendor Details
def vendor_meta_data(inv_id, db):
    try:
        ven_acc_id = db.query(model.Document.vendorAccountID).filter_by(idDocument=inv_id).scalar()
        ven_id = db.query(model.VendorAccount.vendorID).filter_by(idVendorAccount=ven_acc_id).scalar()
        ven_name = db.query(model.Vendor.VendorName).filter_by(idVendor=ven_id).scalar()
        return {"Vendor_Name": ven_name if ven_name else ""}
    except Exception as e:
        print(traceback.format_exc())


# to get name of the user
def user_name(u_id, db):
    try:
        values = db.query(model.User.firstName, model.User.lastName).filter(
            model.User.idUser == u_id).one()
        return {"firstName": values.firstName if values.firstName else "",
                "lastName": values.lastName if values.lastName else ""}
    except Exception as e:
        pass


def template_render_values(template, kwargs):
    db: Session = next(get_db())
    template_tag_values = {}
    tags_in_template = re.compile(r"{{\s(.*?)\s}}")
    tags_in_template = tags_in_template.findall(template)
    for tag in tags_in_template:
        if tag in ["docheaderID", "documentDate", "PODocumentID"] and kwargs["inv_id"]:
            template_tag_values.update(invoice_meta_data(kwargs["inv_id"], db))
            template_tag_values.update(vendor_meta_data(kwargs["inv_id"], db))
        if tag == "VendorName" and kwargs["additional_details"]:
            if "vendorID" in kwargs["additional_details"].keys():
                template_tag_values.update(invoice_meta_data(kwargs["additional_details"]["vendorID"], db))
        if tag in ["firstName", "lastName"]:
            if kwargs['user_id']:
                template_tag_values.update(user_name(kwargs['user_id'], db))
    return template_tag_values


def send_notification(template_data, mq_client, kwargs):
    try:
        addon_details = {}
        current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db: Session = next(get_db())
        if kwargs['additional_details']:
            addon_details = kwargs['additional_details']
        template_data = db.query(model.PullNotificationTemplate.templateMessage,
                                 model.PullNotificationTemplate.notificationPriorityID,
                                 model.PullNotificationTemplate.notificationTypeID).filter_by(
            triggerDescriptionID=kwargs['idTriggerDescription'], notificationCategory=1, notification_on_off=1,
            customerID=kwargs["cust_id"]).one()
        template_message = template_data.templateMessage
        template_tags = template_render_values(template_message, kwargs)
        if template_tags:
            addon_details.update(template_tags)
        template = templateEnv.from_string(template_data.templateMessage)
        template_message = template.render(**addon_details)
        user_notification = {"userID": None, "notificationPriorityID": template_data.notificationPriorityID,
                             "notificationTypeID": template_data.notificationTypeID,
                             "notificationMessage": template_message, "CreatedOn": current_datetime}
        if kwargs['user_id']:
            user_topic = db.query(model.Acl.topicName, model.Acl.userID).filter_by(rw=1).filter(
                model.Acl.userID.in_(kwargs['user_id'])).distinct().all()
            for row in user_topic:
                user_notification["userID"] = row[1]
                user_notification_data = model.PullNotification(**user_notification)
                db.add(user_notification_data)
                try:
                    mq_client.publish(row[0], json.dumps(user_notification), qos=2, retain=True)
                except:
                    pass
        db.commit()
    except Exception as e:
        print(traceback.format_exc())


def email_processor(template_data, mq_client, kwargs):
    try:
        message = MessageSchema(
            subject='',
            recipients=[],
            body="",
            subtype="html",
            cc=[]
        )
        email_secret = "9joxN0XD3jyowKdMALUO1ayOWve9bdS1"
        encoded_data = ''
        if kwargs["additional_details"]:
            addon_details = kwargs["additional_details"]
            if addon_details is not None and "subject" in addon_details.keys():
                message.subject = addon_details["subject"]
            if addon_details is not None and "recipients" in addon_details.keys():
                if type(addon_details["recipients"]) == str:
                    message.recipients.append(addon_details["recipients"])
                else:
                    message.recipients.extend(addon_details["recipients"])
            if addon_details is not None and "user_details" in addon_details.keys():
                addon_details["user_details"]["exp_date"] = datetime.utcnow() + timedelta(days=1)
                addon_details["user_details"]["exp_date"] = addon_details["user_details"]["exp_date"].strftime(
                    "%Y-%m-%d")
                encoded_data = jwt.encode(addon_details["user_details"], email_secret,
                                          algorithm="HS256")
                addon_details.update(addon_details.pop("user_details"))
            if addon_details is not None and "endpoint_url" in addon_details.keys():
                if type(addon_details["endpoint_url"]) != str:
                    for key, url in addon_details.pop("endpoint_url").items():
                        addon_details[key] = url + encoded_data
                else:
                    addon_details["endpoint_url"] = addon_details["endpoint_url"] + encoded_data
        template_sub_html = templateEnv.from_string(template_data.templateMessage)
        template_heading_html = templateEnv.from_string(template_data.templateHeading)
        template_tags = template_render_values(template_data.templateMessage, kwargs)
        if template_tags:
            addon_details.update(template_tags)
        for recipient in message.recipients.copy():
            # in case recipients are coming from db, set username in template using db values
            message.recipients.clear()
            try:
                if type(recipient) == tuple or type(recipient) == list:
                    message.recipients.append(recipient[0])
                    addon_details["firstName"] = recipient[1] if recipient[1] else ""
                    addon_details["lastName"] = recipient[2] if recipient[2] else ""
                if type(recipient[0]) == tuple:
                    message.recipients.append(recipient[0][0])
                    addon_details["firstName"] = recipient[0][1] if recipient[0][1] else ""
                    addon_details["lastName"] = recipient[0][2] if recipient[0][2] else ""
                if type(recipient) == str:
                    message.recipients.append(recipient)
            except Exception as e:
                print(e)
            heading_html = template_heading_html.render(**addon_details)
            sub_html = template_sub_html.render(**addon_details)
            main_html_template = templateEnv.get_template("mail_notification.html")

            output_text = main_html_template.render(heading_html=heading_html, sub_html=sub_html)
            try:
                mq_client.publish("email_queue", json.dumps(
                {"subject": message.subject, "recipients": message.recipients, "cc": message.cc, "html": output_text}), qos=2,
                              retain=True)
            except:
                pass
    except Exception as e:
        print(traceback.format_exc())


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# worker thread for processing new notification
def notification_processor(mqtt_client, msg):
    db: Session = next(get_db())
    notification_template = db.query(model.PullNotificationTemplate).options(
        load_only('templateHeading', 'templateMessage', 'notificationTypeID', 'notificationCategory')).filter_by(
        customerID=msg["cust_id"],
        notification_on_off=1,
        triggerDescriptionID=msg["idTriggerDescription"])
    for template in notification_template.all():
        if template.notificationCategory == 2:
            Thread(target=email_processor, args=(template, mqtt_client, msg), daemon=False).start()
        if template.notificationCategory == 1:
            Thread(target=send_notification, args=(template, mqtt_client, msg), daemon=False).start()


def erp_invoice_updates():
    try:
        db: Session = next(get_db())
        now_date_time = datetime.utcnow()
        past_date_time = now_date_time - timedelta(minutes=15)
        msg = {"user_id": None, "idTriggerDescription": None,
               "trigger_code": None, "cust_id": None, "inv_id": None,
               "additional_details": {"recipients": None,
                                      "subject": None}}
        invoices = db.query(model.Document).options(
            load_only("entityID", "documentStatusID", "documentDate", "CreatedOn")).filter_by(
            idDocumentType=3).filter(model.Document.documentStatusID == 14).filter(
            model.Document.CreatedOn.between(past_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                             now_date_time.strftime("%Y-%m-%d %H:%M:%S"))).all()
        for row in invoices:
            cust_id = db.query(model.Entity.customerID).filter_by(idEntity=row.entityID).scalar()
            # get the related entity of Invoice and get the recipients
            # role based selection
            user_ids = db.query(model.NotificationCategoryRecipient).filter()
            # recepient1 = db.query(model.UserAccess.UserID).filter_by(EntityID=row.entityID, isActive=1).distinct()
            ven_acc_id = db.query(model.Document.vendorAccountID).filter_by(idDocument=row.idDocument).scalar()
            recepient2 = db.query(model.VendorUserAccess.vendorUserID).filter_by(isActive=1,
                                                                                  vendorAccountID=ven_acc_id).distinct()
            recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                  model.User.lastName).filter(
                 model.User.idUser.in_(recepient2)).all()
            user_ids, *email = zip(*list(recepients))
            email_ids = list(zip(email[0], email[1], email[2]))
            msg["user_id"] = user_ids
            msg["idTriggerDescription"] = 64
            msg["trigger_code"] = 8029
            msg["cust_id"] = cust_id
            msg["inv_id"] = row.idDocument
            msg["additional_details"]["recipients"] = email_ids
            msg["additional_details"]["subject"] = "Invoice Posted in ERP"
            notification_processor(client, msg.copy())
    except Exception as e:
        pass


if __name__ == '__main__':
    import ssl
    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client.ws_set_options(path="/console")
    client.on_connect = on_connect
    scheduler.add_job(erp_invoice_updates, 'interval', minutes=15)
    scheduler.add_listener(job_status_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    client.username_pw_set("notification_worker_1", "ExyhM32JaE93xvc7sx2TfDc9KEENK11w")
    client.tls_set_context(ssl_context)
    client.connect(broker_site, 443, 10)
    client.loop_forever()
