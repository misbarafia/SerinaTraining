import Pyro5.api
import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
import json
import asyncio
import model
from session import Session
import nest_asyncio

broker_site = os.getenv('Broker_Site', default='rovedev.centralindia.cloudapp.azure.com')
nest_asyncio.apply()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

email_queue = []
service_batch_queue = []
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
client = mqtt.Client(client_id=f"serina_system_1006", transport="websockets")


def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()


class Mail_Sender:
    def __init__(self):
        pass
        conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME",default="serinaplus.dev@datasemantics.co"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD",default="ravager55@rocket"),
            MAIL_FROM=os.getenv("MAIL_FROM",default="serinaplus.dev@datasemantics.co"),
            MAIL_PORT=587,
            MAIL_SERVER="smtp-mail.outlook.com",
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True
            # TEMPLATE_FOLDER="serina_email/assets",
        )

        self.fm = FastMail(conf)


mail = Mail_Sender()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    MQTT_TOPIC = [("email_queue", 0), ("service_batch_queue", 0), ("vendor_batch_queue", 0)]
    client.subscribe(MQTT_TOPIC)


def send_mail():
    try:
        for x in range(3):
            if len(email_queue) > 0:
                loop.run_until_complete(mail.fm.send_message(email_queue.pop()))
    except Exception as e:
        pass


def send_service_to_batch(client):
    try:
        if len(service_batch_queue):
            print("batch entered")
            tbody = service_batch_queue[0]
            db: Session = next(get_db())
            cid = db.query(model.User.customerID).filter_by(idUser=tbody["user_id"]).scalar()
            trigger_data = db.query(model.GeneralConfig.serviceBatchConf).filter(
                model.GeneralConfig.customerID == cid).scalar()
            if trigger_data["isRunning"] == 0:
                service_batch_queue.pop()
                req_data = requests.post(url=trigger_data["scheduleUrl"], json=tbody)
                if req_data.status_code == 202:
                    trigger_data["isRunning"] = 1
                    db.query(model.BatchTriggerHistory).filter_by(uniqueID=tbody["uniq_id"]).update(
                        {"status": "Started Running"})
                    db.query(model.GeneralConfig).filter(model.GeneralConfig.customerID == cid).update(
                        {"serviceBatchConf": trigger_data})
                    db.commit()
                    ############ start of notification trigger #############
                    # getting recipients for sending notification
                    # filter based on role if added
                    role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(
                        notificationTypeID=4, updated_by=1).distinct().scalar()
                    # getting recipients for sending notification
                    recepients = db.query(model.AccessPermission.userID).filter(
                        model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                    recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                          model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                        model.User.isActive == 1).all()
                    user_ids, *email = zip(*list(recepients))
                    # just format update
                    email_ids = list(zip(email[0], email[1], email[2]))
                    details = {"user_id": None, "trigger_code": 8000, "cust_id": 1, "inv_id": None,
                               "additional_details": {"subject": "Batch Process Start", "recipients": email_ids}}
                    client.publish("notification_processor", json.dumps(details), qos=2, retain=True)
                    ############ End of notification trigger #############
                    # return {"result": "trigger call successful"}
                else:
                    print("trigger failed")
    except Exception as e:
        print(e)


scheduler.start()
job = scheduler.add_job(send_mail, 'interval', seconds=1)
job = scheduler.add_job(send_service_to_batch, 'interval', args=([client]), minutes=5)


# The callback for when a PUBLISH message is received from the server.
def job_queue(client, userdata, msg):
    if msg.retain != 1:
        if msg.topic == "email_queue":
            msg = json.loads(str(msg.payload.decode("utf-8")))
            try:
                if msg["cc"] is not None and type(msg["cc"]) == list:
                    # msg["cc"].append("serina.dev@datasemantics.co")
                    pass
                else:
                    # msg["cc"] = ["serina.dev@datasemantics.co"]
                    msg["cc"] = []
            except Exception as e:
                msg["cc"] = [os.getenv("MAIL_USERNAME",default="serinaplus.dev@datasemantics.co")]
            try:
                message = MessageSchema(
                    **msg,
                    body="",
                    subtype="html"
                )
                email_queue.append(message)
            except Exception as e:
                print(msg, e)
        elif msg.topic == "service_batch_queue":
            try:
                msg = json.loads(str(msg.payload.decode("utf-8")))
                service_batch_queue.append(msg)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    import ssl

    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client.ws_set_options(path="/console")
    client.on_connect = on_connect
    client.on_message = job_queue
    client.username_pw_set("notification_worker_3", "ExyhM32JaE93xvc7sx2TfDc9KEENK11w")
    client.tls_set_context(ssl_context)
    client.connect(broker_site, 443, 10)
    client.loop_forever()
