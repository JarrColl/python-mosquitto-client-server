import random
import sys
import time
from typing import Any

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

broker = "rule100.caia.swin.edu.au"
port = 8883
client_id = f"publish-{random.randint(0, 1000)}"
username = "102988098"
password = "jarron"

CONNECT_TIMEOUT = 5

pub_topic = sys.argv[1]
sub_topics = [("public/#", 1), ("102988098/#", 0)]

cafile = "./ca.crt"


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


def publish(client: Client, msg):
    result = client.publish(pub_topic, msg, qos=1)
    if result.rc == MQTTErrorCode.MQTT_ERR_SUCCESS:
        print(f"Send `{msg}` to topic `{pub_topic}`")
    else:
        print(f"Failed to send message to topic {pub_topic}")


def subscribe(client: Client):
    def on_message(client: Client, userdata: Any, msg: MQTTMessage):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    error_code = client.subscribe(sub_topics)[0]
    if error_code == MQTTErrorCode.MQTT_ERR_NO_CONN:
        raise MQTTException(
            "Subscribe called while the client is not connected to a server."
        )
    client.on_message = on_message


def run():
    client = connect_mqtt()
    error_code = client.loop_start()
    # error_code = client.loop_stop()
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
        if f % 2 == 0:
            publish(client, f"hi: {f}")
        f += 1
        time.sleep(1)
        if f > 30:
            return


if __name__ == "__main__":
    run()
