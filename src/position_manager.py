import pygame
from config.settings import GameSettings

SETTINGS = GameSettings()

class PositionManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.card_positions = {}
        self.detail_panel_width = 400
        self.title_y = 50
        self.subtitle_y = 120
        
        self.calculate_layout()

    def calculate_layout(self):
        character_count = 5  # nombre de personnages
        total_card_width = character_count * SETTINGS.CARD_WIDTH
        total_spacing = (character_count - 1) * SETTINGS.CARD_SPACING
        total_width = total_card_width + total_spacing
        
        self.start_x = (self.screen_width - total_width) // 2
        self.card_y = self.screen_height // 2 - 150

        self.detail_panel_x = self.screen_width - self.detail_panel_width - 20

    def get_card_position(self, index):
        x = self.start_x + (SETTINGS.CARD_WIDTH + SETTINGS.CARD_SPACING) * index
        y = self.card_y
        return pygame.Rect(x, y, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT)

    def get_detail_panel_position(self):
        return pygame.Rect(self.detail_panel_x, 50, self.detail_panel_width, self.screen_height - 100)

    def get_title_position(self):
        return self.screen_width // 2, self.title_y

    def get_subtitle_position(self):
        return self.screen_width // 2, self.subtitle_y

    def update_card_positions(self, fighter_data):
        for index, char_name in enumerate(fighter_data.keys()):
            self.card_positions[char_name] = self.get_card_position(index)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT))
    position_manager = PositionManager(SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT)

    print(f"Card positions: {position_manager.card_positions}")
    print(f"Detail panel position: {position_manager.get_detail_panel_position()}")
    pygame.quit()
