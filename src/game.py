import pygame
from character import Tank, Assassin, Sorcier, Mage, Archer

class Game:
    def __init__(self, player1_character, player2_character):
        self.screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption("Pyth Fighter - Arena")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player1 = player1_character
        self.player2 = player2_character
        self.all_sprites = pygame.sprite.Group(self.player1, self.player2)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player1.move(0, -1)
        if keys[pygame.K_s]:
            self.player1.move(0, 1)
        if keys[pygame.K_a]:
            self.player1.move(-1, 0)
        if keys[pygame.K_d]:
            self.player1.move(1, 0)

        if keys[pygame.K_UP]:
            self.player2.move(0, -1)
        if keys[pygame.K_DOWN]:
            self.player2.move(0, 1)
        if keys[pygame.K_LEFT]:
            self.player2.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.player2.move(1, 0)

        # Collision detection
        if pygame.sprite.collide_rect(self.player1, self.player2):
            self.player1.attack_target(self.player2)
            self.player2.attack_target(self.player1)

    def draw(self):
        self.screen.fill((30, 30, 30))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(100, 50, 800, 500), 5)
        self.all_sprites.draw(self.screen)
        self.display_health_bars()
        pygame.display.flip()

    def display_health_bars(self):
        self.draw_health_bar(self.player1, (50, 550))
        self.draw_health_bar(self.player2, (700, 550))

    def draw_health_bar(self, character, position):
        health_percentage = character.health / character.max_health
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(self.screen, (255, 0, 0), (*position, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (*position, bar_width * health_percentage, bar_height))
