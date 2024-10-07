import datetime
import queue
import tkinter
import tkinter as tk
from tkinter import EventType, Misc, scrolledtext
from typing import Any, Dict, Literal

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from subpubClass import SubPub

cafile = "./certs/ca.crt"
username = "102988098"
password = "jarron"

sub_queue: queue.Queue[str] = queue.Queue()


def config_tk_window(root: tk.Tk, subpub: SubPub) -> tk.Tk:
    def sub_feed_insert(text: str):
        subfeed_text_widget.configure(state=tk.NORMAL)
        subfeed_text_widget.insert(tk.END, text + "\n")
        subfeed_text_widget.see(tk.END)
        subfeed_text_widget.configure(state=tk.DISABLED)

    def too_dry_on_btn_handler():
        subpub.publish("102988098/toodry", "1")

    def too_dry_off_btn_handler():
        subpub.publish("102988098/toodry", "0")

    def too_salty_on_btn_handler():
        subpub.publish("102988098/toosalty", "1")

    def too_salty_off_btn_handler():
        subpub.publish("102988098/toosalty", "0")

    def publish_btn_handler():
        subpub.publish(topic_entry.get(), message_entry.get())

    # Initialize the main window
    root.title("Tkinter Toggle Buttons App")

    # Configure the grid layout for scaling
    root.grid_rowconfigure(3, weight=1)  # Row 1 (Text widget) expands
    root.grid_columnconfigure(0, weight=1)  # Column 0 expands

    # Create a frame to hold the two buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

    # Configure the frame to expand horizontally
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)

    # Create two buttons inside the frame with toggle functionality
    too_dry_on_btn = tk.Button(
        button_frame, text="Too Dry ON", bg="green", command=too_dry_on_btn_handler
    )
    too_dry_on_btn.grid(row=0, column=0, sticky="ew", padx=5)
    too_dry_off_btn = tk.Button(
        button_frame, text="Too Dry OFF", bg="red", command=too_dry_off_btn_handler
    )
    too_dry_off_btn.grid(row=0, column=1, sticky="ew", padx=5)

    too_salty_on_btn = tk.Button(
        button_frame, text="Too Salty ON", bg="green", command=too_salty_on_btn_handler
    )
    too_salty_on_btn.grid(row=0, column=2, sticky="we", padx=5)
    too_salty_off_btn = tk.Button(
        button_frame, text="Too Salty OFF", bg="red", command=too_salty_off_btn_handler
    )
    too_salty_off_btn.grid(row=0, column=3, sticky="we", padx=5)

    # Create two entry widgets for user input
    entry_frame = tk.Frame(root)
    entry_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
    # Configure the entry frame to expand horizontally
    entry_frame.grid_columnconfigure(0, weight=1)
    entry_frame.grid_columnconfigure(1, weight=1)

    # Create labels for entry fields
    topic_label = tk.Label(entry_frame, text="Topic:")
    topic_label.grid(row=0, column=0, sticky="w", padx=5)
    message_label = tk.Label(entry_frame, text="Message:")
    message_label.grid(row=0, column=1, sticky="w", padx=5)

    # Create Entry widgets
    topic_entry = tk.Entry(entry_frame)
    topic_entry.grid(row=1, column=0, sticky="ew", padx=5)
    message_entry = tk.Entry(entry_frame)
    message_entry.grid(row=1, column=1, sticky="ew", padx=5)

    publish_btn = tk.Button(
        entry_frame, text="Publish", bg="green", command=publish_btn_handler
    )
    publish_btn.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5)

    # Create a label for the text widget
    subfeed_label = tk.Label(root, text="Subscription Feed:")
    subfeed_label.grid(row=2, column=0, sticky="w", padx=10)

    # Create a text widget below the buttons
    subfeed_text_widget = scrolledtext.ScrolledText(
        root, state=tk.DISABLED, wrap=tk.WORD
    )
    subfeed_text_widget.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

    def tk_on_message(event: tkinter.Event[Misc]):
        try:
            event_data: str = sub_queue.get_nowait()
            if event_data:
                sub_feed_insert(event_data)
        except queue.Empty:
            pass

    root.bind("<<on_message>>", tk_on_message)  # event triggered by background thread

    return root


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
    sub_queue.put(
        f"{datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} -- <{msg.topic}>: {msg.payload.decode()}"
    )
    userdata["tkRoot"].event_generate(
        "<<on_message>>", when="tail"
    )  # trigger event in main thread


def main():
    root = tk.Tk()
    userdata = {"tkRoot": root}
    subpub = SubPub(username, password)
    client = subpub.connect_mqtt(on_connect, cafile, userdata)
    subpub.loop_start()
    subpub.subscribe(on_message, "#")

    config_tk_window(root, subpub)
    # Start the Tkinter event loop
    root.mainloop()

    client.loop_stop()
    client.disconnect()


main()
