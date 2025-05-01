# Importe toutes les librairies nécessaires
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
    """Gère les entrées des manettes avec plus de stabilité."""

    def __init__(self):
        load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
        self.input_mode = os.getenv('INPUT_MODE', 'keyboard')  # Lit le mode d'entrée depuis le fichier .env
        try:
            pygame.init()
            pygame.joystick.init()
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            print(f"Nombre de manettes détectées : {len(self.joysticks)}")
            for joystick in self.joysticks:
                print(f"Manette {joystick.get_instance_id()} : {joystick.get_name()}")
            self.primary_joystick = self.joysticks[0] if self.joysticks else None
        except Exception as e:
            print(f"Erreur d'initialisation des manettes: {e}")
            self.joysticks = []
            self.primary_joystick = None

    def get_input(self):
        """Récupère les entrées de toutes les manettes avec gestion d'erreur."""
        try:
            pygame.event.pump()
            return [([joystick.get_button(i) for i in range(joystick.get_numbuttons())],
                    [joystick.get_axis(i) for i in range(joystick.get_numaxes())]) for joystick in self.joysticks]
        except Exception:
            return []

    def get_primary_input(self):
        """Récupère les entrées de la manette principale avec gestion d'erreur."""
        try:
            if self.primary_joystick:
                pygame.event.pump()
                return [self.primary_joystick.get_button(i) for i in range(self.primary_joystick.get_numbuttons())], \
                      [self.primary_joystick.get_axis(i) for i in range(self.primary_joystick.get_numaxes())]
        except Exception:
            pass
        return [], []

    def refresh_controllers(self):
        """Rafraîchit la liste des manettes connectées."""
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            self.primary_joystick = self.joysticks[0] if self.joysticks else None
            return len(self.joysticks)
        except Exception:
            self.joysticks = []
            self.primary_joystick = None
            return 0

class ParticleSystem:
    """Système de particules pour effets visuels améliorés."""

    def __init__(self, canvas: ctk.CTkCanvas, x: int, y: int, color: str, count: int = 20, 
                 lifetime: float = 1.0, size_range=(2, 6), velocity_range=(-3, 3), gravity=0.1):
        self.canvas = canvas
        self.particles = []
        self.active = True
        self.gravity = gravity

        for _ in range(count):
            vx = random.uniform(velocity_range[0], velocity_range[1])
            vy = random.uniform(velocity_range[0], velocity_range[1])
            size = random.randint(size_range[0], size_range[1])
            fade_rate = random.uniform(0.01, 0.05)
            alpha = 1.0

            # Format de couleur avec support alpha
            base_color = color if color.startswith("#") else "#FFFFFF"
            
            particle = {
                'id': canvas.create_oval(x - size, y - size, x + size, y + size, fill=base_color, outline=""),
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'size': size, 'alpha': alpha, 'fade_rate': fade_rate,
                'lifetime': random.uniform(0.5, lifetime),
                'base_color': base_color
            }
            self.particles.append(particle)

    def update(self) -> bool:
        """Met à jour les particules et retourne True si le système est encore actif."""
        if not self.active or not self.particles:
            return False

        active_particles = False
        particles_to_remove = []

        for p in self.particles:
            p['lifetime'] -= 0.02
            if p['lifetime'] <= 0:
                self.canvas.delete(p['id'])
                particles_to_remove.append(p)
                continue

            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += self.gravity  # Gravité
            p['alpha'] -= p['fade_rate']

            if p['alpha'] <= 0:
                self.canvas.delete(p['id'])
                particles_to_remove.append(p)
                continue

            active_particles = True

            # Extraire les composants de couleur
            base_color = p['base_color']
            r = int(int(base_color[1:3], 16) * p['alpha'])
            g = int(int(base_color[3:5], 16) * p['alpha'])
            b = int(int(base_color[5:7], 16) * p['alpha'])
            
            # Nouvelle couleur avec alpha
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            try:
                self.canvas.itemconfig(p['id'], fill=color)
                self.canvas.coords(p['id'],
                                  p['x'] - p['size'], p['y'] - p['size'],
                                  p['x'] + p['size'], p['y'] + p['size'])
            except:
                particles_to_remove.append(p)

        # Supprimer les particules mortes
        for p in particles_to_remove:
            if p in self.particles:
                self.particles.remove(p)

        self.active = active_particles
        return active_particles

class TransitionEffect:
    """Classe pour gérer les transitions entre écrans."""
    
    def __init__(self, canvas, width, height, effect_type="fade"):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.effect_type = effect_type
        self.active = False
        self.overlay_id = None
        self.progress = 0
        self.callback = None
        self.direction = "in"  # "in" pour apparaître, "out" pour disparaître
        
    def start(self, direction="in", callback=None):
        """Démarre la transition."""
        self.active = True
        self.progress = 0 if direction == "in" else 1
        self.direction = direction
        self.callback = callback
        
        if self.effect_type == "fade":
            alpha = 255 if direction == "in" else 0
            self.overlay_id = self.canvas.create_rectangle(
                0, 0, self.width, self.height,
                fill=f"#{alpha:02x}000000", outline=""
            )
        elif self.effect_type == "wipe":
            position = 0 if direction == "in" else self.width
            self.overlay_id = self.canvas.create_rectangle(
                0, 0, position, self.height,
                fill="#000000", outline=""
            )
        
        return self
        
    def update(self):
        """Met à jour l'animation de transition."""
        if not self.active:
            return False
            
        step = 0.05 if self.direction == "in" else -0.05
        self.progress += step
        
        if self.effect_type == "fade":
            alpha = int(255 * (1 - self.progress)) if self.direction == "in" else int(255 * self.progress)
            self.canvas.itemconfig(self.overlay_id, fill=f"#{alpha:02x}000000")
        elif self.effect_type == "wipe":
            position = int(self.width * self.progress) if self.direction == "in" else int(self.width * (1 - self.progress))
            self.canvas.coords(self.overlay_id, 0, 0, position, self.height)
            
        # Vérifier la fin de la transition
        if (self.direction == "in" and self.progress >= 1) or (self.direction == "out" and self.progress <= 0):
            self.active = False
            self.canvas.delete(self.overlay_id)
            if self.callback:
                self.callback()
            return False
            
        return True

class SoundManager:
    """Gestionnaire de sons et musiques."""
    
    def __init__(self):
        self.sounds = {}
        self.current_music = None
        self.volume = 0.7
        self.music_volume = 0.5
        self.sound_enabled = True
        self.music_enabled = True
        
        # Initialiser le mixer pygame
        try:
            pygame.mixer.init()
        except:
            print("Erreur d'initialisation du système audio")
            
    def load_sound(self, name, path):
        """Charge un effet sonore."""
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.volume)
        except:
            print(f"Impossible de charger le son: {path}")
    
    def play_sound(self, name):
        """Joue un effet sonore."""
        if not self.sound_enabled or name not in self.sounds:
            return
        try:
            self.sounds[name].play()
        except:
            pass
            
    def load_music(self, path):
        """Charge une musique."""
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            self.current_music = path
        except:
            print(f"Impossible de charger la musique: {path}")
            
    def play_music(self, loop=True):
        """Joue la musique chargée."""
        if not self.music_enabled or not self.current_music:
            return
        try:
            pygame.mixer.music.play(-1 if loop else 0)
        except:
            pass
            
    def stop_music(self):
        """Arrête la musique."""
        try:
            pygame.mixer.music.stop()
        except:
            pass
            
    def set_volume(self, volume):
        """Règle le volume des effets sonores."""
        self.volume = max(0, min(1, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
            
    def set_music_volume(self, volume):
        """Règle le volume de la musique."""
        self.music_volume = max(0, min(1, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass
            
    def toggle_sound(self, enabled=None):
        """Active/désactive les effets sonores."""
        if enabled is not None:
            self.sound_enabled = enabled
        else:
            self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
        
    def toggle_music(self, enabled=None):
        """Active/désactive la musique."""
        if enabled is not None:
            self.music_enabled = enabled
        else:
            self.music_enabled = not self.music_enabled
            
        if self.music_enabled and self.current_music:
            self.play_music()
        else:
            self.stop_music()
            
        return self.music_enabled

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
        'button_border': '#FF4500',
        'success': '#4CAF50',
        'warning': '#FFC107',
        'error': '#F44336'
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
        self.sound_manager = SoundManager()
        self.last_nav_time = time.time()
        self.button_pressed = False
        self.particles = []
        self.input_mode = os.getenv('INPUT_MODE', 'keyboard')
        self.transitions = []
        self.setup_window()
        self.create_canvas()
        self.load_background()
        self.create_interface()
        self.bind_controller()
        
        # Charger les préférences
        self.load_preferences()

        # Créer l'effet de transition initial
        self.transition = TransitionEffect(self.canvas, self.width, self.height, "fade")
        self.transition.start("in")
        self.transitions.append(self.transition)

        # Configuration des sons
        self._setup_sounds()

        # Lancer la boucle d'animation
        self.animate()

    def _setup_sounds(self):
        """Configure les sons du launcher."""
        # Ici, vous pouvez ajouter des sons pour le launcher
        # Par exemple:
        # self.sound_manager.load_sound("hover", "sounds/hover.wav")
        # self.sound_manager.load_sound("click", "sounds/click.wav")
        
        # Pour l'instant, nous allons simuler les sons
        self.has_audio_files = False
        
    def load_preferences(self):
        """Charge les préférences utilisateur."""
        # Par défaut, tout est activé
        self.fullscreen = True
        self.music_enabled = True
        self.sound_enabled = True
        
        # Essayer de charger depuis un fichier de configuration
        try:
            if os.path.exists("config.txt"):
                with open("config.txt", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=")
                            if key == "fullscreen":
                                self.fullscreen = value.lower() == "true"
                            elif key == "music":
                                self.music_enabled = value.lower() == "true"
                            elif key == "sound":
                                self.sound_enabled = value.lower() == "true"
        except:
            pass
        
        # Appliquer les préférences
        self.root.attributes('-fullscreen', self.fullscreen)
        self.sound_manager.toggle_music(self.music_enabled)
        self.sound_manager.toggle_sound(self.sound_enabled)

    def save_preferences(self):
        """Sauvegarde les préférences utilisateur."""
        try:
            with open("config.txt", "w") as f:
                f.write(f"fullscreen={str(self.fullscreen).lower()}\n")
                f.write(f"music={str(self.music_enabled).lower()}\n")
                f.write(f"sound={str(self.sound_enabled).lower()}\n")
        except:
            pass

    def setup_window(self) -> None:
        """Configure la fenêtre principale."""
        self.root.title("PythFighter Launcher")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.COLORS['background'])
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_quit)
        
        # Capturer les dimensions de l'écran
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

    def create_canvas(self) -> None:
        """Crée et configure le canvas principal."""
        self.canvas = ctk.CTkCanvas(self.root, bg=self.COLORS['background'], highlightthickness=0)
        self.canvas.pack(fill=ctk.BOTH, expand=True)

    def load_background(self) -> None:
        """Charge ou crée l'arrière-plan avec des effets améliorés."""
        # Créer un fond avec un effet de grille
        grid_spacing = 50
        grid_color = "#223366"

        # Dessiner un dégradé de fond
        for y in range(0, self.height, 2):  # Plus fins pour un dégradé plus lisse
            # Créer un dégradé du haut vers le bas avec plus de variation
            darkness = int(30 + (y / self.height) * 30)
            blue_value = int(darkness + 20 + 10 * math.sin(y / 100))
            color = f"#{darkness:02x}{darkness:02x}{blue_value:02x}"
            self.canvas.create_line(0, y, self.width, y, fill=color)

        # Créer l'effet de grille avec légère oscillation
        for x in range(0, self.width + grid_spacing, grid_spacing):
            offset = int(5 * math.sin(x / 200))
            self.canvas.create_line(x, 0, x + offset, self.height, fill=grid_color, width=1)

        for y in range(0, self.height + grid_spacing, grid_spacing):
            offset = int(5 * math.sin(y / 200))
            self.canvas.create_line(0, y, self.width + offset, y, fill=grid_color, width=1)

        # Ajouter un effet de lumière au centre plus dynamique
        radial_colors = [
            (120, "#16213E"),
            (350, "#1A1A2E"),
            (700, "#0D0D1A"),
        ]

        center_x, center_y = self.width // 2, self.height // 3
        for radius, color in radial_colors:
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline=""
            )
            
        # Ajouter des particules d'ambiance
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height // 3)
            self._add_ambient_particles(x, y)

    def _add_ambient_particles(self, x, y):
        """Ajoute des particules d'ambiance à l'arrière-plan."""
        colors = [self.COLORS['primary'], self.COLORS['highlight'], "#44AAFF"]
        color = random.choice(colors)
        particle_system = ParticleSystem(
            self.canvas, x, y, color,
            count=random.randint(5, 15), 
            lifetime=random.uniform(1.0, 3.0),
            size_range=(1, 4),
            velocity_range=(-1, 1),
            gravity=0.05
        )
        self.particles.append(particle_system)

    def create_interface(self) -> None:
        """Crée l'interface utilisateur principale."""
        self._create_title()
        self._create_menu_buttons()
        self._create_version_info()
        self._create_controller_indicator()

    def _create_title(self) -> None:
        """Crée le titre du jeu avec un effet d'ombre amélioré."""
        screen_width = self.width
        
        # Créer plusieurs couches d'ombre pour un effet plus profond
        shadow_offsets = [(5, 5), (4, 4), (3, 3), (2, 2)]
        for offset_x, offset_y in shadow_offsets:
            self.canvas.create_text(
                screen_width // 2 + offset_x,
                150 + offset_y,
                text="PYTH FIGHTER",
                font=self.FONTS['title'],
                fill=self.COLORS['shadow'],
                tags="title_shadow"
            )
            
        # Effet de lueur autour du titre
        glow_color = "#FF6B6B22"  # Rouge avec transparence
        for i in range(3, 0, -1):
            self.canvas.create_text(
                screen_width // 2,
                150,
                text="PYTH FIGHTER",
                font=self.FONTS['title'],
                fill=glow_color,
                tags=f"title_glow_{i}"
            )
            
        # Texte principal
        self.title_text = self.canvas.create_text(
            screen_width // 2,
            150,
            text="PYTH FIGHTER",
            font=self.FONTS['title'],
            fill=self.COLORS['primary'],
            tags="title_main"
        )
        
        # Sous-titre avec animation
        self.subtitle_text = self.canvas.create_text(
            screen_width // 2, 
            250,
            text="Édition Ultimate 2.0",
            font=self.FONTS['subtitle'],
            fill=self.COLORS['highlight'],
            tags="subtitle"
        )

    def _create_menu_buttons(self) -> None:
        """Crée les boutons du menu principal avec effets de survol améliorés."""
        menu_items = [
            ("Démarrer", self.launch_game),
            ("Crédits", self.show_credits),
            ("Options", self.show_options),
            ("Tutoriel", self.show_tutorial),
            ("Quitter", self.confirm_quit)
        ]

        self.buttons = []
        button_frame = ctk.CTkFrame(self.root, bg_color=self.COLORS['background'], fg_color="transparent")
        
        for i, (text, command) in enumerate(menu_items):
            # Créer un cadre pour l'animation du bouton
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
            
            # Créer une fonction de rappel pour les survols
            def on_enter(e, btn=button):
                if self.has_audio_files:
                    self.sound_manager.play_sound("hover")
                btn.configure(fg_color=self.COLORS['hover'])
                x, y = self.canvas.winfo_pointerxy()
                x -= self.canvas.winfo_rootx()
                y -= self.canvas.winfo_rooty()
                self._add_hover_particles(x, y)
                
            def on_leave(e, btn=button, index=i):
                btn.configure(fg_color=self.COLORS['secondary'] if self.selected_index != index else self.COLORS['hover'])
                
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
            self.canvas.create_window(
                self.width // 2,
                400 + (i * 100),
                window=button,
                width=400,
                height=70,
                tags=f"button_{i}"
            )
            self.buttons.append(button)

    def _add_hover_particles(self, x, y):
        """Ajoute des particules lors du survol d'un bouton."""
        colors = [self.COLORS['primary'], self.COLORS['highlight'], "#44AAFF"]
        color = random.choice(colors)
        particle_system = ParticleSystem(
            self.canvas, x, y, color,
            count=random.randint(10, 20), 
            lifetime=0.8,
            size_range=(2, 5),
            velocity_range=(-2, 2),
            gravity=0.03
        )
        self.particles.append(particle_system)

    def _create_version_info(self) -> None:
        """Ajoute les informations de version en bas de l'écran."""
        version_text = "Version 2.0.0 - © 2025 PythFighter Team"
        self.canvas.create_text(
            10, self.height - 10,
            text=version_text,
            font=("Arial", 10),
            fill=self.COLORS['text'],
            anchor="sw",
            tags="version_info"
        )

    def _create_controller_indicator(self) -> None:
        """Crée un indicateur de manette connectée."""
        self.controller_icon = self.canvas.create_text(
            self.width - 20, 20,
            text="🎮 Connecté" if self.controller_manager.primary_joystick else "⌨️ Clavier",
            font=("Arial", 12),
            fill="#4CAF50" if self.controller_manager.primary_joystick else "#FFA500",
            anchor="ne",
            tags="controller_indicator"
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
            if i == index:
                # Ajouter un effet de particules autour du bouton sélectionné
                btn_x = self.width // 2
                btn_y = 400 + (i * 100)
                if random.random() < 0.2:  # Limitons la fréquence des particules
                    self._add_selection_particles(btn_x, btn_y)

    def _add_selection_particles(self, x, y):
        """Ajoute des particules autour du bouton sélectionné."""
        offset_x = random.randint(-200, 200)
        offset_y = random.randint(-20, 20)
        
        particle_system = ParticleSystem(
            self.canvas, x + offset_x, y + offset_y,
            self.COLORS['highlight'],
            count=random.randint(3, 8), 
            lifetime=1.0,
            size_range=(2, 5),
            velocity_range=(-1, 1),
            gravity=0.02
        )
        self.particles.append(particle_system)

    def check_controller(self) -> None:
        """Vérifie les entrées de la manette avec gestion améliorée."""
        if not hasattr(self, 'root') or not self.root.winfo_exists():
            return

        # Vérifier périodiquement si la manette est connectée
        if time.time() % 5 < 0.1:  # Environ toutes les 5 secondes
            num_controllers = self.controller_manager.refresh_controllers()
            self.canvas.itemconfig(
                self.controller_icon,
                text="🎮 Connecté" if num_controllers > 0 else "⌨️ Clavier",
                fill="#4CAF50" if num_controllers > 0 else "#FFA500"
            )

        buttons, axes = self.controller_manager.get_primary_input()
        current_time = time.time()

        # Navigation verticale
        if current_time - self.last_nav_time > self.NAV_COOLDOWN:
            if axes and len(axes) > 1:
                if axes[1] < -0.5:  # Haut
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    self._highlight_button(self.selected_index)
                    if self.has_audio_files:
                        self.sound_manager.play_sound("hover")
                    self.last_nav_time = current_time
                elif axes[1] > 0.5:  # Bas
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    self._highlight_button(self.selected_index)
                    if self.has_audio_files:
                        self.sound_manager.play_sound("hover")
                    self.last_nav_time = current_time

        # Bouton A/X pour sélection
        if buttons and len(buttons) > 0:
            if buttons[0] and not self.button_pressed:
                self.button_pressed = True
                if self.has_audio_files:
                    self.sound_manager.play_sound("click")
                self.buttons[self.selected_index].invoke()
            elif not buttons[0]:
                self.button_pressed = False

        # Bouton Start
        if buttons and len(buttons) > 7 and buttons[7]:
            self.confirm_quit()

        self.root.after(50, self.check_controller)  # Fréquence plus rapide pour meilleure réactivité

    def launch_game(self) -> None:
        """Lance le jeu principal avec transition."""
        def start_game():
            game_path = os.path.join(os.path.dirname(__file__), "selector.py")
            try:
                subprocess.Popen([sys.executable, game_path])
                self.root.quit()
            except Exception as e:
                messagebox.showerror("Erreur de lancement", f"Impossible de lancer le jeu:\n{str(e)}")
        
        # Créer une transition avant de lancer le jeu
        transition = TransitionEffect(self.canvas, self.width, self.height, "fade")

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

    def run(self) -> None:
        """Lance le launcher."""
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.run()

if __name__ == "__main__":
    main()