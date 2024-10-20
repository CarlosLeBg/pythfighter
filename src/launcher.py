import pygame
from game import Game
from character import Tank, Assassin, Sorcier, Mage, Archer

class Launcher:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter - Launcher")
        self.clock = pygame.time.Clock()
        self.running = True
        self.characters = [Tank(), Assassin(), Sorcier(), Mage(), Archer()]
        self.selected_character = None

    def run(self):
        while self.running:
            self.handle_events()
            self.draw_menu()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_1] and self.selected_character is None:
                self.selected_character = self.characters[0]
            elif keys[pygame.K_2] and self.selected_character is None:
                self.selected_character = self.characters[1]
            elif keys[pygame.K_3] and self.selected_character is None:
                self.selected_character = self.characters[2]
            elif keys[pygame.K_4] and self.selected_character is None:
                self.selected_character = self.characters[3]
            elif keys[pygame.K_5] and self.selected_character is None:
                self.selected_character = self.characters[4]
            elif keys[pygame.K_RETURN] and self.selected_character is not None:
                self.start_game()

    def draw_menu(self):
        self.screen.fill((50, 50, 50))
        title_font = pygame.font.SysFont("Arial", 40)
        title_surface = title_font.render("Pyth Fighter", True, (255, 255, 255))
        self.screen.blit(title_surface, (200, 50))

        options_font = pygame.font.SysFont("Arial", 30)
        options = ["1: Tank", "2: Assassin", "3: Sorcier", "4: Mage", "5: Archer"]
        for i, option in enumerate(options):
            option_surface = options_font.render(option, True, (255, 255, 255))
            self.screen.blit(option_surface, (200, 150 + i * 50))

        if self.selected_character:
            selected_surface = options_font.render(f"{self.selected_character.name} sélectionné", True, (255, 255, 0))
            self.screen.blit(selected_surface, (200, 400))

    def start_game(self):
        pygame.quit()
        game = Game(self.selected_character)
        game.run()
