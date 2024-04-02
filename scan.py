import sqlite3
import time
from pathlib import Path
from tkinter import messagebox
import tkinter as tk
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


OUTPUT_PATH = Path(__file__).parent
PHOTO_PATH = OUTPUT_PATH / "Photos"

IDTOLOGING = 32
Scanning = False
Scanned = False

connexion = sqlite3.connect(OUTPUT_PATH / "Users.db")
new_cur = connexion.cursor()
new_cur.execute(f"""
        CREATE TABLE IF NOT EXISTS Users (
            IDs INTEGER,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL);
    """)
connexion.commit()

root = tk.Tk()
root.title("Badge projet")
root.geometry("300x200")

welcome = tk.Label(root, text="Welcome !")
id_label_l = tk.Label(root, text="ID:")
name_label = tk.Label(root, text="Nom :")
lastname_label = tk.Label(root, text="Prenom :")
name_entry = tk.Entry(root)
lastname_entry = tk.Entry(root)
register_button = tk.Button(root, text="Register")

scanning_label = tk.Label(root, text="Waiting for badge...")
scanning_label.pack()

def Login(id):
    global Scanning
    Scanning = True
    connexion = sqlite3.connect(OUTPUT_PATH / "Users.db")
    new_cur = connexion.cursor()
    new_cur.execute(f"""SELECT nom, prenom FROM Users WHERE IDs = '{id}'""")
    user_data = new_cur.fetchone()
    connexion.close()
    
    scanning_label.pack_forget()

    if user_data:
        welcome.pack()
        id_label_l.config(text="ID: " + str(id))
        name_label.config(text="Nom : " + str(user_data[0]))
        lastname_label.config(text="Prenom : " + str(user_data[1]))
        id_label_l.pack()
        name_label.pack()
        lastname_label.pack()
        Scanning = False
    else:
        DisplayRegisterMenu(id)

def DisplayRegisterMenu(id):
    id_label_l.pack_forget()
    welcome.pack_forget()
    name_label.pack()
    name_entry.pack()
    lastname_label.pack()
    lastname_entry.pack()
    register_button.pack()

def Register(id):
    global Scanning
    connexion = sqlite3.connect(OUTPUT_PATH / "Users.db")
    new_cur = connexion.cursor()
    new_cur.execute("INSERT INTO Users (IDs, nom, prenom) VALUES (?,?,?)",(int(id), name_entry.get(), lastname_entry.get()))
    connexion.commit()
    messagebox.showinfo("Registration Successful", "User registered successfully.")
    connexion.close()

    scanning_label.pack()
    name_entry.pack_forget()
    lastname_entry.pack_forget()
    register_button.pack_forget()
    Scanning = False

register_button.config(command=lambda: Register(IDTOLOGING))


reader = SimpleMFRC522()


def scanning_loop():
    global IDTOLOGING
    while True:
        if not Scanning and IDTOLOGING != 0:
            try:
                id, text = reader.read()
                IDTOLOGING = id
                print(id)
                print(text)
                Login(IDTOLOGING)
            finally:
                GPIO.cleanup()
            time.sleep(1)

scanning_thread = threading.Thread(target=scanning_loop, daemon=True)
scanning_thread.start() #Start waiting for badge

root.mainloop()
