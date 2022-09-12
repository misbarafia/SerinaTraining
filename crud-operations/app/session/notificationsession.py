import paho.mqtt.client as mqtt
import uuid
import ssl
import os

broker_site = os.getenv('Broker_Site', default='rovedev.centralindia.cloudapp.azure.com')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


ssl_context = ssl.SSLContext()
# disabling ssl verification, if want to enable have to add certificates manually along with its parameters
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
# using websocket protocol along with custom client id
client = mqtt.Client(client_id=f"serina_system_{str(uuid.uuid4())[:5]}", transport="websockets")
# setting path for websocket, as the proxy config path is set to /console
client.ws_set_options(path="/console")
# overriding default connect function to get connection status
client.on_connect = on_connect
# setting username and password to connect to the broker
client.username_pw_set(username="system", password="ExyhM32JaE93xvc7sx2TfDc9KEENK11w")
# setting the ssl context/config for secure web socket connection
client.tls_set_context(ssl_context)
try:
    client.connect(broker_site, 443, 10)
except Exception as e:
    print(e)
client.loop_start()

