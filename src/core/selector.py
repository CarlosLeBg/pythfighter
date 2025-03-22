import subprocess
import pygame
import sys
import os
from math import sin
import random
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Lire la variable INPUT_MODE depuis les variables d'environnement
input_mode = os.getenv('INPUT_MODE', 'keyboard')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import GameSettings
from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser
from managers.position_manager import PositionManager

FIGHTERS = {
    "Mitsu": Mitsu(),
    "Tank": Tank(),
    "Noya": Noya(),
    "ThunderStrike": ThunderStrike(),
    "Bruiser": Bruiser()
}

SETTINGS = GameSettings()
SCREEN_WIDTH = SETTINGS.SCREEN_WIDTH
SCREEN_HEIGHT = SETTINGS.SCREEN_HEIGHT
FPS = SETTINGS.FPS

# Enhanced colors with alpha support
BACKGROUND_COLOR = (15, 15, 25)
TEXT_COLOR = (230, 230, 230)
HOVER_COLOR = (255, 255, 255, 200)
CARD_SHADOW_COLOR = (0, 0, 0, 120)
GRADIENT_TOP = (40, 40, 60)
GRADIENT_BOTTOM = (15, 15, 25)

class ResourceManager:
    def __init__(self, base_path="assets"):
        self.assets = {
            "images": {},
            "sounds": {},
            "fonts": {}
        }
        self.paths = {
            "images": os.path.join(base_path, "images"),
            "sounds": os.path.join(base_path, "sounds"),
            "fonts": os.path.join(base_path, "fonts")
        }
        self.load_resources()

    def load_resources(self):
        self.load_images()
        self.load_sounds()
        self.load_fonts()

    def load_images(self):
        if os.path.exists(self.paths["images"]):
            for file in os.listdir(self.paths["images"]):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        key = os.path.splitext(file)[0]
                        self.assets["images"][key] = pygame.image.load(
                            os.path.join(self.paths["images"], file)).convert_alpha()
                    except Exception as e:
                        print(f"Failed to load image {file}: {e}")

    def load_sounds(self):
        if os.path.exists(self.paths["sounds"]):
            sound_files = {
                "hover": "hover.wav",
                "select": "select.wav",
                "character_select": "character_select.mp3",
                "fight": "fight.wav",
                "versus": "versus.wav"
            }
            for key, file in sound_files.items():
                try:
                    self.assets["sounds"][key] = pygame.mixer.Sound(
                        os.path.join(self.paths["sounds"], file))
                except Exception as e:
                    print(f"Failed to load sound {file}: {e}")

    def load_fonts(self):
        try:
            font_path = os.path.join(self.paths["fonts"], "your-fancy-font.ttf")
            self.assets["fonts"] = {
                'title': pygame.font.Font(font_path if os.path.exists(font_path) else None, 72),
                'subtitle': pygame.font.Font(font_path if os.path.exists(font_path) else None, 48),
                'normal': pygame.font.Font(font_path if os.path.exists(font_path) else None, 36),
                'small': pygame.font.Font(font_path if os.path.exists(font_path) else None, 24)
            }
        except Exception as e:
            print(f"Failed to load fonts: {e}")
            self.assets["fonts"] = {
                'title': pygame.font.Font(None, 72),
                'subtitle': pygame.font.Font(None, 48),
                'normal': pygame.font.Font(None, 36),
                'small': pygame.font.Font(None, 24)
            }

class EnhancedParticleSystem:
    def __init__(self):
        self.particles = []

    def create_particle(self, pos, color, particle_type):
        self.particles.append({
            'pos': list(pos),
            'velocity': [random.uniform(-1, 1), random.uniform(-1, 1)],
            'color': color,
            'size': random.uniform(5, 10),
            'lifetime': random.randint(30, 60),
            'type': particle_type
        })

    def create_explosion(self, pos, color, count=20):
        for _ in range(count):
            self.create_particle(pos, color, 'explosion')

    def update(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['lifetime'] -= 1

            if particle['type'] == 'sparkle':
                particle['size'] *= 0.95
            elif particle['type'] == 'trail':
                particle['velocity'][1] += 0.1  # Gravity effect
            elif particle['type'] == 'explosion':
                particle['size'] *= 0.9
                particle['velocity'][0] *= 0.95
                particle['velocity'][1] *= 0.95

            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            alpha = min(255, particle['lifetime'] * 4)
            color = (*particle['color'][:3], alpha)

            if particle['type'] == 'sparkle':
                pygame.draw.circle(screen, color,
                                   (int(particle['pos'][0]), int(particle['pos'][1])),
                                   int(particle['size']))
            elif particle['type'] in ['trail', 'explosion']:
                size = int(particle['size'])
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                screen.blit(surf, (int(particle['pos'][0] - size), int(particle['pos'][1] - size)))

class CharacterSelect:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pyth Fighter - Character Selection")

        self.resource_manager = ResourceManager()
        self.position_manager = PositionManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.player_devices = {"player1": None, "player2": None}
        self.animation_time = 0
        self.hovered_character = None
        self.particles = EnhancedParticleSystem()
        self.selection_done = False
        self.selection_cooldown = 0

        # Separate cursor positions for each player
        self.cursor_positions = {
            "player1": [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2],
            "player2": [3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
        }

        # Input cooldowns to prevent multiple inputs
        self.input_cooldowns = {
            "keyboard_p1": 0,
            "keyboard_p2": 0
        }

        # Map joysticks to players
        self.joystick_player_map = {}

        # Sound effects
        self.hover_sound = self.resource_manager.assets["sounds"].get("hover")
        self.select_sound = self.resource_manager.assets["sounds"].get("select")

        # Transition effects
        self.transition_alpha = 255
        self.fade_speed = 5
        self.transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transition_surface.fill((0, 0, 0))

        # Track hovered characters for each player
        self.player_hovered = {
            "player1": None,
            "player2": None
        }

        # Ajout pour les animations versus
        self.versus_particles = []
        self.lightning_bolts = []
        self.character_portraits = {}
        self.load_character_portraits()

    def load_character_portraits(self):
        """Charge les portraits des personnages pour l'écran versus"""
        TARGET_SIZE = (200, 250)  # Taille cible désirée
        for fighter_name in FIGHTERS.keys():
            try:
                portrait_path = os.path.join(self.resource_manager.paths["images"], f"{fighter_name.lower()}_portrait.png")
                if os.path.exists(portrait_path):
                    original = pygame.image.load(portrait_path).convert_alpha()
                    # Calculer le ratio pour préserver les proportions
                    width_ratio = TARGET_SIZE[0] / original.get_width()
                    height_ratio = TARGET_SIZE[1] / original.get_height()
                    scale_ratio = min(width_ratio, height_ratio)

                    # Nouvelles dimensions qui préservent le ratio
                    new_width = int(original.get_width() * scale_ratio)
                    new_height = int(original.get_height() * scale_ratio)

                    # Créer une surface de la taille cible
                    portrait = pygame.Surface(TARGET_SIZE, pygame.SRCALPHA)

                    # Redimensionner l'image originale
                    scaled_image = pygame.transform.smoothscale(original, (new_width, new_height))

                    # Centrer l'image redimensionnée
                    x_offset = (TARGET_SIZE[0] - new_width) // 2
                    y_offset = (TARGET_SIZE[1] - new_height) // 2

                    # Coller l'image redimensionnée sur la surface cible
                    portrait.blit(scaled_image, (x_offset, y_offset))

                    self.character_portraits[fighter_name] = portrait
                else:
                    # Portrait par défaut coloré
                    portrait = pygame.Surface(TARGET_SIZE, pygame.SRCALPHA)
                    fighter_color = FIGHTERS[fighter_name].color
                    pygame.draw.rect(portrait, fighter_color, (0, 0, TARGET_SIZE[0], TARGET_SIZE[1]), border_radius=10)
                    self.character_portraits[fighter_name] = portrait
            except Exception as e:
                print(f"Erreur lors du chargement du portrait de {fighter_name}: {e}")
                # Portrait par défaut en cas d'erreur
                portrait = pygame.Surface(TARGET_SIZE, pygame.SRCALPHA)
                pygame.draw.rect(portrait, (100, 100, 100), (0, 0, TARGET_SIZE[0], TARGET_SIZE[1]), border_radius=10)
                self.character_portraits[fighter_name] = portrait

    def draw_gradient_background(self):
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            color = [
                GRADIENT_TOP[i] + (GRADIENT_BOTTOM[i] - GRADIENT_TOP[i]) * progress
                for i in range(3)
            ]
            wave_offset = sin(self.animation_time + y / 100) * 20
            pygame.draw.line(self.screen, color,
                             (max(0, wave_offset), y),
                             (SCREEN_WIDTH + min(0, wave_offset), y))

    def create_card_glow(self, surface, color, radius):
        glow = pygame.Surface((surface.get_width() + radius * 2,
                               surface.get_height() + radius * 2),
                              pygame.SRCALPHA)
        for i in range(radius, 0, -1):
            alpha = int(100 * (i / radius))
            pulse = sin(self.animation_time * 4) * 0.3 + 0.7
            color_pulse = tuple(int(c * pulse) for c in color)
            pygame.draw.rect(glow, (*color_pulse, alpha),
                             (radius - i, radius - i,
                              surface.get_width() + i * 2,
                              surface.get_height() + i * 2),
                             border_radius=20)
        return glow

    def draw_character_card(self, name, data):
        card_rect = self.position_manager.card_positions[name]

        # Check if card is hovered by either player
        p1_hover = card_rect.collidepoint(self.cursor_positions["player1"])
        p2_hover = card_rect.collidepoint(self.cursor_positions["player2"])

        # Update player hovered states
        if p1_hover:
            self.player_hovered["player1"] = name
        if p2_hover:
            self.player_hovered["player2"] = name

        hover = p1_hover or p2_hover

        y_offset = sin(self.animation_time * 3) * 5
        x_offset = 0
        if hover:
            x_offset = sin(self.animation_time * 8) * 3
            self.hovered_character = name
            if pygame.time.get_ticks() % 5 == 0:
                self.particles.create_particle(
                    (card_rect.x + SETTINGS.CARD_WIDTH / 2,
                     card_rect.y + SETTINGS.CARD_HEIGHT),
                    data.color,
                    'trail')
                for _ in range(2):
                    edge_pos = (
                        card_rect.x + random.uniform(0, SETTINGS.CARD_WIDTH),
                        card_rect.y + random.uniform(0, SETTINGS.CARD_HEIGHT)
                    )
                    self.particles.create_particle(edge_pos, data.color, 'sparkle')

        card_surface = pygame.Surface((SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT),
                                      pygame.SRCALPHA)

        shadow_offset = abs(sin(self.animation_time * 2)) * 4 + 4
        pygame.draw.rect(card_surface, CARD_SHADOW_COLOR,
                         (shadow_offset, shadow_offset,
                          SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT),
                         border_radius=20)

        for y in range(SETTINGS.CARD_HEIGHT):
            progress = y / SETTINGS.CARD_HEIGHT
            wave = sin(self.animation_time * 2 + progress * 3) * 0.1
            color = [
                max(0, min(255, data.color[i] * (1 - progress * 0.3 + wave)))
                for i in range(3)
            ]
            alpha = 230 if hover else 200
            pygame.draw.line(card_surface, (*color, alpha),
                             (0, y), (SETTINGS.CARD_WIDTH, y))

        self._draw_card_content(card_surface, data, hover)

        # Show selection glows for both players if selected
        if name == self.selected['player1']:
            glow = self.create_card_glow(card_surface, SETTINGS.PLAYER1_COLOR, 10)
            self.screen.blit(glow,
                            (card_rect.x + x_offset - 10,
                             card_rect.y + y_offset - 10))

        if name == self.selected['player2']:
            glow = self.create_card_glow(card_surface, SETTINGS.PLAYER2_COLOR, 10)
            self.screen.blit(glow,
                            (card_rect.x + x_offset - 10,
                             card_rect.y + y_offset - 10))

        self.screen.blit(card_surface,
                         (card_rect.x + x_offset, card_rect.y + y_offset))

    def _draw_card_content(self, surface, data, hover):
        y_content = 20
        scale = 1 + sin(self.animation_time * 4) * 0.05 if hover else 1
        text = self.resource_manager.assets["fonts"]['subtitle'].render(data.name.split(" ")[0], True, TEXT_COLOR)
        scaled_text = pygame.transform.scale(text,
                                             (int(text.get_width() * scale),
                                              int(text.get_height() * scale)))
        surface.blit(scaled_text,
                     (SETTINGS.CARD_WIDTH // 2 - scaled_text.get_width() // 2, y_content))
        y_content += 50

        style_color = (*TEXT_COLOR[:3], 255 if hover else 200)
        style = self.resource_manager.assets["fonts"]['normal'].render(f"Style: {data.style}", True, style_color)
        surface.blit(style,
                     (SETTINGS.CARD_WIDTH // 2 - style.get_width() // 2, y_content))
        y_content += 40

        for stat_name, value in list(data.stats.items())[:3]:
            stat_text = self.resource_manager.assets["fonts"]['small'].render(stat_name, True, TEXT_COLOR)
            surface.blit(stat_text, (20, y_content))

            bar_width = SETTINGS.CARD_WIDTH - 40
            bg_height = 10 + sin(self.animation_time * 3) * 2 if hover else 10
            pygame.draw.rect(surface, (50, 50, 50),
                             (20, y_content + 20, bar_width, bg_height))

            value_width = int(bar_width * (value / 10 if isinstance(value, (int, float)) else value / 120))
            for x in range(value_width):
                progress = x / bar_width
                wave = sin(self.animation_time * 4 + progress * 10) * 0.1 if hover else 0
                color = [
                    max(0, min(255, data.color[i] * (1 + progress * 0.5 + wave)))
                    for i in range(3)
                ]
                pygame.draw.line(surface, color,
                                 (20 + x, y_content + 20),
                                 (20 + x, y_content + 20 + bg_height))
            y_content += 40

    def draw_detail_panel(self):
        if not self.hovered_character:
            return

        char_data = FIGHTERS[self.hovered_character]
        panel_rect = self.position_manager.get_detail_panel_position()
        surface = pygame.Surface((panel_rect.width, panel_rect.height),
                                 pygame.SRCALPHA)

        for y in range(panel_rect.height):
            progress = y / panel_rect.height
            wave = sin(self.animation_time * 2 + progress * 3) * 0.1
            color = [
                max(0, min(255, int(40 * (1 - progress + wave)))),
                max(0, min(255, int(40 * (1 - progress + wave)))),
                max(0, min(255, int(60 * (1 - progress + wave)))),
                180
            ]
            pygame.draw.line(surface, color, (0, y), (panel_rect.width, y))

        y = 20
        title = self.resource_manager.assets["fonts"]['title'].render(char_data.name.split(" ")[0], True, TEXT_COLOR)
        scale = 1 + sin(self.animation_time * 3) * 0.05
        scaled_title = pygame.transform.scale(title,
                                               (int(title.get_width() * scale),
                                                int(title.get_height() * scale)))
        surface.blit(scaled_title, (20, y))
        y += 60

        words = char_data.description.split()
        line = ""
        highlight_color = (*char_data.color, 150)
        for word in words:
            test_line = line + word + " "
            test_surface = self.resource_manager.assets["fonts"]['normal'].render(test_line, True, TEXT_COLOR)
            if test_surface.get_width() > panel_rect.width - 40:
                desc = self.resource_manager.assets["fonts"]['normal'].render(line, True, TEXT_COLOR)
                highlight = pygame.Surface((desc.get_width(), desc.get_height()),
                                           pygame.SRCALPHA)
                highlight.fill(highlight_color)
                highlight.set_alpha(int(abs(sin(self.animation_time * 2)) * 30))
                surface.blit(highlight, (20, y))
                surface.blit(desc, (20, y))
                y += 30
                line = word + " "
            else:
                line = test_line
        if line:
            desc = self.resource_manager.assets["fonts"]['normal'].render(line, True, TEXT_COLOR)
            highlight = pygame.Surface((desc.get_width(), desc.get_height()),
                                       pygame.SRCALPHA)
            highlight.fill(highlight_color)
            highlight.set_alpha(int(abs(sin(self.animation_time * 2)) * 30))
            surface.blit(highlight, (20, y))
            surface.blit(desc, (20, y))

        self.screen.blit(surface, (panel_rect.x, panel_rect.y))

    def draw_player_prompts(self):
        for player_num, player_type in [("1", "player1"), ("2", "player2")]:
            is_current = not self.selected[player_type]  # Both players can select simultaneously

            text_color = list(TEXT_COLOR)
            if is_current:
                pulse = abs(sin(self.animation_time * 4))
                text_color = [min(255, c + 50 * pulse) for c in text_color]

            # Show device info
            device_info = ""
            if self.player_devices[player_type] == "keyboard":
                device_info = "(Clavier)" if player_num == "1" else "(WASD+Espace)"
            elif self.player_devices[player_type] is not None and self.player_devices[player_type] != "keyboard":
                device_info = "(Manette)"

            player_text = self.resource_manager.assets["fonts"]['normal'].render(
                f"Joueur {player_num}: {self.selected[player_type]} {device_info}"
                if self.selected[player_type] else
                f"Joueur {player_num}: Sélectionner {device_info}",
                True, text_color
            )

            y_pos = SCREEN_HEIGHT - 80
            if is_current:
                y_pos += sin(self.animation_time * 5) * 5

            x_pos = 20 if player_num == "1" else SCREEN_WIDTH - player_text.get_width() - 20
            self.screen.blit(player_text, (x_pos, y_pos))

    def handle_character_selection(self, player, char_name, device_id):
        if not self.selected[player]:
            self.selected[player] = char_name
            pos = self.position_manager.card_positions[char_name].center
            color = SETTINGS.PLAYER1_COLOR if player == "player1" else SETTINGS.PLAYER2_COLOR
            self.particles.create_explosion(pos, color)
            if self.select_sound:
                self.select_sound.play()

            # Store the device used for selection
            self.player_devices[player] = device_id

            # If both players have selected, we're done
            if self.selected['player1'] and self.selected['player2']:
                self.selection_done = True

    def handle_transition(self):
        if self.transition_alpha > 0:
            self.transition_surface.set_alpha(self.transition_alpha)
            self.screen.blit(self.transition_surface, (0, 0))
            self.transition_alpha = max(0, self.transition_alpha - self.fade_speed)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        last_hover_p1 = None
        last_hover_p2 = None

        try:
            pygame.mixer.music.load("assets/sounds/character_select.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

        while running:
            self.animation_time = pygame.time.get_ticks() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A button
                        joystick = pygame.joystick.Joystick(event.instance_id)
                        joystick_id = joystick.get_instance_id()

                        # If this joystick isn't mapped to a player yet
                        if joystick_id not in self.joystick_player_map:
                            # Assign to first available player
                            if self.player_devices["player1"] is None:
                                self.joystick_player_map[joystick_id] = "player1"
                                self.player_devices["player1"] = joystick_id
                            elif self.player_devices["player2"] is None:
                                self.joystick_player_map[joystick_id] = "player2"
                                self.player_devices["player2"] = joystick_id

                        # Get which player this joystick is assigned to
                        player = self.joystick_player_map.get(joystick_id)
                        if player and not self.selected[player]:
                            hovered_char = self.player_hovered[player]
                            if hovered_char:
                                self.handle_character_selection(player, hovered_char, joystick_id)

            # Update hover state for each player
            current_hover_p1 = self.player_hovered["player1"]
            current_hover_p2 = self.player_hovered["player2"]

            if current_hover_p1 != last_hover_p1 and self.hover_sound:
                self.hover_sound.play()
            if current_hover_p2 != last_hover_p2 and self.hover_sound:
                self.hover_sound.play()

            last_hover_p1 = current_hover_p1
            last_hover_p2 = current_hover_p2

            # Update cooldowns
            for key in self.input_cooldowns:
                if self.input_cooldowns[key] > 0:
                    self.input_cooldowns[key] -= 1

            self.handle_input()

            self.screen.fill(BACKGROUND_COLOR)
            self.draw_gradient_background()
            self.particles.update()
            self.particles.draw(self.screen)

            # Reset hovered characters
            self.hovered_character = None
            self.player_hovered = {
                "player1": None,
                "player2": None
            }

            for fighter_name, fighter in FIGHTERS.items():
                self.draw_character_card(fighter_name, fighter)

            self.draw_detail_panel()
            self.draw_player_prompts()
            self.draw_cursors()
            self.handle_transition()

            if self.selection_done:
                self.play_character_intro(self.selected["player1"])
                self.show_versus_screen()

                subprocess.run([sys.executable, "src/core/game.py",
                               self.selected["player1"], self.selected["player2"]])
                sys.exit()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        cursor_speed = 15

        # Player 1 keyboard controls
        if not self.selected["player1"] and (self.player_devices["player1"] is None or self.player_devices["player1"] == "keyboard"):
            moved = False
            if keys[pygame.K_LEFT]:
                self.cursor_positions["player1"][0] -= cursor_speed
                moved = True
            if keys[pygame.K_RIGHT]:
                self.cursor_positions["player1"][0] += cursor_speed
                moved = True
            if keys[pygame.K_UP]:
                self.cursor_positions["player1"][1] -= cursor_speed
                moved = True
            if keys[pygame.K_DOWN]:
                self.cursor_positions["player1"][1] += cursor_speed
                moved = True

            if moved and self.player_devices["player1"] is None:
                self.player_devices["player1"] = "keyboard"

            if keys[pygame.K_RETURN] and self.input_cooldowns["keyboard_p1"] <= 0:
                self.input_cooldowns["keyboard_p1"] = 15
                hovered_char = self.player_hovered["player1"]
                if hovered_char:
                    self.handle_character_selection("player1", hovered_char, "keyboard")

        # Player 2 keyboard controls
        if not self.selected["player2"] and (self.player_devices["player2"] is None or self.player_devices["player2"] == "keyboard"):
            moved = False
            if keys[pygame.K_a]:
                self.cursor_positions["player2"][0] -= cursor_speed
                moved = True
            if keys[pygame.K_d]:
                self.cursor_positions["player2"][0] += cursor_speed
                moved = True
            if keys[pygame.K_w]:
                self.cursor_positions["player2"][1] -= cursor_speed
                moved = True
            if keys[pygame.K_s]:
                self.cursor_positions["player2"][1] += cursor_speed
                moved = True

            if moved and self.player_devices["player2"] is None:
                self.player_devices["player2"] = "keyboard"

            if keys[pygame.K_SPACE] and self.input_cooldowns["keyboard_p2"] <= 0:
                self.input_cooldowns["keyboard_p2"] = 15
                hovered_char = self.player_hovered["player2"]
                if hovered_char:
                    self.handle_character_selection("player2", hovered_char, "keyboard")

        # Handle joystick input
        deadzone = 0.2
        for joystick in self.joysticks:
            joystick_id = joystick.get_instance_id()
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)

            if abs(x_axis) > deadzone or abs(y_axis) > deadzone:
                # Determine which player this joystick controls
                if joystick_id not in self.joystick_player_map:
                    # Assign to first available player
                    if self.player_devices["player1"] is None:
                        self.joystick_player_map[joystick_id] = "player1"
                        self.player_devices["player1"] = joystick_id
                    elif self.player_devices["player2"] is None:
                        self.joystick_player_map[joystick_id] = "player2"
                        self.player_devices["player2"] = joystick_id

                player = self.joystick_player_map.get(joystick_id)
                if player and not self.selected[player]:
                    self.cursor_positions[player][0] += int(x_axis * cursor_speed)
                    self.cursor_positions[player][1] += int(y_axis * cursor_speed)

        # Ensure cursors stay within bounds
        for player in ["player1", "player2"]:
            self.cursor_positions[player][0] = max(0, min(SCREEN_WIDTH, self.cursor_positions[player][0]))
            self.cursor_positions[player][1] = max(0, min(SCREEN_HEIGHT, self.cursor_positions[player][1]))

    def draw_cursors(self):
        # Draw both player cursors if they're active
        for player, position in self.cursor_positions.items():
            if not self.selected[player] and self.player_devices[player] is not None:
                player_color = SETTINGS.PLAYER1_COLOR if player == "player1" else SETTINGS.PLAYER2_COLOR
                time_pulse = abs(sin(self.animation_time * 8)) * 0.5 + 0.5
                size = 15 + int(time_pulse * 10)

                for i in range(3):
                    scaled_size = size - (i * 4)
                    if scaled_size <= 0:
                        continue

                    alpha = int(255 * (1 - i / 3) * time_pulse)
                    color = (*player_color, alpha)

                    cursor_surface = pygame.Surface((scaled_size * 2, scaled_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(cursor_surface, color, (scaled_size, scaled_size), scaled_size, 2)

                    self.screen.blit(cursor_surface,
                                    (position[0] - scaled_size,
                                     position[1] - scaled_size))

    def show_versus_screen(self):
        """Animation améliorée de l'écran versus"""
        # Récupération des données des combattants
        player1_data = FIGHTERS[self.selected["player1"]]
        player2_data = FIGHTERS[self.selected["player2"]]

        # Préparation des sons
        try:
            versus_sound = self.resource_manager.assets["sounds"].get("versus")
            if versus_sound:
                versus_sound.play()
        except:
            pass

        # Paramètres d'animation
        animation_duration = 120  # frames
        transition_in_duration = 30
        hold_duration = 60
        transition_out_duration = 30

        # Surface principale
        vs_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Préparation des portraits
        p1_portrait = self.character_portraits[self.selected["player1"]]
        p2_portrait = self.character_portraits[self.selected["player2"]]
        p1_target_x = SCREEN_WIDTH // 4 - p1_portrait.get_width() // 2
        p2_target_x = 3 * SCREEN_WIDTH // 4 - p2_portrait.get_width() // 2
        p1_target_y = SCREEN_HEIGHT // 2 - p1_portrait.get_height() // 2
        p2_target_y = SCREEN_HEIGHT // 2 - p2_portrait.get_height() // 2

        # Paramètres pour les éclairs
        self.lightning_bolts = []

        # Boucle d'animation
        for frame in range(animation_duration):
            # Calcul des progressions
            if frame < transition_in_duration:
                progress = frame / transition_in_duration
            elif frame < transition_in_duration + hold_duration:
                progress = 1.0
            else:
                progress = 1.0 - (frame - (transition_in_duration + hold_duration)) / transition_out_duration

            # Remplissage du fond avec gradient
            vs_surface.fill(BACKGROUND_COLOR)
            self._draw_versus_background(vs_surface, frame)

            # Animation des portraits
            p1_current_x = int(-p1_portrait.get_width() + (p1_target_x + p1_portrait.get_width()) * min(1.0, progress * 1.5))
            p2_current_x = int(SCREEN_WIDTH + (p2_target_x - SCREEN_WIDTH) * min(1.0, progress * 1.5))

            # Effet de zoom sur les portraits
            portrait_zoom = 1.0 + sin(frame * 0.1) * 0.05 if progress > 0.8 else 1.0

            # Affichage des portraits avec zoom et effets
            p1_scaled = pygame.transform.scale(p1_portrait,
                                               (int(p1_portrait.get_width() * portrait_zoom),
                                                int(p1_portrait.get_height() * portrait_zoom)))
            p2_scaled = pygame.transform.scale(p2_portrait,
                                               (int(p2_portrait.get_width() * portrait_zoom),
                                                int(p2_portrait.get_height() * portrait_zoom)))

            # Aura autour des portraits
            if progress > 0.5:
                self._draw_portrait_aura(vs_surface, p1_current_x, p1_target_y, p1_scaled, player1_data.color, frame)
                self._draw_portrait_aura(vs_surface, p2_current_x, p2_target_y, p2_scaled, player2_data.color, frame)

            # Affichage des portraits
            vs_surface.blit(p1_scaled, (p1_current_x, p1_target_y))
            vs_surface.blit(p2_scaled, (p2_current_x, p2_target_y))

            # Texte VS au centre avec effets
            if progress > 0.7:
                vs_size = int(100 + 30 * sin(frame * 0.2))
                vs_font = pygame.font.Font(None, vs_size)
                vs_text = vs_font.render("VS", True, (255, 255, 255))
                vs_surface.blit(vs_text,
                                (SCREEN_WIDTH // 2 - vs_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2 - vs_text.get_height() // 2))

            # Affichage de l'écran complet
            self.screen.blit(vs_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(16)

        pygame.time.delay(500)

    def _draw_versus_background(self, surface, frame):
        # Draw a dynamic background with gradients and effects
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            wave = sin(frame * 0.05 + progress * 3) * 20
            color = [
                int(GRADIENT_TOP[i] + (GRADIENT_BOTTOM[i] - GRADIENT_TOP[i]) * progress)
                for i in range(3)
            ]
            pygame.draw.line(surface, color,
                           (max(0, wave), y),
                           (SCREEN_WIDTH + min(0, wave), y))

    def _draw_portrait_aura(self, surface, x, y, portrait, color, frame):
        # Draw a glowing aura effect around the portrait
        aura_size = 20
        for i in range(aura_size, 0, -1):
            alpha = int(100 * (i / aura_size))
            pulse = sin(frame * 0.2) * 0.3 + 0.7
            color_pulse = tuple(int(c * pulse) for c in color)
            pygame.draw.rect(surface, (*color_pulse, alpha),
                           (x - i, y - i,
                            portrait.get_width() + i * 2,
                            portrait.get_height() + i * 2),
                           border_radius=10)

    def play_character_intro(self, character_name):
        try:
            sound_file = f"assets/sounds/{character_name.lower()}_intro.wav"
            if os.path.exists(sound_file):
                intro_sound = pygame.mixer.Sound(sound_file)
                intro_sound.play()
        except:
            pass

if __name__ == "__main__":
    game = CharacterSelect()
    game.run()
