# Importe toutes les librairies nécessaires
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from dotenv import load_dotenv
import os
import sys
import subprocess
import pygame
import time
import random
import math
from datetime import datetime
# Add import for CharacterSelect
from selector import CharacterSelect

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

    VERSION = "1.0.0"
    COLORS = {
        'background': '#1A1A2E',
        'primary': '#E94560',
        'secondary': '#16213E',
        'text': '#FFFFFF',
        'hover': '#FF6B6B',
        'shadow': '#121220',
        'highlight': '#FFA500',
        'button_border': '#FF4500',
        'accent': '#00FF7F',
        'card_background': '#1E1E2E',
        'primary_hover': '#D13B50',
        'text_button': '#FFFFFF',
        'text_muted': '#B0B0B0'
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
            ("Multijoueur", self.show_multiplayer_menu),  # Nouveau bouton pour le multijoueur
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
        VERSION = "1.0.0"
        version_text = "Version 1.0.0 - © 2025 Equipe de dev de PythFighter"
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
    def show_multiplayer_menu(self) -> None:
        """Affiche le menu multijoueur."""
        # Clear the current interface
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()

        # Create a frame for the multiplayer menu
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_label = ctk.CTkLabel(
            frame,
            text="Mode Multijoueur",
            font=self.FONTS['subtitle'],
            text_color=self.COLORS['primary']
        )
        title_label.pack(pady=(0, 30))

        # Create Game button
        create_button = ctk.CTkButton(
            frame,
            text="Créer une partie",
            font=self.FONTS['button'],
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['hover'],
            command=self.create_game,
            width=300,
            height=60
        )
        create_button.pack(pady=10)

        # Join Game button
        join_button = ctk.CTkButton(
            frame,
            text="Rejoindre une partie",
            font=self.FONTS['button'],
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['hover'],
            command=self.join_game,
            width=300,
            height=60
        )
        join_button.pack(pady=10)

        # Back button
        back_button = ctk.CTkButton(
            frame,
            text="Retour",
            font=self.FONTS['button'],
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['hover'],
            command=self.return_to_main_menu,
            width=300,
            height=60
        )
        back_button.pack(pady=10)

        self.check_multiplayer_controller()

    def check_multiplayer_controller(self) -> None:
        """Vérifie si des manettes sont connectées pour le mode multijoueur."""
        pygame.joystick.init()
        controller_count = pygame.joystick.get_count()
        
        if controller_count == 0:
            messagebox.showinfo("Information", "Aucune manette détectée. Le mode clavier sera utilisé par défaut.")
        else:
            messagebox.showinfo("Information", f"{controller_count} manette(s) détectée(s).")
            
    def join_game(self) -> None:
        """Affiche un menu pour rejoindre un salon."""
        join_window = ctk.CTkToplevel(self.root)
        join_window.title("Rejoindre un salon")
        join_window.attributes('-topmost', True)
        join_window.geometry("400x300")
        join_window.configure(bg=self.COLORS['background'])

        # Centrer la fenêtre
        join_window.geometry("+{}+{}".format(
            int(self.root.winfo_screenwidth() / 2 - 200),
            int(self.root.winfo_screenheight() / 2 - 150)
        ))

        ctk.CTkLabel(
            join_window,
            text="Rejoindre un salon",
            font=self.FONTS['button'],
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['primary']
        ).pack(pady=10)

        ctk.CTkLabel(
            join_window,
            text="Serveur: 194.9.172.146:25568",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(pady=5)

        # ID du salon
        room_frame = ctk.CTkFrame(
            join_window,
            fg_color=self.COLORS['background']
        )
        room_frame.pack(pady=5)
        
        ctk.CTkLabel(
            room_frame,
            text="ID du salon:",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(side=ctk.LEFT, padx=5)
        
        room_id_var = ctk.StringVar()
        room_id_entry = ctk.CTkEntry(
            room_frame,
            textvariable=room_id_var,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            border_color=self.COLORS['button_border']
        )
        room_id_entry.pack(side=ctk.LEFT, padx=5)
        
        # Sélection du personnage
        fighter_frame = ctk.CTkFrame(
            join_window,
            fg_color=self.COLORS['background']
        )
        fighter_frame.pack(pady=5)
        
        ctk.CTkLabel(
            fighter_frame,
            text="Personnage:",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(side=ctk.LEFT, padx=5)
        
        fighter_var = ctk.StringVar(value="Tank")
        fighter_dropdown = ctk.CTkComboBox(
            fighter_frame,
            values=["Mitsu", "Tank", "Noya", "ThunderStrike", "Bruiser"],
            variable=fighter_var,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            button_color=self.COLORS['button_border'],
            dropdown_fg_color=self.COLORS['secondary']
        )
        fighter_dropdown.pack(side=ctk.LEFT, padx=5)

        # Nom du joueur
        player_frame = ctk.CTkFrame(
            join_window,
            fg_color=self.COLORS['background']
        )
        player_frame.pack(pady=5)
        
        ctk.CTkLabel(
            player_frame,
            text="Nom:",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(side=ctk.LEFT, padx=5)
        
        player_name_var = ctk.StringVar(value="Joueur")
        player_name_entry = ctk.CTkEntry(
            player_frame,
            textvariable=player_name_var,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            border_color=self.COLORS['button_border']
        )
        player_name_entry.pack(side=ctk.LEFT, padx=5)

        def join_existing_room():
            room_id = room_id_var.get()
            player_name = player_name_var.get()
            fighter_type = fighter_var.get()
            
            if not room_id:
                messagebox.showerror("Erreur", "Veuillez entrer un ID de salon valide.")
                return
            
            from core.game_multi import MultiplayerGame
            game = MultiplayerGame(player_name=player_name, fighter_type=fighter_type, room_id=room_id)
            join_window.destroy()
            self.root.withdraw()  # Cacher la fenêtre principale
            
            # Lancer le jeu
            game.run()
            self.root.deiconify()  # Réafficher la fenêtre principale après la partie

        join_button = ctk.CTkButton(
            join_window,
            text="Rejoindre le salon",
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            hover_color=self.COLORS['hover'],
            command=join_existing_room,
            corner_radius=10,
            border_width=2,
            border_color=self.COLORS['button_border']
        )
        join_button.pack(pady=10)

    def create_game(self) -> None:
        """Affiche un menu pour créer un salon."""
        create_window = ctk.CTkToplevel(self.root)
        create_window.title("Créer un salon")
        create_window.attributes('-topmost', True)
        create_window.geometry("400x250")
        create_window.configure(bg=self.COLORS['background'])

        # Centrer la fenêtre
        create_window.geometry("+{}+{}".format(
            int(self.root.winfo_screenwidth() / 2 - 200),
            int(self.root.winfo_screenheight() / 2 - 125)
        ))

        ctk.CTkLabel(
            create_window,
            text="Créer un salon",
            font=self.FONTS['button'],
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['primary']
        ).pack(pady=10)

        ctk.CTkLabel(
            create_window,
            text="Serveur: 194.9.172.146:25568",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(pady=5)
        
        # Sélection du personnage
        fighter_frame = ctk.CTkFrame(
            create_window,
            fg_color=self.COLORS['background']
        )
        fighter_frame.pack(pady=5)
        
        ctk.CTkLabel(
            fighter_frame,
            text="Personnage:",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(side=ctk.LEFT, padx=5)
        
        fighter_var = ctk.StringVar(value="Mitsu")
        fighter_dropdown = ctk.CTkComboBox(
            fighter_frame,
            values=["Mitsu", "Tank", "Noya", "ThunderStrike", "Bruiser"],
            variable=fighter_var,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            button_color=self.COLORS['button_border'],
            dropdown_fg_color=self.COLORS['secondary']
        )
        fighter_dropdown.pack(side=ctk.LEFT, padx=5)

        # Nom du joueur
        player_frame = ctk.CTkFrame(
            create_window,
            fg_color=self.COLORS['background']
        )
        player_frame.pack(pady=5)
        
        ctk.CTkLabel(
            player_frame,
            text="Nom:",
            font=("Arial", 12),
            bg_color=self.COLORS['background'],
            text_color=self.COLORS['text']
        ).pack(side=ctk.LEFT, padx=5)
        
        player_name_var = ctk.StringVar(value="Joueur")
        player_name_entry = ctk.CTkEntry(
            player_frame,
            textvariable=player_name_var,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            border_color=self.COLORS['button_border']
        )
        player_name_entry.pack(side=ctk.LEFT, padx=5)

        def create_new_room():
            player_name = player_name_var.get()
            fighter_type = fighter_var.get()
            
            from core.game_multi import MultiplayerGame
            game = MultiplayerGame(player_name=player_name, fighter_type=fighter_type)
            create_window.destroy()
            self.root.withdraw()  # Cacher la fenêtre principale
            
            # Lancer le jeu
            game.run()
            self.root.deiconify()  # Réafficher la fenêtre principale après la partie

        create_button = ctk.CTkButton(
            create_window,
            text="Créer le salon",
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            text_color=self.COLORS['text'],
            hover_color=self.COLORS['hover'],
            command=create_new_room,
            corner_radius=10,
            border_width=2,
            border_color=self.COLORS['button_border']
        )
        create_button.pack(pady=10)

    def show_credits(self) -> None:
        """Affiche les crédits avec une interface moderne et interactive."""
        credits_window = ctk.CTkToplevel(self.root)
        credits_window.title("Crédits - PythFighter")
        credits_window.attributes('-topmost', True)
        credits_window.geometry("700x500")
        credits_window.configure(bg_color=self.COLORS['background'])
        credits_window.resizable(False, False)

        # Image de titre (à remplacer par votre logo)
        try:
            logo_img = ctk.CTkImage(
                light_image=Image.open("assets/images/logo.png"),
                dark_image=Image.open("assets/images/logo.png"),
                size=(200, 100)
            )
            logo_label = ctk.CTkLabel(
                credits_window,
                image=logo_img,
                text="",
                bg_color=self.COLORS['background']
            )
            logo_label.pack(pady=(20, 10))
        except Exception:
            # Si pas de logo, afficher un titre
            title_label = ctk.CTkLabel(
                credits_window,
                text="PYTHFIGHTER",
                font=ctk.CTkFont(family="Impact", size=42, weight="bold"),
                text_color=self.COLORS['accent'],
                bg_color=self.COLORS['background']
            )
            title_label.pack(pady=(20, 10))

        subtitle_label = ctk.CTkLabel(
            credits_window,
            text="Un jeu de combat révolutionnaire",
            font=ctk.CTkFont(family="Arial", size=16, slant="italic"),
            text_color=self.COLORS['secondary'],
            bg_color=self.COLORS['background']
        )
        subtitle_label.pack(pady=(0, 20))

        # Créer un frame pour le contenu principal
        main_frame = ctk.CTkFrame(
            credits_window,
            fg_color=self.COLORS['card_background'],
            corner_radius=15,
            border_width=2,
            border_color=self.COLORS['accent']
        )
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=40, pady=(0, 30))

        # Tableau d'onglets
        credits_sections = {
            "Équipe": self._get_team_credits(),
            "Design & Assets": self._get_design_credits(),
            "Audio": self._get_audio_credits(),
            "Remerciements": self._get_special_thanks()
        }

        # Créer les onglets
        tabview = ctk.CTkTabview(
            main_frame,
            fg_color=self.COLORS['card_background'],
            segmented_button_fg_color=self.COLORS['accent'],
            segmented_button_selected_color=self.COLORS['primary'],
            segmented_button_selected_hover_color=self.COLORS['primary_hover'],
            segmented_button_unselected_color=self.COLORS['card_background'],
            segmented_button_unselected_hover_color=self.COLORS['secondary'],
            text_color=self.COLORS['text']
        )
        tabview.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        # Ajouter les sections
        for section_name, section_content in credits_sections.items():
            tab = tabview.add(section_name)

            # Créer un cadre défilable pour chaque section
            scroll_frame = ctk.CTkScrollableFrame(
                tab,
                fg_color="transparent",
                scrollbar_fg_color=self.COLORS['secondary'],
                scrollbar_button_color=self.COLORS['primary'],
                scrollbar_button_hover_color=self.COLORS['primary_hover']
            )
            scroll_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

            # Remplir chaque section avec son contenu formaté
            for item in section_content:
                if isinstance(item, dict):
                    # Style pour les titres
                    title = ctk.CTkLabel(
                        scroll_frame,
                        text=item['title'],
                        font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                        text_color=self.COLORS['accent'],
                        anchor="w"
                    )
                    title.pack(fill=ctk.X, pady=(10, 5), padx=5)

                    # Style pour les membres/éléments sous chaque titre
                    for member in item['members']:
                        member_frame = ctk.CTkFrame(
                            scroll_frame,
                            fg_color=self.COLORS['background'],
                            corner_radius=8
                        )
                        member_frame.pack(fill=ctk.X, pady=3, padx=15)

                        member_label = ctk.CTkLabel(
                            member_frame,
                            text=f"• {member}",
                            font=ctk.CTkFont(family="Arial", size=14),
                            text_color=self.COLORS['text'],
                            anchor="w",
                            padx=10,
                            pady=5
                        )
                        member_label.pack(fill=ctk.X)
                else:
                    # Pour les éléments simples textuels
                    text_label = ctk.CTkLabel(
                        scroll_frame,
                        text=item,
                        font=ctk.CTkFont(family="Arial", size=14, slant="italic"),
                        text_color=self.COLORS['secondary'],
                        anchor="w",
                        wraplength=500
                    )
                    text_label.pack(fill=ctk.X, pady=10, padx=5)

        # Définir l'onglet actif par défaut
        tabview.set("Équipe")

        # Bouton de fermeture
        close_button = ctk.CTkButton(
            credits_window,
            text="Fermer",
            font=ctk.CTkFont(family="Arial", size=16),
            fg_color=self.COLORS['primary'],
            hover_color=self.COLORS['primary_hover'],
            text_color=self.COLORS['text_button'],
            corner_radius=10,
            command=credits_window.destroy,
            width=120
        )
        close_button.pack(side=ctk.BOTTOM, pady=(0, 15))

        # Instruction
        instruction = ctk.CTkLabel(
            credits_window,
            text="Appuyez sur Échap ou Croix/A pour revenir",
            font=ctk.CTkFont(family="Arial", size=14),
            text_color=self.COLORS['text_muted'],
            bg_color=self.COLORS['background']
        )
        instruction.pack(side=ctk.BOTTOM, pady=(0, 5))

        # Ajouter une animation simple d'entrée
        credits_window.withdraw()
        credits_window.update_idletasks()
        x = (credits_window.winfo_screenwidth() - credits_window.winfo_reqwidth()) // 2
        y = (credits_window.winfo_screenheight() - credits_window.winfo_reqheight()) // 2
        credits_window.geometry(f"+{x}+{y}")
        credits_window.deiconify()

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

    def _get_team_credits(self) -> list:
        """Retourne la liste formatée de l'équipe de développement."""
        return [
            {"title": "Programmation", "members": [
                "Direction du développement: Équipe PythFighter",
                "Lead Developer: Carl-Albert LIEVAL",
                "Développeurs: Rémi POLVERINI, Timtohé PICHOT"
            ]},
            {"title": "Direction du Projet", "members": [
                "Production: Moinécha SCHULTZE",
                "Conception du jeu: toute l'équipe PythFighter"
            ]},
            "Développé avec passion par l'équipe PythFighter"
        ]

    def _get_design_credits(self) -> list:
        """Retourne la liste formatée des crédits design."""
        return [
            {"title": "Direction Artistique", "members": [
                "Direction artistique: [Nom du directeur artistique]",
                "Interface utilisateur: [Nom du designer UI]"
            ]},
            {"title": "Graphismes", "members": [
                "Conception des personnages: Moinécha SCHULTZE, Benjamin COURAM, site itch.io",
                "Environnements: Moinécha SCHULTZE",
                "Animation et effets visuels: Moinécha SCHULTZE, Carl-Albert LIEVAL"
            ]}
        ]

    def _get_audio_credits(self) -> list:
        """Retourne la liste formatée des crédits audio."""
        return [
            {"title": "Musique", "members": [
                "Composition originale: trouvée par Moinécha SCHULTZE",
            ]},
            {"title": "Design Sonore", "members": [
                "Bibliothèques sonores: Freesound.org"
            ]}
        ]

    def _get_special_thanks(self) -> list:
        """Retourne la liste formatée des remerciements spéciaux."""
        return [
            {"title": "Remerciements Spéciaux", "members": [
                "Communauté Python",
                "\"Coding with Russ\" et ses sources"
            ]},
            {"title": "Technologies", "members": [
                "CustomTkinter",
                "Pygame",
                "Pillow"
            ]},
            "PythFighter utilise des technologies open source.\nMerci à tous les contributeurs !",
            f"Version {self.VERSION} © {datetime.now().year} PythFighter Team"
        ]

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
        """Affiche un tutoriel interactif avec plusieurs sections défilables."""
        # Crée la fenêtre de tutoriel
        tutorial_window = ctk.CTkToplevel(self.root)
        tutorial_window.title("Tutoriel PythFighter")
        tutorial_window.attributes('-topmost', True)
        tutorial_window.geometry(f"{self.width}x{self.height}")
        tutorial_window.attributes('-fullscreen', True)
        tutorial_window.focus_set()  # Forcer le focus pour capter les événements clavier

        tutorial_canvas = ctk.CTkCanvas(tutorial_window, bg=self.COLORS['background'], highlightthickness=0)
        tutorial_canvas.pack(fill=ctk.BOTH, expand=True)

        # Créer un dégradé d’arrière-plan
        for y in range(0, self.height, 4):
            darkness = int(25 + (y / self.height) * 30)
            color = f"#{darkness:02x}{darkness:02x}{darkness + 15:02x}"
            tutorial_canvas.create_line(0, y, self.width, y, fill=color)

        # Ajouter un effet de grille
        grid_color = "#223366"
        grid_spacing = 50
        for x in range(0, self.width + grid_spacing, grid_spacing):
            tutorial_canvas.create_line(x, 0, x, self.height, fill=grid_color, width=1)
        for y in range(0, self.height + grid_spacing, grid_spacing):
            tutorial_canvas.create_line(0, y, self.width, y, fill=grid_color, width=1)

        # Créer un en-tête de tutoriel
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

        # Sections du tutoriel
        sections = [
            {
                "title": "COMMANDES DE BASE",
                "content": [
                    "Petit bug, veuillez cliquer sur la page une fois pour avoir accès aux contrôles",
                    "et aux conseils de combat.",
                    "",
                    "Utilisez les flèches pour naviguer dans le menu.",
                    "Appuyez sur Échap pour quitter.",
                    "",
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
            },
            {
                "title": "ASTUCES AVANCÉES",
                "content": [
                    "⚡ UTILISEZ LES ATTAQUES SPÉCIALES:",
                    "Les attaques spéciales consomment de l'énergie,",
                    "mais elles peuvent renverser le cours du combat.",
                    "",
                    "🎯 PRÉCISEZ VOS MOUVEMENTS:",
                    "Anticipez les mouvements de votre adversaire",
                    "et utilisez des feintes pour le déstabiliser.",
                    "",
                    "🔥 COMBOS:",
                    "Enchaînez vos attaques pour infliger",
                    "des dégâts massifs et impressionner vos adversaires."
                ]
            }
        ]

        # Variables pour la navigation
        self.current_section = 0
        self.total_sections = len(sections)

        # Fonction d’affichage de la section actuelle
        def display_section(index):
            # Effacer le contenu précédent
            tutorial_canvas.delete("section_content")

            section = sections[index]

            # Titre de la section
            tutorial_canvas.create_text(
                self.width // 2,
                180,
                text=section["title"],
                font=("Arial Black", 36, "bold"),
                fill="#FFA500",
                tags="section_content"
            )

            # Contenu de la section
            content_x = self.width // 2
            content_y = 250
            for line in section["content"]:
                tutorial_canvas.create_text(
                    content_x,
                    content_y,
                    text=line,
                    font=("Arial", 20),
                    fill="#FFFFFF",
                    anchor="center",
                    tags="section_content"
                )
                content_y += 30

            # Indicateurs de navigation
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

            # Instructions de navigation
            tutorial_canvas.create_text(
                self.width // 2,
                self.height - 60,
                text="◀ ▶ : Naviguer | Échap : Quitter",
                font=("Arial", 18),
                fill="#FFFFFF",
                tags="section_content"
            )

        # Afficher la première section
        display_section(self.current_section)

        # Ajouter des raccourcis clavier pour la navigation
        def next_section():
            self.current_section = (self.current_section + 1) % self.total_sections
            display_section(self.current_section)

        def prev_section():
            self.current_section = (self.current_section - 1) % self.total_sections
            display_section(self.current_section)

        tutorial_window.bind("<Left>", lambda e: prev_section())
        tutorial_window.bind("<Right>", lambda e: next_section())
        tutorial_window.bind("<Escape>", lambda e: tutorial_window.destroy())

        # Vérification de l’entrée du contrôleur (pour compléter si nécessaire)
        def check_tutorial_controller():
            if not tutorial_window.winfo_exists():
                return

            buttons, axes = self.controller_manager.get_primary_input()
            current_time = time.time()

            if current_time - self.last_nav_time > self.NAV_COOLDOWN:
                if axes and len(axes) > 0:
                    if axes[0] < -0.5:  # Gauche
                        prev_section()
                        self.last_nav_time = current_time
                    elif axes[0] > 0.5:  # Droite
                        next_section()
                        self.last_nav_time = current_time

            # Si le bouton principal est pressé, quitter (par exemple)
            if buttons and len(buttons) > 0 and buttons[0]:
                tutorial_window.destroy()
                return

            tutorial_window.after(100, check_tutorial_controller)

        tutorial_window.after(100, check_tutorial_controller)

    def return_to_main_menu(self) -> None:
        """Retourne au menu principal."""
        # Recréer l'interface principale
        self.create_interface()
        
    def run(self) -> None:
        """Lance le launcher."""
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.run()

if __name__ == "__main__":
    main()
