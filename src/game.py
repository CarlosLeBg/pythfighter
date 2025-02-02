import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser, Fighter
import pygame.joystick
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
                        # Correction ici : seulement 3 paramètres RGB au lieu de 5
                        controller.lightbar.set_color(0 if i == 0 else 255, 0, 255 if i == 0 else 0)
                        self.controllers.append(controller)
                        self.controller_types.append("ps5")
                        print(f"DualSense (PS5) initialisée sur le port {i}")
                    except Exception as e:
                        print(f"Erreur initialisation DualSense: {e}")
                        joystick.quit()
                        continue
                elif "dualshock" in name or "ps4" in name:
                    self.controllers.append(joystick)
                    self.controller_types.append("ps4")
                    print(f"DualShock (PS4) initialisée sur le port {i}")

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
                else:  # ps4
                    self._update_ps4_state(i, controller)
            except Exception as e:
                print(f"Erreur mise à jour controller {i}: {e}")

    def _update_ps5_state(self, index, controller):
        state = self.controller_states[index]
        try:
            # Lecture des sticks avec correction des valeurs négatives
            left_x = getattr(controller, 'left_stick_x', 0)
            left_y = getattr(controller, 'left_stick_y', 0)
            
            if hasattr(left_x, 'value'):
                state['move_x'] = max(-1.0, min(1.0, left_x.value))
            if hasattr(left_y, 'value'):
                state['move_y'] = max(-1.0, min(1.0, left_y.value))

            # Boutons
            state['jump'] = bool(getattr(controller.btn_cross, 'pressed', False))
            state['attack'] = bool(getattr(controller.btn_square, 'pressed', False))
            state['block'] = bool(getattr(controller.btn_l1, 'pressed', False))
            state['special'] = bool(getattr(controller.btn_triangle, 'pressed', False))

        except Exception as e:
            print(f"Erreur lecture PS5 {index}: {e}")

    def _update_ps4_state(self, index, controller):
        state = self.controller_states[index]
        try:
            # Mapping des boutons PS4
            state['move_x'] = controller.get_axis(0)  # Stick gauche X
            state['move_y'] = controller.get_axis(1)  # Stick gauche Y
            state['jump'] = controller.get_button(0)    # X
            state['attack'] = controller.get_button(1)  # Carré
            state['block'] = controller.get_button(4)   # L1
            state['special'] = controller.get_button(3) # Triangle

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
    pygame.display.set_caption("PythFighter - PlayStation Edition")
    
    clock = pygame.time.Clock()
    
    # Initialize controllers
    controller_manager = ControllerManager()
    if len(controller_manager.controllers) < 2:
        print("Erreur: Connectez deux manettes PlayStation (PS4 ou PS5)")
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

        # Mise à jour des états des contrôleurs
        controller_manager.update_controller_states()

        screen.blit(bg_image, (0, 0))
        
        # Gestion des inputs et logique de combat
        for i, fighter in enumerate(fighters):
            input_state = controller_manager.get_player_input(i)
            if input_state:
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