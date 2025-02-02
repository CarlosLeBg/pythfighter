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

class GameState:
    FIGHTING = 0
    PAUSED = 1

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.FIGHTING
        self.font = pygame.font.Font(None, 36)

    def draw_pause(self):
        # Semi-transparent overlay
        s = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # Pause text
        pause_text = self.font.render("PAUSE", True, COLORS['text_primary'])
        text_rect = pause_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)

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
                        if i == 0:
                            controller.lightbar.set_color(0, 0, 255)  # Bleu P1
                        else:
                            controller.lightbar.set_color(255, 0, 0)  # Rouge P2
                        self.controllers.append(controller)
                        self.controller_types.append("ps5")
                        print(f"DualSense (PS5) initialisée sur le port {i}")
                    except Exception as e:
                        print(f"Erreur initialisation DualSense: {e}")
                        try:
                            self.controllers.append(joystick)
                            self.controller_types.append("ps4")
                            print(f"Fallback vers mode standard pour manette sur port {i}")
                        except:
                            joystick.quit()
                elif "dualshock" in name or "ps4" in name:
                    self.controllers.append(joystick)
                    self.controller_types.append("ps4")
                    print(f"DualShock (PS4) initialisée sur le port {i}")
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
                    'special': False,
                    'start': False
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
                self.controller_states[i] = {
                    'move_x': 0, 'move_y': 0,
                    'jump': False, 'attack': False,
                    'block': False, 'special': False,
                    'start': False
                }

    def _update_ps5_state(self, index, controller):
        state = self.controller_states[index]
        try:
            state['move_x'] = getattr(controller, 'left_stick_x', 0)
            state['move_y'] = getattr(controller, 'left_stick_y', 0)
            
            if hasattr(state['move_x'], 'value'):
                state['move_x'] = max(-1.0, min(1.0, state['move_x'].value))
            if hasattr(state['move_y'], 'value'):
                state['move_y'] = max(-1.0, min(1.0, state['move_y'].value))

            state['jump'] = bool(getattr(getattr(controller, 'btn_cross', None), 'pressed', False))
            state['attack'] = bool(getattr(getattr(controller, 'btn_square', None), 'pressed', False))
            state['block'] = bool(getattr(getattr(controller, 'btn_l1', None), 'pressed', False))
            state['special'] = bool(getattr(getattr(controller, 'btn_triangle', None), 'pressed', False))
            state['start'] = bool(getattr(getattr(controller, 'btn_options', None), 'pressed', False))

        except Exception as e:
            print(f"Erreur lecture PS5 {index}: {e}")

    def _update_ps4_state(self, index, controller):
        state = self.controller_states[index]
        try:
            state['move_x'] = controller.get_axis(0)
            state['move_y'] = controller.get_axis(1)
            state['jump'] = controller.get_button(0)    # X
            state['attack'] = controller.get_button(1)  # Carré
            state['block'] = controller.get_button(4)   # L1
            state['special'] = controller.get_button(2) # Triangle
            state['start'] = controller.get_button(9)   # Options

        except Exception as e:
            print(f"Erreur lecture PS4 {index}: {e}")

    def get_player_input(self, player_index):
        if 0 <= player_index < len(self.controllers):
            return self.controller_states[player_index]
        return None

    def cleanup(self):
        for controller, controller_type in zip(self.controllers, self.controller_types):
            try:
                if controller_type == "ps5":
                    controller.deactivate()
                else:
                    controller.quit()
            except Exception as e:
                print(f"Erreur nettoyage controller: {e}")
        pygame.joystick.quit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
    pygame.display.set_caption("PythFighter - PlayStation Edition")
    clock = pygame.time.Clock()
    
    controller_manager = ControllerManager()
    menu = Menu(screen)
    
    # Load background
    try:
        bg_image = pygame.image.load("src/assets/backg.jpg")
        bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
    except Exception as e:
        print(f"Erreur chargement image de fond: {e}")
        bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        bg_image.fill(COLORS['background'])

    fighter1 = AgileFighter()
    fighter2 = Tank()


    
    fighter1.id = 1
    fighter2.id = 2
    fighter1.x = VISIBLE_WIDTH // 4
    fighter1.y = VISIBLE_HEIGHT // 2
    fighter2.x = VISIBLE_WIDTH * 3 // 4
    fighter2.y = VISIBLE_HEIGHT // 2

    fighters = [fighter1, fighter2]


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu.state == GameState.FIGHTING:
                        menu.state = GameState.PAUSED
                    else:
                        menu.state = GameState.FIGHTING

        controller_manager.update_controller_states()

        # Check for pause with controllers
        for i in range(len(controller_manager.controllers)):
            controller_state = controller_manager.get_player_input(i)
            if controller_state and controller_state['start']:
                if menu.state == GameState.FIGHTING:
                    menu.state = GameState.PAUSED
                else:
                    menu.state = GameState.FIGHTING

        # Draw game
        screen.blit(bg_image, (0, 0))

        if menu.state == GameState.FIGHTING:
            # Update fighters
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

            # Draw fighters
            for fighter in fighters:
                fighter.draw(screen)
        else:
            # Draw pause menu
            menu.draw_pause()

        pygame.display.update()
        clock.tick(60)

    controller_manager.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()