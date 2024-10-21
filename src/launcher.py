import pygame
from game import start_game
from character import Tank, Assassin, Sorcerer, Archer

class Launcher:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    BACKGROUND_COLOR = (50, 50, 50)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (100, 100, 100)
    BUTTON_HOVER_COLOR = (150, 150, 150)

    def __init__(self):
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pyth Fighter Launcher")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.menu_running = True
        self.buttons = self.create_buttons()

    def run(self):
        while self.menu_running:
            self.handle_events()
            self.render_menu()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_launcher()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_menu_click(event.pos)

    def handle_menu_click(self, mouse_position):
        for character, button in self.buttons.items():
            if button['rect'].collidepoint(mouse_position):
                self.start_game(character)

    def start_game(self, character_class):
        player1 = character_class()
        player2 = Tank()  # For simplicity, always use Tank as player 2
        start_game(player1, player2)

    def render_menu(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        for character, button in self.buttons.items():
            color = self.BUTTON_HOVER_COLOR if button['rect'].collidepoint(pygame.mouse.get_pos()) else self.BUTTON_COLOR
            pygame.draw.rect(self.screen, color, button['rect'])
            text = self.font.render(character.__name__, True, self.TEXT_COLOR)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)

    def create_buttons(self):
        button_width, button_height = 200, 50
        margin = 20
        characters = [Tank, Assassin, Sorcerer, Archer]
        buttons = {}

        for i, character in enumerate(characters):
            x = (i % 2) * (button_width + margin) + margin
            y = (i // 2) * (button_height + margin) + margin
            buttons[character] = {
                'rect': pygame.Rect(x, y, button_width, button_height)
            }

        return buttons

    def quit_launcher(self):
        self.menu_running = False