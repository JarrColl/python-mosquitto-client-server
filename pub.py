import random
import time
from typing import Any
import sys

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags
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
topic = sys.argv[1]
cafile = "./certs/ca.crt"


def connect_mqtt() -> Client:
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

    client = mqtt_client.Client(CallbackAPIVersion.VERSION2, client_id)
    client.username_pw_set(username, password)
    client.tls_set(ca_certs=cafile)

    client.on_connect = on_connect
    error_code = client.connect(broker, port)

    if error_code != MQTTErrorCode.MQTT_ERR_SUCCESS:
        raise MQTTException(
            "Client failed to connect with error code " + str(error_code) + "."
        )
    return client


def publish(client: Client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg, qos=1)
        if result.rc == MQTTErrorCode.MQTT_ERR_SUCCESS:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 10:
            break


def run():
    client = connect_mqtt()

    error_code = client.loop_start()
    if error_code != MQTTErrorCode.MQTT_ERR_SUCCESS:
        raise MQTTException(
            "Client failed to loop_forever with error code " + str(error_code) + "."
        )

    publish(client)
    error_code = client.loop_stop()
    if error_code == MQTTErrorCode.MQTT_ERR_INVAL:
        raise MQTTException(
            "Client loop stop was called but there was no running client loop on the thread."
        )


if __name__ == "__main__":
    run()
