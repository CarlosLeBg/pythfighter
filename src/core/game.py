import pygame
import sys
import time
import os
from enum import Enum
import logging
import random

# Configuration des logs
logging.basicConfig(filename='launcher.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser

BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

# Constants
GRAVITY = 0.4
GROUND_Y = VISIBLE_HEIGHT - VISIBLE_HEIGHT // 5.4
MAX_JUMP_HEIGHT = 60

class GameState(Enum):
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    PAUSED = "paused"
    VICTORY = "victory"
    OPTIONS = "options"

def load_animation(path, action, frame_count, fighter_width, fighter_height):
    frames = []
    animation_folder = os.path.join(path, f"{action}")
    logging.info(f"Tentative de chargement de l'animation depuis: {animation_folder}")

    if not os.path.exists(animation_folder):
        logging.error(f"Dossier d'animation introuvable - {animation_folder}")
        return frames

    for i in range(frame_count):
        frame_name = f"frame_{i:02}_delay-0.1s.png"
        frame_path = os.path.join(animation_folder, frame_name)

        if not os.path.exists(frame_path):
            logging.error(f"Fichier introuvable - {frame_path}")
            continue

        try:
            img = pygame.image.load(frame_path).convert_alpha()
            img = pygame.transform.scale(img, (fighter_width, fighter_height))
            frames.append(img)
            logging.debug(f"Image chargée avec succès: {frame_path}")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de {frame_path}: {e}")

    if not frames:
        logging.error(f"Aucune frame chargée pour l'action {action} dans {animation_folder}")
    else:
        logging.info(f"Animation '{action}' chargée avec succès: {len(frames)} frames")

    return frames

class Fighter:
    def __init__(self, player, x, y, fighter_data, ground_y):
        self.player = player
        self.name = fighter_data.name
        self.color = fighter_data.color
        self.speed = fighter_data.speed * 0.9
        self.damage = fighter_data.damage
        self.max_health = fighter_data.stats["Vie"]
        self.health = self.max_health
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.direction = 1 if player == 1 else -1
        self.fighter_width = VISIBLE_WIDTH // 16
        self.fighter_height = VISIBLE_HEIGHT // 4
        self.ground_y = ground_y
        self.rect = pygame.Rect(x, y, self.fighter_width, self.fighter_height)
        self.hitbox = pygame.Rect(x + self.fighter_width//4, y + self.fighter_height//4,
                                  self.fighter_width//2, self.fighter_height*3//4)
        self.on_ground = True
        self.attacking = False
        self.can_attack = True
        self.blocking = False
        self.attack_cooldown = 0
        self.invincibility_frames = 0
        self.combo_count = 0
        self.last_hit_time = 0
        self.block_stamina_drain_timer = 0
        self.animations = None
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.special_attack_cooldown = 0

        logging.info(f"Chargement des animations pour {self.name}...")
        base_path = os.path.join("src", "assets", "characters", self.name.lower())

        if not os.path.exists(base_path):
            logging.error(f"Dossier de base pour les animations introuvable: {base_path}")
        else:
            logging.info(f"Dossier de base trouvé: {base_path}")

            self.animations = {
                "idle": load_animation(base_path, "idle", 10, self.fighter_width, self.fighter_height),
                "walk": load_animation(base_path, "walk", 8, self.fighter_width, self.fighter_height),
                "attack": load_animation(base_path, "attack", 21, self.fighter_width, self.fighter_height),
                "dead": load_animation(base_path, "dead", 16, self.fighter_width, self.fighter_height),
                "special_attack": load_animation(base_path, "special_attack", 15, self.fighter_width, self.fighter_height),
            }

            for anim_name, frames in self.animations.items():
                logging.info(f"Animation '{anim_name}': {len(frames)} frames chargées")

    def draw(self, surface):
        if self.animations and any(len(frames) > 0 for frames in self.animations.values()):
            if self.current_animation in self.animations and len(self.animations[self.current_animation]) > 0:
                frame_idx = int(self.animation_frame) % len(self.animations[self.current_animation])
                sprite = self.animations[self.current_animation][frame_idx]

                if self.direction == -1:
                    sprite = pygame.transform.flip(sprite, True, False)

                surface.blit(sprite, (self.rect.x, self.rect.y))
                self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.animations[self.current_animation])
            else:
                if self.invincibility_frames % 4 < 2:
                    pygame.draw.rect(surface, self.color, self.rect)
                pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        else:
            if self.invincibility_frames % 4 < 2:
                pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

        self.draw_health_stamina_bars(surface)

    def draw_health_stamina_bars(self, surface):
        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)
        health_color = (int(255 * (1 - health_percentage)), int(255 * health_percentage), 0)

        bar_x = 20 if self.player == 1 else VISIBLE_WIDTH - bar_width - 20

        pygame.draw.rect(surface, (100, 0, 0), (bar_x, 10, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(surface, health_color, (bar_x, 10, bar_width * health_percentage, bar_height), border_radius=10)

        stamina_percentage = max(0, self.stamina / self.max_stamina)
        stamina_color = (255, 165, 0)

        pygame.draw.rect(surface, (0, 0, 100), (bar_x, 40, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(surface, stamina_color, (bar_x, 40, bar_width * stamina_percentage, bar_height), border_radius=10)

        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.name, True, (220, 220, 240))
        health_text = name_font.render(f"{int(self.health)}/{self.max_health}", True, (150, 150, 180))
        combo_text = name_font.render(f"Combo: {self.combo_count}", True, (255, 215, 0))

        if self.player == 1:
            surface.blit(name_text, (bar_x, 60))
            surface.blit(health_text, (bar_x + bar_width - 100, 60))
            surface.blit(combo_text, (bar_x, 80))
        else:
            surface.blit(name_text, (bar_x + bar_width - name_text.get_width(), 60))
            surface.blit(health_text, (bar_x, 60))
            surface.blit(combo_text, (bar_x + bar_width - combo_text.get_width(), 80))

        if self.blocking and self.stamina > 0:
            block_font = pygame.font.Font(None, 20)
            block_text = block_font.render("BLOCKING", True, (0, 255, 255))
            block_x = bar_x if self.player == 1 else bar_x + bar_width - block_text.get_width()
            surface.blit(block_text, (block_x, 100))

        if self.special_attack_cooldown > 0:
            special_font = pygame.font.Font(None, 20)
            special_text = special_font.render("SPECIAL READY", True, (255, 0, 0))
            special_x = bar_x if self.player == 1 else bar_x + bar_width - special_text.get_width()
            surface.blit(special_text, (special_x, 120))

    def take_damage(self, damage, current_time):
        if self.invincibility_frames <= 0:
            actual_damage = damage * (0.5 if self.blocking and self.stamina > 0 else 1)
            self.health = max(0, self.health - actual_damage)
            self.invincibility_frames = 30
            if current_time - self.last_hit_time < 1.0:
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.last_hit_time = current_time

    def attack(self, opponent_x):
        if self.can_attack and self.attack_cooldown == 0 and not self.blocking and self.stamina >= 10:
            distance = abs(self.rect.centerx - opponent_x)
            if distance < self.rect.width * 2:
                self.attacking = True
                self.can_attack = False
                self.attack_cooldown = 15
                self.stamina -= 10

    def special_attack(self):
        if self.special_attack_cooldown == 0 and self.stamina >= 90:
            self.attacking = True
            self.current_animation = "special_attack"
            self.special_attack_cooldown = 120
            self.stamina -= 90

    def reset_attack(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 0:
                self.attacking = False
                self.can_attack = True

        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1

    def block(self):
        if self.stamina > 0:
            self.blocking = True
            self.block_stamina_drain_timer += 1
            if self.block_stamina_drain_timer >= 6:
                self.stamina = max(0, self.stamina - 12)
                self.block_stamina_drain_timer = 0
        else:
            self.blocking = False

    def stop_blocking(self):
        self.blocking = False
        self.block_stamina_drain_timer = 0

    def recover_stamina(self):
        if not self.blocking and self.stamina < self.max_stamina:
            self.stamina += 0.1
        self.stamina = min(self.stamina, self.max_stamina)

    def update_physics(self):
        if self.animations and any(len(frames) > 0 for frames in self.animations.values()):
            if self.attacking and "attack" in self.animations and len(self.animations["attack"]) > 0:
                self.current_animation = "attack"
            elif not self.on_ground:
                if "idle" in self.animations and len(self.animations["idle"]) > 0:
                    self.current_animation = "idle"
            elif abs(self.vel_x) > 0.5:
                if "walk" in self.animations and len(self.animations["walk"]) > 0:
                    self.current_animation = "walk"
            else:
                if "idle" in self.animations and len(self.animations["idle"]) > 0:
                    self.current_animation = "idle"

            if self.health <= 0 and "dead" in self.animations and len(self.animations["dead"]) > 0:
                self.current_animation = "dead"

        if not self.on_ground:
            self.vel_y += GRAVITY

        friction = 0.85 if self.on_ground else 0.95
        self.vel_x *= friction

        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        if self.pos_y < MAX_JUMP_HEIGHT:
            self.pos_y = MAX_JUMP_HEIGHT
            self.vel_y = 0

        if self.pos_y + self.rect.height >= self.ground_y:
            self.pos_y = self.ground_y - self.rect.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.pos_x = max(0, min(self.pos_x, VISIBLE_WIDTH - self.rect.width))

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        self.hitbox.topleft = (self.rect.x + self.rect.width // 4, self.rect.y + self.rect.height // 4)

        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1

        self.reset_attack()

class Game:
    def __init__(self, player1_type="Mitsu", player2_type="Tank"):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        pygame.display.set_caption("PythFighter")

        self.bg_selected = random.choice(["bg_2.png", "backg.png"])

        try:
            bg_path = os.path.join("src", "assets", "backgrounds", self.bg_selected)
            self.bg_image = pygame.image.load(bg_path)
            self.bg_image = pygame.transform.scale(self.bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
            logging.info(f"Image de fond chargée avec succès: {bg_path}")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de l'image de fond: {e}")
            self.bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
            self.bg_image.fill((50, 50, 80))

        self.ground_y = VISIBLE_HEIGHT - 91 if self.bg_selected == "backg.png" else VISIBLE_HEIGHT - 98
        logging.info(f"Background sélectionné: {self.bg_selected}, hauteur du sol: {self.ground_y}")

        fighter_map = {
            "Mitsu": Mitsu,
            "Tank": Tank,
            "Noya": Noya,
            "ThunderStrike": ThunderStrike,
            "Bruiser": Bruiser
        }
        fighter_height = VISIBLE_HEIGHT // 4

        if player1_type not in fighter_map:
            logging.warning(f"Type de combattant invalide: {player1_type}, utilisation de Mitsu par défaut")
            player1_type = "Mitsu"
        if player2_type not in fighter_map:
            logging.warning(f"Type de combattant invalide: {player2_type}, utilisation de Tank par défaut")
            player2_type = "Tank"

        self.fighters = [
            Fighter(1, VISIBLE_WIDTH//4, self.ground_y - fighter_height,
                    fighter_map[player1_type](), self.ground_y),
            Fighter(2, VISIBLE_WIDTH*3//4, self.ground_y - fighter_height,
                    fighter_map[player2_type](), self.ground_y)
        ]

        self.controllers = []
        for i in range(min(2, pygame.joystick.get_count())):
            try:
                joy = pygame.joystick.Joystick(i)
                joy.init()
                self.controllers.append(joy)
                logging.info(f"Controller {i} initialized with {joy.get_numaxes()} axes and {joy.get_numbuttons()} buttons.")
            except Exception as e:
                logging.error(f"Erreur lors de l'initialisation du contrôleur {i}: {e}")

        self.clock = pygame.time.Clock()
        self.game_state = GameState.COUNTDOWN
        self.start_time = time.time()
        self.game_start_time = None
        self.round_time = 99
        self.font = pygame.font.Font(None, 36)
        self.winner = None

        self.menu_options = ["Resume", "Options", "Quit"]
        self.selected_option = 0

        try:
            pygame.mixer.init()
            self.hit_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "hit.wav"))
            self.victory_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "victory.wav"))
            self.menu_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "menu.wav"))
            self.sounds_loaded = True
            logging.info("Sons chargés avec succès")
        except Exception as e:
            logging.error(f"Impossible de charger les effets sonores: {e}")
            self.sounds_loaded = False
            self.hit_sound = None
            self.victory_sound = None
            self.menu_sound = None

    def draw_timer(self):
        if self.game_start_time:
            remaining_time = max(0, int(self.round_time - (time.time() - self.game_start_time)))
            timer_text = self.font.render(str(remaining_time), True, (255, 255, 255))
            timer_rect = timer_text.get_rect(center=(VISIBLE_WIDTH//2, 30))
            self.screen.blit(timer_text, timer_rect)
            return remaining_time
        return self.round_time

    def draw_pause_menu(self):
        pause_surface = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 180))
        self.screen.blit(pause_surface, (0, 0))

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("PAUSE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4))
        self.screen.blit(title_text, title_rect)

        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2 + i * 50))
            self.screen.blit(option_text, option_rect)

            if i == self.selected_option:
                pygame.draw.rect(self.screen, (255, 255, 0), option_rect.inflate(20, 10), 2)

        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("↑/↓: Navigate   Enter: Select", True, (150, 150, 150))
        controls_rect = controls_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT*3//4 + 50))
        self.screen.blit(controls_text, controls_rect)

        pygame.display.flip()

    def draw_victory_screen(self):
        victory_surface = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        victory_surface.fill((0, 0, 0, 180))
        self.screen.blit(victory_surface, (0, 0))

        title_font = pygame.font.Font(None, 72)
        winner_name = self.fighters[self.winner-1].name
        title_text = title_font.render(f"PLAYER {self.winner} WINS!", True, (255, 215, 0))
        name_text = title_font.render(f"{winner_name}", True, self.fighters[self.winner-1].color)

        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4))
        name_rect = name_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4 + 80))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(name_text, name_rect)

        pulse = abs(pygame.time.get_ticks() % 2000 - 1000) / 1000
        size = 150 + pulse * 50
        pygame.draw.circle(self.screen, self.fighters[self.winner-1].color,
                           (VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2 + 50), size, 5)

        continue_font = pygame.font.Font(None, 36)
        continue_text = continue_font.render("Press ENTER to continue", True, (200, 200, 200))
        continue_rect = continue_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT*3//4 + 50))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()

    def handle_input(self, fighter, controller, keys, current_time):
        deadzone = 0.2

        if controller:
            try:
                x_axis = controller.get_axis(0)
                if abs(x_axis) > deadzone:
                    fighter.vel_x = fighter.speed * 2 * x_axis
                    fighter.direction = 1 if x_axis > 0 else -1

                if controller.get_button(0) and fighter.on_ground:
                    fighter.vel_y = -10
                    fighter.on_ground = False

                if controller.get_button(2):
                    fighter.block()
                else:
                    fighter.stop_blocking()

                if controller.get_button(1):
                    fighter.attack(self.fighters[1 if fighter.player == 1 else 0].rect.centerx)

                if controller.get_button(3):
                    fighter.special_attack()

                if self.game_state in [GameState.PAUSED, GameState.VICTORY]:
                    if controller.get_button(7):
                        if self.game_state == GameState.PAUSED:
                            self.game_state = GameState.PLAYING
                        elif self.game_state == GameState.VICTORY:
                            pygame.quit()
                            sys.exit()

                    try:
                        dpad_y = controller.get_hat(0)[1] if controller.get_numhats() > 0 else 0
                        if dpad_y == 1:
                            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                            pygame.time.delay(200)
                        elif dpad_y == -1:
                            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                            pygame.time.delay(200)
                    except Exception as e:
                        logging.error(f"Erreur lors de la navigation du D-pad: {e}")
            except Exception as e:
                logging.error(f"Erreur lors de la gestion des entrées du contrôleur: {e}")

        if keys:
            if fighter.player == 1:
                if keys[pygame.K_a]:
                    fighter.vel_x = -fighter.speed * 2
                    fighter.direction = -1
                elif keys[pygame.K_d]:
                    fighter.vel_x = fighter.speed * 2
                    fighter.direction = 1

                if keys[pygame.K_w] and fighter.on_ground:
                    fighter.vel_y = -10
                    fighter.on_ground = False

                if keys[pygame.K_LSHIFT]:
                    fighter.block()
                else:
                    fighter.stop_blocking()

                if keys[pygame.K_r]:
                    fighter.attack(self.fighters[1].rect.centerx)

                if keys[pygame.K_t]:
                    fighter.special_attack()
            else:
                if keys[pygame.K_LEFT]:
                    fighter.vel_x = -fighter.speed * 2
                    fighter.direction = -1
                elif keys[pygame.K_RIGHT]:
                    fighter.vel_x = fighter.speed * 2
                    fighter.direction = 1

                if keys[pygame.K_UP] and fighter.on_ground:
                    fighter.vel_y = -10
                    fighter.on_ground = False

                if keys[pygame.K_RSHIFT]:
                    fighter.block()
                else:
                    fighter.stop_blocking()

                if keys[pygame.K_RETURN]:
                    fighter.attack(self.fighters[0].rect.centerx)

                if keys[pygame.K_p]:
                    fighter.special_attack()

    def handle_menu_input(self, keys, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    if self.sounds_loaded and self.menu_sound:
                        try:
                            self.menu_sound.play()
                        except Exception as e:
                            logging.error(f"Erreur lors de la lecture du son de menu: {e}")
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    if self.sounds_loaded and self.menu_sound:
                        try:
                            self.menu_sound.play()
                        except Exception as e:
                            logging.error(f"Erreur lors de la lecture du son de menu: {e}")
                elif event.key == pygame.K_RETURN:
                    self.execute_menu_option()
                elif event.key == pygame.K_ESCAPE:
                    if self.game_state == GameState.PAUSED:
                        self.game_state = GameState.PLAYING

    def execute_menu_option(self):
        selected = self.menu_options[self.selected_option]
        if selected == "Resume":
            self.game_state = GameState.PLAYING
        elif selected == "Options":
            self.game_state = GameState.OPTIONS
            self.show_options_menu()
        elif selected == "Quit":
            pygame.quit()
            sys.exit()

    def show_options_menu(self):
        options_surface = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        options_surface.fill((0, 0, 0, 180))
        self.screen.blit(options_surface, (0, 0))

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("OPTIONS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4))
        self.screen.blit(title_text, title_rect)

        options = ["Sound: ON" if self.sounds_loaded else "Sound: OFF", "Back to Game"]
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2 + i * 50))
            self.screen.blit(option_text, option_rect)

            if i == 0:
                pygame.draw.rect(self.screen, (255, 255, 0), option_rect.inflate(20, 10), 2)

        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("↑/↓: Navigate   Enter: Select", True, (150, 150, 150))
        controls_rect = controls_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT*3//4 + 50))
        self.screen.blit(controls_text, controls_rect)

        pygame.display.flip()

    def draw_countdown(self, number):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_image, (0, 0))

        for fighter in self.fighters:
            fighter.draw(self.screen)

        overlay = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 200)
        text = font.render(str(number), True, (255, 255, 255))
        text_rect = text.get_rect(center=(VISIBLE_WIDTH/2, VISIBLE_HEIGHT/2))

        for i in range(20, 0, -5):
            glow = pygame.Surface((text.get_width() + i*2, text.get_height() + i*2), pygame.SRCALPHA)
            glow.fill((0, 0, 0, 0))
            pygame.draw.rect(glow, (255, 255, 0, 10), (0, 0, text.get_width() + i*2, text.get_height() + i*2), border_radius=10)
            self.screen.blit(glow, (text_rect.x - i, text_rect.y - i))

        self.screen.blit(text, text_rect)

        ready_font = pygame.font.Font(None, 72)
        ready_text = ready_font.render("GET READY!", True, (255, 255, 255))
        ready_rect = ready_text.get_rect(center=(VISIBLE_WIDTH/2, VISIBLE_HEIGHT/2 - 150))
        self.screen.blit(ready_text, ready_rect)

        pygame.display.flip()
        pygame.time.wait(1000)

    def update(self):
        current_time = time.time()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GameState.PLAYING:
                        self.game_state = GameState.PAUSED
                    elif self.game_state == GameState.PAUSED:
                        self.game_state = GameState.PLAYING

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_image, (0, 0))

        keys = pygame.key.get_pressed()

        if self.game_state == GameState.PAUSED:
            for fighter in self.fighters:
                fighter.draw(self.screen)
            self.draw_pause_menu()
            self.handle_menu_input(keys, events)
            return

        if self.game_state == GameState.VICTORY:
            for fighter in self.fighters:
                fighter.draw(self.screen)
            self.draw_victory_screen()
            if keys[pygame.K_RETURN]:
                pygame.quit()
                sys.exit()
            return

        if self.game_state == GameState.OPTIONS:
            self.show_options_menu()
            self.handle_menu_input(keys, events)
            return

        remaining_time = self.draw_timer()
        if remaining_time <= 0:
            health_percent_1 = self.fighters[0].health / self.fighters[0].max_health
            health_percent_2 = self.fighters[1].health / self.fighters[1].max_health
            self.winner = 1 if health_percent_1 >= health_percent_2 else 2
            self.game_state = GameState.VICTORY
            if self.sounds_loaded:
                self.victory_sound.play()
            return

        for fighter in self.fighters:
            fighter.update_physics()
            fighter.recover_stamina()
            fighter.draw(self.screen)

        for i, fighter in enumerate(self.fighters):
            if i < len(self.controllers):
                self.handle_input(fighter, self.controllers[i], None, current_time)

            self.handle_input(fighter, None, keys, current_time)

        if self.fighters[0].hitbox.colliderect(self.fighters[1].hitbox):
            if self.fighters[0].attacking:
                self.fighters[1].take_damage(self.fighters[0].damage, time.time())
                if self.sounds_loaded:
                    self.hit_sound.play()
            elif self.fighters[1].attacking:
                self.fighters[0].take_damage(self.fighters[1].damage, time.time())
                if self.sounds_loaded:
                    self.hit_sound.play()

        for i, fighter in enumerate(self.fighters):
            if fighter.health <= 0:
                self.winner = 2 if i == 0 else 1
                self.game_state = GameState.VICTORY
                if self.sounds_loaded:
                    self.victory_sound.play()
                return

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        if self.game_state == GameState.COUNTDOWN:
            for i in range(3, 0, -1):
                self.draw_countdown(i)
            self.game_state = GameState.PLAYING
            self.game_start_time = time.time()

        while True:
            self.update()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        game = Game(sys.argv[1], sys.argv[2])
    else:
        game = Game()
    game.run()
