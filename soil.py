import random
import sys
import time
from logging import error
from typing import Any, Dict, Literal

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from subpubClass import SubPub

READ_X_SECONDS = 5
SALINITY_DROP_RATE = 8

salinity_topic = "public/salinity"
moisture_topic = "public/moisture"

toosalty_topic = "public/toosalty"
toodry_topic = "public/toodry"

stop_topic = "public/stop"


sub_topics = [("public/stop", 1), (toosalty_topic, 0), (toodry_topic, 0)]

#TODO: make them use all their own accounts
cafile = "./certs/ca.crt"
username = "soil"
password = "soil"

shutdown_flag = False


def on_connect( client: Client, userdata: Any, flags: ConnectFlags, rc: ReasonCode, properties: Properties | None,
):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


def on_message(client: Client, userdata: Any, msg: MQTTMessage):
    payload = msg.payload.decode()
    print("hello")
    if msg.topic == toosalty_topic:
        if payload == "0":
            userdata["desalinate"] = -1
        elif payload == "1":
            userdata["desalinate"] = 1
    elif msg.topic == toodry_topic:
        if payload == "0":
            print("Not Pumping")
            userdata["pump"] = -1
        elif payload == "1":
            print("Pumping")
            userdata["pump"] = 1
    elif msg.topic == "public/stop":
        if payload == "stop":
            print("Stop message sent, shutting down.")
            global shutdown_flag
            shutdown_flag = True

    print(f"Received `{payload}` from `{msg.topic}` topic")


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
            return min(salinity + 30, 100)
        else:
            return salinity
    elif direction == 1:
        return max(salinity - SALINITY_DROP_RATE, 0)


def run():
    global shutdown_flag
    subpub = SubPub(username, password)

    moisture = 70
    salinity = 0
    userdata: Dict[str, Literal[-1, 1]] = {"pump": -1, "desalinate": -1}

    client = None
    try:
        client = subpub.connect_mqtt(on_connect, cafile, userdata)
        subpub.loop_start()
    except TimeoutError:
        print("The client connection timed out...")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if not client:
        return

    try:
        subpub.subscribe(on_message, sub_topics)

        loop_secs = 0
        # Main loop
        while not shutdown_flag:
            loop_secs = loop_secs % READ_X_SECONDS
            if loop_secs == 0:
                moisture = generate_moisture_value(moisture, userdata["pump"])
                salinity = generate_salinity_value(salinity, userdata["desalinate"])
                subpub.publish(moisture_topic, f"{moisture}")
                subpub.publish(salinity_topic, f"{salinity}")
            loop_secs += 1
            time.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()
        client.loop_stop()
        return


if __name__ == "__main__":
    run()
