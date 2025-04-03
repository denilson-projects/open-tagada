import customtkinter as ctk
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
from time import sleep
import time

# Configurazione di CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------------------
# Variabili globali
# ---------------------------
arduino = None
arduino_connected = False

motor_state = False
light_mode = "Manuale"
pistons_relay_state = False
emergency_mode = False

# ---------------------------
# Funzioni per la gestione della connessione
# ---------------------------
def scan_ports():
    """Aggiorna l'OptionMenu con le porte seriali disponibili."""
    ports = list(serial.tools.list_ports.comports())
    port_list = [port.device for port in ports]
    if port_list:
        port_option.configure(values=port_list)
        port_option.set(port_list[0])
        connection_status_label.configure(text="Porte trovate: " + ", ".join(port_list))
    else:
        port_option.configure(values=[])
        port_option.set("")
        connection_status_label.configure(text="Nessun dispositivo trovato.")

def connect_arduino():
    """Prova a connettersi alla porta selezionata e aggiorna lo stato."""
    global arduino, arduino_connected
    port = port_option.get()
    if port:
        try:
            arduino = serial.Serial(port, 9600, timeout=1)
            sleep(2)
            arduino_connected = True
            connection_status_label.configure(text="Connesso a " + port)
            status_label_main.configure(text="Stato Arduino: Connesso")
        except Exception as e:
            arduino = None
            arduino_connected = False
            connection_status_label.configure(text="Errore di connessione a " + port)
            status_label_main.configure(text="Stato Arduino: Non Connesso")
    else:
        connection_status_label.configure(text="Nessuna porta selezionata.")

def disconnect_arduino():
    """Disconnette eventuale Arduino collegato."""
    global arduino, arduino_connected
    if arduino:
        try:
            arduino.close()
        except:
            pass
    arduino = None
    arduino_connected = False
    connection_status_label.configure(text="Disconnesso.")
    status_label_main.configure(text="Stato Arduino: Non Connesso")

# ---------------------------
# Funzioni per inviare comandi (modalità reale o offline)
# ---------------------------
def send_command(command):
    if arduino:
        arduino.write(f"{command}\n".encode())
        print(f"Inviato comando: {command}")
    else:
        print(f"[Offline] Comando simulato: {command}")

# ---------------------------
# Funzioni per il controllo dei Pistoni e del Servo
# ---------------------------
def move_up():
    if pistons_relay_state:
        send_command("PUMP_ON")
        send_command("SERVO_UP")

def stop_move_up(event=None):
    send_command("SERVO_DOWN")
    time.sleep(0.5)
    send_command("SERVO_STOP")
    send_command("SERVO_RESET")

def toggle_pistons_relay():
    global pistons_relay_state
    if pistons_relay_state:
        send_command("PUMP_OFF")
        send_command("SERVO_RESET")
        pistons_relay_state = False
        piston_button.configure(text="Pistoni: OFF")
        jump_button.configure(state=ctk.DISABLED)
    else:
        send_command("PUMP_ON")
        pistons_relay_state = True
        piston_button.configure(text="Pistoni: ON")
        jump_button.configure(state=ctk.NORMAL)

def toggle_motor():
    global motor_state
    if motor_state:
        send_command("MOTOR_OFF")
        motor_button.configure(text="Motore: OFF")
    else:
        send_command("MOTOR_ON")
        motor_button.configure(text="Motore: ON")
    motor_state = not motor_state

# ---------------------------
# Funzioni per il controllo delle luci
# ---------------------------
def press_strobe_effect(event=None):
    send_command("STROBE_ON")

def release_strobe_effect(event=None):
    send_command("STROBE_OFF")

def toggle_light_mode():
    global light_mode
    if light_mode == "Manuale":
        light_mode = "Automatica"
        send_command("AUTO_MODE_ON")
        light_mode_button.configure(text="Effetti: ON")
    else:
        light_mode = "Manuale"
        send_command("AUTO_MODE_OFF")
        light_mode_button.configure(text="Effetti: OFF")

# ---------------------------
# Funzione di emergenza a toggle
# ---------------------------
def emergency_stop():
    global emergency_mode, motor_state, pistons_relay_state, light_mode
    if not emergency_mode:

        emergency_mode = True
        send_command("MOTOR_OFF")
        send_command("PUMP_OFF")
        send_command("SERVO_RESET")
        send_command("STROBE_OFF")
        send_command("AUTO_MODE_OFF")
        motor_state = False
        pistons_relay_state = False
        light_mode = "Manuale"
        motor_button.configure(text="Motore: OFF")
        piston_button.configure(text="Pistoni: OFF")
        jump_button.configure(state=ctk.DISABLED)
        light_mode_button.configure(text="Effetti: OFF")
        status_label_main.configure(text="Emergenza: sistemi arrestati!", text_color="red")
        emergency_button.configure(text="Reset Emergenza", fg_color="green")
    else:

        emergency_mode = False
        status_label_main.configure(text="Sistema pronto", text_color="white")
        emergency_button.configure(text="EMERGENZA STOP", fg_color="red")

# ---------------------------
# Creazione della finestra principale e del Tabview
# ---------------------------
root = ctk.CTk()
root.title("Pannello di controllo Tagadà | Sviluppato da Denilson (IG: @denilson._.p) | Versione: 3-IT")
root.geometry("1920x1080")

tabview = ctk.CTkTabview(root, width=1060, height=1900)
tabview.pack(padx=10, pady=10, fill="both", expand=True)

tabview.add("Connessione")
tabview.add("Controllo")

# ----------------------------
# Scheda "Connessione" - Gestione della porta Arduino
# ----------------------------
connection_tab = tabview.tab("Connessione")

conn_frame = ctk.CTkFrame(connection_tab, corner_radius=10, fg_color="transparent")
conn_frame.pack(pady=20, padx=20, fill="both", expand=True)

conn_title = ctk.CTkLabel(conn_frame, text="🔌 Connessione Arduino", font=("Helvetica", 22, "bold"))
conn_title.pack(pady=(20, 10))
conn_instruction = ctk.CTkLabel(conn_frame,
                                text="Premi 'Rileva Porte' per cercare dispositivi.\nSeleziona una porta e premi 'Connetti'.",
                                font=("Helvetica", 16))
conn_instruction.pack(pady=(0,20))

port_option = ctk.CTkOptionMenu(conn_frame, values=[], width=250, font=("Helvetica", 16))
port_option.pack(pady=10)

scan_button = ctk.CTkButton(conn_frame, text="Rileva Porte", command=scan_ports, font=("Helvetica", 16))
scan_button.pack(pady=10)

connect_button = ctk.CTkButton(conn_frame, text="Connetti", command=connect_arduino, font=("Helvetica", 16))
connect_button.pack(pady=10)

disconnect_button = ctk.CTkButton(conn_frame, text="Disconnetti", command=disconnect_arduino, font=("Helvetica", 16))
disconnect_button.pack(pady=10)

connection_status_label = ctk.CTkLabel(conn_frame, text="Stato: Non Connesso", font=("Helvetica", 16))
connection_status_label.pack(pady=10)

scan_ports()

# ----------------------------
# Scheda "Controllo" - Pannello di Controllo
# ----------------------------
control_tab = tabview.tab("Controllo")

header_frame = ctk.CTkFrame(control_tab, corner_radius=10)
header_frame.pack(pady=20, padx=20, fill="x")
title_label = ctk.CTkLabel(header_frame, text="Pannello di controllo Tagadà \nSviluppato da @denilson._.p", font=("Helvetica", 24, "bold"))
title_label.pack(pady=10)

main_frame = ctk.CTkFrame(control_tab)
main_frame.pack(pady=10, padx=20, fill="both", expand=True)

left_frame = ctk.CTkFrame(main_frame, corner_radius=10)
left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

left_title = ctk.CTkLabel(left_frame, text="Controlli Motore & Pistoni", font=("Helvetica", 20))
left_title.pack(pady=10)

piston_button = ctk.CTkButton(left_frame, text="Pistoni: OFF", command=toggle_pistons_relay,
                              font=("Helvetica", 18), width=300, height=80)
piston_button.pack(pady=10)

jump_button = ctk.CTkButton(left_frame, text="SALTA", command=move_up,
                            font=("Helvetica", 18), width=300, height=80, state=ctk.DISABLED)
jump_button.bind("<ButtonRelease-1>", stop_move_up)
jump_button.pack(pady=10)

motor_button = ctk.CTkButton(left_frame, text="Motore: OFF", command=toggle_motor,
                             font=("Helvetica", 18), width=300, height=80)
motor_button.pack(pady=10)

emergency_button = ctk.CTkButton(left_frame, text="EMERGENZA STOP", command=emergency_stop,
                                 font=("Helvetica", 18, "bold"), width=300, height=80, fg_color="red")
emergency_button.pack(pady=20)

right_frame = ctk.CTkFrame(main_frame, corner_radius=10)
right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

right_title = ctk.CTkLabel(right_frame, text="Controlli Luci", font=("Helvetica", 20))
right_title.pack(pady=10)

strobe_button = ctk.CTkButton(right_frame, text="STROBO", font=("Helvetica", 18),
                              width=300, height=80)
strobe_button.bind("<ButtonPress-1>", press_strobe_effect)
strobe_button.bind("<ButtonRelease-1>", release_strobe_effect)
strobe_button.pack(pady=10)

light_mode_button = ctk.CTkButton(right_frame, text="Effetti: OFF", command=toggle_light_mode,
                                  font=("Helvetica", 18), width=300, height=80)
light_mode_button.pack(pady=10)

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

status_frame = ctk.CTkFrame(control_tab, corner_radius=10)
status_frame.pack(pady=10, padx=20, fill="x")
status_label_main = ctk.CTkLabel(status_frame,
                                 text="Stato Arduino: " + ("Connesso" if arduino_connected else "Non Connesso"),
                                 font=("Helvetica", 16))
status_label_main.pack(side="left", padx=10)

root.mainloop()