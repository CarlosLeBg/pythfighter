import pygame
from math import sin, cos
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from config.settings import GameSettings
from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser

SETTINGS = GameSettings()

FIGHTERS = {
    'Mitsu': Mitsu(),
    'Tank': Tank(),
    'Noya': Noya(),
    'ThunderStrike': ThunderStrike(),
    'Bruiser': Bruiser()
}

@dataclass
class UIElement:
    rect: pygame.Rect
    animation_offset: float = 0.0
    hover_scale: float = 1.0
    selected: bool = False

class PositionManager:
    @property
    def card_positions(self) -> Dict[str, pygame.Rect]:
        """Return the current positions of all fighter cards."""
        return {name: self.get_card_position(name) for name in self.ui_elements}
    ANIMATION_SPEED = 0.05
    HOVER_SCALE = 1.1
    FLOAT_AMPLITUDE = 5
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # UI Constants
        self.CARD_MARGIN = int(screen_width * 0.04)  # Responsive margins
        self.TITLE_OFFSET = int(screen_height * 0.05)
        self.DETAIL_PANEL_MARGIN = int(screen_width * 0.02)
        self.SUBTITLE_OFFSET = int(screen_height * 0.07)
        
        # Initialize positions
        self._initialize_layout()
        
        # Store UI elements
        self.ui_elements: Dict[str, UIElement] = {}
        self._setup_ui_elements()

    def _initialize_layout(self):
        """Calculate initial layout positions"""
        total_cards = len(FIGHTERS)
        total_width = (SETTINGS.CARD_WIDTH * total_cards) + (self.CARD_MARGIN * (total_cards - 1))
        
        # Centered card positions
        self.start_x = (self.screen_width - total_width) // 2
        self.card_y = int(self.screen_height * 0.35)
        
        # Detail panel dimensions
        self.detail_panel_width = min(500, int(self.screen_width * 0.3))
        self.detail_panel_x = self.screen_width - self.detail_panel_width - self.DETAIL_PANEL_MARGIN
        
        # UI positions
        self.title_y = self.TITLE_OFFSET
        self.subtitle_y = self.title_y + self.SUBTITLE_OFFSET

    def _setup_ui_elements(self):
        """Initialize all UI elements with their positions"""
        # Setup fighter cards
        for i, fighter_name in enumerate(FIGHTERS.keys()):
            x = self.start_x + (SETTINGS.CARD_WIDTH + self.CARD_MARGIN) * i
            rect = pygame.Rect(x, self.card_y, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT)
            self.ui_elements[fighter_name] = UIElement(rect=rect)

    def update_animations(self, time_delta: float):
        """Update all animated elements"""
        for element in self.ui_elements.values():
            element.animation_offset += self.ANIMATION_SPEED * time_delta
            if element.selected:
                element.hover_scale = min(self.HOVER_SCALE, element.hover_scale + 0.05)
            else:
                element.hover_scale = max(1.0, element.hover_scale - 0.05)

    def get_card_position(self, fighter_name: str) -> pygame.Rect:
        """Get the current position of a fighter card including animations"""
        element = self.ui_elements[fighter_name]
        base_rect = element.rect.copy()
        
        # Apply floating animation
        base_rect.y += sin(element.animation_offset) * self.FLOAT_AMPLITUDE
        
        # Apply hover/selection scaling
        if element.hover_scale > 1.0:
            width_increase = int(base_rect.width * (element.hover_scale - 1))
            height_increase = int(base_rect.height * (element.hover_scale - 1))
            base_rect.inflate_ip(width_increase, height_increase)
            base_rect.y -= height_increase // 2  # Center the scaled card
            
        return base_rect

    def get_detail_panel_position(self) -> pygame.Rect:
        """Get the position of the detail panel"""
        height = int(self.screen_height * 0.6)
        y = (self.screen_height - height) // 2
        return pygame.Rect(self.detail_panel_x, y, self.detail_panel_width, height)

    def get_title_position(self) -> Tuple[int, int]:
        """Get the centered title position"""
        return (self.screen_width // 2, self.title_y)

    def get_subtitle_position(self) -> Tuple[int, int]:
        """Get the centered subtitle position"""
        return (self.screen_width // 2, self.subtitle_y)

    def get_player_prompt_position(self, player_number: int) -> Tuple[int, int]:
        """Get the position for player prompts"""
        y_offset = int(self.screen_height * 0.85)
        x_offset = int(self.screen_width * (0.25 if player_number == 1 else 0.75))
        return (x_offset, y_offset)

    def set_card_selected(self, fighter_name: str, selected: bool = True):
        """Set a card's selected state"""
        if fighter_name in self.ui_elements:
            self.ui_elements[fighter_name].selected = selected

    def is_card_hovered(self, fighter_name: str, mouse_pos: Tuple[int, int]) -> bool:
        """Check if a card is being hovered"""
        return self.get_card_position(fighter_name).collidepoint(mouse_pos)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT))
    position_manager = PositionManager(SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT)

    print(f"Card positions: {position_manager.ui_elements}")
    print(f"Detail panel position: {position_manager.get_detail_panel_position()}")
    pygame.quit()
