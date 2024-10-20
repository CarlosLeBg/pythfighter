import pygame

class Launcher:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter - Launcher")
        self.clock = pygame.time.Clock()
        self.running = True

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

    def draw_menu(self):
        self.screen.fill((50, 50, 50))
        title_font = pygame.font.SysFont("Arial", 40)
        title_surface = title_font.render("Pyth Fighter", True, (255, 255, 255))
        self.screen.blit(title_surface, (200, 50))

        options_font = pygame.font.SysFont("Arial", 30)
        options = ["Jouer", "Options", "Quitter"]
        for i, option in enumerate(options):
            option_surface = options_font.render(option, True, (255, 255, 255))
            self.screen.blit(option_surface, (200, 150 + i * 50))
