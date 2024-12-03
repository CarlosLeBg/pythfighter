import tkinter as tk
import os
import subprocess
import requests
import logging
from tkinter import messagebox
from PIL import Image, ImageTk
from loguru import logger
import config

class HTTPHandler:
    def __init__(self, url):
        self.url = url

    def get_json(self):
        """Effectue une requête GET et renvoie les données JSON avec gestion des erreurs HTTP."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Erreur HTTP : {http_err}")
            messagebox.showerror("Erreur HTTP", f"Erreur lors de la requête : {http_err}")
        except requests.exceptions.ConnectionError:
            logger.error("Erreur réseau : Impossible de se connecter.")
            messagebox.showerror("Erreur réseau", "Impossible de se connecter au serveur. Vérifiez votre connexion internet.")
        except requests.exceptions.Timeout:
            logger.error("Délai d'attente dépassé.")
            messagebox.showerror("Erreur de connexion", "La connexion a expiré. Réessayez plus tard.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de requête : {e}")
            messagebox.showerror("Erreur inconnue", "Une erreur inconnue est survenue.")
        return None

class PythFighterLauncher:
    def __init__(self, master):
        self.master = master
        self.master.title("Launcher du jeu PythFighter")
        self.master.geometry("1920x1080")
        self.master.configure(bg="#222")
        self.master.minsize(400, 500)

        self.setup_logger()
        self.logo = self.load_logo(config.LOGO_PATH)
        self.logo_label = tk.Label(master, image=self.logo, bg="#222")
        self.logo_label.pack(pady=(20, 10))

        self.create_buttons()
        self.status_var = tk.StringVar(value="Prêt à lancer le jeu.")
        self.status_label = tk.Label(master, textvariable=self.status_var, font=("Arial", 12), bg="#222", fg="white")
        self.status_label.pack(pady=20)

        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def setup_logger(self):
        logger.add("launcher.log", rotation="1 MB")
        logger.info("Lancement du launcher PythFighter.")

    def load_logo(self, logo_path):
        try:
            image = Image.open(logo_path)
            return ImageTk.PhotoImage(image.resize((250, 125)))
        except Exception as e:
            logger.error(f"Erreur lors du chargement du logo : {e}")
            return None

    def create_buttons(self):
        """Création et configuration des boutons principaux avec effets de survol."""
        self.button_frame = tk.Frame(self.master, bg="#222")
        self.button_frame.pack(pady=20, padx=20)

        button_config = {
            "font": ("Sans-Serif", 16, "bold"),
            "bg": "#444", "fg": "white", "relief": "flat", "padx": 20, "pady": 10
        }

        self.launch_button = tk.Button(
            self.button_frame, text="Lancer le jeu", command=self.launch_game, **button_config
        )
        self.launch_button.grid(row=0, column=0, padx=10)

        self.check_updates_button = tk.Button(
            self.button_frame, text="Vérifier les mises à jour", command=self.check_updates, **button_config
        )
        self.check_updates_button.grid(row=0, column=1, padx=10)

        self.help_button = tk.Button(
            self.button_frame, text="Aide", command=self.show_help, **button_config
        )
        self.help_button.grid(row=0, column=2, padx=10)

        for button in [self.launch_button, self.check_updates_button, self.help_button]:
            button.bind("<Enter>", self.animate_button_in)
            button.bind("<Leave>", self.animate_button_out)

    def launch_game(self):
        self.status_var.set("Lancement du jeu...")
        self.launch_button.config(state=tk.DISABLED)
        self.master.after(100, self._run_game)

    def _run_game(self):
        try:
            subprocess.run(["python", "./game.py"], check=True)
            self.status_var.set("Jeu lancé avec succès!")
            logger.info("Jeu lancé avec succès.")
        except subprocess.CalledProcessError as e:
            self.status_var.set(f"Erreur lors du lancement : {e}")
            logger.error(f"Erreur lors du lancement : {e}")
        except Exception as e:
            self.status_var.set(f"Erreur inconnue : {e}")
            logger.error(f"Erreur inconnue : {e}")
        finally:
            self.launch_button.config(state=tk.NORMAL)

    def check_updates(self):
        http_handler = HTTPHandler(config.REPO_URL)
        data = http_handler.get_json()
        
        if data:
            latest_version = data.get("tag_name", "0.0")
            logger.info(f"Vérification des mises à jour : version actuelle : {latest_version}")

            if latest_version != config.CURRENT_VERSION:
                messagebox.showinfo("Mise à jour disponible", f"Nouvelle version ({latest_version}) disponible!")
                self.status_var.set("Nouvelle mise à jour disponible.")
            else:
                messagebox.showinfo("Pas de mise à jour", "Vous avez la dernière version.")
                self.status_var.set("Aucune mise à jour disponible.")

    def show_help(self):
        help_text = (
            "PythFighter Launcher\n\n"
            "Utilisez ce launcher pour lancer le jeu PythFighter.\n"
            "Cliquez sur 'Lancer le jeu' pour démarrer.\n"
            "Cliquez sur 'Vérifier les mises à jour' pour vérifier les dernières versions.\n"
            "Si vous avez besoin d'aide supplémentaire, consultez la documentation du jeu."
            "CARLOS IS SO BESTTTTTT"
        )
        messagebox.showinfo("Aide", help_text)

    def confirm_exit(self):
        if messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter ?"):
            logger.info("Fermeture du launcher.")
            self.master.quit()

    def animate_button_in(self, event):
        event.widget.config(bg="#666", relief="raised", highlightbackground="#555")
        event.widget['font'] = ("Arial", 18, "bold")

    def animate_button_out(self, event):
        event.widget.config(bg="#444", relief="flat")
        event.widget['font'] = ("Arial", 16, "bold")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythFighterLauncher(root)
    root.mainloop()
