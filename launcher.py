import tkinter as tk

def looop():
    root = tk.Tk()
    root.title("Launcher du jeu PythFighter")

    logo = tk.PhotoImage(file=r"C:\Users\carla\Downloads\pythfighter\src\assets\logo.png")

    logom = tk.Label(root, image=logo)
    logom.pack(padx=20, pady=20)

    root.geometry("500x500")  # Taille fixe pour l'équilibre visuel
    root.resizable(False, False)  # Désactiver le redimensionnement pour garder un design propre

    root.mainloop()

looop()
