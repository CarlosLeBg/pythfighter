import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
from dualsense_controller import DualSenseController

# Screen Configuration
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

class DualSenseManager:
    def __init__(self):
        self.controllers = []
        self.controller_states = []
        self.init_controllers()

    def init_controllers(self):
        try:
            controller1 = DualSenseController()
            controller2 = DualSenseController()
            controller1.activate()
            controller2.activate()
            
            # Configuration des LED pour identifier les controllers
            controller1.lightbar.set_color(0, 0, 255)  # Bleu pour J1
            controller2.lightbar.set_color(255, 0, 0)  # Rouge pour J2
            
            self.controllers = [controller1, controller2]
            
            # Initialisation des états des controllers
            for i, controller in enumerate(self.controllers):
                self._setup_controller_callbacks(i, controller)
            
            self.controller_states = [
                {
                    'move_x': 0,
                    'move_y': 0,
                    'jump': False,
                    'attack': False,
                    'block': False,
                    'special': False
                } for _ in range(2)
            ]
            
            return True
        except Exception as e:
            print(f"Erreur d'initialisation des controllers: {e}")
            return False

    def _setup_controller_callbacks(self, index, controller):
        def create_button_callback(button_name):
            def callback(pressed):
                self.controller_states[index][button_name] = pressed
            return callback

        def create_stick_callback(axis_name):
            def callback(value):
                self.controller_states[index][axis_name] = value
            return callback

        # Configuration des boutons
        controller.btn_cross.on_change(create_button_callback('jump'))
        controller.btn_square.on_change(create_button_callback('attack'))
        controller.btn_triangle.on_change(create_button_callback('special'))
        controller.btn_l1.on_change(create_button_callback('block'))
        
        # Configuration des sticks
        controller.left_stick_x.on_change(create_stick_callback('move_x'))
        controller.left_stick_y.on_change(create_stick_callback('move_y'))

        # Configuration des triggers
        if hasattr(controller, 'l2_analog'):
            controller.l2_analog.on_change(lambda value: setattr(self, f'l2_value_{index}', value))

    def get_player_input(self, player_index):
        if player_index >= len(self.controllers):
            return None
            
        return self.controller_states[player_index]

    def cleanup(self):
        for controller in self.controllers:
            try:
                controller.deactivate()
            except:
                pass

class Fighter:
    def __init__(self, player, x, y, data):
        self.player = player
        self.name = data.name
        self.color = data.color
        
        self.speed = data.speed * 1.2
        self.damage = data.damage
        self.max_health = data.stats["Vie"]
        self.health = self.max_health
        
        self.special_meter = 0
        self.max_special = 100
        
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
        self.special_active = False
        self.attack_cooldown = 0
        self.special_cooldown = 0

    def handle_controller_input(self, input_state, opponent_x):
        if not input_state:
            return

        GRAVITY = 0.8
        JUMP_FORCE = -12
        GROUND_Y = VISIBLE_HEIGHT * 0.9
        MAX_SPEED = self.speed * 2

        # Mouvement horizontal avec le stick analogique
        self.vel_x = input_state['move_x'] * MAX_SPEED
        if abs(self.vel_x) > 0.1:
            self.direction = 1 if self.vel_x > 0 else -1

        # Saut
        if input_state['jump'] and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Blocage
        self.blocking = input_state['block']

        # Attaque normale
        if input_state['attack'] and not self.attacking and self.attack_cooldown == 0:
            self.attack(opponent_x)

        # Attaque spéciale
        if input_state['special'] and self.special_meter >= self.max_special:
            self.special_attack(opponent_x)

        # Physique
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
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

    def attack(self, opponent_x):
        if self.attack_cooldown == 0:
            distance = abs(self.rect.centerx - opponent_x)
            if distance < self.rect.width * 2:
                self.attacking = True
                self.attack_cooldown = 15

    def special_attack(self, opponent_x):
        if self.special_meter >= self.max_special and self.special_cooldown == 0:
            self.special_active = True
            self.special_meter = 0
            self.special_cooldown = 45
            return True
        return False

    def draw(self, surface):
        # Draw fighter
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)

        # Health bar
        self.draw_health_bar(surface)
        
        # Special meter
        self.draw_special_meter(surface)

    def draw_health_bar(self, surface):
        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)

        health_color = (
            int(255 * (1 - health_percentage)), 
            int(255 * health_percentage), 
            0
        )

        bar_x = 20 if self.player == 1 else VISIBLE_WIDTH - bar_width - 20

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

    def draw_special_meter(self, surface):
        meter_width = VISIBLE_WIDTH * 0.3
        meter_height = 10
        meter_percentage = self.special_meter / self.max_special

        meter_x = 20 if self.player == 1 else VISIBLE_WIDTH - meter_width - 20
        meter_y = 60

        pygame.draw.rect(surface, (50, 50, 100), 
                        (meter_x, meter_y, meter_width, meter_height), 
                        border_radius=5)
        pygame.draw.rect(surface, (100, 100, 255), 
                        (meter_x, meter_y, meter_width * meter_percentage, meter_height), 
                        border_radius=5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
    pygame.display.set_caption("PythFighter - DualSense Edition")
    
    clock = pygame.time.Clock()
    
    # Initialize DualSense controllers
    controller_manager = DualSenseManager()
    if not controller_manager.controllers:
        print("Erreur: Connectez deux manettes DualSense")
        return

    # Background
    bg_image = pygame.image.load("src/assets/backg.jpg")
    bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
    
    fighter_classes = {
        "AgileFighter": AgileFighter,
        "Tank": Tank,
        "BurstDamage": BurstDamage,
        "ThunderStrike": ThunderStrike,
        "Bruiser": Bruiser
    }
    selected_fighters = ["AgileFighter", "Tank"]
    fighters = [
        Fighter(1, VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[0]]()),
        Fighter(2, VISIBLE_WIDTH*3//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[1]]())
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.blit(bg_image, (0, 0))
        
        # Get and handle controller inputs
        for i, fighter in enumerate(fighters):
            input_state = controller_manager.get_player_input(i)
            fighter.handle_controller_input(input_state, fighters[1-i].rect.centerx)

        # Combat logic
        for i, attacker in enumerate(fighters):
            defender = fighters[1-i]
            
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

        # Draw everything
        for fighter in fighters:
            fighter.draw(screen)

        pygame.display.update()
        clock.tick(60)

    controller_manager.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()