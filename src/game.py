import pygame
import numpy as np
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from character import *

class Game:
    def __init__(self, player1, player2):
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Pyth Fighter - Enhanced Arena")
        self.clock = pygame.time.Clock()
        self.player1 = player1
        self.player2 = player2
        self.running = True
        self.ui_manager = UIManager((1280, 720))
        self.font = pygame.font.SysFont("Arial", 30)
        self.arena_color = (40, 40, 40)
        self.attack_delay = 0

        self.start_button = UIButton(relative_rect=pygame.Rect((540, 360), (200, 50)),
                                     text='Start Fight',
                                     manager=self.ui_manager)

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game_logic()
            self.draw_arena()
            self.ui_manager.update(self.clock.tick(60) / 1000.0)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.USEREVENT:
                if event.user_type == 'ui_button_pressed':
                    if event.ui_element == self.start_button:
                        self.start_combat()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.player1.move(-1, 0)
        if keys[pygame.K_d]:
            self.player1.move(1, 0)
        if keys[pygame.K_w]:
            self.player1.move(0, -1)
        if keys[pygame.K_s]:
            self.player1.move(0, 1)
        if keys[pygame.K_SPACE] and self.attack_delay == 0:
            self.player1.perform_attack(self.player2)
            self.attack_delay = 20

        if keys[pygame.K_LEFT]:
            self.player2.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.player2.move(1, 0)
        if keys[pygame.K_UP]:
            self.player2.move(0, -1)
        if keys[pygame.K_DOWN]:
            self.player2.move(0, 1)
        if keys[pygame.K_RETURN] and self.attack_delay == 0:
            self.player2.perform_attack(self.player1)
            self.attack_delay = 20

    def update_game_logic(self):
        if self.attack_delay > 0:
            self.attack_delay -= 1
        if pygame.sprite.collide_rect(self.player1, self.player2):
            self.handle_collision()
        self.player1.update()
        self.player2.update()

    def handle_collision(self):
        self.player1.rect.x -= 10 * self.player1.velocity
        self.player2.rect.x += 10 * self.player2.velocity

    def draw_arena(self):
        self.screen.fill(self.arena_color)
        pygame.draw.rect(self.screen, (80, 80, 80), (100, 100, 1080, 520), 5)
        self.screen.blit(self.player1.image, self.player1.rect)
        self.screen.blit(self.player2.image, self.player2.rect)
        self.draw_health_bars()

    def draw_health_bars(self):
        pygame.draw.rect(self.screen, (255, 0, 0), (50, 20, 300, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (50, 20, 300 * (self.player1.health / self.player1.max_health), 20))
        pygame.draw.rect(self.screen, (255, 0, 0), (930, 20, 300, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (930, 20, 300 * (self.player2.health / self.player2.max_health), 20))

    def start_game(self):
        player1 = Archer()  # or your other character class
        player2 = Tank()    # or another character class
        game = Game(player1, player2)
        game.run()
