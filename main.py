import tkinter as tk
import os
import subprocess

class PythFighterLauncher:
    def __init__(self, master):
        self.master = master
        self.master.title("Launcher du jeu PythFighter")
        self.master.geometry("500x600")
        self.master.resizable(False, False)

        # Chargement du logo
        logo_path = os.path.join(".", "src", "assets", "logo.png")
        self.logo = tk.PhotoImage(file=logo_path).subsample(2, 2)
        self.logo_label = tk.Label(master, image=self.logo)
        self.logo_label.pack(pady=(10, 0))

        # Configuration du bouton de lancement
        self.launch_button = tk.Button(
            master, text="Lancer le jeu", command=self.launch_game,
            font=("Arial", 16), bg="#333", fg="white", relief="groove", padx=20, pady=10
        )
        self.launch_button.pack(pady=30)

        # Animation des boutons
        self.launch_button.bind("<Enter>", self.animate_button)
        self.launch_button.bind("<Leave>", self.reset_button)

        # Ajout d'un menu
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Fichier", menu=self.file_menu)
        self.file_menu.add_command(label="Quitter", command=master.quit)

        # Message d'état
        self.status_var = tk.StringVar(value="Prêt à lancer le jeu.")
        self.status_label = tk.Label(master, textvariable=self.status_var, font=("Arial", 12))
        self.status_label.pack(pady=20)

    def launch_game(self):
        self.status_var.set("Lancement du jeu...")
        try:
            subprocess.run(["python", "./pythfighter/main.py"], check=True)
            self.status_var.set("Jeu lancé avec succès!")
        except subprocess.CalledProcessError as e:
            self.status_var.set(f"Erreur lors du lancement : {e}")
        except Exception as e:
            self.status_var.set(f"Erreur inconnue : {e}")

    def animate_button(self, event):
        event.widget.config(bg="#444", fg="white", relief="sunken")

    def reset_button(self, event):
        event.widget.config(bg="#333", fg="white", relief="groove")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythFighterLauncher(root)
    root.mainloop()
