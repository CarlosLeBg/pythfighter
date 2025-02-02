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
        pygame.joystick.init()
        self.controllers = []
        self.controller_types = []  # "ps4" ou "ps5"
        self.controller_states = []
        self.init_controllers()

    def init_controllers(self):
        self.controllers.clear()
        self.controller_types.clear()
        self.controller_states.clear()

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
                    controller.lightbar.set_color(255 if i == 0 else 0, 0, 255)
                    self.controllers.append(controller)
                    self.controller_types.append("ps5")
                except Exception as e:
                    print(f"Erreur initialisation DualSense: {e}")
                    joystick.quit()
            else:
                self.controllers.append(joystick)
                self.controller_types.append("ps4")

            self.controller_states.append({
                'move_x': 0,
                'move_y': 0,
                'jump': False,
                'attack': False,
                'block': False,
                'special': False
            })

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
        state['move_x'] = getattr(controller, 'left_stick_x', 0)
        state['move_y'] = getattr(controller, 'left_stick_y', 0)
        state['jump'] = getattr(controller, 'btn_cross', False)
        state['attack'] = getattr(controller, 'btn_square', False)
        state['block'] = getattr(controller, 'btn_l1', False)
        state['special'] = getattr(controller, 'btn_triangle', False)

    def _update_ps4_state(self, index, controller):
        state = self.controller_states[index]
        state['move_x'] = controller.get_axis(0)
        state['move_y'] = controller.get_axis(1)
        state['jump'] = controller.get_button(0)
        state['attack'] = controller.get_button(1)
        state['block'] = controller.get_button(4)
        state['special'] = controller.get_button(3)

    def get_player_input(self, player_index):
        if player_index >= len(self.controllers):
            return None
            
        controller = self.controllers[player_index]
        input_state = {
            'move_x': 0,
            'move_y': 0,
            'jump': False,
            'attack': False,
            'block': False,
            'special': False
        }

        # Lecture des sticks analogiques
        try:
            input_state['move_x'] = controller.left_stick_x.value
            input_state['move_y'] = controller.left_stick_y.value
            
            # Boutons
            input_state['jump'] = controller.btn_cross.value
            input_state['attack'] = controller.btn_square.value
            input_state['block'] = controller.btn_l1.value or controller.l2_analog.value > 0.5
            input_state['special'] = controller.btn_triangle.value
            
            # Feedback haptique pour les actions
            if input_state['attack']:
                controller.right_rumble = 100
            elif input_state['block']:
                controller.left_rumble = 50
            else:
                controller.right_rumble = 0
                controller.left_rumble = 0
                
        except Exception as e:
            print(f"Erreur de lecture controller {player_index}: {e}")
            
        return input_state

    def cleanup(self):
        for controller in self.controllers:
            try:
                controller.deactivate()
            except:
                pass
        pygame.joystick.quit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
    pygame.display.set_caption("PythFighter - PlayStation Edition")
    
    clock = pygame.time.Clock()
    controller_manager = ControllerManager()

    if len(controller_manager.controllers) < 2:
        print("Erreur: Connectez deux manettes PlayStation (PS4 ou PS5)")
        return

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
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        controller_manager.update_controller_states()
        screen.blit(bg_image, (0, 0))
        
        for i, fighter in enumerate(fighters):
            input_state = controller_manager.get_player_input(i)
            if input_state:
                fighter.handle_controller_input(input_state, fighters[1-i].rect.centerx)

        for fighter in fighters:
            fighter.draw(screen)

        pygame.display.update()
        clock.tick(60)

    controller_manager.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
