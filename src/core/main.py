import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv, set_key
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
        self.language = os.getenv('LANGUAGE', 'fr')  # Langue par défaut
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
        self.language = self.controller_manager.language
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
        self._create_stats_section()

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
            ("Changer de Langue", self.change_language),
            ("Quitter", self.confirm_quit)
        ]

        self.buttons = []
        button_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS['background'])
        button_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        for i, (text, command) in enumerate(menu_items):
            button = ctk.CTkButton(
                button_frame,
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
            button.pack(pady=5, padx=10, anchor="e")
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

    def _create_stats_section(self) -> None:
        """Crée une section pour afficher les statistiques de jeu."""
        stats_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS['secondary'], border_width=2, border_color=self.COLORS['button_border'])
        stats_frame.place(relx=0.02, rely=0.05, anchor="nw")

        stats_label = ctk.CTkLabel(
            stats_frame,
            text="Statistiques de Jeu",
            font=self.FONTS['subtitle'],
            text_color=self.COLORS['primary']
        )
        stats_label.pack(pady=10)

        # Exemple de statistiques
        stats_info = [
            ("Temps de Jeu", "10 heures"),
            ("Score Max", "5000"),
            ("Nombre de Parties", "25"),
        ]

        for text, value in stats_info:
            stat_text = f"{text}: {value}"
            stat_label = ctk.CTkLabel(
                stats_frame,
                text=stat_text,
                font=self.FONTS['credits'],
                text_color=self.COLORS['text']
            )
            stat_label.pack(anchor="w", padx=20)

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
        credits_window.bind("<Escape>", lambda e: credits_window.destroy())

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
            int(self.root.winfo_screenwidth()/2 - 200),
            int(self.root.winfo_screenheight()/2 - 150)
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
            int(self.root.winfo_screenwidth()/2 - 200),
            int(self.root.winfo_screenheight()/2 - 100)
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

    def change_language(self) -> None:
        """Change la langue entre Français et Anglais."""
        if self.language == "fr":
            self.language = "en"
            messagebox.showinfo("Langue", "Langue changée en Anglais.")
        else:
            self.language = "fr"
            messagebox.showinfo("Langue", "Langue changée en Français.")

        # Sauvegarder la langue dans le fichier .env
        set_key('.env', 'LANGUAGE', self.language)

    def show_tutorial(self) -> None:
        """Affiche un tutoriel simple pour aider les nouveaux joueurs."""
        tutorial_window = ctk.CTkToplevel(self.root)
        tutorial_window.title("Tutoriel")
        tutorial_window.attributes('-topmost', True)
        tutorial_window.geometry("600x400")
        tutorial_window.configure(bg=self.COLORS['background'])

        # Contenu du tutoriel
        tutorial_text = """
        Bienvenue dans PythFighter !

        Voici quelques conseils pour bien commencer :
        - Utilisez les touches directionnelles ou la manette pour naviguer dans les menus.
        - Appuyez sur Entrée ou le bouton A pour sélectionner une option.
        - Vous pouvez changer la langue dans les options.
        - N'oubliez pas de vérifier régulièrement les mises à jour pour profiter des dernières améliorations.

        Amusez-vous bien !
        """

        tutorial_label = ctk.CTkLabel(
            tutorial_window,
            text=tutorial_text,
            font=self.FONTS['credits'],
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['primary'],
            justify=ctk.CENTER
        )
        tutorial_label.pack(pady=20, padx=20, fill=ctk.BOTH, expand=True)

        # Bouton pour fermer le tutoriel
        close_button = ctk.CTkButton(
            tutorial_window,
            text="Fermer",
            font=self.FONTS['button'],
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            hover_color=self.COLORS['hover'],
            command=tutorial_window.destroy,
            corner_radius=10,
            border_width=2,
            border_color=self.COLORS['button_border']
        )
        close_button.pack(pady=10)

    def run(self) -> None:
        """Lance le launcher."""
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.run()

if __name__ == "__main__":
    main()
