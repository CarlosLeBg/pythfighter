import pygame
import sys
import os
import subprocess
import time
from math import sin, cos, radians
from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import GameSettings
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
from managers.position_manager import PositionManager

FIGHTERS = {
    "AgileFighter": AgileFighter(),
    "Tank": Tank(),
    "BurstDamage": BurstDamage(),
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

class EnhancedParticleSystem:
    def __init__(self):
        self.particles = []
        self.particle_types = {
            'sparkle': self._create_sparkle,
            'trail': self._create_trail,
            'explosion': self._create_explosion
        }

    def _create_sparkle(self, pos, color):
        angle = random.uniform(0, 360)
        speed = random.uniform(2, 4)
        return {
            'pos': list(pos),
            'velocity': [speed * cos(radians(angle)), speed * sin(radians(angle))],
            'lifetime': random.randint(40, 80),
            'color': (*color, 255),
            'size': random.uniform(2, 4),
            'type': 'sparkle'
        }

    def _create_trail(self, pos, color):
        return {
            'pos': list(pos),
            'velocity': [random.uniform(-0.5, 0.5), random.uniform(-1, -2)],
            'lifetime': random.randint(30, 50),
            'color': (*color, 255),
            'size': random.uniform(3, 6),
            'type': 'trail'
        }

    def _create_explosion(self, pos, color):
        angle = random.uniform(0, 360)
        speed = random.uniform(4, 8)
        return {
            'pos': list(pos),
            'velocity': [speed * cos(radians(angle)), speed * sin(radians(angle))],
            'lifetime': random.randint(20, 40),
            'color': (*color, 255),
            'size': random.uniform(4, 8),
            'type': 'explosion'
        }

    def create_particle(self, pos, color, particle_type='sparkle'):
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

        self.position_manager = PositionManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.animation_time = 0
        self.hovered_character = None
        self.particles = EnhancedParticleSystem()
        self.selection_done = False

        # Sound effects
        pygame.mixer.init()
        self.hover_sound = pygame.mixer.Sound("assets/sounds/hover.wav") if os.path.exists("assets/sounds/hover.wav") else None
        self.select_sound = pygame.mixer.Sound("assets/sounds/select.wav") if os.path.exists("assets/sounds/select.wav") else None

        # Load and create fonts with fallback
        try:
            font_path = "assets/fonts/your-fancy-font.ttf"
            self.fonts = {
                'title': pygame.font.Font(font_path if os.path.exists(font_path) else None, 72),
                'subtitle': pygame.font.Font(font_path if os.path.exists(font_path) else None, 48),
                'normal': pygame.font.Font(font_path if os.path.exists(font_path) else None, 36),
                'small': pygame.font.Font(font_path if os.path.exists(font_path) else None, 24)
            }
        except:
            self.fonts = {
                'title': pygame.font.Font(None, 72),
                'subtitle': pygame.font.Font(None, 48),
                'normal': pygame.font.Font(None, 36),
                'small': pygame.font.Font(None, 24)
            }

        # Transition effects
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
            # Add subtle wave effect
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
            # Add pulsing effect
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

        # Enhanced card animation
        y_offset = sin(self.animation_time * 3) * 5
        x_offset = 0
        if hover:
            x_offset = sin(self.animation_time * 8) * 3
            self.hovered_character = name
            # Enhanced particle effects
            if pygame.time.get_ticks() % 5 == 0:
                self.particles.create_particle(
                    (card_rect.x + SETTINGS.CARD_WIDTH/2,
                     card_rect.y + SETTINGS.CARD_HEIGHT),
                    data.color,
                    'trail')

                # Add sparkles around the card
                for _ in range(2):
                    edge_pos = (
                        card_rect.x + random.uniform(0, SETTINGS.CARD_WIDTH),
                        card_rect.y + random.uniform(0, SETTINGS.CARD_HEIGHT)
                    )
                    self.particles.create_particle(edge_pos, data.color, 'sparkle')

        # Create card surface with enhanced effects
        card_surface = pygame.Surface((SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT),
                                    pygame.SRCALPHA)

        # Enhanced card shadow and background
        shadow_offset = abs(sin(self.animation_time * 2)) * 4 + 4
        pygame.draw.rect(card_surface, CARD_SHADOW_COLOR,
                        (shadow_offset, shadow_offset,
                         SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT),
                        border_radius=20)

        # Enhanced card gradient with animation
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

        # Card content with enhanced animations
        self._draw_card_content(card_surface, data, hover)

        # Selection indicators with enhanced effects
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

        # Animated character name
        name_parts = data.name.split(" ")
        scale = 1 + sin(self.animation_time * 4) * 0.05 if hover else 1
        text = self.fonts['subtitle'].render(name_parts[0], True, TEXT_COLOR)
        scaled_text = pygame.transform.scale(text,
                                          (int(text.get_width() * scale),
                                           int(text.get_height() * scale)))
        surface.blit(scaled_text,
                    (SETTINGS.CARD_WIDTH//2 - scaled_text.get_width()//2, y_content))
        y_content += 50

        # Fighting style with hover effect
        style_color = (*TEXT_COLOR[:3], 255 if hover else 200)
        style = self.fonts['normal'].render(f"Style: {data.style}", True, style_color)
        surface.blit(style,
                    (SETTINGS.CARD_WIDTH//2 - style.get_width()//2, y_content))
        y_content += 40

        # Enhanced stats bars with animations
        for stat_name, value in list(data.stats.items())[:3]:
            stat_text = self.fonts['small'].render(stat_name, True, TEXT_COLOR)
            surface.blit(stat_text, (20, y_content))

            bar_width = SETTINGS.CARD_WIDTH - 40
            # Background bar with subtle animation
            bg_height = 10 + sin(self.animation_time * 3) * 2 if hover else 10
            pygame.draw.rect(surface, (50, 50, 50),
                           (20, y_content + 20, bar_width, bg_height))

            # Animated value bar with enhanced gradient
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

        # Enhanced panel background with animated gradient - Fixed color handling
        for y in range(panel_rect.height):
            progress = y / panel_rect.height
            wave = sin(self.animation_time * 2 + progress * 3) * 0.1
            # Ensure color values are integers and clamped between 0 and 255
            color = [
                max(0, min(255, int(40 * (1 - progress + wave)))),
                max(0, min(255, int(40 * (1 - progress + wave)))),
                max(0, min(255, int(60 * (1 - progress + wave)))),
                180  # Fixed alpha value
            ]
            pygame.draw.line(surface, color, (0, y), (panel_rect.width, y))

        # Panel content with enhanced animations
        y = 20
        title = self.fonts['title'].render(char_data.name.split(" ")[0], True, TEXT_COLOR)
        # Add title scale animation
        scale = 1 + sin(self.animation_time * 3) * 0.05
        scaled_title = pygame.transform.scale(title,
                                           (int(title.get_width() * scale),
                                            int(title.get_height() * scale)))
        surface.blit(scaled_title, (20, y))
        y += 60

        # Enhanced description with animated word wrap and highlight effects
        words = char_data.description.split()
        line = ""
        highlight_color = (*char_data.color, 150)
        for word in words:
            test_line = line + word + " "
            test_surface = self.fonts['normal'].render(test_line, True, TEXT_COLOR)
            if test_surface.get_width() > panel_rect.width - 40:
                desc = self.fonts['normal'].render(line, True, TEXT_COLOR)
                # Add subtle highlight effect
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
        # Enhanced player prompts with animations and effects
        for player_num, player_type in [("1", "player1"), ("2", "player2")]:
            is_current = self.current_player == player_type
            text_color = list(TEXT_COLOR)

            # Pulse effect for current player
            if is_current:
                pulse = abs(sin(self.animation_time * 4))
                text_color = [min(255, c + 50 * pulse) for c in text_color]

            player_text = self.fonts['normal'].render(
                f"Joueur {player_num}: {self.selected[player_type]}"
                if self.selected[player_type] else
                f"Joueur {player_num}: Sélectionner",
                True, text_color
            )

            # Position with bounce effect
            y_pos = SCREEN_HEIGHT - 80
            if is_current:
                y_pos += sin(self.animation_time * 5) * 5

            x_pos = 20 if player_num == "1" else SCREEN_WIDTH - player_text.get_width() - 20
            self.screen.blit(player_text, (x_pos, y_pos))

    def handle_character_selection(self, char_name):
        """Handle character selection with enhanced feedback"""
        if self.current_player == "player1" and self.selected['player1'] is None:
            self.selected['player1'] = char_name
            # Create selection effect
            pos = self.position_manager.card_positions[char_name].center
            self.particles.create_explosion(pos, SETTINGS.PLAYER1_COLOR)
            if self.select_sound:
                self.select_sound.play()
        elif self.current_player == "player2" and self.selected['player2'] is None:
            self.selected['player2'] = char_name
            # Create selection effect
            pos = self.position_manager.card_positions[char_name].center
            self.particles.create_explosion(pos, SETTINGS.PLAYER2_COLOR)
            if self.select_sound:
                self.select_sound.play()

        if self.selected['player1'] and self.selected['player2']:
            self.selection_done = True

        self.current_player = "player2" if self.current_player == "player1" else "player1"

    def handle_transition(self):
        """Handle screen transition effects"""
        if self.transition_alpha > 0:
            self.transition_surface.set_alpha(self.transition_alpha)
            self.screen.blit(self.transition_surface, (0, 0))
            self.transition_alpha = max(0, self.transition_alpha - self.fade_speed)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        last_hover = None
        self.joystick_cursor_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]

        while running:
            self.animation_time = pygame.time.get_ticks() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:  # X axis
                        self.joystick_cursor_pos[0] = max(0, min(SCREEN_WIDTH, self.joystick_cursor_pos[0] + int(event.value * 10)))
                    elif event.axis == 1:  # Y axis
                        self.joystick_cursor_pos[1] = max(0, min(SCREEN_HEIGHT, self.joystick_cursor_pos[1] + int(event.value * 10)))
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A button (Cross on PS)
                        for char_name, char_rect in self.position_manager.card_positions.items():
                            if char_rect.collidepoint(self.joystick_cursor_pos):
                                self.handle_character_selection(char_name)
                                break

            # Handle hover sound effects
            current_hover = None
            for char_name, char_rect in self.position_manager.card_positions.items():
                if char_rect.collidepoint(self.joystick_cursor_pos):
                    current_hover = char_name
                    break

            if current_hover != last_hover and self.hover_sound:
                self.hover_sound.play()
            last_hover = current_hover

            # Draw everything
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_gradient_background()
            self.particles.update()
            self.particles.draw(self.screen)

            self.hovered_character = None

            # Draw cards
            for fighter_name, fighter in FIGHTERS.items():
                self.draw_character_card(fighter_name, fighter)

            self.draw_detail_panel()
            self.draw_player_prompts()
            self.handle_transition()

            # Handle game launch with transition
            if self.selection_done:
                # Create final selection effect
                for char_name in [self.selected["player1"], self.selected["player2"]]:
                    pos = self.position_manager.card_positions[char_name].center
                    self.particles.create_explosion(pos, (255, 255, 255))

                pygame.display.flip()
                time.sleep(0.5)

                # Fade out
                alpha = 0
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                while alpha < 255:
                    self.screen.blit(fade_surface, (0, 0))
                    fade_surface.set_alpha(alpha)
                    pygame.display.flip()
                    alpha += 5
                    time.sleep(0.01)

                # Launch the game
                subprocess.run([sys.executable, "src/core/game.py",
                              self.selected["player1"], self.selected["player2"]])
                sys.exit()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = CharacterSelect()
    game.run()