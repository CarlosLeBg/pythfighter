import subprocess
import pygame
import sys
import os
import pygame.gfxdraw
import random
from math import sin, cos, radians
from dataclasses import dataclass
from typing import List, Dict, Tuple

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

BACKGROUND_COLOR = (15, 15, 25)
TEXT_COLOR = (230, 230, 230)
HOVER_COLOR = (255, 255, 255, 200)
CARD_SHADOW_COLOR = (0, 0, 0, 120)
GRADIENT_TOP = (40, 40, 60)
GRADIENT_BOTTOM = (15, 15, 25)

class EnhancedParticleSystem:
    def __init__(self):
        self.particles = []
        self.max_particles = 500
        self.particle_types = {
            'sparkle': self._create_sparkle,
            'trail': self._create_trail,
            'explosion': self._create_explosion,
        }
        self.particle_surfaces = {size: self._create_particle_surface(size) for size in range(1, 20, 2)}

    def _create_particle_surface(self, size):
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(surf, size, size, size, (255, 255, 255, 255))
        return surf

    def _create_particle(self, pos, color, velocity, lifetime, size, particle_type):
        return {
            'pos': list(pos),
            'velocity': velocity,
            'lifetime': lifetime,
            'color': (*color, 255),
            'size': size,
            'type': particle_type
        }

    def _create_sparkle(self, pos, color):
        angle = random.uniform(0, 360)
        speed = random.uniform(2, 4)
        velocity = [speed * cos(radians(angle)), speed * sin(radians(angle))]
        return self._create_particle(pos, color, velocity, random.randint(40, 80), random.uniform(2, 4), 'sparkle')

    def _create_trail(self, pos, color):
        velocity = [random.uniform(-0.5, 0.5), random.uniform(-1, -2)]
        return self._create_particle(pos, color, velocity, random.randint(30, 50), random.uniform(3, 6), 'trail')

    def _create_explosion(self, pos, color):
        angle = random.uniform(0, 360)
        speed = random.uniform(4, 8)
        velocity = [speed * cos(radians(angle)), speed * sin(radians(angle))]
        return self._create_particle(pos, color, velocity, random.randint(20, 40), random.uniform(4, 8), 'explosion')

    def create_particle(self, pos, color, particle_type='sparkle'):
        if len(self.particles) < self.max_particles:
            particle = self.particle_types[particle_type](pos, color)
            self.particles.append(particle)

    def create_explosion(self, pos, color, num_particles=20):
        for _ in range(num_particles):
            self.create_particle(pos, color, 'explosion')

    def update(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['lifetime'] -= 1

            if particle['type'] == 'sparkle':
                particle['size'] *= 0.95
            elif particle['type'] == 'trail':
                particle['velocity'][1] += 0.1
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

        self.position_manager = PositionManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.animation_time = 0
        self.hovered_character = None
        self.particles = EnhancedParticleSystem()
        self.selection_done = False

        pygame.mixer.init()
        self.hover_sound = pygame.mixer.Sound("assets/sounds/hover.wav") if os.path.exists("assets/sounds/hover.wav") else None
        self.select_sound = pygame.mixer.Sound("assets/sounds/select.wav") if os.path.exists("assets/sounds/select.wav") else None

        font_path = "assets/fonts/your-fancy-font.ttf"
        self.fonts = {
            'title': pygame.font.Font(font_path if os.path.exists(font_path) else None, 72),
            'subtitle': pygame.font.Font(font_path if os.path.exists(font_path) else None, 48),
            'normal': pygame.font.Font(font_path if os.path.exists(font_path) else None, 36),
            'small': pygame.font.Font(font_path if os.path.exists(font_path) else None, 24)
        }

        self.transition_alpha = 255
        self.fade_speed = 5
        self.transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transition_surface.fill((0, 0, 0))

    def draw_gradient_background(self):
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            color = [
                GRADIENT_TOP[i] + (GRADIENT_BOTTOM[i] - GRADIENT_TOP[i]) * progress
                for i in range(3)
            ]
            wave_offset = sin(self.animation_time + y/100) * 20
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
        hover = card_rect.collidepoint(self.joystick_cursor_pos)

        y_offset = sin(self.animation_time * 3) * 5
        x_offset = 0
        if hover:
            x_offset = sin(self.animation_time * 8) * 3
            self.hovered_character = name
            if pygame.time.get_ticks() % 5 == 0:
                self.particles.create_particle(
                    (card_rect.x + SETTINGS.CARD_WIDTH/2,
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

        if name in [self.selected['player1'], self.selected['player2']]:
            glow_color = SETTINGS.PLAYER1_COLOR if name == self.selected['player1'] else SETTINGS.PLAYER2_COLOR
            glow = self.create_card_glow(card_surface, glow_color, 10)
            self.screen.blit(glow,
                           (card_rect.x + x_offset - 10,
                            card_rect.y + y_offset - 10))

        self.screen.blit(card_surface,
                        (card_rect.x + x_offset, card_rect.y + y_offset))

    def _draw_card_content(self, surface, data, hover):
        y_content = 20

        name_parts = data.name.split(" ")
        scale = 1 + sin(self.animation_time * 4) * 0.05 if hover else 1
        text = self.fonts['subtitle'].render(name_parts[0], True, TEXT_COLOR)
        scaled_text = pygame.transform.scale(text,
                                          (int(text.get_width() * scale),
                                           int(text.get_height() * scale)))
        surface.blit(scaled_text,
                    (SETTINGS.CARD_WIDTH//2 - scaled_text.get_width()//2, y_content))
        y_content += 50

        style_color = (*TEXT_COLOR[:3], 255 if hover else 200)
        style = self.fonts['normal'].render(f"Style: {data.style}", True, style_color)
        surface.blit(style,
                    (SETTINGS.CARD_WIDTH//2 - style.get_width()//2, y_content))
        y_content += 40

        for stat_name, value in list(data.stats.items())[:3]:
            stat_text = self.fonts['small'].render(stat_name, True, TEXT_COLOR)
            surface.blit(stat_text, (20, y_content))

            bar_width = SETTINGS.CARD_WIDTH - 40
            bg_height = 10 + sin(self.animation_time * 3) * 2 if hover else 10
            pygame.draw.rect(surface, (50, 50, 50),
                           (20, y_content + 20, bar_width, bg_height))

            value_width = int(bar_width * (value/10 if isinstance(value, (int, float)) else value/120))
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
        title = self.fonts['title'].render(char_data.name.split(" ")[0], True, TEXT_COLOR)
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
            test_surface = self.fonts['normal'].render(test_line, True, TEXT_COLOR)
            if test_surface.get_width() > panel_rect.width - 40:
                desc = self.fonts['normal'].render(line, True, TEXT_COLOR)
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
            desc = self.fonts['normal'].render(line, True, TEXT_COLOR)
            highlight = pygame.Surface((desc.get_width(), desc.get_height()),
                                    pygame.SRCALPHA)
            highlight.fill(highlight_color)
            highlight.set_alpha(int(abs(sin(self.animation_time * 2)) * 30))
            surface.blit(highlight, (20, y))
            surface.blit(desc, (20, y))

        self.screen.blit(surface, (panel_rect.x, panel_rect.y))

    def draw_player_prompts(self):
        for player_num, player_type in [("1", "player1"), ("2", "player2")]:
            is_current = self.current_player == player_type
            text_color = list(TEXT_COLOR)

            if is_current:
                pulse = abs(sin(self.animation_time * 4))
                text_color = [min(255, c + 50 * pulse) for c in text_color]

            player_text = self.fonts['normal'].render(
                f"Joueur {player_num}: {self.selected[player_type]}"
                if self.selected[player_type] else
                f"Joueur {player_num}: Sélectionner",
                True, text_color
            )

            y_pos = SCREEN_HEIGHT - 80
            if is_current:
                y_pos += sin(self.animation_time * 5) * 5

            x_pos = 20 if player_num == "1" else SCREEN_WIDTH - player_text.get_width() - 20
            self.screen.blit(player_text, (x_pos, y_pos))

    def handle_character_selection(self, char_name):
        if self.current_player == "player1" and self.selected['player1'] is None:
            self.selected['player1'] = char_name
            pos = self.position_manager.card_positions[char_name].center
            self.particles.create_explosion(pos, SETTINGS.PLAYER1_COLOR)
            if self.select_sound:
                self.select_sound.play()
        elif self.current_player == "player2" and self.selected['player2'] is None:
            self.selected['player2'] = char_name
            pos = self.position_manager.card_positions[char_name].center
            self.particles.create_explosion(pos, SETTINGS.PLAYER2_COLOR)
            if self.select_sound:
                self.select_sound.play()

        if self.selected['player1'] and self.selected['player2']:
            self.selection_done = True

        self.current_player = "player2" if self.current_player == "player1" else "player1"

    def handle_transition(self):
        if self.transition_alpha > 0:
            self.transition_surface.set_alpha(self.transition_alpha)
            self.screen.blit(self.transition_surface, (0, 0))
            self.transition_alpha = max(0, self.transition_alpha - self.fade_speed)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        joy_moved = False
        cursor_speed = 15

        if keys[pygame.K_LEFT]:
            self.joystick_cursor_pos[0] -= cursor_speed
        if keys[pygame.K_RIGHT]:
            self.joystick_cursor_pos[0] += cursor_speed
        if keys[pygame.K_UP]:
            self.joystick_cursor_pos[1] -= cursor_speed
        if keys[pygame.K_DOWN]:
            self.joystick_cursor_pos[1] += cursor_speed

        for joystick in self.joysticks:
            deadzone = 0.2
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)

            if abs(x_axis) > deadzone:
                self.joystick_cursor_pos[0] += int(x_axis * cursor_speed)
                joy_moved = True
            if abs(y_axis) > deadzone:
                self.joystick_cursor_pos[1] += int(y_axis * cursor_speed)
                joy_moved = True

            if joystick.get_numhats() > 0:
                hat = joystick.get_hat(0)
                if hat[0] != 0 or hat[1] != 0:
                    self.joystick_cursor_pos[0] += hat[0] * cursor_speed
                    self.joystick_cursor_pos[1] -= hat[1] * cursor_speed
                    joy_moved = True

        self.joystick_cursor_pos[0] = max(0, min(SCREEN_WIDTH, self.joystick_cursor_pos[0]))
        self.joystick_cursor_pos[1] = max(0, min(SCREEN_HEIGHT, self.joystick_cursor_pos[1]))

        if joy_moved and pygame.time.get_ticks() % 3 == 0:
            color = SETTINGS.PLAYER1_COLOR if self.current_player == "player1" else SETTINGS.PLAYER2_COLOR
            self.particles.create_particle(self.joystick_cursor_pos, color)

        return joy_moved

    def draw_cursor(self):
        player_color = SETTINGS.PLAYER1_COLOR if self.current_player == "player1" else SETTINGS.PLAYER2_COLOR
        time_pulse = abs(sin(self.animation_time * 8)) * 0.5 + 0.5
        size = 15 + int(time_pulse * 10)

        for i in range(3):
            scaled_size = size - (i * 4)
            if scaled_size <= 0:
                continue

            alpha = int(255 * (1 - i/3) * time_pulse)
            color = (*player_color, alpha)

            cursor_surface = pygame.Surface((scaled_size * 2, scaled_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(cursor_surface, color, (scaled_size, scaled_size), scaled_size, 2)

            self.screen.blit(cursor_surface,
                          (self.joystick_cursor_pos[0] - scaled_size,
                           self.joystick_cursor_pos[1] - scaled_size))

    def show_versus_screen(self):
        vs_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player1_data = FIGHTERS[self.selected["player1"]]
        player2_data = FIGHTERS[self.selected["player2"]]

        zoom_duration = 60
        for frame in range(zoom_duration):
            progress = frame / zoom_duration
            vs_surface.fill(BACKGROUND_COLOR)

            for _ in range(5):
                start_pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT//2))
                end_pos = (random.randint(0, SCREEN_WIDTH), random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT))
                pygame.draw.line(vs_surface, (255, 255, 255, 100), start_pos, end_pos, 2)

            vs_text = self.fonts['title'].render("VS", True, (255, 255, 255))
            vs_scale = 1 + sin(progress * 10) * 0.3
            vs_scaled = pygame.transform.scale(vs_text,
                                            (int(vs_text.get_width() * vs_scale),
                                             int(vs_text.get_height() * vs_scale)))
            vs_surface.blit(vs_scaled,
                          (SCREEN_WIDTH//2 - vs_scaled.get_width()//2,
                           SCREEN_HEIGHT//2 - vs_scaled.get_height()//2))

            p1_name = self.fonts['normal'].render(player1_data.name, True, SETTINGS.PLAYER1_COLOR)
            p2_name = self.fonts['normal'].render(player2_data.name, True, SETTINGS.PLAYER2_COLOR)
            vs_surface.blit(p1_name, (SCREEN_WIDTH//4 - p1_name.get_width()//2, SCREEN_HEIGHT//2 + 50))
            vs_surface.blit(p2_name, (3*SCREEN_WIDTH//4 - p2_name.get_width()//2, SCREEN_HEIGHT//2 + 50))

            if frame % 5 == 0:
                self.particles.create_explosion((SCREEN_WIDTH//2, SCREEN_HEIGHT//2), (255, 200, 50), 10)

            self.particles.update()
            self.particles.draw(vs_surface)

            self.screen.blit(vs_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(16)

        pygame.time.delay(1000)

    def play_character_intro(self, character_name):
        try:
            sound_file = f"assets/sounds/{character_name.lower()}_intro.wav"
            if os.path.exists(sound_file):
                intro_sound = pygame.mixer.Sound(sound_file)
                intro_sound.play()
        except:
            pass

    def run(self):
        clock = pygame.time.Clock()
        running = True
        last_hover = None
        self.joystick_cursor_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        selection_cooldown = 0

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
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        self.joystick_cursor_pos[0] = max(0, min(SCREEN_WIDTH, self.joystick_cursor_pos[0] + int(event.value * 10)))
                    elif event.axis == 1:
                        self.joystick_cursor_pos[1] = max(0, min(SCREEN_HEIGHT, self.joystick_cursor_pos[1] + int(event.value * 10)))
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        for char_name, char_rect in self.position_manager.card_positions.items():
                            if char_rect.collidepoint(self.joystick_cursor_pos):
                                self.handle_character_selection(char_name)
                                break

            current_hover = None
            for char_name, char_rect in self.position_manager.card_positions.items():
                if char_rect.collidepoint(self.joystick_cursor_pos):
                    current_hover = char_name
                    break

            if current_hover != last_hover and self.hover_sound:
                self.hover_sound.play()
            last_hover = current_hover

            if selection_cooldown > 0:
                selection_cooldown -= 1

            joy_moved = self.handle_input()

            self.screen.fill(BACKGROUND_COLOR)
            self.draw_gradient_background()
            self.particles.update()
            self.particles.draw(self.screen)

            self.hovered_character = None

            for fighter_name, fighter in FIGHTERS.items():
                self.draw_character_card(fighter_name, fighter)

            self.draw_detail_panel()
            self.draw_player_prompts()
            self.draw_cursor()
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

def preload_assets(base_path="assets"):
    assets = {
        "images": {},
        "sounds": {},
        "fonts": {}
    }

    paths = {
        "images": os.path.join(base_path, "images"),
        "sounds": os.path.join(base_path, "sounds"),
        "fonts": os.path.join(base_path, "fonts")
    }

    if os.path.exists(paths["images"]):
        for file in os.listdir(paths["images"]):
            if file.endswith(('.png', '.jpg', '.jpeg')):
                try:
                    key = os.path.splitext(file)[0]
                    assets["images"][key] = pygame.image.load(
                        os.path.join(paths["images"], file)).convert_alpha()
                except:
                    pass

    if os.path.exists(paths["sounds"]):
        sound_files = {
            "hover": "hover.wav",
            "select": "select.wav",
            "character_select": "character_select.mp3",
            "fight": "fight.wav",
            "versus": "versus.wav"
        }

        for key, file in sound_files.items():
            try:
                assets["sounds"][key] = pygame.mixer.Sound(
                    os.path.join(paths["sounds"], file))
            except:
                pass

    return assets

if __name__ == "__main__":
    game = CharacterSelect()
    game.run()
