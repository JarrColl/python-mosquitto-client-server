import datetime
import queue
import tkinter
import tkinter as tk
from tkinter import EventType, Misc, scrolledtext
from typing import Any, Dict, Literal, Tuple

from paho.mqtt import MQTTException
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from subpubClass import SubPub

cafile = "./certs/ca.crt"
# username, password = "admin", "admin"
username, password = "monitor", "monitor"


PossibleHUDTypes = Literal["", "moisture", "salinity", "light"]
sub_queue: queue.Queue[Tuple[PossibleHUDTypes, str, str]] = queue.Queue()

# All cross client communication is performed in the public channel as explicitly required by the tutor.
toodry_topic = "public/toodry"
toosalty_topic = "public/toosalty"
toodark_topic = "public/toodark"
stop_topic = "public/stop"

salinity_topic = "public/salinity"
moisture_topic = "public/moisture"
light_topic = "public/light"


def config_tk_window(root: tk.Tk, subpub: SubPub) -> tk.Tk:
    def sub_feed_insert(text: str):
        subfeed_text_widget.configure(state=tk.NORMAL)
        subfeed_text_widget.insert(tk.END, text + "\n")
        subfeed_text_widget.see(tk.END)
        subfeed_text_widget.configure(state=tk.DISABLED)

    def too_dry_on_btn_handler():
        subpub.publish(toodry_topic, "1")

    def too_dry_off_btn_handler():
        subpub.publish(toodry_topic, "0")

    def too_salty_on_btn_handler():
        subpub.publish(toosalty_topic, "1")

    def too_salty_off_btn_handler():
        subpub.publish(toosalty_topic, "0")

    def lamp_on_btn_handler():
        subpub.publish(toodark_topic, "1")

    def lamp_off_btn_handler():
        subpub.publish(toodark_topic, "0")

    def publish_btn_handler():
        subpub.publish(topic_entry.get(), message_entry.get())

    def stop_btn_handler():
        subpub.publish(stop_topic, "stop")

    # Initialize the main window
    root.title("Tkinter Toggle Buttons App")

    sub_feed_row = 4

    # Configure the grid layout for scaling
    root.grid_rowconfigure(
        sub_feed_row, weight=1
    )  # Row 1 (Text widget) expands vertically
    root.grid_columnconfigure(0, weight=1)  # Column buttons frame expands
    # root.grid_columnconfigure(2, weight=1)  # Column hud frame expands

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
        button_frame, text="Too Dry ON", bg="#72bf4c", command=too_dry_on_btn_handler
    )
    too_dry_on_btn.grid(row=0, column=0, sticky="ew", padx=5)
    too_dry_off_btn = tk.Button(
        button_frame, text="Too Dry OFF", bg="#bf4c59", command=too_dry_off_btn_handler
    )
    too_dry_off_btn.grid(row=0, column=1, sticky="ew", padx=5)

    too_salty_on_btn = tk.Button(
        button_frame,
        text="Too Salty ON",
        bg="#72bf4c",
        command=too_salty_on_btn_handler,
    )
    too_salty_on_btn.grid(row=0, column=2, sticky="we", padx=5)
    stop_btn = tk.Button(
        button_frame,
        text="Too Salty OFF",
        bg="#bf4c59",
        command=too_salty_off_btn_handler,
    )
    stop_btn.grid(row=0, column=3, sticky="we", padx=5)

    lamp_on_btn = tk.Button(
        button_frame, text="Lamp ON", bg="#72bf4c", command=lamp_on_btn_handler
    )
    lamp_on_btn.grid(row=1, column=0, sticky="we", padx=5)
    lamp_off_btn = tk.Button(
        button_frame, text="Lamp OFF", bg="#bf4c59", command=lamp_off_btn_handler
    )
    lamp_off_btn.grid(row=1, column=1, sticky="we", padx=5)

    stop_btn = tk.Button(button_frame, text="STOP", bg="red", command=stop_btn_handler)
    stop_btn.grid(row=1, column=2, columnspan=2, sticky="we", padx=5)

    # HUD Values
    hud_frame = tk.Frame(root)
    hud_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    hud_frame.grid_columnconfigure(0, weight=1)
    hud_frame.grid_columnconfigure(1, weight=1)
    hud_frame.grid_columnconfigure(2, weight=1)

    large_font = ("Helvetica", 48, "bold")
    text_font = ("Helvetica", 20)

    moisture_label = tk.Label(hud_frame, text="XX", font=large_font)
    moisture_label.grid(row=0, column=0, padx=10, pady=20)
    salinity_label = tk.Label(hud_frame, text="XX", font=large_font)
    salinity_label.grid(row=0, column=1, padx=10, pady=20)
    light_label = tk.Label(hud_frame, text="XX", font=large_font)
    light_label.grid(row=0, column=2, padx=10, pady=20)

    # Add the descriptive labels below each value
    desc_moisture = tk.Label(hud_frame, text="Moisture", font=text_font)
    desc_moisture.grid(row=1, column=0, padx=10, pady=10)

    desc_salinity = tk.Label(hud_frame, text="Salinity", font=text_font)
    desc_salinity.grid(row=1, column=1, padx=10, pady=10)

    desc_light = tk.Label(hud_frame, text="Light", font=text_font)
    desc_light.grid(row=1, column=2, padx=10, pady=10)

    entry_frame = tk.Frame(root)
    entry_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
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
    subfeed_label.grid(row=3, column=0, sticky="w", padx=10)

    # Create a text widget below the buttons
    subfeed_text_widget = scrolledtext.ScrolledText(
        root, state=tk.DISABLED, wrap=tk.WORD
    )
    subfeed_text_widget.grid(
        row=sub_feed_row, column=0, sticky="nsew", padx=10, pady=10
    )

    def tk_on_message(event: tkinter.Event):
        try:
            event_data = sub_queue.get_nowait()
            if event_data:
                data_type, payload, data = event_data
                colour = "red" if payload in ("100", "0") else "green"
                if data_type == "moisture":
                    moisture_label.configure(text=payload, fg=colour)
                elif data_type == "salinity":
                    salinity_label.configure(text=payload, fg=colour)
                elif data_type == "light":
                    light_label.configure(text=payload, fg=colour)


                sub_feed_insert(data)
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
    data_type = ""

    if msg.topic == moisture_topic:
        data_type = "moisture"
    elif msg.topic == salinity_topic:
        data_type = "salinity"
    elif msg.topic == light_topic:
        data_type = "light"


    sub_queue.put(
        (data_type, msg.payload.decode(), f"{datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} -- <{msg.topic}>: {msg.payload.decode()}")
    )
    userdata["tkRoot"].event_generate(
        "<<on_message>>", when="tail"
    )  # trigger event in main thread


def main():
    root = tk.Tk()
    userdata = {"tkRoot": root}
    subpub = SubPub(username, password)

    client = None
    try:
        client = subpub.connect_mqtt(on_connect, cafile, userdata)
        subpub.loop_start()
    except TimeoutError:
        print("The client connection timed out...")
    except Exception as e:
        print(f"An error occurred: {e}")

    if not client:
        return

    try:
        subpub.subscribe(on_message, "#")

        config_tk_window(root, subpub)
        # Start the Tkinter event loop
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        return




main()
