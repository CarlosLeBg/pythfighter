import pygame
import sys
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from character import Character
import random

class Game:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    ARENA_COLOR = (40, 40, 40)
    ARENA_BORDER_COLOR = (80, 80, 80)
    HEALTH_BAR_WIDTH = 300
    HEALTH_BAR_HEIGHT = 20
    ATTACK_COOLDOWN = 20

    def __init__(self, player1: Character, player2: Character, ai_controlled=False):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pyth Fighter - Enhanced Arena")
        self.clock = pygame.time.Clock()
        self.player1 = player1
        self.player2 = player2
        self.ai_controlled = ai_controlled
        self.running = True
        self.ui_manager = UIManager((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.font = pygame.font.Font(None, 30)
        self.attack_cooldown = 0

        self.start_button = UIButton(
            relative_rect=pygame.Rect((self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT // 2 - 25), (200, 50)),
            text='Start Fight',
            manager=self.ui_manager
        )

        # Load background image
        self.background = pygame.image.load("assets/background.png").convert()
        self.background = pygame.transform.scale(self.background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Load character sprites
        self.player1.load_sprite("assets/player1_sprite.png")
        self.player2.load_sprite("assets/player2_sprite.png")

        # Particle system
        self.particles = []

    def run(self):
        while self.running:
            time_delta = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update_game_logic()
            self.draw()
            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.USEREVENT:
                if event.user_type == 'ui_button_pressed' and event.ui_element == self.start_button:
                    self.start_combat()
            self.ui_manager.process_events(event)

        keys = pygame.key.get_pressed()
        self.handle_player_input(self.player1, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_SPACE])
        
        if not self.ai_controlled:
            self.handle_player_input(self.player2, keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_RETURN])
        else:
            self.handle_ai_input(self.player2)

    def handle_player_input(self, player, left, right, up, down, attack):
        if left:
            player.move(-1, 0)
        if right:
            player.move(1, 0)
        if up:
            player.move(0, -1)
        if down:
            player.move(0, 1)
        if attack and self.attack_cooldown == 0:
            player.perform_attack(self.player2 if player == self.player1 else self.player1)
            self.attack_cooldown = self.ATTACK_COOLDOWN
            self.create_attack_particles(player)

    def handle_ai_input(self, ai_player):
        target = self.player1
        dx = target.rect.x - ai_player.rect.x
        dy = target.rect.y - ai_player.rect.y

        # Simple AI movement
        if abs(dx) > abs(dy):
            ai_player.move(1 if dx > 0 else -1, 0)
        else:
            ai_player.move(0, 1 if dy > 0 else -1)

        # AI attack logic
        if self.attack_cooldown == 0 and random.random() < 0.05:  # 5% chance to attack each frame when possible
            ai_player.perform_attack(target)
            self.attack_cooldown = self.ATTACK_COOLDOWN
            self.create_attack_particles(ai_player)

    def update_game_logic(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.handle_collision()
        self.player1.update()
        self.player2.update()
        self.update_particles()

    def handle_collision(self):
        if pygame.sprite.collide_rect(self.player1, self.player2):
            self.player1.rect.x -= self.player1.velocity
            self.player2.rect.x += self.player2.velocity

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player1.image, self.player1.rect)
        self.screen.blit(self.player2.image, self.player2.rect)
        self.draw_health_bars()
        self.draw_particles()

    def draw_health_bars(self):
        self.draw_health_bar(50, 20, self.player1.health / self.player1.max_health)
        self.draw_health_bar(self.SCREEN_WIDTH - 350, 20, self.player2.health / self.player2.max_health)

    def draw_health_bar(self, x, y, health_percentage):
        pygame.draw.rect(self.screen, (255, 0, 0), (x, y, self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, self.HEALTH_BAR_WIDTH * health_percentage, self.HEALTH_BAR_HEIGHT))

    def create_attack_particles(self, attacker):
        for _ in range(20):
            particle = {
                'pos': [attacker.rect.centerx, attacker.rect.centery],
                'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
                'timer': 30
            }
            self.particles.append(particle)

    def update_particles(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['timer'] -= 1
            if particle['timer'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self):
        for particle in self.particles:
            pygame.draw.circle(self.screen, (255, 255, 0), [int(particle['pos'][0]), int(particle['pos'][1])], 2)

    def start_combat(self):
        self.start_button.hide()

    def quit_game(self):
        self.running = False
        pygame.quit()
        sys.exit()

def start_game(player1: Character, player2: Character, ai_controlled=False):
    game = Game(player1, player2, ai_controlled)
    game.run()