import tkinter as tk
from tkinter import scrolledtext


def publish():
    pass


def publish_btn_handler():
    pass


def sub_feed_insert(text):
    text_widget.configure(state=tk.NORMAL)
    text_widget.insert(tk.END, text + "\n")
    text_widget.see(tk.END)
    text_widget.configure(state=tk.DISABLED)


# Function to toggle Button 1
def toggle_button1():
    if button1_state.get():
        button1.config(text="Moisture OK", bg="green")
        button1_state.set(False)
    else:
        button1.config(text="Increasing Moisture", bg="red")
        button1_state.set(True)


# Function to toggle Button 1
def toggle_button2():
    if button2_state.get():
        button2.config(text="Salinity OK", bg="green")
        button2_state.set(False)
    else:
        button2.config(text="Reducing Salinity", bg="red")
        button2_state.set(True)


# Initialize the main window
root = tk.Tk()
root.title("Tkinter Toggle Buttons App")

# Configure the grid layout for scaling
root.grid_rowconfigure(3, weight=1)  # Row 1 (Text widget) expands
root.grid_columnconfigure(0, weight=1)  # Column 0 expands

# Boolean variables to track the button states
button1_state = tk.BooleanVar(value=False)
button2_state = tk.BooleanVar(value=False)

# Create a frame to hold the two buttons
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Configure the frame to expand horizontally
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)


# Create two buttons inside the frame with toggle functionality
button1 = tk.Button(
    button_frame, text="Moisture OK", bg="green", command=toggle_button1
)
button1.grid(row=0, column=0, sticky="ew", padx=5)

button2 = tk.Button(
    button_frame, text="Salinity OK", bg="green", command=toggle_button2
)
button2.grid(row=0, column=1, sticky="ew", padx=5)


# Create two entry widgets for user input
entry_frame = tk.Frame(root)
entry_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
# Configure the entry frame to expand horizontally
entry_frame.grid_columnconfigure(0, weight=1)
entry_frame.grid_columnconfigure(1, weight=1)

# Create labels for entry fields
label1 = tk.Label(entry_frame, text="Topic:")
label1.grid(row=0, column=0, sticky="w", padx=5)
label2 = tk.Label(entry_frame, text="Message:")
label2.grid(row=0, column=1, sticky="w", padx=5)

# Create Entry widgets
entry1 = tk.Entry(entry_frame)
entry1.grid(row=1, column=0, sticky="ew", padx=5)
entry2 = tk.Entry(entry_frame)
entry2.grid(row=1, column=1, sticky="ew", padx=5)

publish_btn = tk.Button(
    entry_frame, text="Publish", bg="green", command=publish_btn_handler
)
publish_btn.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5)

# Create a label for the text widget
text_label = tk.Label(root, text="Subscription Feed:")
text_label.grid(row=2, column=0, sticky="w", padx=10)

# Create a text widget below the buttons
text_widget = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD)
text_widget.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)


# Start the Tkinter event loop
root.mainloop()
