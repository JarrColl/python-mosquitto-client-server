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

from subpubClass import SubPub

READ_X_SECONDS = 5
SALINITY_DROP_RATE = 5

salinity_topic = "102988098/salinity"
moisture_topic = "102988098/moisture"
sub_topics = [("public/#", 1), ("102988098/toosalty", 0), ("102988098/toodry", 0)]

cafile = "./certs/ca.crt"
username = "102988098"
password = "jarron"


def on_connect( client: Client, userdata: Any, flags: ConnectFlags, rc: ReasonCode, properties: Properties | None,
):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


def on_message(client: Client, userdata: Any, msg: MQTTMessage):
    print("hello")
    if msg.topic == "102988098/toosalty":
        if msg.payload.decode() == "0":
            userdata["pump"] = -1
        elif msg.payload.decode() == "1":
            userdata["pump"] = 1
    elif msg.topic == "102988098/toodry":
        if msg.payload.decode() == "0":
            print("Not Pumping")
            userdata["pump"] = -1
        elif msg.payload.decode() == "1":
            print("Pumping")
            userdata["pump"] = 1

    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


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
        if random.random() > 0.95:
            return 100
        else:
            return salinity
    elif direction == 1:
        return max(salinity - SALINITY_DROP_RATE, 0)


def run():
    subpub = SubPub(username, password)

    moisture = 70
    salinity = 0
    userdata: Dict[str, Literal[-1, 1]] = {"pump": -1}

    client = subpub.connect_mqtt(on_connect, cafile, userdata)
    subpub.loop_start()
    subpub.subscribe(on_message, sub_topics)

    f = 0
    # Main loop
    while True:
        f = f % READ_X_SECONDS
        if f == 0:
            moisture = generate_moisture_value(moisture, userdata["pump"])
            salinity = generate_salinity_value(salinity, userdata["pump"])
            subpub.publish(moisture_topic, f"{moisture}")
            subpub.publish(salinity_topic, f"{salinity}")
        f += 1
        time.sleep(1)


if __name__ == "__main__":
    run()
