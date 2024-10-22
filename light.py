from logging import error
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

light_topic = "102988098/light"
sub_topics = [("public/#", 1), ("102988098/toodark", 1)]

# TODO: move everythong to public and give everything its own username then have each client publish its data also to its private user topic.
cafile = "./certs/ca.crt"
username = "102988098"
password = "jarron"

shutdown_flag = False

def on_connect( client: Client, userdata: Any, flags: ConnectFlags, rc: ReasonCode, properties: Properties | None,
):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


def on_message(client: Client, userdata: Any, msg: MQTTMessage):
    payload = msg.payload.decode()
    if msg.topic == "102988098/toodark":
        if payload == "0":
            userdata["light"] = 0
        elif payload == "1":
            userdata["light"] = 100
    elif msg.topic == "public/stop":
        if payload == "stop":
            print("Stop message sent, shutting down.")
            global shutdown_flag
            shutdown_flag = True

    print(f"Received `{payload}` from `{msg.topic}` topic")



def generate_light_value(light_avg: float, count: int, curr_light: Literal[0, 100]) -> float:
    return round(light_avg + (curr_light - light_avg) / count, 2)

def run():
    global shutdown_flag
    subpub = SubPub(username, password)
    light = 70
    num_readings = 1
    userdata: Dict[str, Literal[0, 100]] = {"light": 0}

    client = subpub.connect_mqtt(on_connect, cafile, userdata)
    subpub.loop_start()
    subpub.subscribe(on_message, sub_topics)

    loop_secs = 0
    try:
        # Main loop
        while not shutdown_flag:
            loop_secs = loop_secs % READ_X_SECONDS
            if loop_secs == 0:
                light = generate_light_value(light, num_readings, userdata["light"])
                subpub.publish(light_topic, f"{light}")
            loop_secs += 1
            time.sleep(1)
    except Exception as e:
        error(e)
    finally:
        client.disconnect()
        client.loop_stop()
        return


if __name__ == "__main__":
    run()
