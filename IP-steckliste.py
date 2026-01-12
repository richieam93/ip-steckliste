import tkinter as tk
from tkinter import ttk
import requests
import json
import os

# Konfigurationsdatei
CONFIG_FILE = "config.json"

# Standardkonfiguration
DEFAULT_CONFIG = {
    "IP_ADRESSE": "192.168.41.100",
    "PORT": "80",
    "BENUTZERNAME": "admin",
    "PASSWORT": "302010",
    "NAME_1": "IF Kamera",
    "NAME_2": "CW Kamera",
    "NAME_3": "CW Box",
    "NAME_4": "Netzwerk"
}

# Globale Variable, um den Zustand der Steckdosen zu speichern
steckdosen_status = {1: 0, 2: 0, 3: 0, 4: 0}  # 0 = AUS, 1 = EIN

def load_config():
    """Lädt die Konfiguration aus der Datei."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return DEFAULT_CONFIG

def save_config(config):
    """Speichert die Konfiguration in der Datei."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Lade die Konfiguration beim Start
config = load_config()
IP_ADRESSE = config["IP_ADRESSE"]
PORT = config["PORT"]
BENUTZERNAME = config["BENUTZERNAME"]
PASSWORT = config["PASSWORT"]
NAME_1 = config["NAME_1"]
NAME_2 = config["NAME_2"]
NAME_3 = config["NAME_3"]
NAME_4 = config["NAME_4"]

def get_power_status():
    """Ruft den aktuellen Status aller Steckdosen ab."""
    global steckdosen_status
    url = f"http://{BENUTZERNAME}:{PASSWORT}@{IP_ADRESSE}/Set.cmd?CMD=GetPower"
    try:
        print(f"URL: {url}")
        antwort = requests.get(url)
        antwort.raise_for_status()
        print(f"Antwort Statuscode: {antwort.status_code}")
        print(f"Antwort Inhalt: {antwort.text}")

        # Annahme: Die Antwort enthält etwas wie "P60=1 P61=0 P62=1 P63=0"
        data = antwort.text
        for i in range(0, 4): # Assuming P60 to P63
            key = f'P6{i}'
            if f'{key}=1' in data:
                steckdosen_status[i+1] = 1
            else:
                steckdosen_status[i+1] = 0

        print(f"Aktueller Steckdosenstatus: {steckdosen_status}")

    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen des Steckdosenstatus: {e}")
        # Bei Fehler Standardwerte setzen, damit die GUI funktioniert.
        steckdosen_status = {1: 0, 2: 0, 3: 0, 4: 0}

def schalte_steckdose(steckdose, status):
    """Schaltet eine bestimmte Steckdose ein oder aus."""
    url = f"http://{BENUTZERNAME}:{PASSWORT}@{IP_ADRESSE}/Set.cmd?CMD=SetPower+P6{steckdose-1}={status}"
    try:
        print(f"URL: {url}")
        antwort = requests.get(url)  # Sende die Anfrage
        print(f"Antwort Statuscode: {antwort.status_code}")
        print(f"Antwort Inhalt: {antwort.text}")
        antwort.raise_for_status()  # Wirf einen Fehler für schlechte Statuscodes
        print(f"Steckdose {steckdose}: {status}")
        #steckdosen_status[steckdose] = status  # Aktualisiere den globalen Status
        return True  # Erfolgreich
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Schalten von Steckdose {steckdose}: {e}")
        return False  # Fehler

def update_button_text(button, steckdose):
    """Aktualisiert den Text des Buttons basierend auf dem aktuellen Status."""
    # Hier die Änderung: Nur noch den Namen der Steckdose
    button.config(text=f"{steckdosen_namen[steckdose]}")

def update_lampe(lampe, steckdose):
    """Aktualisiert die Farbe der Lampe basierend auf dem Status."""
    if steckdosen_status[steckdose] == 1:
        lampe.config(bg="green")
    else:
        lampe.config(bg="red")

def toggle_power(steckdose, button, lampe):
    """Schaltet die Steckdose um und aktualisiert den Button-Text und die Lampe."""
    if steckdosen_status[steckdose] == 0:
        status = 1
    else:
        status = 0

    if schalte_steckdose(steckdose, status):
        steckdosen_status[steckdose] = status # Update state AFTER successfully switching
        update_button_text(button, steckdose)
        update_lampe(lampe, steckdose)

def alle_schalten(status):
    """Schaltet alle Steckdosen gleichzeitig ein oder aus."""
    for steckdose in range(1, 5):
        if schalte_steckdose(steckdose, status):
            steckdosen_status[steckdose] = status
            update_button_text(buttons[steckdose-1], steckdose)
            update_lampe(lampen[steckdose-1], steckdose)

def save_settings():
    """Speichert die Einstellungen aus den Eingabefeldern."""
    global IP_ADRESSE, PORT, BENUTZERNAME, PASSWORT, NAME_1, NAME_2, NAME_3, NAME_4
    IP_ADRESSE = ip_adresse_entry.get()
    PORT = port_entry.get()
    BENUTZERNAME = benutzername_entry.get()
    PASSWORT = passwort_entry.get()
    NAME_1 = name_1_entry.get()
    NAME_2 = name_2_entry.get()
    NAME_3 = name_3_entry.get()
    NAME_4 = name_4_entry.get()

    config["IP_ADRESSE"] = IP_ADRESSE
    config["PORT"] = PORT
    config["BENUTZERNAME"] = BENUTZERNAME
    config["PASSWORT"] = PASSWORT
    config["NAME_1"] = NAME_1
    config["NAME_2"] = NAME_2
    config["NAME_3"] = NAME_3
    config["NAME_4"] = NAME_4
    save_config(config)

    # Aktualisiere die globalen Variablen und die GUI
    update_global_vars()
    update_button_names()

    print("Einstellungen gespeichert!")

def update_global_vars():
    """Aktualisiert die globalen Variablen mit den neuen Werten aus der Konfiguration."""
    global IP_ADRESSE, PORT, BENUTZERNAME, PASSWORT, NAME_1, NAME_2, NAME_3, NAME_4
    global steckdosen_namen

    IP_ADRESSE = config["IP_ADRESSE"]
    PORT = config["PORT"]
    BENUTZERNAME = config["BENUTZERNAME"]
    PASSWORT = config["PASSWORT"]
    NAME_1 = config["NAME_1"]
    NAME_2 = config["NAME_2"]
    NAME_3 = config["NAME_3"]
    NAME_4 = config["NAME_4"]

    steckdosen_namen = {
        1: NAME_1,
        2: NAME_2,
        3: NAME_3,
        4: NAME_4
    }

def update_button_names():
    """Aktualisiert die Namen der Buttons."""
    for i in range(1, 5):
        # Hier die Änderung: Nur noch den Namen der Steckdose
        buttons[i-1].config(text=f"{steckdosen_namen[i]}")
        labels[i-1].config(text=f"{steckdosen_namen[i]}:") # Aktualisiere auch die Label-Texte

def update_gui():
    """Aktualisiert die GUI-Elemente basierend auf dem aktuellen Steckdosenstatus."""
    for i in range(1, 5):
        update_button_text(buttons[i-1], i)
        update_lampe(lampen[i-1], i)


# GUI erstellen
fenster = tk.Tk()
fenster.title("IP Power 9258 Steuerung Foto-Studio")

# Tab-Control erstellen
tab_control = ttk.Notebook(fenster)

# Tab für die Steuerung
steuerung_tab = ttk.Frame(tab_control)
tab_control.add(steuerung_tab, text="Steuerung")

# Tab für die Einstellungen
einstellungen_tab = ttk.Frame(tab_control)
tab_control.add(einstellungen_tab, text="Einstellungen")

tab_control.pack(expand=1, fill="both")

# Steckdosen-Namen (wird initial aus der Konfiguration geladen)
steckdosen_namen = {
    1: NAME_1,
    2: NAME_2,
    3: NAME_3,
    4: NAME_4
}

# Listen für Buttons und Lampen
buttons = []
lampen = []
labels = [] # Liste für die Labels

# Schleife zum Erstellen der Buttons und Lampen für jede Steckdose
for i in range(1, 5):
    # Frame für jede Steckdose
    frame = tk.Frame(steuerung_tab)
    frame.pack(pady=5)

    # Label für die Steckdose
    label = tk.Label(frame, text=f"{steckdosen_namen[i]}:")
    label.pack(side=tk.LEFT, padx=5)
    labels.append(label) # Füge das Label zur Liste hinzu

    # Lampe erstellen
    lampe = tk.Canvas(frame, bg="red", height=20, width=20, highlightthickness=0)
    lampe.pack(side=tk.LEFT, padx=5)
    lampen.append(lampe)

    # Button erstellen
    button = tk.Button(frame, text=f"{steckdosen_namen[i]}") # Geändert
    button.config(command=lambda i=i, lampe=lampe, button=button: toggle_power(i, button, lampe))
    button.pack(side=tk.LEFT, padx=5)
    buttons.append(button)

    #Ausschalter entfernen
    #aus_button = tk.Button(frame, text="AUS", command=lambda i=i, button=button, lampe=lampe: ausschalten(i, button, lampe))
    #aus_button.pack(side=tk.LEFT, padx=5)

# Globaler Schalter
global_frame = tk.Frame(steuerung_tab)
global_frame.pack(pady=10)
global_ein = tk.Button(global_frame, text="ALLE EIN", command=lambda: alle_schalten(1))
global_ein.pack(side=tk.LEFT, padx=5)
global_aus = tk.Button(global_frame, text="ALLE AUS", command=lambda: alle_schalten(0))
global_aus.pack(side=tk.LEFT, padx=5)

# --- Einstellungen Tab ---

einstellungen_frame = tk.Frame(einstellungen_tab)
einstellungen_frame.pack(padx=20, pady=20)

# IP-Adresse
ip_adresse_label = tk.Label(einstellungen_frame, text="IP-Adresse:")
ip_adresse_label.grid(row=0, column=0, sticky="w")
ip_adresse_entry = tk.Entry(einstellungen_frame)
ip_adresse_entry.grid(row=0, column=1, sticky="e")
ip_adresse_entry.insert(0, IP_ADRESSE)

# Port
port_label = tk.Label(einstellungen_frame, text="Port:")
port_label.grid(row=1, column=0, sticky="w")
port_entry = tk.Entry(einstellungen_frame)
port_entry.grid(row=1, column=1, sticky="e")
port_entry.insert(0, PORT)

# Benutzername
benutzername_label = tk.Label(einstellungen_frame, text="Benutzername:")
benutzername_label.grid(row=2, column=0, sticky="w")
benutzername_entry = tk.Entry(einstellungen_frame)
benutzername_entry.grid(row=2, column=1, sticky="e")
benutzername_entry.insert(0, BENUTZERNAME)

# Passwort
passwort_label = tk.Label(einstellungen_frame, text="Passwort:")
passwort_label.grid(row=3, column=0, sticky="w")
passwort_entry = tk.Entry(einstellungen_frame, show="*")  # Passwort verbergen
passwort_entry.grid(row=3, column=1, sticky="e")
passwort_entry.insert(0, PASSWORT)

# Namen der Steckdosen
name_1_label = tk.Label(einstellungen_frame, text="Name Steckdose 1:")
name_1_label.grid(row=4, column=0, sticky="w")
name_1_entry = tk.Entry(einstellungen_frame)
name_1_entry.grid(row=4, column=1, sticky="e")
name_1_entry.insert(0, NAME_1)

# Name der Steckdosen
name_2_label = tk.Label(einstellungen_frame, text="Name Steckdose 2:")
name_2_label.grid(row=5, column=0, sticky="w")
name_2_entry = tk.Entry(einstellungen_frame)
name_2_entry.grid(row=5, column=1, sticky="e")
name_2_entry.insert(0, NAME_2)

# Name der Steckdosen
name_3_label = tk.Label(einstellungen_frame, text="Name Steckdose 3:")
name_3_label.grid(row=6, column=0, sticky="w")
name_3_entry = tk.Entry(einstellungen_frame)
name_3_entry.grid(row=6, column=1, sticky="e")
name_3_entry.insert(0, NAME_3)

# Name der Steckdosen
name_4_label = tk.Label(einstellungen_frame, text="Name Steckdose 4:")
name_4_label.grid(row=7, column=0, sticky="w")
name_4_entry = tk.Entry(einstellungen_frame)
name_4_entry.grid(row=7, column=1, sticky="e")
name_4_entry.insert(0, NAME_4)

# Speicher-Button
speichern_button = tk.Button(einstellungen_frame, text="Einstellungen speichern", command=save_settings)
speichern_button.grid(row=8, column=0, columnspan=2, pady=10)

# Initialisiere die GUI mit den Werten aus der Konfiguration
update_global_vars()
update_button_names()

# Rufe den Status der Steckdosen beim Start ab
get_power_status()
update_gui() # GUI entsprechend anpassen

# Fenster starten
fenster.mainloop()
