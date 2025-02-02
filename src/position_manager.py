import pygame
from math import sin
from config.settings import GameSettings
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

SETTINGS = GameSettings()

FIGHTERS = {
    'AgileFighter': AgileFighter(),
    'Tank': Tank(),
    'BurstDamage': BurstDamage(),
    'ThunderStrike': ThunderStrike(),
    'Bruiser': Bruiser()
}

class PositionManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Constantes de mise en page
        self.CARD_MARGIN = 50
        self.TITLE_OFFSET = 50
        self.DETAIL_PANEL_MARGIN = 20
        self.SUBTITLE_OFFSET = 70
        
        # Calcul des positions des cartes
        total_cards = 5  # Nombre de personnages
        total_width = (SETTINGS.CARD_WIDTH * total_cards) + (self.CARD_MARGIN * (total_cards - 1))
        
        # Position de départ centrée horizontalement
        self.start_x = (self.screen_width - total_width) // 2
        # Position verticale au tiers supérieur de l'écran
        self.card_y = (self.screen_height * 0.35)
        
        # Panneau de détails
        self.detail_panel_width = min(500, screen_width * 0.3)
        self.detail_panel_x = self.screen_width - self.detail_panel_width - self.DETAIL_PANEL_MARGIN
        
        # Positions UI
        self.title_y = self.TITLE_OFFSET
        self.subtitle_y = self.title_y + self.SUBTITLE_OFFSET
        
        # Création du dictionnaire des positions des cartes
        self.card_positions = {}
        for i, fighter_name in enumerate(FIGHTERS.keys()):
            x = self.start_x + (SETTINGS.CARD_WIDTH + self.CARD_MARGIN) * i
            self.card_positions[fighter_name] = pygame.Rect(x, self.card_y, 
                                                          SETTINGS.CARD_WIDTH, 
                                                          SETTINGS.CARD_HEIGHT)

    def get_card_position(self, index, animation_offset=0):
        x = self.start_x + (SETTINGS.CARD_WIDTH + self.CARD_MARGIN) * index
        y = self.card_y + sin(animation_offset) * 5  # Animation de flottement
        return pygame.Rect(x, y, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT)

    def get_detail_panel_position(self):
        height = self.screen_height * 0.6  # 60% de la hauteur de l'écran
        y = (self.screen_height - height) // 2  # Centré verticalement
        return pygame.Rect(self.detail_panel_x, y, 
                         self.detail_panel_width, height)

    def get_title_position(self):
        return (self.screen_width // 2, self.title_y)

    def get_subtitle_position(self):
        return (self.screen_width // 2, self.subtitle_y)

    def get_player_prompt_position(self, player_number):
        y_offset = self.screen_height * 0.85
        x_offset = self.screen_width * (0.25 if player_number == 1 else 0.75)
        return (x_offset, y_offset)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT))
    position_manager = PositionManager(SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT)

    print(f"Card positions: {position_manager.card_positions}")
    print(f"Detail panel position: {position_manager.get_detail_panel_position()}")
    pygame.quit()