import pygame
import sys
import time
from math import sin, cos
from dataclasses import dataclass
from typing import List, Dict, Tuple
from config.settings import GameSettings
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
from position_manager import PositionManager

SETTINGS = GameSettings()
SCREEN_WIDTH = SETTINGS.SCREEN_WIDTH
SCREEN_HEIGHT = SETTINGS.SCREEN_HEIGHT
FPS = SETTINGS.FPS

# Enhanced colors
BACKGROUND_COLOR = (15, 15, 25)
TEXT_COLOR = (230, 230, 230)
HOVER_COLOR = (255, 255, 255, 200)
CARD_SHADOW_COLOR = (0, 0, 0, 120)
GRADIENT_TOP = (40, 40, 60)
GRADIENT_BOTTOM = (15, 15, 25)

@dataclass
class Character:
    name: str
    description: str
    abilities: List[str]
    combo_tips: List[str]
    lore: str
    height: int
    weight: int
    color: Tuple[int, int, int]
    style: str
    difficulty: str
    stats: Dict[str, int]

FIGHTERS = {
    "AgileFighter": AgileFighter(),
    "Tank": Tank(),
    "BurstDamage": BurstDamage(),
    "ThunderStrike": ThunderStrike(),
    "Bruiser": Bruiser()
}

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def create_particle(self, pos, color):
        particle = {
            'pos': list(pos),
            'velocity': [((pygame.time.get_ticks() % 10) - 5) / 2, -3],
            'lifetime': 60,
            'color': (*color, 255),
            'size': 4
        }
        self.particles.append(particle)
        
    def update(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['lifetime'] -= 1
            particle['size'] *= 0.95
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, screen):
        for particle in self.particles:
            alpha = min(255, particle['lifetime'] * 4)
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(screen, color, 
                             (int(particle['pos'][0]), int(particle['pos'][1])), 
                             int(particle['size']))

class CharacterSelect:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.position_manager = PositionManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.set_caption("Pyth Fighter - Character Selection")
        
        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.animation_time = 0
        self.hovered_character = None
        self.particles = ParticleSystem()
        
        # Load and create fonts
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 48),
            'normal': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }
        
        self.position_manager.update_card_positions(FIGHTERS)
        
    def draw_gradient_background(self):
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            color = [
                GRADIENT_TOP[i] + (GRADIENT_BOTTOM[i] - GRADIENT_TOP[i]) * progress
                for i in range(3)
            ]
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
    def create_card_glow(self, surface, color, radius):
        glow = pygame.Surface((surface.get_width() + radius * 2, 
                             surface.get_height() + radius * 2), 
                            pygame.SRCALPHA)
        for i in range(radius, 0, -1):
            alpha = int(100 * (i / radius))
            pygame.draw.rect(glow, (*color, alpha),
                           (radius - i, radius - i,
                            surface.get_width() + i * 2,
                            surface.get_height() + i * 2),
                           border_radius=20)
        return glow

    def draw_character_card(self, name, data):
        card_rect = self.position_manager.card_positions[name]
        hover = card_rect.collidepoint(pygame.mouse.get_pos())
        
        # Card animation
        y_offset = sin(self.animation_time * 3) * 5
        x_offset = 0
        if hover:
            x_offset = sin(self.animation_time * 8) * 3
            self.hovered_character = name
            if pygame.time.get_ticks() % 10 == 0:
                self.particles.create_particle(
                    (card_rect.x + SETTINGS.CARD_WIDTH/2, 
                     card_rect.y + SETTINGS.CARD_HEIGHT),
                    data.color)
        
        # Create card surface
        card_surface = pygame.Surface((SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), 
                                    pygame.SRCALPHA)
        
        # Draw card shadow and background
        pygame.draw.rect(card_surface, CARD_SHADOW_COLOR,
                        (4, 4, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT),
                        border_radius=20)
        
        # Card base color with gradient
        for y in range(SETTINGS.CARD_HEIGHT):
            progress = y / SETTINGS.CARD_HEIGHT
            color = [
                max(0, min(255, data.color[i] * (1 - progress * 0.3)))
                for i in range(3)
            ]
            alpha = 230 if hover else 200
            pygame.draw.line(card_surface, (*color, alpha),
                           (0, y), (SETTINGS.CARD_WIDTH, y))
            
        # Card content
        y_content = 20
        
        # Character name
        text = self.fonts['subtitle'].render(name, True, TEXT_COLOR)
        card_surface.blit(text, 
                         (SETTINGS.CARD_WIDTH//2 - text.get_width()//2, y_content))
        y_content += 50
        
        # Fighting style
        style = self.fonts['normal'].render(f"Style: {data.style}", True, TEXT_COLOR)
        card_surface.blit(style, 
                         (SETTINGS.CARD_WIDTH//2 - style.get_width()//2, y_content))
        y_content += 40
        
        # Stats bars
        for stat_name, value in list(data.stats.items())[:3]:
            stat_text = self.fonts['small'].render(stat_name, True, TEXT_COLOR)
            card_surface.blit(stat_text, (20, y_content))
            
            bar_width = SETTINGS.CARD_WIDTH - 40
            # Background bar
            pygame.draw.rect(card_surface, (50, 50, 50),
                           (20, y_content + 20, bar_width, 10))
            # Value bar with gradient
            for x in range(int(bar_width * (value/10))):
                progress = x / bar_width
                color = [
                    max(0, min(255, data.color[i] * (1 + progress * 0.5)))
                    for i in range(3)
                ]
                pygame.draw.line(card_surface, color,
                               (20 + x, y_content + 20),
                               (20 + x, y_content + 29))
            y_content += 40
            
        # Selection indicators
        if name == self.selected['player1']:
            glow = self.create_card_glow(card_surface, SETTINGS.PLAYER1_COLOR, 10)
            self.screen.blit(glow, 
                           (card_rect.x + x_offset - 10,
                            card_rect.y + y_offset - 10))
        elif name == self.selected['player2']:
            glow = self.create_card_glow(card_surface, SETTINGS.PLAYER2_COLOR, 10)
            self.screen.blit(glow,
                           (card_rect.x + x_offset - 10,
                            card_rect.y + y_offset - 10))
            
        self.screen.blit(card_surface,
                        (card_rect.x + x_offset, card_rect.y + y_offset))

    def draw_detail_panel(self):
        if not self.hovered_character:
            return
            
        char_data = FIGHTERS[self.hovered_character]
        panel_rect = self.position_manager.get_detail_panel_position()
        surface = pygame.Surface((panel_rect.width, panel_rect.height),
                               pygame.SRCALPHA)
        
        # Panel background with gradient
        for y in range(panel_rect.height):
            progress = y / panel_rect.height
            color = [
                int(40 * (1 - progress)),
                int(40 * (1 - progress)),
                int(60 * (1 - progress))
            ]
            pygame.draw.line(surface, (*color, 180),
                           (0, y), (panel_rect.width, y))
        
        # Panel content
        y = 20
        title = self.fonts['title'].render(self.hovered_character, True, TEXT_COLOR)
        surface.blit(title, (20, y))
        y += 60
        
        # Description with word wrap
        words = char_data.description.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            test_surface = self.fonts['normal'].render(test_line, True, TEXT_COLOR)
            if test_surface.get_width() > panel_rect.width - 40:
                desc = self.fonts['normal'].render(line, True, TEXT_COLOR)
                surface.blit(desc, (20, y))
                y += 30
                line = word + " "
            else:
                line = test_line
        if line:
            desc = self.fonts['normal'].render(line, True, TEXT_COLOR)
            surface.blit(desc, (20, y))
        y += 50
        
        # Stats with animated bars
        for stat_name, value in char_data.stats.items():
            stat_text = self.fonts['normal'].render(f"{stat_name}:", True, TEXT_COLOR)
            surface.blit(stat_text, (20, y))
            
            bar_width = panel_rect.width - 180
            bar_progress = (1 + sin(self.animation_time * 2)) / 2
            current_width = bar_width * (value/10) * bar_progress
            
            pygame.draw.rect(surface, (50, 50, 50),
                           (140, y + 8, bar_width, 10))
            pygame.draw.rect(surface, char_data.color,
                           (140, y + 8, current_width, 10))
            
            value_text = self.fonts['normal'].render(str(value), True, TEXT_COLOR)
            surface.blit(value_text,
                        (150 + bar_width, y))
            y += 40
        
        self.screen.blit(surface, panel_rect.topleft)

    def draw_player_prompts(self):
        prompt_text = f"Player {self.current_player[-1]} Select"
        text = self.fonts['subtitle'].render(prompt_text, True, TEXT_COLOR)
        x = SCREEN_WIDTH // 2 - text.get_width() // 2
        y = 80
        
        # Add glow effect
        color = SETTINGS.PLAYER1_COLOR if self.current_player == "player1" else SETTINGS.PLAYER2_COLOR
        glow_surface = pygame.Surface((text.get_width() + 20,
                                     text.get_height() + 20),
                                    pygame.SRCALPHA)
        for i in range(10, 0, -1):
            alpha = int(25 * (i / 10))
            pygame.draw.rect(glow_surface, (*color, alpha),
                           (10 - i, 10 - i,
                            text.get_width() + i * 2,
                            text.get_height() + i * 2),
                           border_radius=5)
        
        self.screen.blit(glow_surface, (x - 10, y - 10))
        self.screen.blit(text, (x, y))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.animation_time = pygame.time.get_ticks() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for char_name, char_rect in self.position_manager.card_positions.items():
                        if char_rect.collidepoint(event.pos):
                            self.selected[self.current_player] = char_name
                            self.current_player = "player2" if self.current_player == "player1" else "player1"
                            break
                            
            # Draw everything
            self.draw_gradient_background()
            self.particles.update()
            self.particles.draw(self.screen)
            
            for char_name in FIGHTERS:
                self.draw_character_card(char_name, FIGHTERS[char_name])
                
            self.draw_detail_panel()
            self.draw_player_prompts()
            
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CharacterSelect()
    game.run()