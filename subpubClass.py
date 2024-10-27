import random
import time
from typing import Any

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import (
    CallbackOnConnect,
    CallbackOnMessage,
    Client,
)
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode

CONNECT_TIMEOUT = 5

class SubPub:
    
    def __init__(self, username: str, password: str):
        self.client: Client | None = None
        self.broker = "rule100.caia.swin.edu.au"
        self.port = 8883
        self.client_id = f"publish-{random.randint(0, 1000)}"
        self.username = username
        self.password = password


    def connect_mqtt(
        self, on_connect: CallbackOnConnect, ca_path: str, userdata: Any = None
    ) -> Client | None:
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

    def loop_start(self):
        if not self.client:
            raise Exception("Called loop_start with an uninitialised client.")

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
                    raise TimeoutError("Client loop start timed out.")
                time_waiting += 0.1
                time.sleep(0.1)

    def publish(self, pub_topic: str, msg: str):
        if not self.client:
            raise Exception("Called loop_start with an uninitialised client.")

        result = self.client.publish(pub_topic, msg, qos=1)
        if result.rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
            print(f"Failed to send message to topic {pub_topic}")

        # Log all messages to a specified private user topic.
        self.client.publish(f"{self.username}/logs", msg, qos=1)

    def subscribe(self, on_message: CallbackOnMessage, sub_topics: Any):
        if not self.client:
            raise Exception("Called loop_start with an uninitialised client.")

        error_code = self.client.subscribe(sub_topics)[0]
        if error_code == MQTTErrorCode.MQTT_ERR_NO_CONN:
            raise MQTTException(
                "Subscribe called while the client is not connected to a server."
            )
        self.client.on_message = on_message
