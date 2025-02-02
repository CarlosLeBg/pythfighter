
import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

fighter_classes = {
    "AgileFighter": AgileFighter,
    "Tank": Tank,
    "BurstDamage": BurstDamage,
    "ThunderStrike": ThunderStrike,
    "Bruiser": Bruiser
}
from dualsense_controller import DualSenseController

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

class ControllerManager:
    def __init__(self):
        self.controllers = []
        self.controller_types = []
        self.controller_states = []
        pygame.joystick.init()
        self.init_controllers()

    def init_controllers(self):
        try:
            num_joysticks = pygame.joystick.get_count()
            print(f"Nombre de manettes détectées : {num_joysticks}")

            for i in range(num_joysticks):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                name = joystick.get_name().lower()
                print(f"Manette {i+1}: {name}")

                if "dualsense" in name or "ps5" in name:
                    try:
                        controller = DualSenseController()
                        controller.activate()
                        controller.lightbar.set_color(0 if i == 0 else 255, 0, 255 if i == 0 else 0)
                        self.controllers.append(controller)
                        self.controller_types.append("ps5")
                        print(f"DualSense (PS5) initialisée sur le port {i}")
                    except Exception as e:
                        print(f"Erreur initialisation DualSense: {e}")
                        joystick.quit()
                        continue
                else:
                    self.controllers.append(joystick)
                    self.controller_types.append("ps4")
                    print(f"Manette générique initialisée sur le port {i}")

            self.controller_states = [
                {
                    'move_x': 0,
                    'move_y': 0,
                    'jump': False,
                    'attack': False,
                    'block': False,
                    'special': False
                } for _ in range(len(self.controllers))
            ]

            return len(self.controllers) > 0
        except Exception as e:
            print(f"Erreur globale d'initialisation: {e}")
            return False

    def update_controller_states(self):
        for i, (controller, controller_type) in enumerate(zip(self.controllers, self.controller_types)):
            try:
                if controller_type == "ps5":
                    self._update_ps5_state(i, controller)
                else:
                    self._update_ps4_state(i, controller)
            except Exception as e:
                print(f"Erreur mise à jour controller {i}: {e}")

    def _update_ps5_state(self, index, controller):
        state = self.controller_states[index]
        try:
            state['move_x'] = controller.left_stick_x if hasattr(controller, 'left_stick_x') else 0
            state['move_y'] = controller.left_stick_y if hasattr(controller, 'left_stick_y') else 0
            state['jump'] = controller.btn_cross.pressed if hasattr(controller, 'btn_cross') else False
            state['attack'] = controller.btn_square.pressed if hasattr(controller, 'btn_square') else False
            state['block'] = controller.btn_l1.pressed if hasattr(controller, 'btn_l1') else False
            state['special'] = controller.btn_triangle.pressed if hasattr(controller, 'btn_triangle') else False
        except Exception as e:
            print(f"Erreur lecture PS5 {index}: {e}")

    def _update_ps4_state(self, index, controller):
        state = self.controller_states[index]
        try:
            state['move_x'] = controller.get_axis(0)
            state['move_y'] = controller.get_axis(1)
            state['jump'] = controller.get_button(0)
            state['attack'] = controller.get_button(1)
            state['block'] = controller.get_button(4)
            state['special'] = controller.get_button(3)
        except Exception as e:
            print(f"Erreur lecture PS4 {index}: {e}")

    def get_player_input(self, player_index):
        if player_index >= len(self.controllers):
            return None
        return self.controller_states[player_index]

    def cleanup(self):
        for controller, controller_type in zip(self.controllers, self.controller_types):
            try:
                if controller_type == "ps5":
                    controller.deactivate()
                else:
                    controller.quit()
            except:
                pass
        pygame.joystick.quit()


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
        
        # Animation states
        self.current_animation = "idle"
        self.animation_frame = 0

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

        # Limites de l'écran
        self.rect.left = max(0, min(self.rect.left, VISIBLE_WIDTH - self.rect.width))
        self.hitbox.topleft = (self.rect.x + self.rect.width//4, self.rect.y + self.rect.height//4)

        # Mise à jour des cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

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

        # Name and health text
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
    controller_manager = ControllerManager()
    if not controller_manager.controllers:
        print("Erreur: Connectez deux manettes DualSense")
        return

    # Background
    bg_image = pygame.image.load("src/assets/backg.jpg")
    bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
    
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
