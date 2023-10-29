import time
from random import randint

import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])

def connected(client):
    print("Connected to Adafruit IO!  Listening for DemoFeed changes...")
    client.subscribe("DemoFeed")


def subscribe(client, userdata, topic, granted_qos):
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def disconnected(client):
    print("Disconnected from Adafruit IO!")



def message(client, feed_id, payload):
    print("Feed {0} received new value: {1}".format(feed_id, payload))



pool = socketpool.SocketPool(wifi.radio)


mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

io = IO_MQTT(mqtt_client)

io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = message

print("Connecting to Adafruit IO...")
io.connect()

last = 0
print("Publishing a new message every 10 seconds...")
while True:
    io.loop()
    if (time.monotonic() - last) >= 10:
        value = randint(0, 100)
        print("Publishing {0} to DemoFeed.".format(value))
        io.publish("DemoFeed", value)
        last = time.monotonic()