import tkinter as tk

def launch_other_script():
    # Commande pour lancer un autre script Python
    pass

def looop():
    root = tk.Tk()
    root.title("Launcher du jeu PythFighter")

    root.geometry("500x600")
    root.resizable(False, False)

    logo = tk.PhotoImage(file=r"C:\Users\carla\Downloads\pythfighter\src\assets\logo.png")

    # Redimensionnement de l'image en la forçant dans une taille spécifique
    logo = logo.subsample(2, 2)  # Redimensionne en divisant la taille de l'image par 2

    logom = tk.Label(root, image=logo)
    logom.pack(pady=(10, 0))

    launch_button = tk.Button(root, text="Lancer le jeu", command=launch_other_script,
                              font=("Arial", 16), bg="#333", fg="white", relief="groove", padx=20, pady=10)
    launch_button.pack(pady=30)

    root.mainloop()

looop()
