import pygame
import sys
import json
from enum import Enum
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser, Fighter
import pygame.joystick
from dualsense_controller import DualSenseController
import os
from pygame import mixer

# Screen Configuration
BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

# Couleurs
COLORS = {
    'background': (40, 40, 60),
    'menu_bg': (30, 30, 50),
    'text_primary': (220, 220, 240),
    'text_secondary': (150, 150, 180),
    'button_normal': (60, 60, 100),
    'button_hover': (80, 80, 120),
    'health_bar': (255, 0, 0),
    'special_bar': (0, 255, 255),
    'victory_text': (255, 215, 0)
}

class GameState(Enum):
    MENU = 1
    CHARACTER_SELECT = 2
    FIGHTING = 3
    PAUSED = 4
    SETTINGS = 5
    VICTORY = 6

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            'music_volume': 0.7,
            'sfx_volume': 0.8,
            'rumble_enabled': True,
            'control_scheme': 'default',
            'display_fps': False
        }
        self.current_settings = self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return {**self.default_settings, **json.load(f)}
            return self.default_settings.copy()
        except:
            return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f)
        except Exception as e:
            print(f"Erreur sauvegarde paramètres: {e}")

class SoundManager:
    def __init__(self, settings):
        self.settings = settings
        mixer.init()
        self.load_sounds()
        
    def load_sounds(self):
        self.sounds = {
            'hit': self.load_sound('hit.wav'),
            'block': self.load_sound('block.wav'),
            'special': self.load_sound('special.wav'),
            'menu_move': self.load_sound('menu_move.wav'),
            'menu_select': self.load_sound('menu_select.wav'),
            'victory': self.load_sound('victory.wav')
        }
        
        try:
            mixer.music.load('src/assets/music/theme.mp3')
            mixer.music.set_volume(self.settings.current_settings['music_volume'])
            mixer.music.play(-1)
        except:
            print("Erreur chargement musique")

    def load_sound(self, filename):
        try:
            sound = mixer.Sound(f'src/assets/sounds/{filename}')
            sound.set_volume(self.settings.current_settings['sfx_volume'])
            return sound
        except:
            print(f"Erreur chargement son: {filename}")
            return None

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

class Menu:
    def __init__(self, screen, sound_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.font = pygame.font.Font(None, 36)
        self.menu_items = {
            GameState.MENU: ['Jouer', 'Paramètres', 'Quitter'],
            GameState.CHARACTER_SELECT: ['AgileFighter', 'Tank', 'BurstDamage', 'ThunderStrike', 'Bruiser'],
            GameState.SETTINGS: ['Volume Musique', 'Volume Effets', 'Vibrations', 'Retour']
        }
        self.selected_item = 0
        self.char_select_p1 = 0
        self.char_select_p2 = 1

    def draw(self, state):
        self.screen.fill(COLORS['menu_bg'])
        
        if state == GameState.MENU:
            self.draw_main_menu()
        elif state == GameState.CHARACTER_SELECT:
            self.draw_character_select()
        elif state == GameState.SETTINGS:
            self.draw_settings()
        elif state == GameState.VICTORY:
            self.draw_victory_screen()

    def draw_main_menu(self):
        title = self.font.render('PythFighter', True, COLORS['text_primary'])
        title_rect = title.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//4))
        self.screen.blit(title, title_rect)

        for i, item in enumerate(self.menu_items[GameState.MENU]):
            color = COLORS['text_primary'] if i == self.selected_item else COLORS['text_secondary']
            text = self.font.render(item, True, color)
            text_rect = text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2 + i * 50))
            self.screen.blit(text, text_rect)

    def draw_character_select(self):
        title = self.font.render('Sélection des Personnages', True, COLORS['text_primary'])
        self.screen.blit(title, (VISIBLE_WIDTH//4, 50))

        for i, fighter in enumerate(self.menu_items[GameState.CHARACTER_SELECT]):
            color_p1 = COLORS['text_primary'] if i == self.char_select_p1 else COLORS['text_secondary']
            color_p2 = COLORS['text_primary'] if i == self.char_select_p2 else COLORS['text_secondary']
            
            # P1 selection
            text_p1 = self.font.render(f"P1: {fighter}" if i == self.char_select_p1 else fighter, True, color_p1)
            self.screen.blit(text_p1, (100, 150 + i * 40))
            
            # P2 selection
            text_p2 = self.font.render(f"P2: {fighter}" if i == self.char_select_p2 else fighter, True, color_p2)
            self.screen.blit(text_p2, (VISIBLE_WIDTH - 300, 150 + i * 40))

    def draw_settings(self):
        title = self.font.render('Paramètres', True, COLORS['text_primary'])
        self.screen.blit(title, (VISIBLE_WIDTH//4, 50))

        settings = Settings().current_settings
        items = [
            f"Volume Musique: {int(settings['music_volume'] * 100)}%",
            f"Volume Effets: {int(settings['sfx_volume'] * 100)}%",
            f"Vibrations: {'Activées' if settings['rumble_enabled'] else 'Désactivées'}",
            "Retour"
        ]

        for i, item in enumerate(items):
            color = COLORS['text_primary'] if i == self.selected_item else COLORS['text_secondary']
            text = self.font.render(item, True, color)
            self.screen.blit(text, (VISIBLE_WIDTH//4, 150 + i * 50))

    def draw_victory_screen(self):
        title = self.font.render('VICTOIRE!', True, COLORS['victory_text'])
        self.screen.blit(title, (VISIBLE_WIDTH//2 - 100, VISIBLE_HEIGHT//3))
        
        continue_text = self.font.render('Appuyez sur Options pour continuer', True, COLORS['text_secondary'])
        self.screen.blit(continue_text, (VISIBLE_WIDTH//2 - 200, VISIBLE_HEIGHT*2//3))

class ControllerManager:
    def __init__(self, settings):
        self.settings = settings
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
                        # Configuration DualSense
                        if i == 0:
                            controller.lightbar.set_color(0, 0, 255)  # Bleu P1
                            if self.settings.current_settings['rumble_enabled']:
                                controller.right_trigger.set_mode(1)  # Mode gâchette adaptative
                                controller.left_trigger.set_mode(1)
                        else:
                            controller.lightbar.set_color(255, 0, 0)  # Rouge P2
                            if self.settings.current_settings['rumble_enabled']:
                                controller.right_trigger.set_mode(1)
                                controller.left_trigger.set_mode(1)
                        
                        self.controllers.append(controller)
                        self.controller_types.append("ps5")
                        print(f"DualSense (PS5) initialisée sur le port {i}")
                    except Exception as e:
                        print(f"Erreur initialisation DualSense: {e}")
                        self.fallback_to_standard_controller(joystick, i)
                elif "dualshock" in name or "ps4" in name:
                    self.controllers.append(joystick)
                    self.controller_types.append("ps4")
                    print(f"DualShock (PS4) initialisée sur le port {i}")
                else:
                    self.fallback_to_standard_controller(joystick, i)

            self.init_controller_states()
            return len(self.controllers) > 0

        except Exception as e:
            print(f"Erreur globale d'initialisation: {e}")
            return False

    def fallback_to_standard_controller(self, joystick, index):
        self.controllers.append(joystick)
        self.controller_types.append("ps4")
        print(f"Utilisation mode standard pour manette {index}")

    def init_controller_states(self):
        self.controller_states = [
            {
                'move_x': 0, 'move_y': 0,
                'jump': False, 'attack': False,
                'block': False, 'special': False,
                'start': False, 'select': False,
                'menu_up': False, 'menu_down': False,
                'menu_left': False, 'menu_right': False
            } for _ in range(len(self.controllers))
        ]

    def update_controller_states(self):
        for i, (controller, controller_type) in enumerate(zip(self.controllers, self.controller_types)):
            try:
                if controller_type == "ps5":
                    self._update_ps5_state(i, controller)
                else:
                    self._update_ps4_state(i, controller)
            except Exception as e:
                print(f"Erreur mise à jour controller {i}: {e}")
                self.reset_controller_state(i)

    def _update_ps5_state(self, index, controller):
        state = self.controller_states[index]
        try:
            # Mouvements
            state['move_x'] = getattr(controller, 'left_stick_x', 0)
            state['move_y'] = getattr(controller, 'left_stick_y', 0)
            if hasattr(state['move_x'], 'value'):
                state['move_x'] = max(-1.0, min(1.0, state['move_x'].value))
            if hasattr(state['move_y'], 'value'):
                state['move_y'] = max(-1.0, min(1.0, state['move_y'].value))

            # Boutons d'action
            state['jump'] = bool(getattr(getattr(controller, 'btn_cross', None), 'pressed', False))
            state['attack'] = bool(getattr(getattr(controller, 'btn_square', None), 'pressed', False))
            state['block'] = bool(getattr(getattr(controller, 'btn_l1', None), 'pressed', False))
            state['special'] = bool(getattr(getattr(controller, 'btn_triangle', None), 'pressed', False))

            # Boutons menu
            state['start'] = bool(getattr(getattr(controller, 'btn_options', None), 'pressed', False))
            state['select'] = bool(getattr(getattr(controller, 'btn_create', None), 'pressed', False))
            
            # D-pad pour menus
            state['menu_up'] = bool(getattr(getattr(controller, 'dpad_up', None), 'pressed', False))
            state['menu_down'] = bool(getattr(getattr(controller, 'dpad_down', None), 'pressed', False))
            state['menu_left'] = bool(getattr(getattr(controller, 'dpad_left', None), 'pressed', False))
            state['menu_right'] = bool(getattr(getattr(controller, 'dpad_right', None), 'pressed', False))

            # Vibrations si activé
            if self.settings.current_settings['rumble_enabled']:
                if state['attack'] or state['special']:
                    controller.light_motor.set_intensity(0.7)
                    controller.heavy_motor.set_intensity(0.3)
                else:
                    controller.light_motor.set_intensity(0)
                    controller.heavy_motor.set_intensity(0)

        except Exception as e:
            print(f"Erreur lecture PS5 {index}: {e}")

    def _update_ps4_state(self, index, controller):
        state = self.controller_states[index]
        try:
            # Mouvements
            state['move_x'] = controller.get_axis(0)
            state['move_y'] = controller.get_axis(1)

            # Boutons d'action
            state['jump'] = controller.get_button(0)    # X
            state['attack'] = controller.get_button(1)  # Carré
            state['block'] = controller.get_button(4)   # L1
            state['special'] = controller.get_button(2) # Triangle

            # Boutons menu
            state['start'] = controller.get_button(9)   # Options
            state['select'] = controller.get_button(8)  # Share/Create

            # D-pad pour menus (axes ou boutons selon la manette)
            try:
                hat = controller.get_hat(0)
                state['menu_up'] = hat[1] > 0
                state['menu_down'] = hat[1] < 0
                state['menu_left'] = hat[0] < 0
                state['menu_right'] = hat[0] > 0
            except:
                # Fallback pour les manettes sans hat
                state['menu_up'] = controller.get_button(11)
                state['menu_down'] = controller.get_button(12)
                state['menu_left'] = controller.get_button(13)
                state['menu_right'] = controller.get_button(14)

        except Exception as e:
            print(f"Erreur lecture PS4 {index}: {e}")

    def reset_controller_state(self, index):
        self.controller_states[index] = {
            'move_x': 0, 'move_y': 0,
            'jump': False, 'attack': False,
            'block': False, 'special': False,
            'start': False, 'select': False,
            'menu_up': False, 'menu_down': False,
            'menu_left': False, 'menu_right': False
        }

    def get_player_input(self, player_index):
        if 0 <= player_index < len(self.controllers):
            return self.controller_states[player_index]
        return None

    def cleanup(self):
        for controller, controller_type in zip(self.controllers, self.controller_types):
            try:
                if controller_type == "ps5":
                    controller.light_motor.set_intensity(0)
                    controller.heavy_motor.set_intensity(0)
                    controller.right_trigger.set_mode(0)
                    controller.left_trigger.set_mode(0)
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
    
    # Initialisation des systèmes
    settings = Settings()
    sound_manager = SoundManager(settings)
    controller_manager = ControllerManager(settings)
    menu = Menu(screen, sound_manager)
    
    # État initial
    game_state = GameState.MENU
    
    # Chargement des ressources
    try:
        bg_image = pygame.image.load("src/assets/backg.jpg")
        bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
    except Exception as e:
        print(f"Erreur chargement image de fond: {e}")
        bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        bg_image.fill(COLORS['background'])

    fighter_classes = {
        "AgileFighter": AgileFighter,
        "Tank": Tank,
        "BurstDamage": BurstDamage,
        "ThunderStrike": ThunderStrike,
        "Bruiser": Bruiser
    }

    fighters = []
    round_timer = 99  # 99 secondes par round
    round_start_time = 0
    winner = None

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GameState.FIGHTING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.PAUSED:
                        game_state = GameState.FIGHTING
                    else:
                        running = False

        controller_manager.update_controller_states()
        
        # Gestion des états du jeu
        if game_state == GameState.MENU:
            menu.draw(game_state)
            
            # Navigation menu principal
            for i in range(2):  # Check both controllers
                controller_state = controller_manager.get_player_input(i)
                if controller_state:
                    if controller_state['menu_up'] and not menu.prev_up:
                        menu.selected_item = (menu.selected_item - 1) % len(menu.menu_items[GameState.MENU])
                        sound_manager.play_sound('menu_move')
                    elif controller_state['menu_down'] and not menu.prev_down:
                        menu.selected_item = (menu.selected_item + 1) % len(menu.menu_items[GameState.MENU])
                        sound_manager.play_sound('menu_move')
                    elif controller_state['jump']:  # X pour sélectionner
                        sound_manager.play_sound('menu_select')
                        if menu.selected_item == 0:  # Jouer
                            game_state = GameState.CHARACTER_SELECT
                        elif menu.selected_item == 1:  # Paramètres
                            game_state = GameState.SETTINGS
                        elif menu.selected_item == 2:  # Quitter
                            running = False

        elif game_state == GameState.CHARACTER_SELECT:
            menu.draw(game_state)
            
            # Sélection des personnages
            controller_state_p1 = controller_manager.get_player_input(0)
            controller_state_p2 = controller_manager.get_player_input(1)
            
            if controller_state_p1:
                if controller_state_p1['menu_up']:
                    menu.char_select_p1 = (menu.char_select_p1 - 1) % len(menu.menu_items[GameState.CHARACTER_SELECT])
                    sound_manager.play_sound('menu_move')
                elif controller_state_p1['menu_down']:
                    menu.char_select_p1 = (menu.char_select_p1 + 1) % len(menu.menu_items[GameState.CHARACTER_SELECT])
                    sound_manager.play_sound('menu_move')
            
            if controller_state_p2:
                if controller_state_p2['menu_up']:
                    menu.char_select_p2 = (menu.char_select_p2 - 1) % len(menu.menu_items[GameState.CHARACTER_SELECT])
                    sound_manager.play_sound('menu_move')
                elif controller_state_p2['menu_down']:
                    menu.char_select_p2 = (menu.char_select_p2 + 1) % len(menu.menu_items[GameState.CHARACTER_SELECT])
                    sound_manager.play_sound('menu_move')
            
            # Validation des choix et début du combat
            if ((controller_state_p1 and controller_state_p1['start']) or 
                (controller_state_p2 and controller_state_p2['start'])):
                selected_fighters = [
                    menu.menu_items[GameState.CHARACTER_SELECT][menu.char_select_p1],
                    menu.menu_items[GameState.CHARACTER_SELECT][menu.char_select_p2]
                ]
                
                fighters = [
                    Fighter(1, VISIBLE_WIDTH//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[0]]()),
                    Fighter(2, VISIBLE_WIDTH*3//4, VISIBLE_HEIGHT//2, fighter_classes[selected_fighters[1]]())
                ]
                
                round_start_time = current_time
                game_state = GameState.FIGHTING
                sound_manager.play_sound('menu_select')

        elif game_state == GameState.FIGHTING:
            # Affichage du combat
            screen.blit(bg_image, (0, 0))
            
            # Timer
            remaining_time = max(0, round_timer - (current_time - round_start_time) // 1000)
            timer_text = pygame.font.Font(None, 74).render(str(remaining_time), True, COLORS['text_primary'])
            screen.blit(timer_text, (VISIBLE_WIDTH//2 - 20, 20))
            
            # Mise à jour et combat
            for i, fighter in enumerate(fighters):
                input_state = controller_manager.get_player_input(i)
                if input_state:
                    fighter.handle_controller_input(input_state, fighters[1-i].rect.centerx)
                
                # Logique de combat
                if fighter.attacking and fighter.hitbox.colliderect(fighters[1-i].hitbox):
                    if not fighters[1-i].blocking:
                        fighters[1-i].health -= fighter.damage
                        fighter.special_meter = min(fighter.max_special, 
                                                 fighter.special_meter + fighter.damage * 2)
                        sound_manager.play_sound('hit')
                    else:
                        fighters[1-i].special_meter = min(fighters[1-i].max_special, 
                                                       fighters[1-i].special_meter + fighter.damage)
                        sound_manager.play_sound('block')
                    fighter.attacking = False
                
                if fighter.special_active and fighter.hitbox.colliderect(fighters[1-i].hitbox):
                    if not fighters[1-i].blocking:
                        fighters[1-i].health -= fighter.damage * 2
                        sound_manager.play_sound('special')
                    else:
                        fighters[1-i].health -= fighter.damage
                        sound_manager.play_sound('block')
                    fighter.special_active = False
                
                # Vérification de la victoire
                if fighters[1-i].health <= 0:
                    winner = fighter
                    game_state = GameState.VICTORY
                    sound_manager.play_sound('victory')
                elif remaining_time <= 0:
                    winner = max(fighters, key=lambda f: f.health)
                    game_state = GameState.VICTORY
                    sound_manager.play_sound('victory')
                
                fighter.draw(screen)
                
            # Pause
            for i in range(2):
                controller_state = controller_manager.get_player_input(i)
                if controller_state and controller_state['start']:
                    game_state = GameState.PAUSED
                    break

        elif game_state == GameState.PAUSED:
            # Afficher menu pause
            s = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            screen.blit(s, (0, 0))
            
            pause_text = pygame.font.Font(None, 74).render("PAUSE", True, COLORS['text_primary'])
            screen.blit(pause_text, (VISIBLE_WIDTH//2 - 100, VISIBLE_HEIGHT//2))
            
            # Retour au jeu
            for i in range(2):
                controller_state = controller_manager.get_player_input(i)
                if controller_state and controller_state['start']:
                    game_state = GameState.FIGHTING
                    break

        elif game_state == GameState.SETTINGS:
            menu.draw(game_state)
            
            # Navigation paramètres
            for i in range(2):
                controller_state = controller_manager.get_player_input(i)
                if controller_state:
                    if controller_state['menu_up']:
                        menu.selected_item = (menu.selected_item - 1) % len(menu.menu_items[GameState.SETTINGS])
                        sound_manager.play_sound('menu_move')
                    elif controller_state['menu_down']:
                        menu.selected_item = (menu.selected_item + 1) % len(menu.menu_items[GameState.SETTINGS])
                        sound_manager.play_sound('menu_move')
                    elif controller_state['menu_left'] or controller_state['menu_right']:
                        if menu.selected_item == 0:  # Volume Musique
                            delta = 0.1 if controller_state['menu_right'] else -0.1
                            settings.current_settings['music_volume'] = max(0, min(1, settings.current_settings['music_volume'] + delta))
                            mixer.music.set_volume(settings.current_settings['music_volume'])
                        elif menu.selected_item == 1:  # Volume Effets
                            delta = 0.1 if controller_state['menu_right'] else -0.1
                            settings.current_settings['sfx_volume'] = max(0, min(1, settings.current_settings['sfx_volume'] + delta))
                            for sound in sound_manager.sounds.values():
                                if sound:
                                    sound.set_volume(settings.current_settings['sfx_volume'])
                        elif menu.selected_item == 2:  # Vibrations
                            settings.current_settings['rumble_enabled'] = not settings.current_settings['rumble_enabled']
                    elif controller_state['jump'] and menu.selected_item == 3:  # Retour
                        settings.save_settings()
                        game_state = GameState.MENU

        elif game_state == GameState.VICTORY:
            menu.draw(game_state)
            
            victory_text = pygame.font.Font(None, 74).render(f"JOUEUR {winner.player_num} GAGNE!", True, COLORS['victory_text'])
            screen.blit(victory_text, (VISIBLE_WIDTH//2 - 200, VISIBLE_HEIGHT//2))
            
            # Retour au menu principal
            for i in range(2):
                controller_state = controller_manager.get_player_input(i)
                if controller_state and controller_state['start']:
                    game_state = GameState.MENU
                    menu.selected_item = 0
                    break

        pygame.display.update()
        clock.tick(60)

    controller_manager.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()