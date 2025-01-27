import pygame
import sys
import time
from math import sin
from dataclasses import dataclass
from typing import List, Dict, Tuple
from config.settings import GameSettings
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
from position_manager import PositionManager

# Chargement des paramètres
SETTINGS = GameSettings()

# Configuration de l'interface
SCREEN_WIDTH = SETTINGS.SCREEN_WIDTH
SCREEN_HEIGHT = SETTINGS.SCREEN_HEIGHT
FPS = SETTINGS.FPS
DEBUG_MODE = SETTINGS.DEBUG_MODE

# Couleurs
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = SETTINGS.TEXT_COLOR
HOVER_COLOR = (255, 255, 255, SETTINGS.HOVER_ALPHA)
CARD_SHADOW_COLOR = (0, 0, 0, 100)

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

class CharacterSelect:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.position_manager = PositionManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.set_caption("Pyth Fighter - Selection")

        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.animation_time = 0
        self.hovered_character = None

        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 48),
            'normal': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }

        self.position_manager.update_card_positions(FIGHTERS)

    def draw_character_card(self, name, data):
        card_rect = self.position_manager.card_positions[name]
        x, y = card_rect.x, card_rect.y + sin(self.animation_time * 3) * 5

        card_surface = pygame.Surface((SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), pygame.SRCALPHA)
        hover = card_rect.collidepoint(pygame.mouse.get_pos())
        base_color = data.color

        pygame.draw.rect(card_surface, CARD_SHADOW_COLOR, (4, 4, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), border_radius=20)
        alpha = 230 if hover else 200
        pygame.draw.rect(card_surface, (*base_color, alpha), (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), border_radius=20)

        if hover:
            self.hovered_character = name
            pygame.draw.rect(card_surface, HOVER_COLOR, (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), 4, border_radius=20)

        if name == self.selected['player1']:
            pygame.draw.rect(card_surface, SETTINGS.PLAYER1_COLOR, (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), 4, border_radius=20)
        elif name == self.selected['player2']:
            pygame.draw.rect(card_surface, SETTINGS.PLAYER2_COLOR, (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), 4, border_radius=20)

        y_content = 20
        text = self.fonts['subtitle'].render(name, True, TEXT_COLOR)
        card_surface.blit(text, (SETTINGS.CARD_WIDTH // 2 - text.get_width() // 2, y_content))
        y_content += 50

        style = self.fonts['normal'].render(f"Style: {data.style}", True, TEXT_COLOR)
        card_surface.blit(style, (SETTINGS.CARD_WIDTH // 2 - style.get_width() // 2, y_content))
        y_content += 40

        for stat_name, value in list(data.stats.items())[:3]:
            stat_text = self.fonts['small'].render(stat_name, True, TEXT_COLOR)
            card_surface.blit(stat_text, (20, y_content))

            bar_width = SETTINGS.CARD_WIDTH - 40
            pygame.draw.rect(card_surface, (50, 50, 50), (20, y_content + 20, bar_width, 10))
            pygame.draw.rect(card_surface, TEXT_COLOR, (20, y_content + 20, bar_width * (value / 10), 10))
            y_content += 40

        self.screen.blit(card_surface, (x, y))

    def draw_detail_panel(self):
        if not self.hovered_character:
            return

        char_data = FIGHTERS[self.hovered_character]
        panel_rect = self.position_manager.get_detail_panel_position()
        surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)

        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, panel_rect.width, panel_rect.height), border_radius=15)

        y = 20
        title = self.fonts['title'].render(self.hovered_character, True, TEXT_COLOR)
        surface.blit(title, (20, y))
        y += 60

        desc = self.fonts['normal'].render(char_data.description, True, TEXT_COLOR)
        surface.blit(desc, (20, y))
        y += 50

        for stat_name, value in char_data.stats.items():
            stat_text = self.fonts['normal'].render(f"{stat_name}: {value}", True, TEXT_COLOR)
            surface.blit(stat_text, (20, y))
            y += 40

        self.screen.blit(surface, panel_rect.topleft)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.animation_time += clock.get_time() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for char_name, char_rect in self.position_manager.card_positions.items():
                        if char_rect.collidepoint(event.pos):
                            self.selected[self.current_player] = char_name
                            self.current_player = "player2" if self.current_player == "player1" else "player1"
                            break

            self.screen.fill(BACKGROUND_COLOR)

            title_text = self.fonts['title'].render("Select a Character", True, TEXT_COLOR)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))

            for char_name in FIGHTERS:
                self.draw_character_card(char_name, FIGHTERS[char_name])

            self.draw_detail_panel()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CharacterSelect()
    game.run()
