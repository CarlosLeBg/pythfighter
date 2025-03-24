import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
import os
import sys
import subprocess
import pygame
import time
import random
import math

class ControllerManager:
    """Gère les entrées des manettes."""

    def __init__(self):
        load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
        self.input_mode = os.getenv('INPUT_MODE', 'keyboard')  # Lit le mode d'entrée depuis le fichier .env
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print(f"Nombre de manettes détectées : {len(self.joysticks)}")
        for joystick in self.joysticks:
            print(f"Manette {joystick.get_instance_id()} : {joystick.get_name()}")
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

class ParticleSystem:
    """Système de particules pour effets visuels."""

    def __init__(self, canvas: ctk.CTkCanvas, x: int, y: int, color: str, count: int = 20, lifetime: float = 1.0):
        self.canvas = canvas
        self.particles = []
        self.active = True

        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-3, 3)
            size = random.randint(2, 6)
            fade_rate = random.uniform(0.01, 0.05)
            alpha = 1.0

            particle = {
                'id': canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline=""),
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'size': size, 'alpha': alpha, 'fade_rate': fade_rate,
                'lifetime': random.uniform(0.5, lifetime)
            }
            self.particles.append(particle)

    def update(self) -> bool:
        """Met à jour les particules et retourne True si le système est encore actif."""
        if not self.active:
            return False

        active_particles = False
        for p in self.particles:
            p['lifetime'] -= 0.02
            if p['lifetime'] <= 0:
                self.canvas.delete(p['id'])
                continue

            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # Gravité
            p['alpha'] -= p['fade_rate']

            if p['alpha'] <= 0:
                self.canvas.delete(p['id'])
                continue

            active_particles = True

            # Mettre à jour la position et l'opacité
            alpha_hex = int(min(255, p['alpha'] * 255))
            color = f"#{alpha_hex:02x}0000"  # Rouge avec alpha
            self.canvas.itemconfig(p['id'], fill=color)
            self.canvas.coords(p['id'],
                               p['x'] - p['size'], p['y'] - p['size'],
                               p['x'] + p['size'], p['y'] + p['size'])

        self.active = active_particles
        return active_particles

class LauncherPythFighter:
    """Launcher principal pour le jeu PythFighter avec une interface graphique améliorée."""

    COLORS = {
        'background': '#1A1A2E',
        'primary': '#E94560',
        'secondary': '#16213E',
        'text': '#FFFFFF',
        'hover': '#FF6B6B',
        'shadow': '#121220',
        'highlight': '#FFA500',
        'button_border': '#FF4500'
    }

    FONTS = {
        'title': ("Impact", 100, "bold"),
        'subtitle': ("Arial Black", 30),
        'button': ("Arial Black", 20, "bold"),
        'credits': ("Arial", 20),
        'version': ("Consolas", 12)
    }

    NAV_COOLDOWN = 0.2

    def __init__(self) -> None:
        """Initialise le launcher avec une configuration de base."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.controller_manager = ControllerManager()
        self.last_nav_time = time.time()
        self.button_pressed = False
        self.particles = []
        self.input_mode = os.getenv('INPUT_MODE', 'keyboard')
        self.setup_window()
        self.create_canvas()
        self.load_background()
        self.create_interface()
        self.bind_controller()

        # Lancer la boucle d'animation
        self.animate()

    def setup_window(self) -> None:
        """Configure la fenêtre principale."""
        self.root.title("PythFighter Launcher")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.COLORS['background'])
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_quit)

    def create_canvas(self) -> None:
        """Crée et configure le canvas principal."""
        self.canvas = ctk.CTkCanvas(self.root, bg=self.COLORS['background'], highlightthickness=0)
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        # Stocker les dimensions pour référence facile
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

    def load_background(self) -> None:
        """Charge ou crée l'arrière-plan."""
        # Créer un fond avec un effet de grille
        grid_spacing = 50
        grid_color = "#223366"

        # Dessiner un dégradé de fond
        for y in range(0, self.height, 4):
            # Créer un dégradé du haut vers le bas
            darkness = int(40 + (y / self.height) * 20)
            color = f"#{darkness:02x}{darkness:02x}{darkness + 20:02x}"
            self.canvas.create_line(0, y, self.width, y, fill=color)

        # Créer l'effet de grille
        for x in range(0, self.width + grid_spacing, grid_spacing):
            self.canvas.create_line(x, 0, x, self.height, fill=grid_color, width=1)

        for y in range(0, self.height + grid_spacing, grid_spacing):
            self.canvas.create_line(0, y, self.width, y, fill=grid_color, width=1)

        # Ajouter un effet de lumière au centre
        radial_colors = [
            (100, "#16213E"),
            (300, "#1A1A2E"),
            (600, "#0D0D1A"),
        ]

        center_x, center_y = self.width // 2, self.height // 3
        for radius, color in radial_colors:
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline=""
            )

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
        self.title_text = self.canvas.create_text(
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
            ("Tutoriel", self.show_tutorial),
            ("Quitter", self.confirm_quit)
        ]

        self.buttons = []
        for i, (text, command) in enumerate(menu_items):
            button = ctk.CTkButton(
                self.root,
                text=text,
                font=self.FONTS['button'],
                fg_color=self.COLORS['secondary'],
                text_color=self.COLORS['text'],
                hover_color=self.COLORS['hover'],
                command=command,
                corner_radius=10,
                border_width=2,
                border_color=self.COLORS['button_border']
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
        version_text = "Version 2.0.0 - © 2025 PythFighter Team"
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
            button.configure(fg_color=self.COLORS['hover'] if i == index else self.COLORS['secondary'])

    def check_controller(self) -> None:
        """Vérifie les entrées de la manette."""
        if not hasattr(self, 'root') or not self.root.winfo_exists():
            return

        buttons, axes = self.controller_manager.get_primary_input()
        current_time = time.time()

        # Navigation verticale
        if current_time - self.last_nav_time > self.NAV_COOLDOWN:
            if axes and len(axes) > 1:
                if axes[1] < -0.5:  # Haut
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    self._highlight_button(self.selected_index)
                    self.last_nav_time = current_time
                elif axes[1] > 0.5:  # Bas
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    self._highlight_button(self.selected_index)
                    self.last_nav_time = current_time

        # Bouton A/X
        if buttons and len(buttons) > 0:
            if buttons[0] and not self.button_pressed:
                self.button_pressed = True
                self.buttons[self.selected_index].invoke()
            elif not buttons[0]:
                self.button_pressed = False

        # Bouton Start
        if buttons and len(buttons) > 7 and buttons[7]:
            self.confirm_quit()

        self.root.after(100, self.check_controller)

    def launch_game(self) -> None:
        """Lance le jeu principal avec gestion d'erreurs améliorée."""
        game_path = os.path.join(os.path.dirname(__file__), "selector.py")
        try:
            subprocess.Popen([sys.executable, game_path])
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Erreur de lancement", f"Impossible de lancer le jeu:\n{str(e)}")

    def show_credits(self) -> None:
        """Affiche les crédits en version très simplifiée."""
        credits_window = ctk.CTkToplevel(self.root)
        credits_window.title("Crédits")
        credits_window.attributes('-topmost', True)
        credits_window.geometry("600x400")
        credits_window.configure(bg=self.COLORS['background'])

        # Conteneur principal
        main_frame = ctk.CTkFrame(credits_window, bg_color=self.COLORS['background'])
        main_frame.pack(fill=ctk.BOTH, expand=True)

        # Texte des crédits simple
        credits_label = ctk.CTkLabel(
            main_frame,
            text=self._get_credits_text(),
            font=self.FONTS['credits'],
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['primary'],
            justify=ctk.CENTER
        )
        credits_label.pack(pady=50, expand=True)

        # Instruction
        instruction = ctk.CTkLabel(
            credits_window,
            text="Appuyez sur Échap ou Croix/A pour revenir",
            font=("Arial", 16),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        )
        instruction.pack(side=ctk.BOTTOM, pady=20)

        # Gestion des touches clavier
        credits_window.bind("<Escape>", lambda _: credits_window.destroy())

        # Vérification du contrôleur
        def check_credits_input():
            if not credits_window.winfo_exists():
                return

            buttons, _ = self.controller_manager.get_primary_input()
            if buttons and len(buttons) > 0 and buttons[0]:
                credits_window.destroy()
                return

            credits_window.after(100, check_credits_input)

        credits_window.after(100, check_credits_input)

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
        - Freesound.org
        - Design sonore


        Remerciements spéciaux:
        - Communauté Python
        - Nos testeurs dévoués
        - Tous nos joueurs
        - "Coding with Russ" et ses sources

        PythFighter utilise des technologies open source.
        Merci à tous les contributeurs !
        """

    def show_options(self) -> None:
        """Affiche le menu des options avec prise en charge de la manette."""
        self.option_button_pressed = False

        options_window = ctk.CTkToplevel(self.root)
        options_window.title("Options")
        options_window.attributes('-topmost', True)
        options_window.geometry("400x300")
        options_window.configure(bg=self.COLORS['background'])

        # Centrer la fenêtre
        options_window.geometry("+{}+{}".format(
            int(self.root.winfo_screenwidth() / 2 - 200),
            int(self.root.winfo_screenheight() / 2 - 150)
        ))

        ctk.CTkLabel(
            options_window,
            text="Options",
            font=self.FONTS['button'],
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['primary']
        ).pack(pady=20)

        options_frame = ctk.CTkFrame(options_window, bg_color=self.COLORS['background'])
        options_frame.pack(pady=10)

        options = [
            ("Plein écran", ctk.BooleanVar(value=True)),
            ("Musique", ctk.BooleanVar(value=True)),
            ("Effets sonores", ctk.BooleanVar(value=True)),
            ("Retour", None)
        ]

        option_buttons = []
        for i, (text, var) in enumerate(options):
            if var:
                btn = ctk.CTkCheckBox(
                    options_frame,
                    text=text,
                    variable=var,
                    font=("Arial", 12),
                    bg_color=self.COLORS['secondary'],
                    fg_color=self.COLORS['text'],
                    hover_color=self.COLORS['hover'],
                    checkbox_width=20,
                    checkbox_height=20,
                    border_width=2,
                    border_color=self.COLORS['button_border']
                )
            else:
                btn = ctk.CTkButton(
                    options_frame,
                    text=text,
                    font=("Arial", 12),
                    fg_color=self.COLORS['secondary'],
                    text_color=self.COLORS['text'],
                    hover_color=self.COLORS['hover'],
                    command=options_window.destroy,
                    corner_radius=10,
                    border_width=2,
                    border_color=self.COLORS['button_border']
                )
            btn.pack(pady=10, fill=ctk.X, padx=20)
            option_buttons.append(btn)

        selected_option = 0

        def highlight_option(index):
            for i, btn in enumerate(option_buttons):
                btn.configure(fg_color=self.COLORS['hover'] if i == index else self.COLORS['secondary'])

        highlight_option(selected_option)

        def check_options_controller():
            nonlocal selected_option
            if not options_window.winfo_exists():
                return

            buttons, axes = self.controller_manager.get_primary_input()
            current_time = time.time()

            # Navigation verticale
            if current_time - self.last_nav_time > self.NAV_COOLDOWN:
                if axes and len(axes) > 1:
                    if axes[1] < -0.5:  # Haut
                        selected_option = max(0, selected_option - 1)
                        highlight_option(selected_option)
                        self.last_nav_time = current_time
                    elif axes[1] > 0.5:  # Bas
                        selected_option = min(len(option_buttons) - 1, selected_option + 1)
                        highlight_option(selected_option)
                        self.last_nav_time = current_time

            # Action par bouton
            if buttons and len(buttons) > 0:
                if buttons[0] and not self.option_button_pressed:
                    self.option_button_pressed = True
                    if selected_option == len(option_buttons) - 1:
                        options_window.destroy()
                        return
                    else:
                        option_buttons[selected_option].invoke()
                elif not buttons[0]:
                    self.option_button_pressed = False

            options_window.after(100, check_options_controller)

        options_window.after(100, check_options_controller)

    def confirm_quit(self) -> None:
        """Demande confirmation avant de quitter."""
        self.quit_button_pressed = False

        quit_window = ctk.CTkToplevel(self.root)
        quit_window.title("Confirmation")
        quit_window.attributes('-topmost', True)
        quit_window.geometry("400x200")
        quit_window.configure(bg=self.COLORS['background'])

        # Centrer la fenêtre
        quit_window.geometry("+{}+{}".format(
            int(self.root.winfo_screenwidth() / 2 - 200),
            int(self.root.winfo_screenheight() / 2 - 100)
        ))

        ctk.CTkLabel(
            quit_window,
            text="Voulez-vous vraiment quitter ?",
            font=("Arial", 14),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(pady=20)

        buttons_frame = ctk.CTkFrame(quit_window, bg_color=self.COLORS['background'])
        buttons_frame.pack(pady=20)

        no_button = ctk.CTkButton(
            buttons_frame,
            text="Non",
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            hover_color=self.COLORS['hover'],
            command=quit_window.destroy,
            corner_radius=10,
            border_width=2,
            border_color=self.COLORS['button_border']
        )
        no_button.pack(side=ctk.LEFT, padx=20)

        yes_button = ctk.CTkButton(
            buttons_frame,
            text="Oui",
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            hover_color=self.COLORS['hover'],
            command=self.root.quit,
            corner_radius=10,
            border_width=2,
            border_color=self.COLORS['button_border']
        )
        yes_button.pack(side=ctk.RIGHT, padx=20)

        selected_button = 0  # 0 = Non (gauche), 1 = Oui (droite)
        confirmation_buttons = [no_button, yes_button]

        def highlight_confirmation(index):
            for i, btn in enumerate(confirmation_buttons):
                btn.configure(fg_color=self.COLORS['hover'] if i == index else self.COLORS['secondary'])

        highlight_confirmation(selected_button)

        def check_confirmation_controller():
            nonlocal selected_button
            if not quit_window.winfo_exists():
                return

            buttons, axes = self.controller_manager.get_primary_input()

            # Navigation horizontale
            if axes and len(axes) > 0:
                if axes[0] < -0.5:  # Gauche (Non)
                    selected_button = 0
                    highlight_confirmation(selected_button)
                elif axes[0] > 0.5:  # Droite (Oui)
                    selected_button = 1
                    highlight_confirmation(selected_button)

            # Action par bouton
            if buttons and len(buttons) > 0:
                if buttons[0] and not self.quit_button_pressed:
                    self.quit_button_pressed = True
                    if selected_button == 0:  # Non
                        quit_window.destroy()
                        return
                    else:  # Oui
                        self.root.quit()
                elif not buttons[0]:
                    self.quit_button_pressed = False

            quit_window.after(100, check_confirmation_controller)

        quit_window.after(100, check_confirmation_controller)

    def animate(self) -> None:
        """Gère l'animation des éléments visuels."""
        # Animer le titre avec un effet de pulsation
        scale = 1.0 + 0.03 * math.sin(time.time() * 2)
        new_font = (self.FONTS['title'][0], int(self.FONTS['title'][1] * scale), self.FONTS['title'][2])
        self.canvas.itemconfig(self.title_text, font=new_font)

        # Mettre à jour tous les systèmes de particules
        active_particles = []
        for particle_system in self.particles:
            if particle_system.update():
                active_particles.append(particle_system)

        # Ne garder que les systèmes de particules actifs
        self.particles = active_particles

        # Ajouter de nouvelles particules aléatoirement
        if random.random() < 0.05:  # 5% de chance à chaque frame
            x = random.randint(0, self.width)
            y = random.randint(0, self.height // 2)
            particle_system = ParticleSystem(
                self.canvas, x, y, self.COLORS['primary'],
                count=random.randint(3, 10), lifetime=1.0
            )
            self.particles.append(particle_system)

        # Continuer l'animation
        self.root.after(50, self.animate)

    def _add_tutorial_particles(self, canvas):
        """Adds dynamic particles to the tutorial screen."""
        colors = ["#E94560", "#FFA500", "#44AAFF"]

        for _ in range(3):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = random.choice(colors)
            particle_system = ParticleSystem(canvas, x, y, color, count=15, lifetime=1.5)
            self.particles.append(particle_system)

    def _create_controller_icon(self, canvas, x, y, tags=None):
        """Creates a placeholder controller icon on the canvas."""
        icon_id = canvas.create_oval(
            x - 50, y - 50, x + 50, y + 50,
            fill="#E94560", outline="#FFFFFF", width=2, tags=tags
        )
        canvas.create_text(
            x, y, text="🎮", font=("Arial", 30), fill="#FFFFFF", tags=tags
        )
        return icon_id

    def _create_tips_icon(self, canvas, x, y, tags=None):
        """Creates a placeholder tips icon on the canvas."""
        icon_id = canvas.create_rectangle(
            x - 50, y - 50, x + 50, y + 50,
            fill="#FFA500", outline="#FFFFFF", width=2, tags=tags
        )
        canvas.create_text(
            x, y, text="💡", font=("Arial", 30), fill="#FFFFFF", tags=tags
        )
        return icon_id

    def _create_combo_icon(self, canvas, x, y, tags=None):
        """Creates a placeholder combo icon on the canvas."""
        icon_id = canvas.create_oval(
            x - 50, y - 50, x + 50, y + 50,
            fill="#44AAFF", outline="#FFFFFF", width=2, tags=tags
        )
        canvas.create_text(
            x, y, text="⚡", font=("Arial", 30), fill="#FFFFFF", tags=tags
        )
        return icon_id

    def show_tutorial(self) -> None:
        """Displays an interactive, visually rich tutorial with Street Fighter style elements."""
        # Create the tutorial window
        tutorial_window = ctk.CTkToplevel(self.root)
        tutorial_window.title("Tutoriel PythFighter")
        tutorial_window.attributes('-topmost', True)
        tutorial_window.geometry(f"{self.width}x{self.height}")
        tutorial_window.attributes('-fullscreen', True)

        tutorial_canvas = ctk.CTkCanvas(tutorial_window, bg=self.COLORS['background'], highlightthickness=0)
        tutorial_canvas.pack(fill=ctk.BOTH, expand=True)

        grid_color = "#223366"
        grid_spacing = 50

        # Create background gradient
        for y in range(0, self.height, 4):
            darkness = int(25 + (y / self.height) * 30)
            color = f"#{darkness:02x}{darkness:02x}{darkness + 15:02x}"
            tutorial_canvas.create_line(0, y, self.width, y, fill=color)

        # Add grid effect
        for x in range(0, self.width + grid_spacing, grid_spacing):
            tutorial_canvas.create_line(x, 0, x, self.height, fill=grid_color, width=1)
        for y in range(0, self.height + grid_spacing, grid_spacing):
            tutorial_canvas.create_line(0, y, self.width, y, fill=grid_color, width=1)

        # Create tutorial header
        tutorial_canvas.create_text(
            self.width // 2,
            80,
            text="TUTORIEL",
            font=("Impact", 80, "bold"),
            fill="#E94560"
        )
        tutorial_canvas.create_text(
            self.width // 2 + 3,
            80 + 3,
            text="TUTORIEL",
            font=("Impact", 80, "bold"),
            fill="#121220"
        )

        # Create sections for different tutorial elements
        sections = [
            {
                "title": "COMMANDES DE BASE",
                "icon": self._create_controller_icon,
                "content": [
                    "🎮 MANETTE PS4/PS5:",
                    "⬅️➡️ Joystick gauche: Se déplacer",
                    "🇽 Touche X: Sauter",
                    "⚪ Touche O: Attaque",
                    "🔼 Touche triangle: Attaque spéciale",
                    "⚙️ Touche options: Menu pause",
                    "",
                    "⌨️ CLAVIER JOUEUR 1:",
                    "🇦/🇩: Gauche/Droite",
                    "🇼: Sauter",
                    "🇷: Attaquer",
                    "🇹: Attaque spéciale",
                    "",
                    "⌨️ CLAVIER JOUEUR 2:",
                    "⬅️➡️: Gauche/Droite",
                    "⬆️: Sauter",
                    "↪️ Entrée: Attaquer",
                    "🇵: Attaque spéciale"
                ]
            },
            {
                "title": "CONSEILS DE COMBAT",
                "icon": self._create_tips_icon,
                "content": [
                    "🛡️ BLOQUER: Maintenez la direction opposée à votre",
                    "adversaire pour bloquer ses attaques",
                    "",
                    "⏱️ TIMING: Les combos doivent être exécutés rapidement",
                    "et avec précision",
                    "",
                    "📊 JAUGE D'ÉNERGIE: Se remplit quand vous donnez ou",
                    "recevez des coups",
                    "",
                    "🔄 CONTRE-ATTAQUE: Bloquez puis ripostez immédiatement",
                    "pour surprendre votre adversaire"
                ]
            }
        ]

        # Variables for navigation
        self.current_section = 0
        self.total_sections = len(sections)

        # Function to display current section
        def display_section(index):
            # Clear previous content
            for item in tutorial_canvas.find_withtag("section_content"):
                tutorial_canvas.delete(item)

            section = sections[index]

            # Create section title with shadow effect
            y_pos = 180
            shadow_offset = 3

            # Shadow for title
            tutorial_canvas.create_text(
                self.width // 2 + shadow_offset,
                y_pos + shadow_offset,
                text=section["title"],
                font=("Arial Black", 36, "bold"),
                fill="#121220",
                tags="section_content"
            )

            # Title
            tutorial_canvas.create_text(
                self.width // 2,
                y_pos,
                text=section["title"],
                font=("Arial Black", 36, "bold"),
                fill="#FFA500",
                tags="section_content"
            )

            # Section icon
            icon_id = section["icon"](tutorial_canvas, self.width // 4, 300, tags="section_content")

            # Content
            content_x = self.width // 2 + 100
            content_y = 250

    
            # Add keyboard bindings for navigation
            tutorial_window.bind("<Left>", lambda e: prev_section())
            tutorial_window.bind("<Right>", lambda e: next_section())
            tutorial_window.bind("<Escape>", lambda e: tutorial_window.destroy())

            for line in section["content"]:
                tutorial_canvas.create_text(
                    content_x,
                    content_y,
                    text=line,
                    font=("Arial", 20),
                    fill="#FFFFFF",
                    anchor="w",
                    tags="section_content"
                )
                content_y += 30

            # Navigation indicators
            indicator_y = self.height - 100
            for i in range(self.total_sections):
                color = "#E94560" if i == index else "#555555"
                tutorial_canvas.create_oval(
                    self.width // 2 - 50 + i * 40,
                    indicator_y,
                    self.width // 2 - 30 + i * 40,
                    indicator_y + 20,
                    fill=color,
                    outline="",
                    tags="section_content"
                )

            # Navigation instructions
            tutorial_canvas.create_text(
                self.width // 2,
                self.height - 60,
                text="◀ ▶ : Naviguer | X/B : Fermer",
                font=("Arial", 18),
                fill="#FFFFFF",
                tags="section_content"
            )

            # Add particle effects
            self._add_tutorial_particles(tutorial_canvas)

        # Create the icons for each section
        def _create_controller_icon(canvas, x, y, tags=""):
            # Controller base
            canvas.create_rectangle(x-60, y, x+60, y+120, fill="#303030", outline="#000000", width=2, tags=tags)
            canvas.create_oval(x-40, y+20, x+40, y+100, fill="#202020", outline="#000000", width=2, tags=tags)

            # D-pad
            canvas.create_rectangle(x-40, y+130, x+40, y+210, fill="#303030", outline="#000000", width=2, tags=tags)
            canvas.create_polygon(x, y+140, x-30, y+170, x, y+200, x+30, y+170, fill="#404040", outline="#000000", width=2, tags=tags)

            # Buttons
            button_colors = ["#FF4444", "#44FF44", "#4444FF", "#FFFF44"]
            for i, color in enumerate(button_colors):
                angle = i * math.pi/2
                bx = x + 30 * math.cos(angle)
                by = y + 60 + 30 * math.sin(angle)
                canvas.create_oval(bx-15, by-15, bx+15, by+15, fill=color, outline="#000000", width=2, tags=tags)

            return canvas.create_text(x, y-20, text="CONTRÔLES", font=("Arial Black", 14), fill="#FFFFFF", tags=tags)

        def _create_combo_icon(canvas, x, y, tags=""):
            # Create a combo chart
            width, height = 120, 120
            canvas.create_rectangle(x-width//2, y, x+width//2, y+height, fill="#303030", outline="#E94560", width=3, tags=tags)

            # Draw arrow sequence for a hadouken
            arrow_size = 15
            start_x = x - 45
            start_y = y + 30

            # Down arrow
            canvas.create_polygon(
                start_x, start_y,
                start_x - arrow_size, start_y - arrow_size,
                start_x - arrow_size/2, start_y - arrow_size,
                start_x - arrow_size/2, start_y - arrow_size*2,
                start_x + arrow_size/2, start_y - arrow_size*2,
                start_x + arrow_size/2, start_y - arrow_size,
                start_x + arrow_size, start_y - arrow_size,
                fill="#44AAFF", outline="#000000", width=1, tags=tags
            )

            # Down-right arrow
            start_x += 30
            canvas.create_polygon(
                start_x, start_y,
                start_x - arrow_size, start_y - arrow_size,
                start_x - arrow_size/2, start_y - arrow_size/2,
                start_x - arrow_size, start_y,
                start_x - arrow_size/2, start_y + arrow_size/2,
                start_x, start_y + arrow_size,
                start_x + arrow_size, start_y,
                fill="#44AAFF", outline="#000000", width=1, tags=tags
            )

            # Right arrow
            start_x += 30
            canvas.create_polygon(
                start_x + arrow_size, start_y,
                start_x, start_y - arrow_size,
                start_x, start_y - arrow_size/2,
                start_x - arrow_size, start_y - arrow_size/2,
                start_x - arrow_size, start_y + arrow_size/2,
                start_x, start_y + arrow_size/2,
                start_x, start_y + arrow_size,
                fill="#44AAFF", outline="#000000", width=1, tags=tags
            )

            # Punch button
            canvas.create_oval(start_x + 30, start_y - 10, start_x + 50, start_y + 10, fill="#FF4444", outline="#000000", width=2, tags=tags)
            canvas.create_text(start_x + 40, start_y, text="P", font=("Arial Black", 10), fill="#FFFFFF", tags=tags)

            # Fire effect
            for i in range(8):
                angle = i * math.pi/4
                radius = 20 + random.randint(0, 10)
                fx = x
                fy = y + 80
                canvas.create_oval(
                   fx + radius * math.cos(angle) - 5,
                   fy + radius * math.sin(angle) - 5,
                    fx + radius * math.cos(angle) + 5,
                    fy + radius * math.sin(angle) + 5,
                    fill="#FF8800", outline="", tags=tags
            )

            canvas.create_oval(x-15, y+80-15, x+15, y+80+15, fill="#FFAA00", outline="#FF4400", width=2, tags=tags)

            return canvas.create_text(x, y-20, text="COMBOS", font=("Arial Black", 14), fill="#FFFFFF", tags=tags)

        def _create_tips_icon(canvas, x, y, tags=""):
            # Create a health and energy bar diagram
            width, height = 120, 120

            # Background
            canvas.create_rectangle(x-width//2, y, x+width//2, y+height, fill="#303030", outline="#E94560", width=3, tags=tags)

            # Health bar - P1
            bar_width = 100
            canvas.create_rectangle(x-bar_width//2, y+20, x+bar_width//2, y+30, fill="#222222", outline="#000000", width=1, tags=tags)
            canvas.create_rectangle(x-bar_width//2, y+20, x-bar_width//2+70, y+30, fill="#FF4444", outline="", tags=tags)

            # Health bar - P2
            canvas.create_rectangle(x-bar_width//2, y+40, x+bar_width//2, y+50, fill="#222222", outline="#000000", width=1, tags=tags)
            canvas.create_rectangle(x-bar_width//2, y+40, x-bar_width//2+40, y+50, fill="#FF4444", outline="", tags=tags)

            # Energy bar
            canvas.create_rectangle(x-bar_width//2, y+70, x+bar_width//2, y+85, fill="#222222", outline="#000000", width=1, tags=tags)

            # Energy segments (flashing)
            segments = 5
            segment_width = bar_width / segments

            for i in range(segments):
                if i < 3:  # First 3 segments filled
                    color = "#FFAA00"
                else:
                    color = "#444444"

                canvas.create_rectangle(
                    x-bar_width//2 + i*segment_width, y+70,
                    x-bar_width//2 + (i+1)*segment_width, y+85,
                    fill=color, outline="#000000", width=1, tags=tags
                )

            # Combat icons
            icon_y = y + 110

            # Block icon
            block_x = x - 40
            canvas.create_rectangle(block_x-10, icon_y-10, block_x+10, icon_y+10, fill="#4444FF", outline="#000000", width=1, tags=tags)
            canvas.create_text(block_x, icon_y, text="🛡️", font=("Arial", 12), tags=tags)

            # Timing icon
            time_x = x
            canvas.create_oval(time_x-10, icon_y-10, time_x+10, icon_y+10, fill="#44FF44", outline="#000000", width=1, tags=tags)
            canvas.create_text(time_x, icon_y, text="⏱️", font=("Arial", 12), tags=tags)

            # Counter icon
            counter_x = x + 40
            canvas.create_polygon(
                counter_x, icon_y-10,
                counter_x-10, icon_y+5,
                counter_x, icon_y,
                counter_x+10, icon_y+5,
                fill="#FF4444", outline="#000000", width=1, tags=tags
            )
            canvas.create_text(counter_x, icon_y, text="↩️", font=("Arial", 12), tags=tags)

            return canvas.create_text(x, y-20, text="STRATÉGIE", font=("Arial Black", 14), fill="#FFFFFF", tags=tags)

        def _add_tutorial_particles(canvas):
            """Adds dynamic particles to the tutorial screen."""
            colors = ["#E94560", "#FFA500", "#44AAFF"]

            for _ in range(3):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                color = random.choice(colors)
                particle_system = ParticleSystem(canvas, x, y, color, count=15, lifetime=1.5)
                self.particles.append(particle_system)

            # Ensure navigation functions are properly bound
        def next_section():
                self.current_section = (self.current_section + 1) % self.total_sections
                display_section(self.current_section)
    
        def prev_section():
                self.current_section = (self.current_section - 1) % self.total_sections
                display_section(self.current_section)

        # Display first section
        display_section(self.current_section)


        # Add keyboard bindings for navigation
        tutorial_window.bind("<Left>", lambda e: prev_section())
        tutorial_window.bind("<Right>", lambda e: next_section())
        tutorial_window.bind("<Escape>", lambda e: tutorial_window.destroy())

        # Add mouse wheel scrolling for navigation
        def on_mouse_wheel(event):
            if event.delta > 0:  # Scroll up
                prev_section()
            elif event.delta < 0:  # Scroll down
                next_section()

        tutorial_window.bind("<MouseWheel>", on_mouse_wheel)
        tutorial_window.bind("<Left>", lambda e: prev_section())
        tutorial_window.bind("<Right>", lambda e: next_section())
        tutorial_window.bind("<Escape>", lambda e: tutorial_window.destroy())

        # Controller input checking
        def check_tutorial_controller():
            if not tutorial_window.winfo_exists():
                return

            buttons, axes = self.controller_manager.get_primary_input()
            current_time = time.time()

            # Navigation with axes
            if current_time - self.last_nav_time > self.NAV_COOLDOWN:
                if axes and len(axes) > 0:
                    if axes[0] < -0.5:  # Left
                        prev_section()
                        self.last_nav_time = current_time
                    elif axes[0] > 0.5:  # Right
                        next_section()
                        self.last_nav_time = current_time

            # Exit with button
            if buttons and len(buttons) > 0 and buttons[0]:
                tutorial_window.destroy()
                return

            # Continue checking
            tutorial_window.after(100, check_tutorial_controller)

        # Start checking for controller input
        tutorial_window.after(100, check_tutorial_controller)

        # Animation update loop
        def update_animations():
            if not tutorial_window.winfo_exists():
                return

            # Update particles
            active_particles = []
            for particle_system in self.particles:
                if particle_system.update():
                    active_particles.append(particle_system)

            self.particles = active_particles

            # Continue animations
            tutorial_window.after(50, update_animations)

        update_animations()

    def run(self) -> None:
        """Lance le launcher."""
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.run()

if __name__ == "__main__":
    main()
