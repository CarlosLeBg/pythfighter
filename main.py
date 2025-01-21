import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
import subprocess
import logging

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
        self.root.geometry("400x300")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)

        # Configuration des polices
        self.title_font = Font(family="Helvetica", size=20, weight="bold")
        self.button_font = Font(family="Helvetica", size=12)

        # Création des éléments de l'interface
        self.create_widgets()

    def create_widgets(self):
        # Titre principal
        title_label = tk.Label(self.root, text="PythFighter", font=self.title_font, fg="white", bg="#2c3e50")
        title_label.pack(pady=20)

        # Bouton de lancement
        self.launch_button = tk.Button(
            self.root,
            text="Lancer le jeu",
            font=self.button_font,
            bg="#16a085",
            fg="white",
            activebackground="#1abc9c",
            activeforeground="white",
            command=self.run_game
        )
        self.launch_button.pack(pady=20)

        # Animations sur le bouton
        self.launch_button.bind("<Enter>", lambda e: self.animate_button(self.launch_button, True))
        self.launch_button.bind("<Leave>", lambda e: self.animate_button(self.launch_button, False))

        # Bouton pour quitter
        quit_button = tk.Button(
            self.root,
            text="Quitter",
            font=self.button_font,
            bg="#c0392b",
            fg="white",
            activebackground="#e74c3c",
            activeforeground="white",
            command=self.root.quit
        )
        quit_button.pack(pady=10)

    def run_game(self):
        # Chemin du fichier selector.py
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "selector.py")
        logger.info("Lancement du jeu...")

        if not os.path.exists(script_path):
            logger.error(f"Fichier introuvable : {script_path}")
            messagebox.showerror("Erreur", f"Impossible de trouver le fichier : {script_path}")
            return

        try:
            # Exécution du script avec subprocess
            subprocess.run([sys.executable, script_path], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors du lancement : {e}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors du lancement du jeu.\n{e}")
        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")
            messagebox.showerror("Erreur", f"Une erreur inattendue s'est produite.\n{e}")

    def animate_button(self, button, hover):
        # Animation du bouton (changement de couleur au survol)
        try:
            bg_start = button["bg"]
            bg_end = "#1abc9c" if hover else "#16a085"
            new_bg = self.interpolate_color(bg_start, bg_end, 0.3 if hover else 1)
            button.configure(bg=new_bg)
        except Exception as e:
            logger.warning(f"Erreur dans l'animation du bouton : {e}")

    @staticmethod
    def interpolate_color(start, end, factor):
        def hex_to_rgb(hex_color):
            if not hex_color.startswith("#") or len(hex_color) != 7:
                return (255, 255, 255)  # Blanc par défaut
            return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

        def rgb_to_hex(rgb_color):
            return "#{:02x}{:02x}{:02x}".format(*rgb_color)

        start_rgb = hex_to_rgb(start)
        end_rgb = hex_to_rgb(end)
        blended_rgb = tuple(
            int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * factor) for i in range(3)
        )
        return rgb_to_hex(blended_rgb)

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
