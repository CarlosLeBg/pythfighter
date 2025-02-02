import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
import pygame.joystick
from dualsense_controller import DualSenseController

BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

COLORS = {
    'background': (40, 40, 60),
    'menu_bg': (30, 30, 50),
    'text_primary': (220, 220, 240),
    'text_secondary': (150, 150, 180),
    'button_normal': (60, 60, 100),
    'button_hover': (80, 80, 120)
}

class GameState:
    FIGHTING = 0
    PAUSED = 1

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.FIGHTING
        self.font = pygame.font.Font(None, 36)

    def draw_pause(self):
        s = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        pause_text = self.font.render("PAUSE", True, COLORS['text_primary'])
        text_rect = pause_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        pygame.display.set_caption("PythFighter")
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        
        self.fighter1 = AgileFighter()
        self.fighter2 = Tank()
        
        self.fighter1.x = VISIBLE_WIDTH // 4
        self.fighter1.y = VISIBLE_HEIGHT // 2
        self.fighter2.x = VISIBLE_WIDTH * 3 // 4
        self.fighter2.y = VISIBLE_HEIGHT // 2
        
        try:
            self.bg_image = pygame.image.load("src/assets/backg.jpg")
            self.bg_image = pygame.transform.scale(self.bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
        except:
            self.bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
            self.bg_image.fill(COLORS['background'])

    def update(self):
        # Combat logic
        for attacker, defender in [(self.fighter1, self.fighter2), (self.fighter2, self.fighter1)]:
            if attacker.attacking and attacker.hitbox.colliderect(defender.hitbox):
                if not defender.blocking:
                    defender.health -= attacker.damage
                    attacker.special_meter = min(attacker.max_special, 
                                               attacker.special_meter + attacker.damage * 2)
                else:
                    defender.special_meter = min(defender.max_special, 
                                               defender.special_meter + attacker.damage)
                attacker.attacking = False
            
            if attacker.special_active and attacker.hitbox.colliderect(defender.hitbox):
                if not defender.blocking:
                    defender.health -= attacker.damage * 2
                else:
                    defender.health -= attacker.damage
                attacker.special_active = False

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.fighter1.draw(self.screen)
        self.fighter2.draw(self.screen)
        if self.menu.state == GameState.PAUSED:
            self.menu.draw_pause()
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu.state = (GameState.FIGHTING 
                                     if self.menu.state == GameState.PAUSED 
                                     else GameState.PAUSED)
            
        keys = pygame.key.get_pressed()
        if self.menu.state == GameState.FIGHTING:
            # Fighter 1 controls (ZQSD)
            self.fighter1.handle_keyboard_input(
                {"left": keys[pygame.K_q],
                 "right": keys[pygame.K_d],
                 "up": keys[pygame.K_z],
                 "down": keys[pygame.K_s],
                 "attack": keys[pygame.K_v],
                 "block": keys[pygame.K_b],
                 "special": keys[pygame.K_n]},
                self.fighter2.x
            )
            
            # Fighter 2 controls (Arrows)
            self.fighter2.handle_keyboard_input(
                {"left": keys[pygame.K_LEFT],
                 "right": keys[pygame.K_RIGHT],
                 "up": keys[pygame.K_UP],
                 "down": keys[pygame.K_DOWN],
                 "attack": keys[pygame.K_KP1],
                 "block": keys[pygame.K_KP2],
                 "special": keys[pygame.K_KP3]},
                self.fighter1.x
            )
        return True

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            if self.menu.state == GameState.FIGHTING:
                self.update()
            self.draw()
            self.clock.tick(60)

def main():
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()