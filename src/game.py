import pygame
from character import Tank, Assassin, Sorcier, Mage, Archer

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.characters = [Tank(), Assassin(), Sorcier(), Mage(), Archer()]
        self.selected_character = None
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 120
        self.combo_counter = 0

    def run(self):
        self.show_character_selection()
        self.game_loop()

    def show_character_selection(self):
        while self.selected_character is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.screen.fill((50, 50, 50))
            font = pygame.font.SysFont("Arial", 30)
            title_surface = font.render("Sélectionnez votre personnage", True, (255, 255, 255))
            self.screen.blit(title_surface, (200, 50))

            for i, character in enumerate(self.characters):
                character_surface = font.render(character.name, True, (255, 255, 255))
                self.screen.blit(character_surface, (200, 100 + i * 50))

                # Détection de sélection
                keys = pygame.key.get_pressed()
                if keys[pygame.K_1] and i == 0:
                    self.selected_character = character
                elif keys[pygame.K_2] and i == 1:
                    self.selected_character = character
                elif keys[pygame.K_3] and i == 2:
                    self.selected_character = character
                elif keys[pygame.K_4] and i == 3:
                    self.selected_character = character
                elif keys[pygame.K_5] and i == 4:
                    self.selected_character = character

            pygame.display.flip()

    def game_loop(self):
        while self.running:
            self.check_time()
            self.handle_events()
            self.screen.fill((0, 0, 0))
            self.draw_health_bar(self.selected_character)
            pygame.display.flip()
            self.clock.tick(60)

    def check_time(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        if elapsed_time > self.time_limit:
            self.end_game()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def draw_health_bar(self, character):
        health_percentage = character.health / character.max_health
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(self.screen, (255, 0, 0), (character.rect.x, character.rect.y - 20, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (character.rect.x, character.rect.y - 20, bar_width * health_percentage, bar_height))

    def end_game(self):
        print("Le temps est écoulé !")
        pygame.quit()
        sys.exit()
