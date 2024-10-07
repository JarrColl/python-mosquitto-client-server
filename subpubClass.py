import random
import sys
import time
from typing import Any

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import (
    CallbackOnConnect,
    CallbackOnMessage,
    Client,
    ConnectFlags,
    MQTTMessage,
)
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

CONNECT_TIMEOUT = 5

class SubPub:
    client: Client | None = None
    broker = "rule100.caia.swin.edu.au"
    port = 8883
    client_id = f"publish-{random.randint(0, 1000)}"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password


    def connect_mqtt(
        self, on_connect: CallbackOnConnect, ca_path: str, userdata: Any = None
    ) -> Client:
        client = mqtt_client.Client(
            CallbackAPIVersion.VERSION2, self.client_id, userdata=userdata
        )
        client.username_pw_set(self.username, self.password)
        client.tls_set(ca_certs=ca_path)

        client.on_connect = on_connect
        error_code = client.connect(self.broker, self.port)

        if error_code != MQTTErrorCode.MQTT_ERR_SUCCESS:
            raise MQTTException(
                "Client failed to connect with error code " + str(error_code) + "."
            )

        self.client = client
        return self.client

    def loop_start(self) -> bool:
        if self.client:
            error_code = self.client.loop_start()
            # error_code = client.loop_stop()
            if error_code == MQTTErrorCode.MQTT_ERR_INVAL:
                raise MQTTException(
                    "Client loop stop was called but there was no running client loop on the thread."
                )

            # Wait for the connection to be acknowledged by the server before starting.
            time_waiting = 0
            while True:
                if self.client.is_connected():
                    break
                else:
                    if time_waiting >= CONNECT_TIMEOUT:
                        print("Connection timed out...")
                        return False
                    time_waiting += 0.1
                    time.sleep(0.1)
            return True
        return False

    def publish(self, pub_topic: str, msg: str):
        if self.client:
            result = self.client.publish(pub_topic, msg, qos=1)
            if result.rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
                print(f"Failed to send message to topic {pub_topic}")

    def subscribe(self, on_message: CallbackOnMessage, sub_topics: Any):
        if self.client:
            error_code = self.client.subscribe(sub_topics)[0]
            if error_code == MQTTErrorCode.MQTT_ERR_NO_CONN:
                raise MQTTException(
                    "Subscribe called while the client is not connected to a server."
                )
            self.client.on_message = on_message
