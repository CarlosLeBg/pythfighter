import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import pygame
from typing import Tuple, List, Callable
import time

class ControllerManager:
    """Gère les entrées des manettes."""

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print(f"Nombre de manettes détectées : {len(self.joysticks)}")
        for joystick in self.joysticks:
            joystick.init()
            print(f"Manette {joystick.get_id()} : {joystick.get_name()}")
        self.primary_joystick = self.joysticks[0] if self.joysticks else None

    def get_input(self):
        pygame.event.pump()
        return [([joystick.get_button(i) for i in range(joystick.get_numbuttons())],
                 [joystick.get_axis(i) for i in range(joystick.get_numaxes())]) for joystick in self.joysticks]

    def get_primary_input(self):
        if self.primary_joystick:
            pygame.event.pump()
            return [self.primary_joystick.get_button(i) for i in range(self.primary_joystick.get_numbuttons())], \
                   [self.primary_joystick.get_axis(i) for i in range(self.primary_joystick.get_numaxes())]
        return [], []

class LauncherPythFighter:
    """Launcher principal pour le jeu PythFighter avec une interface graphique améliorée."""

    COLORS = {
        'background': '#1A1A2E',
        'primary': '#E94560',
        'secondary': '#16213E',
        'text': '#FFFFFF',
        'hover': '#FF6B6B',
        'shadow': '#121220'
    }

    FONTS = {
        'title': ("Arial Black", 100),
        'button': ("Arial", 30),
        'credits': ("Arial", 20)
    }

    NAV_COOLDOWN = 0.3  # Délai en secondes entre chaque mouvement du joystick

    def __init__(self) -> None:
        """Initialise le launcher avec une configuration de base."""
        self.root = tk.Tk()
        self.controller_manager = ControllerManager()
        self.last_nav_time = time.time()
        self.button_pressed = False
        self.setup_window()
        self.create_canvas()
        self.create_interface()
        self.bind_controller()

    def setup_window(self) -> None:
        """Configure la fenêtre principale."""
        self.root.title("PythFighter Launcher")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.COLORS['background'])
        self.root.bind("<Button-1>", lambda e: None)
        self.root.bind("<Key>", lambda e: None)

    def create_canvas(self) -> None:
        """Crée et configure le canvas principal."""
        self.canvas = tk.Canvas(self.root, bg=self.COLORS['background'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_interface(self) -> None:
        """Crée l'interface utilisateur principale."""
        self._create_title()
        self._create_menu_buttons()
        self._create_version_info()

    def _create_title(self) -> None:
        """Crée le titre du jeu avec un effet d'ombre."""
        screen_width = self.root.winfo_screenwidth()
        offset = 3
        for i in range(3):
            self.canvas.create_text(
                screen_width // 2 + offset + i,
                150 + offset + i,
                text="PYTH FIGHTER",
                font=self.FONTS['title'],
                fill=self.COLORS['shadow']
            )
        self.canvas.create_text(
            screen_width // 2,
            150,
            text="PYTH FIGHTER",
            font=self.FONTS['title'],
            fill=self.COLORS['primary']
        )

    def _create_menu_buttons(self) -> None:
        """Crée les boutons du menu principal avec effets de survol."""
        menu_items = [
            ("Démarrer", self.launch_game),
            ("Crédits", self.show_credits),
            ("Options", self.show_options),
            ("Quitter", self.confirm_quit)
        ]

        self.buttons = []
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
            self.canvas.create_window(
                self.root.winfo_screenwidth() // 2,
                400 + (i * 100),
                window=button,
                width=400,
                height=70
            )
            self.buttons.append(button)

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

    def bind_controller(self) -> None:
        """Configure les entrées de la manette."""
        self.selected_index = 0
        self._highlight_button(self.selected_index)
        self.check_controller()

    def _highlight_button(self, index: int) -> None:
        """Met en surbrillance le bouton sélectionné."""
        for i, button in enumerate(self.buttons):
            button.config(bg=self.COLORS['hover'] if i == index else self.COLORS['secondary'])

    def check_controller(self) -> None:
        """Vérifie les entrées de la manette."""
        buttons, axes = self.controller_manager.get_primary_input()
        current_time = time.time()

        if current_time - self.last_nav_time > self.NAV_COOLDOWN:
            if axes and (axes[1] < -0.5 or axes[3] < -0.5):  # Joystick gauche ou droit vers le haut
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self._highlight_button(self.selected_index)
                self.last_nav_time = current_time
            elif axes and (axes[1] > 0.5 or axes[3] > 0.5):  # Joystick gauche ou droit vers le bas
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self._highlight_button(self.selected_index)
                self.last_nav_time = current_time

        if buttons and len(buttons) > 0 and buttons[0] and not self.button_pressed:
            self.button_pressed = True
            self.buttons[self.selected_index].invoke()
        elif buttons and len(buttons) > 0 and not buttons[0]:
            self.button_pressed = False

        start_button_index = 9 if len(buttons) > 9 else (7 if len(buttons) > 7 else -1)
        if start_button_index >= 0 and buttons[start_button_index]:
            self.confirm_quit()

        self.root.after(50, self.check_controller)

    def launch_game(self) -> None:
        """Lance le jeu principal avec gestion d'erreurs améliorée."""
        game_path = os.path.join(os.path.dirname(__file__), "selector.py")
        try:
            subprocess.Popen([sys.executable, game_path])
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Erreur de lancement", f"Impossible de lancer le jeu:\n{str(e)}")

    def show_credits(self) -> None:
        """Affiche les crédits avec navigation par manette."""
        self.credits_window = tk.Toplevel(self.root)
        self.credits_window.attributes('-fullscreen', True)
        self.credits_window.configure(bg=self.COLORS['background'])
        self.credits_window.bind("<Button-1>", lambda e: None)

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

        instruction = tk.Label(
            self.credits_window,
            text="Appuyez sur Croix/A pour fermer",
            font=("Arial", 16),
            bg=self.COLORS['background'],
            fg=self.COLORS['text']
        )
        instruction.place(x=20, y=20)

        self.credits_position = self.root.winfo_screenheight()
        self._animate_credits()
        self._check_credits_controller()

    def _check_credits_controller(self):
        """Vérifie les entrées de la manette pour la fenêtre de crédits."""
        if hasattr(self, 'credits_window') and self.credits_window.winfo_exists():
            buttons, axes = self.controller_manager.get_primary_input()
            current_time = time.time()

            if current_time - self.last_nav_time > self.NAV_COOLDOWN:
                if axes and (axes[1] < -0.5 or axes[3] < -0.5):  # Joystick vers le haut
                    self.credits_position += 20
                    self.credits_label.place(relx=0.5, y=self.credits_position, anchor=tk.S)
                    self.last_nav_time = current_time
                elif axes and (axes[1] > 0.5 or axes[3] > 0.5):  # Joystick vers le bas
                    self.credits_position -= 20
                    self.credits_label.place(relx=0.5, y=self.credits_position, anchor=tk.S)
                    self.last_nav_time = current_time

            if buttons and len(buttons) > 0 and buttons[0]:  # Bouton Croix/A
                self.credits_window.destroy()

            self.credits_window.after(100, self._check_credits_controller)

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
        """Affiche le menu des options avec prise en charge de la manette."""
        options_window = tk.Toplevel(self.root)
        options_window.title("Options")
        options_window.geometry("400x300")
        options_window.configure(bg=self.COLORS['background'])
        options_window.bind("<Button-1>", lambda e: None)
        options_window.bind("<Key>", lambda e: None)

        tk.Label(
            options_window,
            text="Options",
            font=self.FONTS['button'],
            bg=self.COLORS['background'],
            fg=self.COLORS['primary']
        ).pack(pady=20)

        options_frame = tk.Frame(options_window, bg=self.COLORS['background'])
        options_frame.pack(pady=10)

        options = [
            ("Plein écran", tk.BooleanVar(value=True)),
            ("Musique", tk.BooleanVar(value=True)),
            ("Effets sonores", tk.BooleanVar(value=True)),
            ("Retour", None)
        ]

        option_buttons = []
        for i, (text, var) in enumerate(options):
            if var:
                btn = tk.Checkbutton(
                    options_frame,
                    text=text,
                    variable=var,
                    font=("Arial", 12),
                    bg=self.COLORS['secondary'],
                    fg=self.COLORS['text'],
                    selectcolor=self.COLORS['secondary'],
                    activebackground=self.COLORS['hover']
                )
            else:
                btn = tk.Button(
                    options_frame,
                    text=text,
                    font=("Arial", 12),
                    bg=self.COLORS['secondary'],
                    fg=self.COLORS['text'],
                    activebackground=self.COLORS['hover'],
                    command=options_window.destroy
                )
            btn.pack(pady=10, fill=tk.X)
            option_buttons.append(btn)

        selected_option = 0

        def highlight_option(index):
            for i, btn in enumerate(option_buttons):
                btn.config(bg=self.COLORS['hover'] if i == index else self.COLORS['secondary'])

        highlight_option(selected_option)

        def check_options_controller():
            nonlocal selected_option
            if options_window.winfo_exists():
                buttons, axes = self.controller_manager.get_primary_input()
                current_time = time.time()

                if current_time - self.last_nav_time > self.NAV_COOLDOWN:
                    if axes and (axes[1] < -0.5 or axes[3] < -0.5):
                        selected_option = (selected_option - 1) % len(option_buttons)
                        highlight_option(selected_option)
                        self.last_nav_time = current_time
                    elif axes and (axes[1] > 0.5 or axes[3] > 0.5):
                        selected_option = (selected_option + 1) % len(option_buttons)
                        highlight_option(selected_option)
                        self.last_nav_time = current_time

                if buttons and len(buttons) > 0 and buttons[0] and not self.button_pressed:
                    self.button_pressed = True
                    if selected_option == len(option_buttons) - 1:
                        options_window.destroy()
                    else:
                        option_buttons[selected_option].invoke()
                elif buttons and len(buttons) > 0 and not buttons[0]:
                    self.button_pressed = False

                options_window.after(50, check_options_controller)

        check_options_controller()

    def confirm_quit(self) -> None:
        """Demande confirmation avant de quitter avec prise en charge de la manette."""
        quit_window = tk.Toplevel(self.root)
        quit_window.attributes('-topmost', True)
        quit_window.geometry("400x200")
        quit_window.title("Confirmation")
        quit_window.configure(bg=self.COLORS['background'])
        quit_window.geometry("+{}+{}".format(
            int(self.root.winfo_screenwidth()/2 - 200),
            int(self.root.winfo_screenheight()/2 - 100)
        ))

        tk.Label(
            quit_window,
            text="Voulez-vous vraiment quitter ?",
            font=("Arial", 14),
            bg=self.COLORS['background'],
            fg=self.COLORS['text']
        ).pack(pady=20)

        buttons_frame = tk.Frame(quit_window, bg=self.COLORS['background'])
        buttons_frame.pack(pady=20)

        yes_button = tk.Button(
            buttons_frame,
            text="Oui",
            font=("Arial", 12),
            bg=self.COLORS['secondary'],
            fg=self.COLORS['text'],
            command=self.root.quit
        )
        yes_button.pack(side=tk.LEFT, padx=20)

        no_button = tk.Button(
            buttons_frame,
            text="Non",
            font=("Arial", 12),
            bg=self.COLORS['secondary'],
            fg=self.COLORS['text'],
            command=quit_window.destroy
        )
        no_button.pack(side=tk.RIGHT, padx=20)

        selected_button = 0
        confirmation_buttons = [no_button, yes_button]

        def highlight_confirmation(index):
            for i, btn in enumerate(confirmation_buttons):
                btn.config(bg=self.COLORS['hover'] if i == index else self.COLORS['secondary'])

        highlight_confirmation(selected_button)

        def check_confirmation_controller():
            nonlocal selected_button
            if quit_window.winfo_exists():
                buttons, axes = self.controller_manager.get_primary_input()

                if axes and axes[0] < -0.5:
                    selected_button = 0
                    highlight_confirmation(selected_button)
                elif axes and axes[0] > 0.5:
                    selected_button = 1
                    highlight_confirmation(selected_button)

                if buttons and len(buttons) > 0 and buttons[0]:
                    if selected_button == 0:
                        quit_window.destroy()
                    else:
                        self.root.quit()

                quit_window.after(50, check_confirmation_controller)

        check_confirmation_controller()

    def run(self) -> None:
        """Lance le launcher."""
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.run()

if __name__ == "__main__":
    main()
