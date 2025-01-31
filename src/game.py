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
pygame.font.init()
screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
pygame.display.set_caption("PythFighter")

# Fonts
TITLE_FONT = pygame.font.Font(None, 48)
MENU_FONT = pygame.font.Font(None, 32)
TEXT_FONT = pygame.font.Font(None, 24)

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
    def __init__(self, x, y, width, height, text, font, inactive_color, active_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.hover = False

    def draw(self, surface):
        color = self.active_color if self.hover else self.inactive_color
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
                   VISIBLE_WIDTH//2, 50, "Sound", MENU_FONT, 
                   COLORS['button_normal'], COLORS['button_hover']),
            Button(VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2, 
                   VISIBLE_WIDTH//2, 50, "Controls", MENU_FONT, 
                   COLORS['button_normal'], COLORS['button_hover']),
            Button(VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2 + 100, 
                   VISIBLE_WIDTH//2, 50, "Back", MENU_FONT, 
                   COLORS['button_normal'], COLORS['button_hover'])
        ]

    def draw(self, surface):
        surface.fill(COLORS['menu_bg'])
        
        # Title
        title = TITLE_FONT.render("Settings", True, COLORS['text_primary'])
        title_rect = title.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEMOTION:
                for button in self.buttons:
                    button.hover = button.rect.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.is_clicked(event.pos):
                        if button.text == "Back":
                            return False
        return True

class Fighter:
    def __init__(self, player, x, y, data):
        self.player = player
        self.name = data.name
        # Enhanced color palette
        self.color = (
            min(255, data.color[0] + 50),
            min(255, data.color[1] + 50),
            min(255, data.color[2] + 50)
        )
        
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

        # Movement logic remains the same as previous version
        # (Omitted for brevity, use previous implementation)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)

        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)

        # Gradient health bar
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

        # Enhanced text rendering
        name_text = TEXT_FONT.render(self.name, True, COLORS['text_primary'])
        health_text = TEXT_FONT.render(f"{int(self.health)}/{self.max_health}", True, COLORS['text_secondary'])

        if self.player == 1:
            surface.blit(name_text, (bar_x, 35))
            surface.blit(health_text, (bar_x + bar_width - 100, 35))
        else:
            surface.blit(name_text, (bar_x + bar_width - name_text.get_width(), 35))
            surface.blit(health_text, (bar_x, 35))

# Main Game Loop
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
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_settings = not show_settings

        if show_settings:
            continue_menu = settings_menu.handle_events()
            settings_menu.draw(screen)
            pygame.display.update()
            continue

        # Game rendering logic
        screen.blit(bg_image, (0, 0))
        
        fighters[0].move(keys, fighters[1].rect.centerx)
        fighters[1].move(keys, fighters[0].rect.centerx)

        for fighter in fighters:
            fighter.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()