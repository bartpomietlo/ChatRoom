
import socketfile as sf
from customtkinter import *
import socket
import tkinter
import threading

# Client declaration
client = sf.Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
server_ip, server_port = client.discover_server()
threading.Thread(target=client.start, args=(server_ip, server_port)).start()

# GUI creation

# Set appearance and theme
set_appearance_mode("System")
set_default_color_theme("dark-blue")

# Create main window
root = CTk()
root.geometry("1280x720")


# Sending message
def send_message():
    message = entry.get()
    if message:
        client.send_messages(message)
        display_message(message, 'right')
        entry.delete(0, tkinter.END)


# Create frame for entry and send-button
input_frame = CTkFrame(master=root)
input_frame.pack(side="bottom", fill="x", padx=10, pady=10)

# Create entry for sending messages
entry = CTkEntry(master=input_frame)
entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)

# Create send-button
s_button = CTkButton(master=input_frame, text="Send", command=send_message)
s_button.pack(side="right")

# Create frame for sent messages
frame = CTkFrame(master=root)
frame.pack(side="top", fill="both", expand=True)


def display_message(message, align):
    message_label = CTkLabel(master=frame, text=message, bg_color='blue', anchor='w' if align == 'left' else 'e')
    message_label.pack(anchor='w' if align == 'left' else 'e', padx=10, pady=5)


# Function to handle incoming messages and display them
def handle_incoming_messages():
    while True:
        message = client.receive_messages()
        if message:
            display_message(message, 'left')


# Start thread to handle incoming messages
threading.Thread(target=handle_incoming_messages).start()

# Start the main loop
root.mainloop()





