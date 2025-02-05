import os
import sys
import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter.font import Font
import subprocess
import logging
from tkinter import ttk
from tkinter.ttk import Style

# Configuration des couleurs
class Colors:
    BACKGROUND = "#181825"
    BUTTON_BG = "#3B82F6"
    BUTTON_ACTIVE_BG = "#2563EB"
    BUTTON_TEXT = "white"
    TITLE_TEXT = "#E4E4E7"
    HELP_TEXT = "#D1D5DB"
    ERROR_BG = "#EF4444"
    ERROR_ACTIVE_BG = "#B91C1C"
    MODAL_BG = "#1F2937"

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
        self.root = tk.Tk()
        self.root.title("PythFighter Launcher")
        self.root.geometry("1280x720")
        self.root.configure(bg=Colors.BACKGROUND)
        self.root.resizable(True, True)  # Rendre la fenêtre redimensionnable

        self.title_font = Font(family="Verdana", size=60, weight="bold")
        self.button_font = Font(family="Verdana", size=20)
        self.text_font = Font(family="Verdana", size=14)

        self.create_widgets()

    def create_widgets(self):
        # Titre principal
        title_label = tk.Label(self.root, text="PythFighter", font=self.title_font, fg=Colors.TITLE_TEXT, bg=Colors.BACKGROUND)
        title_label.grid(row=0, column=0, pady=50)

        button_style = {
            "font": self.button_font,
            "bg": Colors.BUTTON_BG,
            "fg": Colors.BUTTON_TEXT,
            "activebackground": Colors.BUTTON_ACTIVE_BG,
            "activeforeground": Colors.BUTTON_TEXT,
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
        self.launch_button.grid(row=1, column=0, pady=20, ipadx=50, ipady=20)

        # Bouton pour afficher l'aide
        help_button = tk.Button(
            self.root,
            text="Aide",
            command=self.show_help,
            **button_style
        )
        help_button.grid(row=2, column=0, pady=15, ipadx=50, ipady=20)

        # Bouton pour afficher les crédits
        credits_button = tk.Button(
            self.root,
            text="Crédits",
            command=self.show_credits,
            **button_style
        )
        credits_button.grid(row=3, column=0, pady=15, ipadx=50, ipady=20)

        # Bouton pour quitter
        quit_button = tk.Button(
            self.root,
            text="Quitter",
            command=self.root.quit,
            **button_style
        )
        quit_button.grid(row=4, column=0, pady=15, ipadx=50, ipady=20)

    def show_modal(self, title, content):
        modal_window = Toplevel(self.root)
        modal_window.title(title)
        modal_window.geometry("800x600")
        modal_window.configure(bg=Colors.MODAL_BG)
        
        content_label = tk.Label(modal_window, text=content, font=self.text_font, fg=Colors.HELP_TEXT, bg=Colors.MODAL_BG, justify="left", wraplength=700)
        content_label.pack(pady=20, padx=20)

        close_button = tk.Button(modal_window, text="Fermer", font=self.button_font, bg=Colors.ERROR_BG, fg=Colors.BUTTON_TEXT, activebackground=Colors.ERROR_ACTIVE_BG, activeforeground=Colors.BUTTON_TEXT, command=modal_window.destroy)
        close_button.pack(pady=20, ipadx=20, ipady=10)

    def show_help(self):
        help_content = (
            "Bienvenue dans l'aide de PythFighter!\n\n"
            "- Cliquez sur 'Lancer le jeu' pour commencer.\n"
            "- Utilisez les flèches pour naviguer dans le jeu.\n"
            "- Consultez les crédits pour plus d'informations."
        )
        self.show_modal("Aide", help_content)

    def show_credits(self):
        credits_content = (
            "Crédits de PythFighter\n\n"
            "Développé par :\n"
            "- Développeur 1\n"
            "- Développeur 2\n\n"
            "Merci d'avoir joué!"
        )
        self.show_modal("Crédits", credits_content)

    def show_loading(self):
        self.spinner = ttk.Progressbar(self.root, mode="indeterminate")
        self.spinner.grid(row=5, column=0, pady=30)
        self.spinner.start()

    def hide_loading(self):
        self.spinner.stop()
        self.spinner.grid_forget()

    def run_game(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selector.py")
        logger.info("Lancement du jeu...")

        if not os.path.exists(script_path):
            logger.error(f"Fichier introuvable : {script_path}")
            messagebox.showerror("Erreur", f"Impossible de trouver le fichier : {script_path}")
            return

        try:
            self.show_loading()
            subprocess.run([sys.executable, script_path], check=True)
            logger.info("Jeu lancé avec succès.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors du lancement : {e}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors du lancement du jeu.\n{e}")
        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")
            messagebox.showerror("Erreur", f"Une erreur inattendue s'est produite.\n{e}")
        finally:
            self.hide_loading()

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
