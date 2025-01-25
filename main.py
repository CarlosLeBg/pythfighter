import os
import sys
import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter.font import Font
import subprocess
import logging
from tkinter.ttk import Style

# Configuration du logger
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()

class PythFighterLauncher:
    def __init__(self):
        # Configuration de la fenêtre principale
        self.root = tk.Tk()
        self.root.title("PythFighter Launcher")
        self.root.geometry("1280x720")
        self.root.configure(bg="#181825")
        self.root.attributes("-fullscreen", True)

        # Configuration des polices
        self.title_font = Font(family="Verdana", size=60, weight="bold")
        self.button_font = Font(family="Verdana", size=20)
        self.text_font = Font(family="Verdana", size=14)

        # Création des éléments de l'interface
        self.create_widgets()

    def create_widgets(self):
        # Titre principal
        title_label = tk.Label(self.root, text="PythFighter", font=self.title_font, fg="#E4E4E7", bg="#181825")
        title_label.pack(pady=50)

        # Style des boutons
        button_style = {
            "font": self.button_font,
            "bg": "#3B82F6",
            "fg": "white",
            "activebackground": "#2563EB",
            "activeforeground": "white",
            "relief": "flat",
            "cursor": "hand2",
            "bd": 0,
            "highlightthickness": 0
        }

        # Bouton de lancement
        self.launch_button = tk.Button(
            self.root,
            text="Lancer le jeu",
            command=self.run_game,
            **button_style
        )
        self.launch_button.pack(pady=20, ipadx=50, ipady=20)

        # Bouton pour afficher l'aide
        help_button = tk.Button(
            self.root,
            text="Aide",
            command=self.show_help,
            **button_style
        )
        help_button.pack(pady=15, ipadx=50, ipady=20)

        # Bouton pour afficher les crédits
        credits_button = tk.Button(
            self.root,
            text="Crédits",
            command=self.show_credits,
            **button_style
        )
        credits_button.pack(pady=15, ipadx=50, ipady=20)

        # Bouton pour quitter
        quit_button = tk.Button(
            self.root,
            text="Quitter",
            command=self.root.quit,
            **button_style
        )
        quit_button.pack(pady=15, ipadx=50, ipady=20)

    def run_game(self):
        # Chemin du fichier selector.py
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "selector.py")
        logger.info("Lancement du jeu...")

        if not os.path.exists(script_path):
            logger.error(f"Fichier introuvable : {script_path}")
            messagebox.showerror("Erreur", f"Impossible de trouver le fichier : {script_path}")
            return

        try:
            subprocess.run([sys.executable, script_path], check=True)
            logger.info("Jeu lancé avec succès.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors du lancement : {e}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors du lancement du jeu.\n{e}")
        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")
            messagebox.showerror("Erreur", f"Une erreur inattendue s'est produite.\n{e}")

    def show_help(self):
        help_window = Toplevel(self.root)
        help_window.title("Aide")
        help_window.geometry("800x600")
        help_window.configure(bg="#1F2937")

        help_label = tk.Label(
            help_window, 
            text=(
                "Bienvenue dans l'aide de PythFighter!\n\n"
                "- Cliquez sur 'Lancer le jeu' pour commencer.\n"
                "- Utilisez les flèches pour naviguer dans le jeu.\n"
                "- Consultez les crédits pour plus d'informations."
            ), 
            font=self.text_font, 
            fg="#D1D5DB", 
            bg="#1F2937", 
            justify="left",
            wraplength=700
        )
        help_label.pack(pady=20, padx=20)

        close_button = tk.Button(
            help_window,
            text="Fermer",
            font=self.button_font,
            bg="#EF4444",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            command=help_window.destroy
        )
        close_button.pack(pady=20, ipadx=20, ipady=10)

    def show_credits(self):
        credits_window = Toplevel(self.root)
        credits_window.title("Crédits")
        credits_window.geometry("800x600")
        credits_window.configure(bg="#1F2937")

        credits_label = tk.Label(
            credits_window, 
            text=(
                "Crédits de PythFighter\n\n"
                "Développé par :\n"
                "- Développeur 1\n"
                "- Développeur 2\n\n"
                "Merci d'avoir joué!"
            ), 
            font=self.text_font, 
            fg="#D1D5DB", 
            bg="#1F2937", 
            justify="center",
            wraplength=700
        )
        credits_label.pack(pady=20, padx=20)

        close_button = tk.Button(
            credits_window,
            text="Fermer",
            font=self.button_font,
            bg="#EF4444",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            command=credits_window.destroy
        )
        close_button.pack(pady=20, ipadx=20, ipady=10)

    def run(self):
        logger.info("Lancement du launcher PythFighter.")
        self.root.mainloop()

# Point d'entrée
if __name__ == "__main__":
    try:
        launcher = PythFighterLauncher()
        launcher.run()
    except Exception as e:
        logger.critical(f"Erreur critique : {e}")
        sys.exit(1)
