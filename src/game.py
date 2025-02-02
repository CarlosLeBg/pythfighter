import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
import pygame.joystick
from dualsense_controller import DualSenseController

BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR
GRAVITY = 0.8
JUMP_FORCE = -15
GROUND_Y = VISIBLE_HEIGHT - 100

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
        pause_text = self.font.render("PAUSE", True, (220, 220, 240))
        text_rect = pause_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)

def draw_health_bars(screen, fighter1, fighter2):
    bar_width = 200
    bar_height = 20
    margin = 20
    
    # Player 1 Health Bar (Left)
    p1_health = (fighter1.health / 100) * bar_width
    p1_special = (fighter1.special_meter / fighter1.max_special) * bar_width
    pygame.draw.rect(screen, (255, 0, 0), (margin, margin, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (margin, margin, p1_health, bar_height))
    pygame.draw.rect(screen, (0, 0, 255), (margin, margin + bar_height + 5, p1_special, 10))
    
    # Player 2 Health Bar (Right)
    p2_health = (fighter2.health / 100) * bar_width
    p2_special = (fighter2.special_meter / fighter2.max_special) * bar_width
    pygame.draw.rect(screen, (255, 0, 0), (VISIBLE_WIDTH - margin - bar_width, margin, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (VISIBLE_WIDTH - margin - p2_health, margin, p2_health, bar_height))
    pygame.draw.rect(screen, (0, 0, 255), (VISIBLE_WIDTH - margin - p2_special, margin + bar_height + 5, p2_special, 10))

class Fighter:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.health = 100
        self.special_meter = 0
        self.max_special = 100
        self.attacking = False
        self.blocking = False
        self.special_active = False
        self.facing_right = True
        self.rect = pygame.Rect(x, y, width, height)
        self.hitbox = self.rect.inflate(-10, -10)

    def update(self):
        # Physics
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        self.x += self.velocity_x
        
        # Ground collision
        if self.y > GROUND_Y:
            self.y = GROUND_Y
            self.velocity_y = 0
            self.on_ground = True
        
        # Screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x > VISIBLE_WIDTH - self.width:
            self.x = VISIBLE_WIDTH - self.width
            
        # Update rectangles
        self.rect.x = self.x
        self.rect.y = self.y
        self.hitbox.center = self.rect.center

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.blocking:
            shield_width = 10
            shield_x = self.x - shield_width if not self.facing_right else self.x + self.width
            pygame.draw.rect(screen, (200, 200, 200), (shield_x, self.y, shield_width, self.height))
        
        if self.attacking:
            attack_width = 30
            attack_x = self.x + self.width if self.facing_right else self.x - attack_width
            pygame.draw.rect(screen, (255, 255, 0), (attack_x, self.y + self.height//4, attack_width, self.height//2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
    clock = pygame.time.Clock()
    menu = Menu(screen)
    
    try:
        bg_image = pygame.image.load("src/assets/backg.jpg")
        bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
    except:
        bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        bg_image.fill((40, 40, 60))

    fighter1 = Fighter(VISIBLE_WIDTH//4, GROUND_Y, 50, 100, (0, 200, 255))
    fighter2 = Fighter(3*VISIBLE_WIDTH//4, GROUND_Y, 50, 100, (255, 100, 100))
    fighters = [fighter1, fighter2]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu.state = GameState.PAUSED if menu.state == GameState.FIGHTING else GameState.FIGHTING

        keys = pygame.key.get_pressed()
        
        if menu.state == GameState.FIGHTING:
            # Player 1 Controls
            fighter1.velocity_x = (keys[pygame.K_d] - keys[pygame.K_a]) * 5
            if keys[pygame.K_w] and fighter1.on_ground:
                fighter1.velocity_y = JUMP_FORCE
                fighter1.on_ground = False
            fighter1.attacking = keys[pygame.K_f]
            fighter1.blocking = keys[pygame.K_g]
            if keys[pygame.K_t] and fighter1.special_meter >= fighter1.max_special:
                fighter1.special_active = True
                fighter1.special_meter = 0
                
            # Player 2 Controls
            fighter2.velocity_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
            if keys[pygame.K_UP] and fighter2.on_ground:
                fighter2.velocity_y = JUMP_FORCE
                fighter2.on_ground = False
            fighter2.attacking = keys[pygame.K_l]
            fighter2.blocking = keys[pygame.K_k]
            if keys[pygame.K_o] and fighter2.special_meter >= fighter2.max_special:
                fighter2.special_active = True
                fighter2.special_meter = 0

            # Update fighters
            for fighter in fighters:
                fighter.update()
                if fighter.velocity_x > 0:
                    fighter.facing_right = True
                elif fighter.velocity_x < 0:
                    fighter.facing_right = False

            # Combat logic
            for i, attacker in enumerate(fighters):
                defender = fighters[1-i]
                if attacker.attacking and attacker.hitbox.colliderect(defender.hitbox):
                    if not defender.blocking:
                        defender.health = max(0, defender.health - 10)
                        attacker.special_meter = min(attacker.max_special, attacker.special_meter + 20)
                    else:
                        defender.special_meter = min(defender.max_special, defender.special_meter + 10)
                
                if attacker.special_active and attacker.hitbox.colliderect(defender.hitbox):
                    if not defender.blocking:
                        defender.health = max(0, defender.health - 20)
                    else:
                        defender.health = max(0, defender.health - 10)
                    attacker.special_active = False

        # Drawing
        screen.blit(bg_image, (0, 0))
        for fighter in fighters:
            fighter.draw(screen)
        draw_health_bars(screen, fighter1, fighter2)
        
        if menu.state == GameState.PAUSED:
            menu.draw_pause()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()