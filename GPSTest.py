import board
import time
import busio
import adafruit_gps
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from ideaboard import IdeaBoard

from adafruit_io.adafruit_io import IO_MQTT

IdSensor = 1
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

ib = IdeaBoard()
uart = busio.UART(board.IO22,board.IO21, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b"PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")


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

last_print = time.monotonic()
while True:

    gps.update()
    # Verificar si hay un fix en el GPS
    current = time.monotonic()
    if current - last_print >= 3.0:
        last_print = current
        if not gps.has_fix:
            # Intentar hasta encontrara una señal
            print("Esperando por un fix...")
            continue
        # Se encontro un fix
        print("=" * 40) 
        print(
            "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,
                gps.timestamp_utc.tm_mday,
                gps.timestamp_utc.tm_year,
                gps.timestamp_utc.tm_hour,
                gps.timestamp_utc.tm_min,
                gps.timestamp_utc.tm_sec,
            )
        )
        print("Latitude: {0:.6f} degrees".format(gps.latitude))
        LatitudeV = gps.latitude
        print("Longitude: {0:.6f} degrees".format(gps.longitude))
        LongitudeV = gps.latitude
        print(
            "Precise Latitude: {:2.}{:2.4f} degrees".format(
                gps.latitude_degrees, gps.latitude_minutes
            )
        )
        print(
            "Precise Longitude: {:2.}{:2.4f} degrees".format(
                gps.longitude_degrees, gps.longitude_minutes
            )
        )
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
        
        value = [LatitudeV,LongitudeV,IdSensor]
        io.publish("DemoFeed", value)


        
        
        
        
        

