import customtkinter as ctk
from PIL import Image, ImageTk # Image and ImageTk are imported but not used in the provided code.
import serial
import serial.tools.list_ports
from time import sleep
import time

# CustomTkinter Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------------------
# Global Variables
# ---------------------------
arduino = None
arduino_connected = False

motor_state = False
light_mode = "Manual" # Changed from "Manuale"
pistons_relay_state = False
emergency_mode = False

# ---------------------------
# Connection Management Functions
# ---------------------------
def scan_ports():
    """Updates the OptionMenu with available serial ports."""
    ports = list(serial.tools.list_ports.comports())
    port_list = [port.device for port in ports]
    if port_list:
        port_option.configure(values=port_list)
        port_option.set(port_list[0])
        connection_status_label.configure(text="Ports found: " + ", ".join(port_list)) # Changed text
    else:
        port_option.configure(values=[])
        port_option.set("")
        connection_status_label.configure(text="No devices found.") # Changed text

def connect_arduino():
    """Attempts to connect to the selected port and updates the status."""
    global arduino, arduino_connected
    port = port_option.get()
    if port:
        try:
            arduino = serial.Serial(port, 9600, timeout=1)
            sleep(2)
            arduino_connected = True
            connection_status_label.configure(text="Connected to " + port) # Changed text
            status_label_main.configure(text="Arduino Status: Connected") # Changed text
        except Exception as e:
            arduino = None
            arduino_connected = False
            connection_status_label.configure(text="Connection error to " + port) # Changed text
            status_label_main.configure(text="Arduino Status: Disconnected") # Changed text
    else:
        connection_status_label.configure(text="No port selected.") # Changed text

def disconnect_arduino():
    """Disconnects any connected Arduino."""
    global arduino, arduino_connected
    if arduino:
        try:
            arduino.close()
        except:
            pass
    arduino = None
    arduino_connected = False
    connection_status_label.configure(text="Disconnected.") # Changed text
    status_label_main.configure(text="Arduino Status: Disconnected") # Changed text

# ---------------------------
# Functions to send commands (real or offline mode)
# ---------------------------
def send_command(command):
    if arduino:
        arduino.write(f"{command}\n".encode())
        print(f"Sent command: {command}") # Changed text
    else:
        print(f"[Offline] Simulated command: {command}") # Changed text

# ---------------------------
# Functions for Piston and Servo Control
# ---------------------------
def move_up():
    if pistons_relay_state:
        send_command("PUMP_ON")
        send_command("SERVO_UP")

def stop_move_up(event=None):
    send_command("SERVO_DOWN")
    time.sleep(0.5)
    send_command("SERVO_STOP")
    send_command("SERVO_RESET") # Note: "SERVO_RESET" command is not present in the Arduino code provided.

def toggle_pistons_relay():
    global pistons_relay_state
    if pistons_relay_state:
        send_command("PUMP_OFF")
        send_command("SERVO_RESET") # Note: "SERVO_RESET" command is not present in the Arduino code provided.
        pistons_relay_state = False
        piston_button.configure(text="Pistons: OFF") # Changed text
        jump_button.configure(state=ctk.DISABLED)
    else:
        send_command("PUMP_ON")
        pistons_relay_state = True
        piston_button.configure(text="Pistons: ON") # Changed text
        jump_button.configure(state=ctk.NORMAL)

def toggle_motor():
    global motor_state
    if motor_state:
        send_command("MOTOR_OFF")
        motor_button.configure(text="Motor: OFF") # Changed text
    else:
        send_command("MOTOR_ON")
        motor_button.configure(text="Motor: ON") # Changed text
    motor_state = not motor_state

# ---------------------------
# Functions for Light Control
# ---------------------------
def press_strobe_effect(event=None):
    send_command("STROBE_ON")

def release_strobe_effect(event=None):
    send_command("STROBE_OFF")

def toggle_light_mode():
    global light_mode
    if light_mode == "Manual": # Changed text
        light_mode = "Automatic" # Changed text
        send_command("AUTO_MODE_ON")
        light_mode_button.configure(text="Effects: ON") # Changed text
    else:
        light_mode = "Manual" # Changed text
        send_command("AUTO_MODE_OFF")
        light_mode_button.configure(text="Effects: OFF") # Changed text

# ---------------------------
# Toggle Emergency Function
# ---------------------------
def emergency_stop():
    global emergency_mode, motor_state, pistons_relay_state, light_mode
    if not emergency_mode:
        emergency_mode = True
        send_command("MOTOR_OFF")
        send_command("PUMP_OFF")
        send_command("SERVO_RESET") # Note: "SERVO_RESET" command is not present in the Arduino code provided.
        send_command("STROBE_OFF")
        send_command("AUTO_MODE_OFF")
        motor_state = False
        pistons_relay_state = False
        light_mode = "Manual" # Changed text
        motor_button.configure(text="Motor: OFF") # Changed text
        piston_button.configure(text="Pistons: OFF") # Changed text
        jump_button.configure(state=ctk.DISABLED)
        light_mode_button.configure(text="Effects: OFF") # Changed text
        status_label_main.configure(text="Emergency: systems stopped!", text_color="red") # Changed text
        emergency_button.configure(text="Emergency Reset", fg_color="green") # Changed text
    else:
        emergency_mode = False
        status_label_main.configure(text="System ready", text_color="white") # Changed text
        emergency_button.configure(text="EMERGENCY STOP", fg_color="red") # Changed text

# ---------------------------
# Create Main Window and Tabview
# ---------------------------
root = ctk.CTk()
root.title("Tagadà Control Panel | Developed by Denilson (IG: @denilson._.p) | Version: 3-EN") # Changed title
root.geometry("1920x1080")

tabview = ctk.CTkTabview(root, width=1060, height=1900)
tabview.pack(padx=10, pady=10, fill="both", expand=True)

tabview.add("Connection") # Changed tab name
tabview.add("Control") # Changed tab name

# ----------------------------
# "Connection" Tab - Arduino Port Management
# ----------------------------
connection_tab = tabview.tab("Connection") # Changed tab name

conn_frame = ctk.CTkFrame(connection_tab, corner_radius=10, fg_color="transparent")
conn_frame.pack(pady=20, padx=20, fill="both", expand=True)

conn_title = ctk.CTkLabel(conn_frame, text="🔌 Arduino Connection", font=("Helvetica", 22, "bold")) # Changed text
conn_title.pack(pady=(20, 10))
conn_instruction = ctk.CTkLabel(conn_frame,
                                 text="Press 'Detect Ports' to search for devices.\nSelect a port and press 'Connect'.", # Changed text
                                 font=("Helvetica", 16))
conn_instruction.pack(pady=(0,20))

port_option = ctk.CTkOptionMenu(conn_frame, values=[], width=250, font=("Helvetica", 16))
port_option.pack(pady=10)

scan_button = ctk.CTkButton(conn_frame, text="Detect Ports", command=scan_ports, font=("Helvetica", 16)) # Changed text
scan_button.pack(pady=10)

connect_button = ctk.CTkButton(conn_frame, text="Connect", command=connect_arduino, font=("Helvetica", 16)) # Changed text
connect_button.pack(pady=10)

disconnect_button = ctk.CTkButton(conn_frame, text="Disconnect", command=disconnect_arduino, font=("Helvetica", 16)) # Changed text
disconnect_button.pack(pady=10)

connection_status_label = ctk.CTkLabel(conn_frame, text="Status: Disconnected", font=("Helvetica", 16)) # Changed text
connection_status_label.pack(pady=10)

scan_ports()

# ----------------------------
# "Control" Tab - Control Panel
# ----------------------------
control_tab = tabview.tab("Control") # Changed tab name

header_frame = ctk.CTkFrame(control_tab, corner_radius=10)
header_frame.pack(pady=20, padx=20, fill="x")
title_label = ctk.CTkLabel(header_frame, text="Tagadà Control Panel \nDeveloped by @denilson._.p", font=("Helvetica", 24, "bold")) # Changed text
title_label.pack(pady=10)

main_frame = ctk.CTkFrame(control_tab)
main_frame.pack(pady=10, padx=20, fill="both", expand=True)

left_frame = ctk.CTkFrame(main_frame, corner_radius=10)
left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

left_title = ctk.CTkLabel(left_frame, text="Motor & Piston Controls", font=("Helvetica", 20)) # Changed text
left_title.pack(pady=10)

piston_button = ctk.CTkButton(left_frame, text="Pistons: OFF", command=toggle_pistons_relay, # Changed text
                              font=("Helvetica", 18), width=300, height=80)
piston_button.pack(pady=10)

jump_button = ctk.CTkButton(left_frame, text="JUMP", command=move_up, # Changed text
                            font=("Helvetica", 18), width=300, height=80, state=ctk.DISABLED)
jump_button.bind("<ButtonRelease-1>", stop_move_up)
jump_button.pack(pady=10)

motor_button = ctk.CTkButton(left_frame, text="Motor: OFF", command=toggle_motor, # Changed text
                             font=("Helvetica", 18), width=300, height=80)
motor_button.pack(pady=10)

emergency_button = ctk.CTkButton(left_frame, text="EMERGENCY STOP", command=emergency_stop, # Changed text
                                 font=("Helvetica", 18, "bold"), width=300, height=80, fg_color="red")
emergency_button.pack(pady=20)

right_frame = ctk.CTkFrame(main_frame, corner_radius=10)
right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

right_title = ctk.CTkLabel(right_frame, text="Light Controls", font=("Helvetica", 20)) # Changed text
right_title.pack(pady=10)

strobe_button = ctk.CTkButton(right_frame, text="STROBE", font=("Helvetica", 18), # Changed text
                              width=300, height=80)
strobe_button.bind("<ButtonPress-1>", press_strobe_effect)
strobe_button.bind("<ButtonRelease-1>", release_strobe_effect)
strobe_button.pack(pady=10)

light_mode_button = ctk.CTkButton(right_frame, text="Effects: OFF", command=toggle_light_mode, # Changed text
                                  font=("Helvetica", 18), width=300, height=80)
light_mode_button.pack(pady=10)

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

status_frame = ctk.CTkFrame(control_tab, corner_radius=10)
status_frame.pack(pady=10, padx=20, fill="x")
status_label_main = ctk.CTkLabel(status_frame,
                                 text="Arduino Status: " + ("Connected" if arduino_connected else "Disconnected"), # Changed text
                                 font=("Helvetica", 16))
status_label_main.pack(side="left", padx=10)

root.mainloop()