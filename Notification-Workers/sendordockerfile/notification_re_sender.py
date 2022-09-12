import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import paho.mqtt.client as mqtt
from pytz import utc
from sqlalchemy.orm import  load_only
from sqlalchemy.orm import Session
from queue import PriorityQueue
import json
from threading import Thread
import model
from session import Session
import ssl
from datetime import datetime

# client initialization
client = mqtt.Client(client_id=f"serina_system_1008", transport="websockets")


def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()


# notification queue
waited_notification = PriorityQueue(maxsize=0)
executed_notification = {}


# Scheduler instance
scheduler = BackgroundScheduler( daemonic=False)
# starting scheduler
scheduler.start()


def resend_notification(*args):
    try:
        db: Session = next(get_db())
        user_id = json.loads(args[0])
        client_publisher = args[1]
        data = db.query(model.PullNotification).options(
            load_only("notificationPriorityID", "notificationTypeID", "notificationMessage",
                      "CreatedOn")).filter_by(userID=user_id["user_id"], isSeen=0).all()
        title = ["idPullNotification", "notificationMessage", "notificationPriorityID", "notificationTypeID",
                 "CreatedOn"]
        user_topic = db.query(model.Acl.topicName).filter_by(rw=1, userID=user_id["user_id"]).limit(1).scalar()
        msg = [
            dict(zip(title, [x.idPullNotification, x.notificationMessage, x.notificationPriorityID, x.notificationTypeID,
                            x.CreatedOn.strftime("%Y-%m-%d %H:%M:%S")]))
            for x in data]
        client_publisher.publish(user_topic, json.dumps(msg), qos=1, retain=True)
    except Exception as e:
        print(traceback.format_exc())


def queue_processor():
    while True:
        if waited_notification.not_empty:
            data = waited_notification.get()
            job = scheduler.add_job(resend_notification, args=(data))
            executed_notification[job.id] = job


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    MQTT_TOPIC = [("notification_re_sender", 0)]
    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def job_queue(client, userdata, msg):
    if msg.retain != 1:
        waited_notification.put((str(msg.payload.decode("utf-8")), client))


if __name__ == '__main__':
    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client.ws_set_options(path="/console")
    client.on_connect = on_connect
    client.on_connect = on_connect
    client.on_message = job_queue
    client.username_pw_set("notification_worker_2", "ExyhM32JaE93xvc7sx2TfDc9KEENK11w")
    client.tls_set_context(ssl_context)
    client.connect("rovedev.centralindia.cloudapp.azure.com", 443, 10)
    Thread(target=queue_processor, daemon=False).start()
    client.loop_forever()
