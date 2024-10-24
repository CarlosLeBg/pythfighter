import tkinter as tk
import subprocess

def launch_other_script():
    subprocess.Popen(["python", "C:/chemin/vers/ton_script.py"])

def looop():
    root = tk.Tk()
    root.title("Launcher du jeu PythFighter")

    root.geometry("500x600")
    root.resizable(False, False)

    logo = tk.PhotoImage(file=r"C:\Users\carla\Downloads\pythfighter\src\assets\logo.png")

    logom = tk.Label(root, image=logo)
    logom.pack(pady=(10, 0))  # Met l'image en haut avec une légère marge

    launch_button = tk.Button(root, text="Lancer le jeu", command=launch_other_script,
                              font=("Arial", 16), bg="#333", fg="white", relief="groove", padx=20, pady=10)
    launch_button.pack(pady=30)  # Beau bouton stylé avec marges ajustées

    root.mainloop()

looop()
