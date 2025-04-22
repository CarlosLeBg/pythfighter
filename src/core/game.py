import pygame
import sys
import time
import os
from enum import Enum
import logging
import random
from threading import Thread
import math

# Configuration des logs
logging.basicConfig(filename='launcher.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser

# Constants
BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

GRAVITY = 0.4
GROUND_Y = VISIBLE_HEIGHT - VISIBLE_HEIGHT // 5.4
MAX_JUMP_HEIGHT = 60
BLOCK_STAMINA_DRAIN = 0.2
SPECIAL_ATTACK_MULTIPLIER = 2.5

class GameState(Enum):
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    PAUSED = "paused"
    VICTORY = "victory"
    OPTIONS = "options"

# Cache pour les images chargées
image_cache = {}

def load_image(path):
    if not os.path.exists(path):
        logging.error(f"Image file not found: {path}")
        return None
    if path not in image_cache:
        try:
            image = pygame.image.load(path).convert_alpha()
            image_cache[path] = image
            logging.info(f"Image loaded successfully: {path}")
        except Exception as e:
            logging.error(f"Error loading image {path}: {e}")
            return None
    return image_cache[path]

def update(self):
    current_time = time.time()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Toggle options menu instead of quitting
                if self.game_state == GameState.PLAYING:
                    self.game_state = GameState.OPTIONS
                elif self.game_state == GameState.OPTIONS:
                    self.game_state = GameState.PLAYING
            elif self.game_state == GameState.VICTORY and event.key == pygame.K_r:
                self.__init__()  # Réinitialiser le jeu
                self.game_state = GameState.COUNTDOWN
                return

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
        fighter.update_effects()

    if self.fighters[0].hitbox.colliderect(self.fighters[1].hitbox):
        if self.fighters[0].attacking and not self.fighters[1].stunned:
            if self.fighters[0].special_attack():
                opponent = self.fighters[1]
                side_length = min(opponent.rect.width, opponent.rect.height)
                opponent.hitbox = pygame.Rect(
                    opponent.rect.centerx - side_length // 2,
                    opponent.rect.centery - side_length // 2,
                    side_length,
                    side_length
                )
                opponent.take_damage(self.fighters[0].damage * SPECIAL_ATTACK_MULTIPLIER, time.time(), is_special=True)
            else:
                self.fighters[1].take_damage(self.fighters[0].damage, time.time())
            if self.sounds_loaded:
                self.hit_sound.play()

        if self.fighters[1].attacking and not self.fighters[0].stunned:
            if self.fighters[1].special_attack():
                self.fighters[0].take_damage(self.fighters[1].damage * SPECIAL_ATTACK_MULTIPLIER, time.time(), is_special=True)
            else:
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

def load_animation(path, action, frame_count, fighter_width, fighter_height):
    frames = []
    animation_folder = os.path.join(path, action)

    if not os.path.exists(animation_folder):
        logging.error(f"Animation folder not found - {animation_folder}")
        return frames

    frame_index = 0
    while True:
        frame_name = f"frame_{frame_index:02}_delay-0.1s.png"
        frame_path = os.path.join(animation_folder, frame_name)

        if not os.path.exists(frame_path):
            break

        img = load_image(frame_path)
        if img:
            # Supprimer les espaces vides autour de l'image
            img_rect = img.get_bounding_rect()
            cropped_img = img.subsurface(img_rect)

            # Redimensionner l'image à 600x800
            resized_img = pygame.transform.scale(cropped_img, (fighter_width, fighter_height))
            frames.append(resized_img)

        frame_index += 1

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

        # Ajuster les dimensions des personnages
        self.fighter_width = int(600 / 3.5)  # Largeur divisée par 3.5
        self.fighter_height = int(800 / 3.5)  # Hauteur divisée par 3.5

        self.ground_y = ground_y
        self.rect = pygame.Rect(x, y, self.fighter_width, self.fighter_height)

        # Créer une hitbox légèrement plus fine
        hitbox_width = int(self.fighter_width * 0.7)  # 70% de la largeur
        hitbox_height = int(self.fighter_height * 0.85)  # 85% de la hauteur
        hitbox_x = self.rect.centerx - hitbox_width // 2
        hitbox_y = self.rect.bottom - hitbox_height  # Alignée avec les pieds
        self.hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

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
        self.animation_speed = 0.3
        self.special_attack_cooldown = 0
        self.using_special_attack = False
        self.special_attack_frames = 0
        self.special_attack_effect = None
        self.special_attack_effect_duration = 60
        self.stunned = False  # Ajout de l'attribut stunned

        logging.info(f"Loading animations for {self.name}...")
        base_path = os.path.join("src", "assets", "characters", self.name.lower())
        self.animations = {}

        # Définir le nombre de frames pour chaque animation en fonction du personnage
        if self.name == "ThunderStrike":
            frame_counts = {
                "idle": 10,
                "walk": 8,
                "attack": 21,
                "dead": 16,
                "special_attack": 4
            }
        elif self.name == "Tank":
            frame_counts = {
                "idle": 6,
                "walk": 6,
                "attack": 5,
                "dead": 6,
                "special_attack": 5
            }
        elif self.name == "Mitsu":
            frame_counts = {
                "idle": 5,
                "walk": 6,
                "attack": 4,
                "dead": 5,
                "special_attack": 4
            }
        elif self.name == "Noya":
            frame_counts = {
                "idle": 5,
                "walk": 7,
                "attack": 6,
                "dead": 6,
                "special_attack": 5
            }
        elif self.name == "Bruiser":
            frame_counts = {
                "idle": 6,
                "walk": 6,
                "attack": 5,
                "dead": 6,
                "special_attack": 5
            }
        else:
            frame_counts = {
                "idle": 4,
                "walk": 4,
                "attack": 4,
                "dead": 4,
                "special_attack": 4
            }

        # Charger les animations en fonction du nombre de frames défini
        for action, frame_count in frame_counts.items():
            self.animations[action] = load_animation(base_path, action, frame_count, self.fighter_width, self.fighter_height)

        # Log des animations chargées
        for anim_name, frames in self.animations.items():
            logging.info(f"Animation '{anim_name}' pour {self.name}: {len(frames)} frames chargées.")

    def draw(self, surface):
        # Draw dynamic aura
        self.draw_aura(surface)

        if self.special_attack_effect and self.special_attack_effect_duration > 0:
            effect_alpha = min(255, self.special_attack_effect_duration * 4)
            self.special_attack_effect.set_alpha(effect_alpha)
            effect_x = self.rect.x - self.fighter_width // 2
            effect_y = self.rect.y - self.fighter_height // 4
            effect_rect = self.special_attack_effect.get_rect(center=self.hitbox.center)
            surface.blit(self.special_attack_effect, effect_rect)
            self.special_attack_effect_duration -= 1

        if self.animations and any(len(frames) > 0 for frames in self.animations.values()):
            current_anim = self.current_animation

            if current_anim not in self.animations or len(self.animations[current_anim]) == 0:
                if "idle" in self.animations and len(self.animations["idle"]) > 0:
                    current_anim = "idle"
                else:
                    if self.invincibility_frames % 4 < 2:
                        pygame.draw.rect(surface, self.color, self.rect)
                    pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
                    self.draw_health_stamina_bars(surface)
                    return

            frame_idx = int(self.animation_frame) % len(self.animations[current_anim])
            sprite = self.animations[current_anim][frame_idx]

            if self.direction == -1:
                sprite = pygame.transform.flip(sprite, True, False)

            surface.blit(sprite, (self.rect.x, self.rect.y))

            if current_anim == "special_attack":
                self.animation_frame = (self.animation_frame + 0.15) % len(self.animations[current_anim])
            elif current_anim == "attack":
                self.animation_frame = (self.animation_frame + 0.25) % len(self.animations[current_anim])
            else:
                self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.animations[current_anim])

            if self.invincibility_frames > 0:
                glow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                glow_color = (255, 255, 255, 100 if self.invincibility_frames % 4 < 2 else 50)
                glow_surface.fill(glow_color)
                surface.blit(glow_surface, self.rect)
        else:
            if self.invincibility_frames % 4 < 2:
                pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

        self.draw_health_stamina_bars(surface)

    def draw_aura(self, surface):
        aura_radius = int(max(self.rect.width, self.rect.height) * 0.7)
        aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        t = pygame.time.get_ticks() / 400.0
        for i in range(8, 0, -1):
            alpha = int(30 + 18 * i + 10 * abs(pygame.math.Vector2(1,0).rotate(t*40*i).x))
            color = (
                min(255, self.color[0] + 40),
                min(255, self.color[1] + 40),
                min(255, self.color[2] + 40),
                alpha
            )
            pygame.draw.circle(
                aura_surface,
                color,
                (aura_radius, aura_radius),
                int(aura_radius * (i / 8) * (1.05 + 0.07 * sin(t + i))),
                width=0
            )
        aura_pos = (self.rect.centerx - aura_radius, self.rect.centery - aura_radius)
        surface.blit(aura_surface, aura_pos, special_flags=pygame.BLEND_ADD)

    def draw_aura(self, surface):
        aura_radius = int(max(self.rect.width, self.rect.height) * 0.7)
        aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        t = pygame.time.get_ticks() / 400.0
        for i in range(8, 0, -1):
            alpha = int(30 + 18 * i + 10 * abs(pygame.math.Vector2(1,0).rotate(t*40*i).x))
            color = (
                min(255, self.color[0] + 40),
                min(255, self.color[1] + 40),
                min(255, self.color[2] + 40),
                alpha
            )
            pygame.draw.circle(
                aura_surface,
                color,
                (aura_radius, aura_radius),
                int(aura_radius * (i / 8) * (1.05 + 0.07 * math.sin(t + i))),
                width=0
            )
        aura_pos = (self.rect.centerx - aura_radius, self.rect.centery - aura_radius)
        surface.blit(aura_surface, aura_pos, special_flags=pygame.BLEND_ADD)

    def draw_health_stamina_bars(self, surface):
        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)
        health_color = (int(255 * (1 - health_percentage)), int(255 * health_percentage), 0)
        bar_x = 20 if self.player == 1 else VISIBLE_WIDTH - bar_width - 20

        for i in range(int(bar_width)):
            ratio = i / bar_width
            color = (100 - int(50 * ratio), 0, 0)
            pygame.draw.line(surface, color, (bar_x + i, 10), (bar_x + i, 10 + bar_height))

        if health_percentage > 0:
            # Glow effect under the health bar
            glow_surface = pygame.Surface((int(bar_width), bar_height*2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surface, (health_color[0], health_color[1], health_color[2], 80), (0, bar_height//2, int(bar_width), bar_height))
            surface.blit(glow_surface, (bar_x, 10 - bar_height//2), special_flags=pygame.BLEND_ADD)

            health_width = bar_width * health_percentage
            pygame.draw.rect(surface, health_color, (bar_x, 10, health_width, bar_height), border_radius=10)
            pygame.draw.rect(surface, (255, 255, 255), (bar_x, 10, health_width, bar_height), 1, border_radius=10)

            highlight_height = bar_height // 3
            highlight_surface = pygame.Surface((int(health_width), highlight_height), pygame.SRCALPHA)
            highlight_color = (255, 255, 255, 100)
            pygame.draw.rect(highlight_surface, highlight_color, (0, 0, int(health_width), highlight_height), border_radius=5)
            surface.blit(highlight_surface, (bar_x, 10))

        stamina_percentage = max(0, self.stamina / self.max_stamina)
        stamina_color = (255, 165 + int(90 * stamina_percentage), 0)

        for i in range(int(bar_width)):
            ratio = i / bar_width
            color = (0, 0, 100 - int(50 * ratio))
            pygame.draw.line(surface, color, (bar_x + i, 40), (bar_x + i, 40 + bar_height))

        if stamina_percentage > 0:
            stamina_width = bar_width * stamina_percentage
            pygame.draw.rect(surface, stamina_color, (bar_x, 40, stamina_width, bar_height), border_radius=10)
            pygame.draw.rect(surface, (255, 255, 255), (bar_x, 40, stamina_width, bar_height), 1, border_radius=10)

            highlight_height = bar_height // 3
            highlight_surface = pygame.Surface((int(stamina_width), highlight_height), pygame.SRCALPHA)
            highlight_color = (255, 255, 255, 100)
            pygame.draw.rect(highlight_surface, highlight_color, (0, 0, int(stamina_width), highlight_height), border_radius=5)
            surface.blit(highlight_surface, (bar_x, 40))

        name_font = pygame.font.Font(None, 24)
        name_color = (220, 220, 240)
        name_text = name_font.render(self.name, True, name_color)
        name_shadow = name_font.render(self.name, True, (0, 0, 0))
        health_text = name_font.render(f"{int(self.health)}/{self.max_health}", True, (150, 150, 180))
        health_shadow = name_font.render(f"{int(self.health)}/{self.max_health}", True, (0, 0, 0))

        combo_scale = 1.0 + (0.2 * min(self.combo_count, 5)) if self.combo_count > 1 else 1.0
        combo_font = pygame.font.Font(None, int(24 * combo_scale))
        combo_color = (255, 215, 0) if self.combo_count > 1 else (200, 200, 100)
        combo_text = combo_font.render(f"Combo: {self.combo_count}", True, combo_color)
        combo_shadow = combo_font.render(f"Combo: {self.combo_count}", True, (0, 0, 0))

        if self.player == 1:
            surface.blit(name_shadow, (bar_x + 2, 62))
            surface.blit(health_shadow, (bar_x + bar_width - 98, 62))
            surface.blit(combo_shadow, (bar_x + 2, 82))
            surface.blit(name_text, (bar_x, 60))
            surface.blit(health_text, (bar_x + bar_width - 100, 60))
            surface.blit(combo_text, (bar_x, 80))
        else:
            surface.blit(name_shadow, (bar_x + bar_width - name_text.get_width() + 2, 62))
            surface.blit(health_shadow, (bar_x + 2, 62))
            surface.blit(combo_shadow, (bar_x + bar_width - combo_text.get_width() + 2, 82))
            surface.blit(name_text, (bar_x + bar_width - name_text.get_width(), 60))
            surface.blit(health_text, (bar_x, 60))
            surface.blit(combo_text, (bar_x + bar_width - combo_text.get_width(), 80))

        if self.blocking and self.stamina > 0:
            block_font = pygame.font.Font(None, 20)
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            alpha = 128 + int(127 * pulse)
            block_color = (0, 255, 255, alpha)
            block_text = block_font.render("BLOCKING", True, block_color)
            block_shadow = block_font.render("BLOCKING", True, (0, 0, 0))
            block_x = bar_x if self.player == 1 else bar_x + bar_width - block_text.get_width()

            shield_radius = 20 + int(5 * pulse)
            shield_pos = (block_x + block_text.get_width() // 2, 100)
            pygame.draw.circle(surface, (0, 200, 255, 50), shield_pos, shield_radius, 2)

            surface.blit(block_shadow, (block_x + 1, 101))
            surface.blit(block_text, (block_x, 100))

        if self.special_attack_cooldown <= 0:
            special_font = pygame.font.Font(None, 20)
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            special_color = (255, 50 + int(205 * pulse), 50 + int(100 * pulse))
            special_text = special_font.render("SPECIAL READY", True, special_color)
            special_shadow = special_font.render("SPECIAL READY", True, (0, 0, 0))
            special_x = bar_x if self.player == 1 else bar_x + bar_width - special_text.get_width()

            glow_surface = pygame.Surface((special_text.get_width() + 10, special_text.get_height() + 10), pygame.SRCALPHA)
            glow_radius = 5 + int(3 * pulse)
            glow_color = (255, 100, 100, 50 + int(50 * pulse))
            pygame.draw.rect(glow_surface, glow_color, (0, 0, special_text.get_width() + 10, special_text.get_height() + 10),
                             border_radius=glow_radius)
            surface.blit(glow_surface, (special_x - 5, 115))

            surface.blit(special_shadow, (special_x + 1, 121))
            surface.blit(special_text, (special_x, 120))
        else:
            cooldown_font = pygame.font.Font(None, 18)
            cooldown_text = cooldown_font.render(f"SPECIAL: {self.special_attack_cooldown // 60 + 1}s", True, (200, 200, 200))
            cooldown_x = bar_x if self.player == 1 else bar_x + bar_width - cooldown_text.get_width()
            surface.blit(cooldown_text, (cooldown_x, 120))

    def take_damage(self, damage, current_time, is_special=False):
        if self.invincibility_frames <= 0:
            damage_multiplier = SPECIAL_ATTACK_MULTIPLIER if is_special else 1.0
            actual_damage = damage * damage_multiplier

            if self.blocking and self.stamina > 0:
                actual_damage *= 0.5
                self.stamina = max(0, self.stamina - 10)
                self.show_block_effect()

            self.health = max(0, self.health - actual_damage)
            self.invincibility_frames = 30

            if current_time - self.last_hit_time < 1.0:
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.last_hit_time = current_time

            knockback_direction = -1 if self.direction == 1 else 1
            knockback_force = 3 if is_special else 1
            if not self.blocking:
                self.vel_x += knockback_direction * knockback_force

            # Déclenche le tremblement d'écran lors d'un coup puissant ou d'un KO
            if is_special or self.health <= 0:
                if hasattr(self, 'game_ref'):
                    self.game_ref.shake_timer = 20
                    self.game_ref.shake_intensity = 12 if is_special else 8

            return True
        return False

    def show_block_effect(self):
        shield_size = self.fighter_width * 1.5
        shield_surface = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
        shield_color = (0, 200, 255, 150)
        pygame.draw.circle(shield_surface, shield_color, (shield_size // 2, shield_size // 2), shield_size // 2, 5)
        self.special_attack_effect = shield_surface
        self.special_attack_effect_duration = 20

    def attack(self, opponent_x):
        if self.can_attack and self.attack_cooldown == 0 and not self.blocking and self.stamina >= 10:
            distance = abs(self.rect.centerx - opponent_x)
            if distance < self.rect.width * 2:
                self.attacking = True
                self.can_attack = False
                self.attack_cooldown = 30
                self.animation_frame = 0
                self.current_animation = "attack"
                self.stamina -= 10
                return True
        return False

    def special_attack(self):
        """Effectue une attaque spéciale unique pour chaque personnage."""
        if self.special_attack_cooldown <= 0 and self.stamina >= 30 and not self.blocking:
            self.using_special_attack = True
            self.attacking = True
            self.can_attack = False
            self.current_animation = "special_attack"
            self.animation_frame = 0
            self.special_attack_cooldown = 240  # Cooldown de 4 secondes
            self.stamina -= 30

            # Effet visuel pour l'attaque spéciale
            effect_size = self.fighter_width * 3
            effect_surface = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)

            for i in range(10, 0, -1):
                alpha = 150 - i * 10
                size = effect_size - i * 10
                r, g, b = self.color
                pygame.draw.circle(effect_surface, (r, g, b, alpha), (effect_size // 2, effect_size // 2), size // 2)

            self.special_attack_effect = effect_surface
            self.special_attack_effect_duration = 60

            return True
        return False

    def apply_special_effect(self, opponent):
        """Applique l'effet spécial unique du personnage à l'adversaire."""
        if self.name == "Mitsu":
            # Mitsu : Réduit les dégâts subis pendant 3 secondes
            self.invincibility_frames = 180  # 3 secondes d'invincibilité
            logging.info(f"{self.name} active Esquive parfaite : invincibilité temporaire.")
        elif self.name == "Tank (Carl)":
            # Tank : Réduit les dégâts subis de moitié pendant 5 secondes
            self.invincibility_frames = 300  # 5 secondes d'invincibilité
            logging.info(f"{self.name} active Bouclier indestructible : réduction des dégâts.")
        elif self.name == "Noya":
            # Noya : Applique un effet de brûlure à l'adversaire
            opponent.apply_burn(3, 3)  # 3 dégâts par seconde pendant 3 secondes
            logging.info(f"{self.name} inflige Brûlure à {opponent.name}.")
        elif self.name == "ThunderStrike":
            # ThunderStrike : Chance d'étourdir l'adversaire
            if random.random() < 0.2:  # 20% de chance
                opponent.stun(90)  # Étourdit pendant 1.5 secondes
                logging.info(f"{self.name} étourdit {opponent.name} avec Thunderstorm.")
        elif self.name == "Bruiser":
            # Bruiser : Augmente temporairement les dégâts ou la vitesse
            self.boost_stat("damage", 1.15, 180)  # +15% de dégâts pendant 3 secondes
            logging.info(f"{self.name} active Boost : augmentation des dégâts.")

    def apply_burn(self, damage_per_second, duration):
        """Applique un effet de brûlure au personnage."""
        self.burn_damage = damage_per_second
        self.burn_duration = duration
        logging.info(f"{self.name} subit une brûlure : {damage_per_second} dégâts/s pendant {duration} secondes.")

    def stun(self, duration):
        """Étourdit le personnage pour une durée donnée."""
        self.stunned = True
        self.stun_duration = duration
        logging.info(f"{self.name} est étourdi pendant {duration / 60:.2f} secondes.")

    def boost_stat(self, stat, multiplier, duration):
        """Augmente temporairement une statistique."""
        if stat == "damage":
            self.damage *= multiplier
        elif stat == "speed":
            self.speed *= multiplier
        self.boost_duration = duration
        self.boost_stat_name = stat
        logging.info(f"{self.name} reçoit un boost de {stat} de {multiplier * 100 - 100:.0f}% pendant {duration / 60:.2f} secondes.")

    def update_effects(self):
        """Met à jour les effets spéciaux actifs."""
        # Gestion de la brûlure
        if hasattr(self, "burn_duration") and self.burn_duration > 0:
            self.health -= self.burn_damage / 60  # Applique les dégâts par seconde
            self.burn_duration -= 1
            if self.burn_duration <= 0:
                del self.burn_damage
                del self.burn_duration

        # Gestion de l'étourdissement
        if hasattr(self, "stun_duration") and self.stun_duration > 0:
            self.stun_duration -= 1
            if self.stun_duration <= 0:
                self.stunned = False
                del self.stun_duration

        # Gestion du boost
        if hasattr(self, "boost_duration") and self.boost_duration > 0:
            self.boost_duration -= 1
            if self.boost_duration <= 0:
                if self.boost_stat_name == "damage":
                    self.damage /= 1.15
                elif self.boost_stat_name == "speed":
                    self.speed /= 1.15
                del self.boost_duration
                del self.boost_stat_name

    def reset_attack(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

            if self.attack_cooldown == 1:
                self.attacking = False
                self.can_attack = True
                self.using_special_attack = False

                if self.current_animation in ["attack", "special_attack"]:
                    self.current_animation = "idle"
                    self.animation_frame = 0

        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1

    def block(self):
        if self.stamina > 0 and not self.attacking:
            self.blocking = True

            if "block" in self.animations and len(self.animations["block"]) > 0:
                self.current_animation = "block"

            self.stamina = max(0, self.stamina - BLOCK_STAMINA_DRAIN)
        else:
            self.blocking = False

    def stop_blocking(self):
        if self.blocking:
            self.blocking = False
            self.current_animation = "idle"
            self.animation_frame = 0

    def recover_stamina(self):
        recovery_rate = 0.15 if self.special_attack_cooldown <= 180 else 0.05

        if not self.blocking and self.stamina < self.max_stamina:
            self.stamina += recovery_rate
        self.stamina = min(self.stamina, self.max_stamina)

    def update_physics(self):
        if self.health <= 0:
            if "dead" in self.animations and len(self.animations["dead"]) > 0:
                self.current_animation = "dead"
            return  # Arrêter les mises à jour physiques si le personnage est mort

        if self.using_special_attack and "special_attack" in self.animations and len(self.animations["special_attack"]) > 0:
            self.current_animation = "special_attack"
        elif self.attacking and "attack" in self.animations and len(self.animations["attack"]) > 0:
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
        side = min(self.rect.width, self.rect.height)
        hitbox_x = self.rect.centerx - side // 2
        hitbox_y = self.rect.centery - side // 2
        self.hitbox.update(hitbox_x, hitbox_y, side, side)

        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1

        self.reset_attack()


class Game:
    def __init__(self, player1_type="Mitsu", player2_type="Tank"):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        pygame.display.set_caption("PythFighter")

        random.seed(time.time()*time.time())  # Ensure randomness by seeding with the current time
        self.bg_selected = random.choice(["bg_2.png", "backg.png", "bgtree.png", "bg-ile.png", "bgjoconde.png", " bgmatrix.png","jard.png"])

        try:
            bg_path = os.path.join("src", "assets", "backgrounds", self.bg_selected)
            self.bg_image = pygame.image.load(bg_path).convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
            logging.info(f"Background image loaded successfully: {bg_path}")
        except Exception as e:
            logging.error(f"Error loading background image: {e}")
            self.bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
            self.bg_image.fill((50, 50, 80))

        self.ground_y = VISIBLE_HEIGHT - 91 if self.bg_selected == "backg.png" else VISIBLE_HEIGHT - 98
        logging.info(f"Background selected: {self.bg_selected}, ground height: {self.ground_y}")

        fighter_map = {
            "Mitsu": Mitsu,
            "Tank": Tank,
            "Noya": Noya,
            "ThunderStrike": ThunderStrike,
            "Bruiser": Bruiser
        }
        fighter_height = VISIBLE_HEIGHT // 5  # Ajuster la hauteur initiale des personnages

        if player1_type not in fighter_map:
            logging.warning(f"Invalid fighter type: {player1_type}, defaulting to Mitsu")
            player1_type = "Mitsu"
        if player2_type not in fighter_map:
            logging.warning(f"Invalid fighter type: {player2_type}, defaulting to Tank")

        # Ensure the background image is properly scaled to fit the screen
        if self.bg_image.get_width() != VISIBLE_WIDTH or self.bg_image.get_height() != VISIBLE_HEIGHT:
            self.bg_image = pygame.transform.scale(self.bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
            logging.info("Background image resized to fit the screen dimensions.")

        # The fighters will now use their original image dimensions (800x800)

        self.fighters = [
            Fighter(1, VISIBLE_WIDTH // 4 - 75, self.ground_y - fighter_height,  # Position ajustée pour le joueur 1
                    fighter_map[player1_type](), self.ground_y),
            Fighter(2, VISIBLE_WIDTH * 3 // 4 - 75, self.ground_y - fighter_height,  # Position ajustée pour le joueur 2
                    fighter_map[player2_type](), self.ground_y)
        ]
        # Ajoute une référence au jeu pour chaque fighter
        for fighter in self.fighters:
            fighter.game_ref = self

        self.controllers = []
        for i in range(min(2, pygame.joystick.get_count())):
            try:
                joy = pygame.joystick.Joystick(i)
                joy.init()
                self.controllers.append(joy)
                logging.info(f"Controller {i} initialized with {joy.get_numaxes()} axes and {joy.get_numbuttons()} buttons.")
            except Exception as e:
                logging.error(f"Error initializing controller {i}: {e}")

        self.clock = pygame.time.Clock()
        self.game_state = GameState.COUNTDOWN
        self.start_time = time.time()
        self.game_start_time = None
        self.round_time = 99
        self.font = pygame.font.Font(None, 36)
        self.winner = None
        self.shake_timer = 0
        self.shake_intensity = 0

        self.menu_options = ["Resume", "Options", "Quit"]
        self.selected_option = 0

        try:
            pygame.mixer.init()
            self.hit_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "hit.wav"))
            self.victory_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "victory.wav"))
            self.menu_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "menu.wav"))
            self.sounds_loaded = True
            logging.info("Sounds loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load sound effects: {e}")
            self.sounds_loaded = False
            self.hit_sound = None
            self.victory_sound = None
            self.menu_sound = None

    def draw_timer(self):
        if self.game_start_time:
            remaining_time = max(0, int(self.round_time - (time.time() - self.game_start_time)))
            timer_text = self.font.render(str(remaining_time), True, (255, 255, 255))
            timer_rect = timer_text.get_rect(center=(VISIBLE_WIDTH // 2, 30))
            self.screen.blit(timer_text, timer_rect)
            return remaining_time
        return self.round_time

    def draw_pause_menu(self):
        pause_surface = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 180))
        self.screen.blit(pause_surface, (0, 0))

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("PAUSE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 + i * 50))
            self.screen.blit(option_text, option_rect)

            if i == self.selected_option:
                pygame.draw.rect(self.screen, (255, 255, 0), option_rect.inflate(20, 10), 2)

        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("↑/↓: Navigate   Enter: Select", True, (150, 150, 150))
        controls_rect = controls_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT * 3 // 4 + 50))
        self.screen.blit(controls_text, controls_rect)

        pygame.display.flip()

    def draw_victory_screen(self):
        victory_surface = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        victory_surface.fill((0, 0, 0, 180))
        self.screen.blit(victory_surface, (0, 0))

        title_font = pygame.font.Font(None, 72)
        winner_name = self.fighters[self.winner - 1].name
        title_text = title_font.render(f"PLAYER {self.winner} WINS!", True, (255, 215, 0))
        name_text = title_font.render(f"{winner_name}", True, self.fighters[self.winner - 1].color)

        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 4))
        name_rect = name_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 4 + 80))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(name_text, name_rect)

        # Ajouter une option "Rejouer"
        replay_font = pygame.font.Font(None, 36)
        replay_text = replay_font.render("Press R to Replay or ESC to Quit", True, (200, 200, 200))
        replay_rect = replay_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT * 3 // 4 + 50))
        self.screen.blit(replay_text, replay_rect)

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
                        logging.error(f"Error navigating D-pad: {e}")
            except Exception as e:
                logging.error(f"Error handling controller input: {e}")

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
                            logging.error(f"Error playing menu sound: {e}")
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    if self.sounds_loaded and self.menu_sound:
                        try:
                            self.menu_sound.play()
                        except Exception as e:
                            logging.error(f"Error playing menu sound: {e}")
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
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        options = ["Sound: ON" if self.sounds_loaded else "Sound: OFF", "Back to Game"]
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 + i * 50))
            self.screen.blit(option_text, option_rect)

            if i == 0:
                pygame.draw.rect(self.screen, (255, 255, 0), option_rect.inflate(20, 10), 2)

        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("↑/↓: Navigate   Enter: Select", True, (150, 150, 150))
        controls_rect = controls_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT * 3 // 4 + 50))
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
        text_rect = text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2))

        for i in range(20, 0, -5):
            glow = pygame.Surface((text.get_width() + i * 2, text.get_height() + i * 2), pygame.SRCALPHA)
            glow.fill((0, 0, 0, 0))
            pygame.draw.rect(glow, (255, 255, 0, 10), (0, 0, text.get_width() + i * 2, text.get_height() + i * 2), border_radius=10)
            self.screen.blit(glow, (text_rect.x - i, text_rect.y - i))

        self.screen.blit(text, text_rect)

        ready_font = pygame.font.Font(None, 72)
        ready_text = ready_font.render("GET READY!", True, (255, 255, 255))
        ready_rect = ready_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 - 150))
        self.screen.blit(ready_text, ready_rect)

        pygame.display.flip()
        pygame.time.wait(1000)

    def update(self):
        current_time = time.time()
        events = pygame.event.get()

        shake_offset = [0, 0]
        if self.shake_timer > 0:
            self.shake_timer -= 1
            shake_offset[0] = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_offset[1] = random.randint(-self.shake_intensity, self.shake_intensity)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif self.game_state == GameState.VICTORY and event.key == pygame.K_r:
                    self.__init__()  # Réinitialiser le jeu
                    self.game_state = GameState.COUNTDOWN
                    return

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_image, (shake_offset[0], shake_offset[1]))

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

            # Appliquer les effets spéciaux actifs
            fighter.update_effects()

        if self.fighters[0].hitbox.colliderect(self.fighters[1].hitbox):
            if self.fighters[0].attacking and not self.fighters[1].stunned:
                if self.fighters[0].special_attack():
                    # Adjust the opponent's hitbox to be a square before applying the special attack damage
                    opponent = self.fighters[1]
                    side_length = min(opponent.rect.width, opponent.rect.height)
                    opponent.hitbox = pygame.Rect(
                        opponent.rect.centerx - side_length // 2,
                        opponent.rect.centery - side_length // 2,
                        side_length,
                        side_length
                    )
                    opponent.take_damage(self.fighters[0].damage * SPECIAL_ATTACK_MULTIPLIER, time.time(), is_special=True)
                else:
                    self.fighters[1].take_damage(self.fighters[0].damage, time.time())
                if self.sounds_loaded:
                    self.hit_sound.play()

            if self.fighters[1].attacking and not self.fighters[0].stunned:
                if self.fighters[1].special_attack():
                    self.fighters[0].take_damage(self.fighters[1].damage * SPECIAL_ATTACK_MULTIPLIER, time.time(), is_special=True)
                else:
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
            # Do not scale fighter graphics so that background and hitbox sizes remain correct.
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