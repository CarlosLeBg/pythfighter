import pygame
from game import Game
from character import Tank, Assassin, Sorcerer, Archer

class Launcher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter Launcher")

        self.selected_character = None
        self.menu_running = True

    def run(self):
        while self.menu_running:
            self.handle_events()
            self.render_menu()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.menu_running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_menu_click(event.pos)

    def handle_menu_click(self, mouse_position):
        x, y = mouse_position
        if 100 <= x <= 200 and 100 <= y <= 150:
            self.selected_character = Tank()
        elif 300 <= x <= 400 and 100 <= y <= 150:
            self.selected_character = Assassin()
        elif 100 <= x <= 200 and 200 <= y <= 250:
            self.selected_character = Sorcerer()
        elif 300 <= x <= 400 and 200 <= y <= 250:
            self.selected_character = Archer()

        if self.selected_character:
            self.start_game()

    def start_game(self):
        game = Game()
        game.player1 = self.selected_character
        game.run()

    def render_menu(self):
        self.screen.fill((50, 50, 50))  # Dark gray background
        font = pygame.font.Font(None, 36)
        
        tank_text = font.render("Tank", True, (0, 128, 255))
        assassin_text = font.render("Assassin", True, (255, 0, 0))
        sorcerer_text = font.render("Sorcerer", True, (128, 0, 128))
        archer_text = font.render("Archer", True, (0, 255, 0))

        self.screen.blit(tank_text, (100, 100))
        self.screen.blit(assassin_text, (300, 100))
        self.screen.blit(sorcerer_text, (100, 200))
        self.screen.blit(archer_text, (300, 200))
