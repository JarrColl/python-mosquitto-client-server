import random
from typing import Any

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from subpubClass import SubPub

topics = [("public/#", 1), ("102988098/#", 0)]

username = "102988098"
password = "jarron"
cafile = "./certs/ca.crt"

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


def on_message(client: Client, userdata: Any, msg: MQTTMessage):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

def run():
    subpub = SubPub(username, password)
    client = subpub.connect_mqtt(on_connect, cafile)
    subpub.subscribe(on_message, topics)

    error_code = client.loop_forever()
    if error_code != MQTTErrorCode.MQTT_ERR_SUCCESS:
        raise MQTTException(
            "Client failed to loop_forever with error code " + str(error_code) + "."
        )


if __name__ == "__main__":
    run()
