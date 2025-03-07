import tkinter as tk
from tkinter import messagebox, ttk
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
        buttons = []
        axes = []
        for joystick in self.joysticks:
            buttons.append([joystick.get_button(i) for i in range(joystick.get_numbuttons())])
            axes.append([joystick.get_axis(i) for i in range(joystick.get_numaxes())])
        return buttons, axes

    def get_primary_input(self):
        if self.primary_joystick:
            pygame.event.pump()  # Ajout pour assurer la mise à jour des événements
            buttons = [self.primary_joystick.get_button(i) for i in range(self.primary_joystick.get_numbuttons())]
            axes = [self.primary_joystick.get_axis(i) for i in range(self.primary_joystick.get_numaxes())]
            return buttons, axes
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

    FONTS: Dict[str, tuple] = {
        'title': ("Helvetica", 100, "bold"),
        'subtitle': ("Helvetica", 28),
        'button': ("Helvetica", 18, "bold"),
        'credits': ("Helvetica", 16),
        'version': ("Helvetica", 14)
    }

    def __init__(self) -> None:
        """Initialise le launcher avec une configuration de base."""
        self.root = tk.Tk()
        self.controller_manager = ControllerManager()
        
        # Initialisation des variables de contrôle des manettes
        self.last_nav_time = time.time()
        self.nav_cooldown = 0.3  # Délai en secondes entre chaque mouvement du joystick
        self.button_pressed = False  # Pour éviter les répétitions de bouton
        
        self.setup_window()
        self.create_canvas()
        self.create_interface()
        self.bind_controller()

    def setup_window(self) -> None:
        """Configure la fenêtre principale."""
        self.root.title("PythFighter Launcher")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.COLORS['background'])
        
        # Désactiver le clavier et la souris
        self.root.bind("<Button-1>", lambda e: None)
        self.root.bind("<Key>", lambda e: None)

    def create_canvas(self) -> None:
        """Crée et configure le canvas principal."""
        try:
            self.canvas = tk.Canvas(
                self.root,
                bg=self.COLORS['background'],
                width=self.screen_width,
                height=self.screen_height,
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            logging.error(f"Error setting up canvas: {str(e)}")
            raise

    def setup_particles(self) -> None:
        """Initialise les particules d'arrière-plan."""
        try:
            self.particles = []
            for _ in range(50):
                self.particles.append({
                    'x': random.random() * self.screen_width,
                    'y': random.random() * self.screen_height,
                    'size': random.randint(2, 5),
                    'speed': random.random() * 2 + 0.5,
                    'alpha': random.random()  # Pour l'effet de scintillement
                })
            
        except Exception as e:
            logging.error(f"Error setting up particles: {str(e)}")
            raise

    def create_interface(self) -> None:
        """Crée tous les éléments de l'interface."""
        try:
            self._create_background()
            self._create_title()
            self._create_menu_buttons()
            self._create_version_info()
            self._create_decorative_elements()
            
        except Exception as e:
            logging.error(f"Error creating interface: {str(e)}")
            raise

    def _create_background(self) -> None:
        """Crée un arrière-plan avec gradient amélioré."""
        try:
            # Gradient vertical principal
            gradient_steps = 100
            for i in range(gradient_steps):
                y = i * self.screen_height / gradient_steps
                color = self._interpolate_color(
                    self.COLORS['background'],
                    self.COLORS['secondary'],
                    i / gradient_steps
                )
                self.canvas.create_line(
                    0, y, self.screen_width, y,
                    fill=color,
                    width=2
                )
                
            # Ajout d'un effet de vignette
            self._create_vignette()
            
        except Exception as e:
            logging.error(f"Error creating background: {str(e)}")
            raise

    def _create_vignette(self) -> None:
        """Crée un effet de vignette sur les bords."""
        try:
            vignette_size = 100
            for i in range(vignette_size):
                alpha = i / vignette_size
                color = self._interpolate_color(
                    self.COLORS['background'],
                    '#000000',
                    alpha
                )
                # Bords horizontaux
                self.canvas.create_line(
                    0, i,
                    self.screen_width, i,
                    fill=color
                )
                self.canvas.create_line(
                    0, self.screen_height - i,
                    self.screen_width, self.screen_height - i,
                    fill=color
                )
                # Bords verticaux
                self.canvas.create_line(
                    i, 0,
                    i, self.screen_height,
                    fill=color
                )
                self.canvas.create_line(
                    self.screen_width - i, 0,
                    self.screen_width - i, self.screen_height,
                    fill=color
                )
                
        except Exception as e:
            logging.error(f"Error creating vignette: {str(e)}")
            raise

    def _create_title(self) -> None:
        """Crée le titre du jeu avec un effet d'ombre."""
        screen_width = self.root.winfo_screenwidth()
        offset = 3
        for i in range(3):
            self.canvas.create_text(
                self.screen_width // 2,
                title_y,
                text="PYTH",
                font=self.FONTS['title'],
                fill=self.COLORS['primary']
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
        menu_items: List[Tuple[str, Callable]] = [
            ("Démarrer", self.launch_game),
            ("Crédits", self.show_credits),
            ("Options", self.show_options),
            ("Quitter", self.confirm_quit)
        ]

        self.buttons = []
        for i, (text, command) in enumerate(menu_items):
            button = tk.Button(
                self.root,
                bg=self.COLORS['background']
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

    def _on_button_hover(self, button: tk.Button, entering: bool) -> None:
        """Gère l'effet de survol des boutons."""
        button.configure(
            bg=self.COLORS['hover'] if entering else self.COLORS['secondary']
        )

    def bind_controller(self) -> None:
        """Configure les entrées de la manette."""
        self.selected_index = 0
        self._highlight_button(self.selected_index)
        self.check_controller()

    def _highlight_button(self, index: int) -> None:
        """Met en surbrillance le bouton sélectionné."""
        for i, button in enumerate(self.buttons):
            if i == index:
                button.config(bg=self.COLORS['hover'])
            else:
                button.config(bg=self.COLORS['secondary'])

    def check_controller(self) -> None:
        """Vérifie les entrées de la manette."""
        buttons, axes = self.controller_manager.get_primary_input()
        current_time = time.time()

        # Vérification du joystick avec délai (cooldown) pour éviter le défilement trop rapide
        if current_time - self.last_nav_time > self.nav_cooldown:
            if axes and (axes[1] < -0.5 or axes[3] < -0.5):  # Joystick gauche ou droit vers le haut
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self._highlight_button(self.selected_index)
                self.last_nav_time = current_time
            elif axes and (axes[1] > 0.5 or axes[3] > 0.5):  # Joystick gauche ou droit vers le bas
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self._highlight_button(self.selected_index)
                self.last_nav_time = current_time
                
        # Vérification des boutons (avec gestion pour éviter les répétitions)
        # Bouton Croix/A qui est souvent à l'index 0 sur les manettes PS4/Xbox
        if buttons and len(buttons) > 0 and buttons[0] and not self.button_pressed:
            self.button_pressed = True
            self.buttons[self.selected_index].invoke()
        elif buttons and len(buttons) > 0 and not buttons[0]:
            self.button_pressed = False
            
        # Bouton Options/Start/Menu (souvent à l'index 7 ou 9)
        start_button_index = 9 if len(buttons) > 9 else (7 if len(buttons) > 7 else -1)
        if start_button_index >= 0 and buttons[start_button_index]:
            self.confirm_quit()

        self.root.after(50, self.check_controller)  # Vérification plus fréquente pour plus de réactivité

    def launch_game(self) -> None:
        """Lance le jeu principal avec gestion d'erreurs améliorée."""
        game_path = os.path.join(os.path.dirname(__file__), "selector.py")
        try:
            subprocess.Popen([sys.executable, game_path])
            self.root.quit()
        except Exception as e:
            logging.error(f"Error creating menu buttons: {str(e)}")
            raise

    
    def show_credits(self) -> None:
        """Affiche les crédits avec une animation améliorée."""
        self.credits_window = tk.Toplevel(self.root)
        self.credits_window.attributes('-fullscreen', True)
        self.credits_window.configure(bg=self.COLORS['background'])
        
        # Gestion manette pour fenêtre de crédits
        self.credits_window.bind("<Button-1>", lambda e: None)  # Désactiver souris
        
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
        
        # Instruction pour fermer avec manette
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
            buttons, _ = self.controller_manager.get_primary_input()
            if buttons and len(buttons) > 0 and buttons[0]:  # Bouton Croix/A
                self.credits_window.destroy()
            self.credits_window.after(100, self._check_credits_controller)

    def _get_credits_text(self) -> str:
        """Retourne le texte des crédits avec mise en forme améliorée."""
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        PYTHFIGHTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Un jeu de combat révolutionnaire

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ÉQUIPE DE DÉVELOPPEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Direction du Projet
------------------
Lead Developer: [Nom]
Project Manager: [Nom]

Programmation
------------
Core Engine: [Nom]
Combat System: [Nom]
UI/UX: [Nom]
Physics Engine: [Nom]

Design
------
Direction Artistique: [Nom]
Character Design: [Nom]
Environment Art: [Nom]
VFX Artist: [Nom]

Audio
-----
Composition Musicale: [Nom]
Sound Design: [Nom]
Voice Acting: [Nom]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    REMERCIEMENTS SPÉCIAUX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testeurs
--------
[Liste des testeurs]

Contributeurs
------------
[Liste des contributeurs]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TECHNOLOGIES UTILISÉES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Python
Tkinter
[Autres technologies]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copyright © 2024 PythFighter
Tous droits réservés

Version 1.0.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        
        # Désactiver souris et clavier
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
            ("Retour", None)  # Option pour revenir
        ]
        
        option_buttons = []
        for i, (text, var) in enumerate(options):
            if var:
                # Créer un bouton de type checkbox
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
                # Créer un bouton normal pour "Retour"
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
            
        # Gestion de navigation avec manette pour les options
        selected_option = 0
        
        def highlight_option(index):
            for i, btn in enumerate(option_buttons):
                if i == index:
                    btn.config(bg=self.COLORS['hover'])
                else:
                    btn.config(bg=self.COLORS['secondary'])
        
        highlight_option(selected_option)
        
        def check_options_controller():
            nonlocal selected_option
            if options_window.winfo_exists():
                buttons, axes = self.controller_manager.get_primary_input()
                current_time = time.time()
                
                # Vérification du joystick avec délai
                if current_time - self.last_nav_time > self.nav_cooldown:
                    if axes and (axes[1] < -0.5 or axes[3] < -0.5):  # Haut
                        selected_option = (selected_option - 1) % len(option_buttons)
                        highlight_option(selected_option)
                        self.last_nav_time = current_time
                    elif axes and (axes[1] > 0.5 or axes[3] > 0.5):  # Bas
                        selected_option = (selected_option + 1) % len(option_buttons)
                        highlight_option(selected_option)
                        self.last_nav_time = current_time
                
                # Action sur bouton
                if buttons and len(buttons) > 0 and buttons[0] and not self.button_pressed:
                    self.button_pressed = True
                    if selected_option == len(option_buttons) - 1:  # Option "Retour"
                        options_window.destroy()
                    else:
                        # Simuler un clic sur le checkbutton
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
        
        # Centrer la fenêtre
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
        
        # Gestion de la navigation avec manette
        selected_button = 0  # 0 pour Non, 1 pour Oui
        confirmation_buttons = [no_button, yes_button]
        
        def highlight_confirmation(index):
            for i, btn in enumerate(confirmation_buttons):
                if i == index:
                    btn.config(bg=self.COLORS['hover'])
                else:
                    btn.config(bg=self.COLORS['secondary'])
        
        highlight_confirmation(selected_button)
        
        def check_confirmation_controller():
            nonlocal selected_button
            if quit_window.winfo_exists():
                buttons, axes = self.controller_manager.get_primary_input()
                
                # Navigation gauche/droite
                if axes and axes[0] < -0.5:  # Gauche
                    selected_button = 0
                    highlight_confirmation(selected_button)
                elif axes and axes[0] > 0.5:  # Droite
                    selected_button = 1
                    highlight_confirmation(selected_button)
                
                # Action sur bouton
                if buttons and len(buttons) > 0 and buttons[0]:  # Bouton Croix/A
                    if selected_button == 0:  # Non
                        quit_window.destroy()
                    else:  # Oui
                        self.root.quit()
                
                quit_window.after(50, check_confirmation_controller)
        
        check_confirmation_controller()

    def run(self) -> None:
        """Lance le launcher avec gestion d'erreurs."""
        try:
            self.root.mainloop()
            
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            sys.exit(1)

def main():
    try:
        launcher = LauncherPythFighter()
        launcher.run()
        
    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}")
        messagebox.showerror("Fatal Error", f"Cannot start launcher: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()