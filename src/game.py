import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

# Screen Configuration
BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7  # Reduced height
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

# Initialization
pygame.init()
screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
pygame.display.set_caption("PythFighter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Background
bg_image = pygame.image.load("src/assets/backg.jpg")
bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))

# Fighter Classes
fighter_classes = {
    "AgileFighter": AgileFighter,
    "Tank": Tank,
    "BurstDamage": BurstDamage,
    "ThunderStrike": ThunderStrike,
    "Bruiser": Bruiser
}

class Fighter:
    def __init__(self, player, x, y, data):
        self.player = player
        self.name = data.name
        self.color = data.color  # Restore original color
        
        self.speed = data.speed * 1.2
        self.damage = data.damage
        
        # Health Management
        self.max_health = data.stats["Vie"]
        self.health = self.max_health
        
        # Sizing
        fighter_width = VISIBLE_WIDTH // 16
        fighter_height = VISIBLE_HEIGHT // 4
        
        self.rect = pygame.Rect(x, y, fighter_width, fighter_height)
        self.hitbox = pygame.Rect(x + fighter_width//4, y + fighter_height//4, 
                                   fighter_width//2, fighter_height*3//4)
        
        # Street Fighter-style Movement
        self.vel_x = 0
        self.vel_y = 0
        self.direction = 1 if player == 1 else -1
        self.combo_meter = 0
        
        # Combat States
        self.on_ground = True
        self.attacking = False
        self.blocking = False
        self.attack_cooldown = 0

    def move(self, keys, opponent_x):
        GRAVITY = 0.8
        JUMP_FORCE = -12
        GROUND_Y = VISIBLE_HEIGHT * 0.9
        MAX_SPEED = self.speed * 2

        # Street Fighter-style movement
        if self.player == 1:
            if keys[pygame.K_a]:
                self.vel_x = -MAX_SPEED
                self.direction = -1
            elif keys[pygame.K_d]:
                self.vel_x = MAX_SPEED
                self.direction = 1
            else:
                self.vel_x = 0

            # Complex jump and attack mechanics
            if keys[pygame.K_w] and self.on_ground:
                self.vel_y = JUMP_FORCE
                self.on_ground = False
            
            self.blocking = keys[pygame.K_LSHIFT]
            
            if keys[pygame.K_r]:
                self.attack(opponent_x)

        else:
            if keys[pygame.K_LEFT]:
                self.vel_x = -MAX_SPEED
                self.direction = -1
            elif keys[pygame.K_RIGHT]:
                self.vel_x = MAX_SPEED
                self.direction = 1
            else:
                self.vel_x = 0

            if keys[pygame.K_UP] and self.on_ground:
                self.vel_y = JUMP_FORCE
                self.on_ground = False
            
            self.blocking = keys[pygame.K_RSHIFT]
            
            if keys[pygame.K_KP1]:
                self.attack(opponent_x)

        # Physics
        self.vel_y += GRAVITY
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        # Ground collision
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        # Screen boundaries
        self.rect.left = max(0, min(self.rect.left, VISIBLE_WIDTH - self.rect.width))
        self.hitbox.topleft = (self.rect.x + self.rect.width//4, self.rect.y + self.rect.height//4)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, surface):
        # Draw fighter with original color
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Advanced Health Bar
        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)

        # Position based on player
        if self.player == 1:
            bar_x = 20
        else:
            bar_x = VISIBLE_WIDTH - bar_width - 20

        # Background bar
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, 10, bar_width, bar_height), border_radius=10)
        
        # Health bar with color gradient
        health_color = (
            int(255 * (1 - health_percentage)), 
            int(255 * health_percentage), 
            0
        )
        pygame.draw.rect(surface, health_color, 
                         (bar_x, 10, bar_width * health_percentage, bar_height), 
                         border_radius=10)

        # Text rendering
        font = pygame.font.SysFont("Arial", 16)
        name_text = font.render(self.name, True, WHITE)
        health_text = font.render(f"{int(self.health)}/{self.max_health}", True, WHITE)

        if self.player == 1:
            surface.blit(name_text, (bar_x, 35))
            surface.blit(health_text, (bar_x + bar_width - 100, 35))
        else:
            surface.blit(name_text, (bar_x + bar_width - name_text.get_width(), 35))
            surface.blit(health_text, (bar_x, 35))

    def attack(self, opponent_x):
        if self.attack_cooldown == 0:
            # Street Fighter-style attack with direction consideration
            distance = abs(self.rect.centerx - opponent_x)
            if distance < self.rect.width * 2:
                self.attacking = True
                self.attack_cooldown = 15
                self.combo_meter += 1

    def take_damage(self, damage):
        # Blocking reduces damage
        actual_damage = damage * (0.5 if self.blocking else 1)
        self.health = max(0, self.health - actual_damage)

# Game Setup
selected_fighters = ["AgileFighter", "Tank"]
fighters = [
    Fighter(1, VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[0]]()),
    Fighter(2, VISIBLE_WIDTH*3//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[1]]())
]

# Game Loop
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    screen.blit(bg_image, (0, 0))

    keys = pygame.key.get_pressed()
    
    # Update fighters
    fighters[0].move(keys, fighters[1].rect.centerx)
    fighters[1].move(keys, fighters[0].rect.centerx)

    # Draw fighters
    for fighter in fighters:
        fighter.draw(screen)

    # Combat mechanics
    if fighters[0].attacking and fighters[0].hitbox.colliderect(fighters[1].hitbox):
        fighters[1].take_damage(fighters[0].damage)
        fighters[0].attacking = False

    if fighters[1].attacking and fighters[1].hitbox.colliderect(fighters[0].hitbox):
        fighters[0].take_damage(fighters[1].damage)
        fighters[1].attacking = False

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
sys.exit()