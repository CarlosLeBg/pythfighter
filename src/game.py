import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

# Screen Configuration
BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

# Color Palette
COLORS = {
    'background': (40, 40, 60),
    'menu_bg': (30, 30, 50),
    'text_primary': (220, 220, 240),
    'text_secondary': (150, 150, 180),
    'button_normal': (60, 60, 100),
    'button_hover': (80, 80, 120)
}

# Initialization
pygame.init()
screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
pygame.display.set_caption("PythFighter")

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

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.hover = False

    def draw(self, surface):
        color = COLORS['button_hover'] if self.hover else COLORS['button_normal']
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_surface = self.font.render(self.text, True, COLORS['text_primary'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class SettingsMenu:
    def __init__(self):
        self.buttons = [
            Button(VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2 - 100, 
                   VISIBLE_WIDTH//2, 50, "Sound"),
            Button(VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2, 
                   VISIBLE_WIDTH//2, 50, "Controls"),
            Button(VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2 + 100, 
                   VISIBLE_WIDTH//2, 50, "Back")
        ]
        self.title_font = pygame.font.Font(None, 48)

    def draw(self, surface):
        surface.fill(COLORS['menu_bg'])
        
        title = self.title_font.render("Settings", True, COLORS['text_primary'])
        title_rect = title.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)

    def handle_events(self, mouse_pos):
        for button in self.buttons:
            button.hover = button.rect.collidepoint(mouse_pos)

class Fighter:
    def __init__(self, player, x, y, data):
        self.player = player
        self.name = data.name
        self.color = data.color
        
        self.speed = data.speed * 1.2
        self.damage = data.damage
        
        self.max_health = data.stats["Vie"]
        self.health = self.max_health
        
        fighter_width = VISIBLE_WIDTH // 16
        fighter_height = VISIBLE_HEIGHT // 4
        
        self.rect = pygame.Rect(x, y, fighter_width, fighter_height)
        self.hitbox = pygame.Rect(x + fighter_width//4, y + fighter_height//4, 
                                   fighter_width//2, fighter_height*3//4)
        
        self.vel_x = 0
        self.vel_y = 0
        self.direction = 1 if player == 1 else -1
        
        self.on_ground = True
        self.attacking = False
        self.blocking = False
        self.attack_cooldown = 0

    def move(self, keys, opponent_x):
        GRAVITY = 0.8
        JUMP_FORCE = -12
        GROUND_Y = VISIBLE_HEIGHT * 0.9
        MAX_SPEED = self.speed * 2

        if self.player == 1:
            if keys[pygame.K_a]:
                self.vel_x = -MAX_SPEED
                self.direction = -1
            elif keys[pygame.K_d]:
                self.vel_x = MAX_SPEED
                self.direction = 1
            else:
                self.vel_x = 0

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

        self.vel_y += GRAVITY
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        self.rect.left = max(0, min(self.rect.left, VISIBLE_WIDTH - self.rect.width))
        self.hitbox.topleft = (self.rect.x + self.rect.width//4, self.rect.y + self.rect.height//4)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)

        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)

        health_color = (
            int(255 * (1 - health_percentage)), 
            int(255 * health_percentage), 
            0
        )

        if self.player == 1:
            bar_x = 20
        else:
            bar_x = VISIBLE_WIDTH - bar_width - 20

        pygame.draw.rect(surface, (100, 0, 0), 
                         (bar_x, 10, bar_width, bar_height), 
                         border_radius=10)
        pygame.draw.rect(surface, health_color, 
                         (bar_x, 10, bar_width * health_percentage, bar_height), 
                         border_radius=10)

        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.name, True, COLORS['text_primary'])
        health_text = name_font.render(f"{int(self.health)}/{self.max_health}", True, COLORS['text_secondary'])

        if self.player == 1:
            surface.blit(name_text, (bar_x, 35))
            surface.blit(health_text, (bar_x + bar_width - 100, 35))
        else:
            surface.blit(name_text, (bar_x + bar_width - name_text.get_width(), 35))
            surface.blit(health_text, (bar_x, 35))

    def attack(self, opponent_x):
        if self.attack_cooldown == 0:
            distance = abs(self.rect.centerx - opponent_x)
            if distance < self.rect.width * 2:
                self.attacking = True
                self.attack_cooldown = 15

    def take_damage(self, damage):
        actual_damage = damage * (0.5 if self.blocking else 1)
        self.health = max(0, self.health - actual_damage)

def main():
    clock = pygame.time.Clock()
    
    selected_fighters = ["AgileFighter", "Tank"]
    fighters = [
        Fighter(1, VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[0]]()),
        Fighter(2, VISIBLE_WIDTH*3//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[1]]())
    ]

    settings_menu = SettingsMenu()
    show_settings = False
    running = True

    while running:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_settings = not show_settings
            
            if show_settings and event.type == pygame.MOUSEMOTION:
                settings_menu.handle_events(mouse_pos)
            
            if show_settings and event.type == pygame.MOUSEBUTTONDOWN:
                for button in settings_menu.buttons:
                    if button.is_clicked(mouse_pos) and button.text == "Back":
                        show_settings = False

        if show_settings:
            settings_menu.draw(screen)
            pygame.display.update()
            continue

        screen.blit(bg_image, (0, 0))
        
        fighters[0].move(keys, fighters[1].rect.centerx)
        fighters[1].move(keys, fighters[0].rect.centerx)

        if fighters[0].attacking and fighters[0].hitbox.colliderect(fighters[1].hitbox):
            fighters[1].take_damage(fighters[0].damage)
            fighters[0].attacking = False

        if fighters[1].attacking and fighters[1].hitbox.colliderect(fighters[0].hitbox):
            fighters[0].take_damage(fighters[1].damage)
            fighters[1].attacking = False

        for fighter in fighters:
            fighter.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()