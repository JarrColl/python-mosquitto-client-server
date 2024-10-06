import math
import random
import sys
import time
from typing import Any, Dict, Literal

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

broker = "rule100.caia.swin.edu.au"
port = 8883
# topic = "private/mqtt"
# Generate a Client ID with the publish prefix.
client_id = f"publish-{random.randint(0, 1000)}"
username = "102988098"
password = "jarron"

CONNECT_TIMEOUT = 5
READ_X_SECONDS = 5
GOOD_MOISTURE = 80
BAD_MOISTURE = 30
SALINITY_DROP_RATE = 5

salinity_topic = "102988098/salinity"
moisture_topic = "102988098/moisture"
sub_topics = [("public/#", 1), ("102988098/toosalty", 0), ("102988098/tooddry", 0)]

cafile = "./ca.crt"


def generate_moisture_value(moisture: int, direction: Literal[-1, 1]) -> int:
    """Simulates a sensor reading the moisutre value of the soil."""
    new_moisture = round(moisture + (direction * random.random() * 5))
    if new_moisture > 100 or new_moisture < 0:
        return moisture

    moisture = new_moisture
    return new_moisture

def generate_salinity_value(salinity: int, direction: Literal[-1, 1]) -> int:
    """Simulates a sensor reading the salinity value of the soil."""
    if direction == -1:
        if random.random() > 0.75:
            return 100
    elif direction == 1:
        return salinity - SALINITY_DROP_RATE

def connect_mqtt(userdata: Any) -> Client:
    def on_connect(
        client: Client,
        userdata: Any,
        flags: ConnectFlags,
        rc: ReasonCode,
        properties: Properties | None,
    ):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(CallbackAPIVersion.VERSION2, client_id, userdata=userdata)
    client.username_pw_set(username, password)
    client.tls_set(ca_certs=cafile)

    client.on_connect = on_connect
    error_code = client.connect(broker, port)

    if error_code != MQTTErrorCode.MQTT_ERR_SUCCESS:
        raise MQTTException(
            "Client failed to connect with error code " + str(error_code) + "."
        )
    return client


def publish(client: Client, pub_topic, msg):
    result = client.publish(pub_topic, msg, qos=1)
    if result.rc == MQTTErrorCode.MQTT_ERR_SUCCESS:
        print(f"Send `{msg}` to topic `{pub_topic}`")
    else:
        print(f"Failed to send message to topic {pub_topic}")


def subscribe(client: Client):
    def on_message(client: Client, userdata: Any, msg: MQTTMessage):
        moisture_value = int(msg.payload.decode())
        
        if msg.topic == "102988098/toosalty": 
                userdata["pump"] = 1
        elif msg.topic == "102988098/toodry": 
            if msg.payload.decode() == 0:
                userdata["pump"] = -1
            elif msg.payload.decode() == 1:
                userdata["pump"] = 1

        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    error_code = client.subscribe(sub_topics)[0]
    if error_code == MQTTErrorCode.MQTT_ERR_NO_CONN:
        raise MQTTException(
            "Subscribe called while the client is not connected to a server."
        )
    client.on_message = on_message


def run():
    moisture = 70
    salinity = 0

    userdata: Dict[str, Literal[-1, 1]] = {"pump": 1}

    client = connect_mqtt()
    error_code = client.loop_start()
    error_code = client.loop_stop()
    if error_code == MQTTErrorCode.MQTT_ERR_INVAL:
        raise MQTTException(
            "Client loop stop was called but there was no running client loop on the thread."
        )

    # Wait for the connection to be acknowledged by the server before starting.
    time_waiting = 0
    while True:
        if client.is_connected():
            break
        else:
            if time_waiting >= CONNECT_TIMEOUT:
                print("Connection timed out...")
                return
            time_waiting += 0.1
            time.sleep(0.1)

    subscribe(client)

    f = 0
    # Main loop
    while True:
        f = f % READ_X_SECONDS
        if f == 0:
            moisture = generate_moisture_value(moisture, userdata["pump"])
            salinity = generate_salinity_value(salinity, userdata["pump"])
            publish(client, moisture_topic, f"{moisture}")
            publish(client, salinity_topic, f"{moisture}")
        f += 1
        time.sleep(1)


if __name__ == "__main__":
    run()
