import pygame
import sys
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from character import Character

class Game:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    ARENA_COLOR = (40, 40, 40)
    ARENA_BORDER_COLOR = (80, 80, 80)
    HEALTH_BAR_WIDTH = 300
    HEALTH_BAR_HEIGHT = 20
    ATTACK_COOLDOWN = 20

    def __init__(self, player1: Character, player2: Character):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pyth Fighter - Enhanced Arena")
        self.clock = pygame.time.Clock()
        self.player1 = player1
        self.player2 = player2
        self.running = True
        self.ui_manager = UIManager((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.font = pygame.font.Font(None, 30)
        self.attack_cooldown = 0

        self.start_button = UIButton(
            relative_rect=pygame.Rect((self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT // 2 - 25), (200, 50)),
            text='Start Fight',
            manager=self.ui_manager
        )

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
        self.handle_player_input(self.player2, keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_RETURN])

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

    def update_game_logic(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.handle_collision()
        self.player1.update()
        self.player2.update()

    def handle_collision(self):
        if pygame.sprite.collide_rect(self.player1, self.player2):
            self.player1.rect.x -= self.player1.velocity
            self.player2.rect.x += self.player2.velocity

    def draw(self):
        self.screen.fill(self.ARENA_COLOR)
        pygame.draw.rect(self.screen, self.ARENA_BORDER_COLOR, (100, 100, self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT - 200), 5)
        self.screen.blit(self.player1.image, self.player1.rect)
        self.screen.blit(self.player2.image, self.player2.rect)
        self.draw_health_bars()

    def draw_health_bars(self):
        self.draw_health_bar(50, 20, self.player1.health / self.player1.max_health)
        self.draw_health_bar(self.SCREEN_WIDTH - 350, 20, self.player2.health / self.player2.max_health)

    def draw_health_bar(self, x, y, health_percentage):
        pygame.draw.rect(self.screen, (255, 0, 0), (x, y, self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, self.HEALTH_BAR_WIDTH * health_percentage, self.HEALTH_BAR_HEIGHT))

    def start_combat(self):
        self.start_button.hide()
        # Additional combat initialization logic can be added here

    def quit_game(self):
        self.running = False
        pygame.quit()
        sys.exit()

# The start_game function should be outside the Game class
def start_game(player1: Character, player2: Character):
    game = Game(player1, player2)
    game.run()