import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
from typing import Tuple, List, Callable

class LauncherPythFighter:
    """Launcher principal pour le jeu PythFighter avec une interface graphique améliorée."""
    
    COLORS = {
        'background': '#1A1A2E',
        'primary': '#E94560',
        'secondary': '#16213E',
        'text': '#FFFFFF',
        'hover': '#FF6B6B',
        'shadow': '#121220'  # Couleur plus sombre pour l'ombre
    }

    FONTS = {
        'title': ("Arial Black", 100),
        'button': ("Arial", 30),
        'credits': ("Arial", 20)
    }

    def __init__(self) -> None:
        """Initialise le launcher avec une configuration de base."""
        self.root = tk.Tk()
        self.setup_window()
        self.create_canvas()
        self.create_interface()
        self.bind_keys()

    def setup_window(self) -> None:
        """Configure la fenêtre principale."""
        self.root.title("PythFighter Launcher")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.COLORS['background'])
        
        # Ajout d'une option pour quitter avec Escape
        self.root.bind('<Escape>', lambda e: self.confirm_quit())

    def create_canvas(self) -> None:
        """Crée et configure le canvas principal."""
        self.canvas = tk.Canvas(
            self.root,
            bg=self.COLORS['background'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_interface(self) -> None:
        """Crée l'interface utilisateur principale."""
        self._create_title()
        self._create_menu_buttons()
        self._create_version_info()

    def _create_title(self) -> None:
        """Crée le titre du jeu avec un effet d'ombre."""
        screen_width = self.root.winfo_screenwidth()
        # Plusieurs couches d'ombre pour un effet de profondeur
        offset = 3
        for i in range(3):
            self.canvas.create_text(
                screen_width // 2 + offset + i,
                150 + offset + i,
                text="PYTH FIGHTER",
                font=self.FONTS['title'],
                fill=self.COLORS['shadow']
            )
        # Texte principal
        self.canvas.create_text(
            screen_width // 2,
            150,
            text="PYTH FIGHTER",
            font=self.FONTS['title'],
            fill=self.COLORS['primary']
        )

    def _create_menu_buttons(self) -> None:
        """Crée les boutons du menu principal avec effets de survol."""
        menu_items: List[Tuple[str, Callable]] = [
            ("Démarrer", self.launch_game),
            ("Crédits", self.show_credits),
            ("Options", self.show_options),
            ("Quitter", self.confirm_quit)
        ]

        for i, (text, command) in enumerate(menu_items):
            button = tk.Button(
                self.root,
                text=text,
                font=self.FONTS['button'],
                bg=self.COLORS['secondary'],
                fg=self.COLORS['text'],
                activebackground=self.COLORS['primary'],
                command=command,
                relief=tk.FLAT,
                cursor="hand2"
            )
            
            # Ajout des effets de survol
            button.bind('<Enter>', lambda e, b=button: self._on_button_hover(b, True))
            button.bind('<Leave>', lambda e, b=button: self._on_button_hover(b, False))
            
            self.canvas.create_window(
                self.root.winfo_screenwidth() // 2,
                400 + (i * 100),
                window=button,
                width=400,
                height=70
            )

    def _create_version_info(self) -> None:
        """Ajoute les informations de version en bas de l'écran."""
        version_text = "Version 1.0.0 - © 2025 PythFighter Team"
        self.canvas.create_text(
            10, self.root.winfo_screenheight() - 10,
            text=version_text,
            font=("Arial", 10),
            fill=self.COLORS['text'],
            anchor="sw"
        )

    def _on_button_hover(self, button: tk.Button, entering: bool) -> None:
        """Gère l'effet de survol des boutons."""
        button.configure(
            bg=self.COLORS['hover'] if entering else self.COLORS['secondary']
        )

    def bind_keys(self) -> None:
        """Configure les raccourcis clavier."""
        self.root.bind('<Return>', lambda e: self.launch_game())
        self.root.bind('<c>', lambda e: self.show_credits())
        self.root.bind('<o>', lambda e: self.show_options())

    def launch_game(self) -> None:
        """Lance le jeu principal avec gestion d'erreurs améliorée."""
        game_path = os.path.join(os.path.dirname(__file__), "selector.py")
        try:
            subprocess.Popen([sys.executable, game_path])
            self.root.quit()
        except Exception as e:
            messagebox.showerror(
                "Erreur de lancement",
                f"Impossible de lancer le jeu:\n{str(e)}"
            )

    def show_credits(self) -> None:
        """Affiche les crédits avec une animation améliorée."""
        self.credits_window = tk.Toplevel(self.root)
        self.credits_window.attributes('-fullscreen', True)
        self.credits_window.configure(bg=self.COLORS['background'])
        
        credits_text = self._get_credits_text()
        
        self.credits_label = tk.Label(
            self.credits_window,
            text=credits_text,
            font=self.FONTS['credits'],
            bg=self.COLORS['background'],
            fg=self.COLORS['primary'],
            justify=tk.CENTER
        )
        self.credits_label.place(relx=0.5, rely=1.0, anchor=tk.S)

        # Ajout d'un bouton pour fermer les crédits
        close_button = tk.Button(
            self.credits_window,
            text="×",
            font=("Arial", 20),
            command=self.credits_window.destroy,
            bg=self.COLORS['primary'],
            fg=self.COLORS['text'],
            relief=tk.FLAT
        )
        close_button.place(x=20, y=20)

        self.credits_position = self.root.winfo_screenheight()
        self._animate_credits()

    def _get_credits_text(self) -> str:
        """Retourne le texte des crédits."""
        return """
        PythFighter - Un jeu de combat révolutionnaire

        Développé avec passion par l'équipe PythFighter

        Programmation:
        - Équipe de développement principale
        - Contributeurs de la communauté

        Design et Assets:
        - Direction artistique
        - Conception des personnages
        - Animation et effets visuels

        Audio:
        - Composition musicale
        - Design sonore
        - Voix et doublage

        Remerciements spéciaux:
        - Communauté Python
        - Nos testeurs dévoués
        - Tous nos joueurs

        PythFighter utilise des technologies open source.
        Merci à tous les contributeurs !
        """

    def _animate_credits(self) -> None:
        """Anime le défilement des crédits."""
        self.credits_position -= 2
        self.credits_label.place(relx=0.5, y=self.credits_position, anchor=tk.S)
        
        if self.credits_position > -self.credits_label.winfo_reqheight():
            self.credits_window.after(50, self._animate_credits)
        else:
            self.credits_window.destroy()

    def show_options(self) -> None:
        """Affiche le menu des options."""
        options_window = tk.Toplevel(self.root)
        options_window.title("Options")
        options_window.geometry("400x300")
        options_window.configure(bg=self.COLORS['background'])
        
        tk.Label(
            options_window,
            text="Options",
            font=self.FONTS['button'],
            bg=self.COLORS['background'],
            fg=self.COLORS['primary']
        ).pack(pady=20)
        
        # Exemple d'options
        options = [
            ("Plein écran", tk.BooleanVar(value=True)),
            ("Musique", tk.BooleanVar(value=True)),
            ("Effets sonores", tk.BooleanVar(value=True))
        ]
        
        for text, var in options:
            tk.Checkbutton(
                options_window,
                text=text,
                variable=var,
                font=("Arial", 12),
                bg=self.COLORS['background'],
                fg=self.COLORS['text'],
                selectcolor=self.COLORS['secondary']
            ).pack(pady=10)

    def confirm_quit(self) -> None:
        """Demande confirmation avant de quitter."""
        if messagebox.askyesno(
            "Quitter",
            "Voulez-vous vraiment quitter PythFighter ?"
        ):
            self.root.quit()

    def run(self) -> None:
        """Lance le launcher."""
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.run()

if __name__ == "__main__":
    main()