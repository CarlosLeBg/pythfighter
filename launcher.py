import tkinter as tk
import os

def launch_other_script():
    os.system("python ./main.py")  # Lancement du script main.py dans le dossier parent

def looop():
    root = tk.Tk()
    root.title("Launcher du jeu PythFighter")

    root.geometry("500x600")
    root.resizable(False, False)

    # Chemin relatif de l'image par rapport au script launcher.py
    logo_path = os.path.join(".", "src", "assets", "logo.png")
    logo = tk.PhotoImage(file=logo_path)

    logo = logo.subsample(2, 2)  # Redimensionner l'image

    logom = tk.Label(root, image=logo)
    logom.pack(pady=(10, 0))

    launch_button = tk.Button(root, text="Lancer le jeu", command=launch_other_script,
                              font=("Arial", 16), bg="#333", fg="white", relief="groove", padx=20, pady=10)
    launch_button.pack(pady=30)

    root.mainloop()

looop()
