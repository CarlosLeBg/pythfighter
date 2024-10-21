import pygame
import random

class Game:
    def __init__(self, player1, player2):
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Pyth Fighter - Arena")
        self.clock = pygame.time.Clock()
        self.player1 = player1
        self.player2 = player2
        self.running = True
        self.font = pygame.font.SysFont("Arial", 30)
        self.arena_color = (40, 40, 40)
        self.attack_delay = 0  # pour contrôler la vitesse d'attaque

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game_logic()
            self.draw_arena()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()

        # Contrôles du joueur 1
        if keys[pygame.K_a]:
            self.player1.move(-1, 0)
        if keys[pygame.K_d]:
            self.player1.move(1, 0)
        if keys[pygame.K_w]:
            self.player1.move(0, -1)
        if keys[pygame.K_s]:
            self.player1.move(0, 1)
        if keys[pygame.K_SPACE] and self.attack_delay == 0:  # Attaque de base
            self.player1.attack(self.player2)
            self.attack_delay = 20  # Délai pour éviter l'abus d'attaques

        # Contrôles du joueur 2
        if keys[pygame.K_LEFT]:
            self.player2.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.player2.move(1, 0)
        if keys[pygame.K_UP]:
            self.player2.move(0, -1)
        if keys[pygame.K_DOWN]:
            self.player2.move(0, 1)
        if keys[pygame.K_RETURN] and self.attack_delay == 0:  # Attaque de base
            self.player2.attack(self.player1)
            self.attack_delay = 20  # Délai pour éviter l'abus d'attaques

    def update_game_logic(self):
        # Réduction progressive du délai d'attaque
        if self.attack_delay > 0:
            self.attack_delay -= 1

        # Vérification des collisions
        if pygame.sprite.collide_rect(self.player1, self.player2):
            self.handle_collision()

        # Mise à jour de l'état des personnages
        self.player1.update()
        self.player2.update()

    def handle_collision(self):
        """Réagit lorsque les personnages entrent en collision."""
        # Recul des personnages pour simuler un choc
        self.player1.rect.x -= 10 * self.player1.velocity
        self.player2.rect.x += 10 * self.player2.velocity

    def draw_arena(self):
        self.screen.fill(self.arena_color)
        pygame.draw.rect(self.screen, (80, 80, 80), (100, 100, 1080, 520), 5)  # Les bords de l'arène

        # Affichage des personnages
        self.screen.blit(self.player1.image, self.player1.rect)
        self.screen.blit(self.player2.image, self.player2.rect)

        # Affichage des barres de santé
        self.draw_health_bars()

    def draw_health_bars(self):
        # Barre de santé du joueur 1
        pygame.draw.rect(self.screen, (255, 0, 0), (50, 20, 300, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (50, 20, 300 * (self.player1.health / self.player1.max_health), 20))

        # Barre de santé du joueur 2
        pygame.draw.rect(self.screen, (255, 0, 0), (930, 20, 300, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (930, 20, 300 * (self.player2.health / self.player2.max_health), 20))
