import pygame
import sys
import time
import os
import logging
import random
import json
import uuid
import socket
import threading
from enum import Enum
import math

# Configuration des logs
logging.basicConfig(filename='multiplayer.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser

# Constants
BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

GRAVITY = 0.4
GROUND_Y = VISIBLE_HEIGHT - VISIBLE_HEIGHT // 5.4
MAX_JUMP_HEIGHT = 60
BLOCK_STAMINA_DRAIN = 0.2
SPECIAL_ATTACK_MULTIPLIER = 2.5

# Configuration du serveur
# Utiliser une variable d'environnement ou une valeur par défaut
SERVER_HOST = os.environ.get('SERVER_HOST', '194.9.172.146')
SERVER_PORT = 25568
PING_PORT = 25569

# Fonction pour définir l'adresse du serveur
def set_server_address(host):
    global SERVER_HOST
    SERVER_HOST = host
    return SERVER_HOST

class GameState(Enum):
    WAITING = "waiting"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    PAUSED = "paused"
    VICTORY = "victory"
    DEFEAT = "defeat"
    DISCONNECTED = "disconnected"

# Cache pour les images chargées
image_cache = {}

def load_image(path):
    if not os.path.exists(path):
        logging.error(f"Image file not found: {path}")
        return None
    if path not in image_cache:
        try:
            image = pygame.image.load(path).convert_alpha()
            image_cache[path] = image
            logging.info(f"Image loaded successfully: {path}")
        except Exception as e:
            logging.error(f"Error loading image {path}: {e}")
            return None
    return image_cache[path]

class Fighter:
    def __init__(self, player_num, x, y, fighter_type, ground_y):
        self.player_num = player_num
        self.pos_x = x
        self.pos_y = y
        self.vel_x = 0
        self.vel_y = 0
        self.ground_y = ground_y
        self.width = 150
        self.height = 150
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen = 0.2
        self.direction = 1  # 1 = droite, -1 = gauche
        self.jumping = False
        self.attacking = False
        self.blocking = False
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.special_cooldown = 0
        self.stun_time = 0
        self.knockback = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.fighter_type = fighter_type
        self.name = fighter_type.__class__.__name__
        
        # Animations
        self.animations = {
            "idle": self._load_animation("idle", 4),
            "walk": self._load_animation("walk", 6),
            "jump": self._load_animation("jump", 4),
            "attack": self._load_animation("attack", 4),
            "special": self._load_animation("special", 6),
            "block": self._load_animation("block", 2),
            "hit": self._load_animation("hit", 3),
            "victory": self._load_animation("victory", 6),
            "defeat": self._load_animation("defeat", 6)
        }
        
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.animation_time = 0
        
        # Sons
        try:
            self.attack_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "attack.wav"))
            self.jump_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "jump.wav"))
            self.hit_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "hit.wav"))
            self.special_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "special.wav"))
            self.sounds_loaded = True
        except Exception as e:
            logging.error(f"Failed to load fighter sounds: {e}")
            self.sounds_loaded = False
    
    def _load_animation(self, animation_name, frames):
        animation_frames = []
        for i in range(frames):
            frame_path = os.path.join("src", "assets", "fighters", self.name.lower(), f"{animation_name}_{i+1}.png")
            frame = load_image(frame_path)
            if frame:
                frame = pygame.transform.scale(frame, (self.width, self.height))
                animation_frames.append(frame)
            else:
                # Utiliser une image de remplacement si l'image n'est pas trouvée
                fallback = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                fallback.fill((255, 0, 255, 128))  # Violet semi-transparent
                animation_frames.append(fallback)
        return animation_frames
    
    def update(self, dt, opponent=None):
        # Mettre à jour les timers
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.special_cooldown > 0:
            self.special_cooldown -= dt
        if self.stun_time > 0:
            self.stun_time -= dt
            return  # Ne pas mettre à jour si étourdi
        
        # Régénération de stamina
        if not self.attacking and not self.blocking:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen * dt)
        
        # Appliquer la gravité
        if self.pos_y < self.ground_y - self.height:
            self.vel_y += GRAVITY
            self.jumping = True
        else:
            self.pos_y = self.ground_y - self.height
            self.vel_y = 0
            self.jumping = False
        
        # Appliquer le knockback
        if self.knockback != 0:
            self.vel_x = self.knockback
            self.knockback *= 0.9  # Réduire progressivement
            if abs(self.knockback) < 0.1:
                self.knockback = 0
        
        # Mettre à jour la position
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        # Limites de l'écran
        if self.pos_x < 0:
            self.pos_x = 0
            self.vel_x = 0
        elif self.pos_x > VISIBLE_WIDTH - self.width:
            self.pos_x = VISIBLE_WIDTH - self.width
            self.vel_x = 0
        
        # Mettre à jour le rectangle de collision
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        
        # Mettre à jour l'animation
        self.update_animation(dt)
        
        # Vérifier les collisions avec l'adversaire
        if opponent and self.attacking and self.attack_cooldown <= 0:
            if self.check_hit(opponent):
                damage = self.fighter_type.attack_damage
                if self.current_animation == "special":
                    damage *= SPECIAL_ATTACK_MULTIPLIER
                opponent.take_hit(damage, self.direction)
                self.attack_cooldown = 0.5
    
    def update_animation(self, dt):
        self.animation_time += dt
        
        # Déterminer l'animation actuelle
        if self.stun_time > 0:
            new_animation = "hit"
        elif self.attacking:
            if self.current_animation == "special" and self.animation_frame < len(self.animations["special"]) - 1:
                new_animation = "special"
            elif self.current_animation == "attack" and self.animation_frame < len(self.animations["attack"]) - 1:
                new_animation = "attack"
            else:
                self.attacking = False
                new_animation = "idle"
        elif self.blocking:
            new_animation = "block"
        elif self.jumping:
            new_animation = "jump"
        elif abs(self.vel_x) > 0.5:
            new_animation = "walk"
        else:
            new_animation = "idle"
        
        # Changer d'animation si nécessaire
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.animation_frame = 0
            self.animation_time = 0
        
        # Mettre à jour l'image de l'animation
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animations[self.current_animation])
    
    def move(self, direction):
        if self.stun_time > 0 or self.blocking:
            return
        
        self.direction = direction
        self.vel_x = direction * self.fighter_type.speed
    
    def stop(self):
        self.vel_x = 0
    
    def jump(self):
        if not self.jumping and self.stun_time <= 0 and not self.blocking:
            self.vel_y = -self.fighter_type.jump_power
            self.jumping = True
            if self.sounds_loaded:
                self.jump_sound.play()
    
    def attack(self):
        if not self.attacking and not self.jumping and self.stun_time <= 0 and not self.blocking and self.attack_cooldown <= 0:
            self.attacking = True
            self.current_animation = "attack"
            self.animation_frame = 0
            self.animation_time = 0
            if self.sounds_loaded:
                self.attack_sound.play()
    
    def special_attack(self):
        if not self.attacking and self.stun_time <= 0 and not self.blocking and self.special_cooldown <= 0 and self.stamina >= 30:
            self.attacking = True
            self.current_animation = "special"
            self.animation_frame = 0
            self.animation_time = 0
            self.stamina -= 30
            self.special_cooldown = 2.0
            if self.sounds_loaded:
                self.special_sound.play()
    
    def block(self, is_blocking):
        if self.stun_time <= 0 and not self.attacking and not self.jumping:
            self.blocking = is_blocking
            if is_blocking:
                self.vel_x = 0
    
    def take_hit(self, damage, direction):
        if self.hit_cooldown <= 0:
            if self.blocking:
                # Réduire les dégâts si le joueur bloque
                damage *= 0.3
                self.stamina -= damage * 0.5
                if self.stamina < 0:
                    self.stamina = 0
                    self.blocking = False
                    self.stun_time = 0.5
            else:
                self.health -= damage
                self.stun_time = 0.3
                self.knockback = direction * 5
            
            self.hit_cooldown = 0.5
            if self.sounds_loaded:
                self.hit_sound.play()
    
    def check_hit(self, opponent):
        # Créer un rectangle pour la zone d'attaque
        attack_width = 50
        attack_x = self.pos_x + self.width if self.direction > 0 else self.pos_x - attack_width
        attack_rect = pygame.Rect(attack_x, self.pos_y, attack_width, self.height)
        
        # Vérifier si la zone d'attaque touche l'adversaire
        return attack_rect.colliderect(opponent.rect)
    
    def draw(self, screen):
        current_frame = self.animations[self.current_animation][self.animation_frame]
        
        # Retourner l'image si le personnage regarde à gauche
        if self.direction < 0:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        screen.blit(current_frame, (self.pos_x, self.pos_y))
        
        # Dessiner la barre de vie
        health_width = 100
        health_height = 10
        health_x = self.pos_x + (self.width - health_width) / 2
        health_y = self.pos_y - 20
        
        # Fond de la barre de vie
        pygame.draw.rect(screen, (50, 50, 50), (health_x, health_y, health_width, health_height))
        
        # Barre de vie
        health_percent = max(0, self.health / 100)
        pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width * health_percent, health_height))
        
        # Dessiner la barre de stamina
        stamina_width = 80
        stamina_height = 5
        stamina_x = self.pos_x + (self.width - stamina_width) / 2
        stamina_y = self.pos_y - 8
        
        # Fond de la barre de stamina
        pygame.draw.rect(screen, (50, 50, 50), (stamina_x, stamina_y, stamina_width, stamina_height))
        
        # Barre de stamina
        stamina_percent = max(0, self.stamina / self.max_stamina)
        pygame.draw.rect(screen, (0, 255, 255), (stamina_x, stamina_y, stamina_width * stamina_percent, stamina_height))

class MultiplayerGame:
    def __init__(self, player_name="Player", fighter_type="Mitsu", room_id=None):
        self.player_name = player_name
        self.fighter_type = fighter_type
        self.room_id = room_id
        self.is_host = room_id is None
        self.mp_manager = MultiplayerManager()
        self.connected = False
        self.opponent_fighter = None
        self.host_uuid = None
        self.status_message = ""
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        pygame.display.set_caption("PythFighter - Multijoueur")
        
        # Identifiants uniques
        self.client_id = str(uuid.uuid4())
        self.player_name = player_name
        self.fighter_type = fighter_type
        self.room_id = room_id
        self.is_host = room_id is None
        
        # Informations réseau
        self.server_connected = False
        self.opponent_connected = False
        self.last_sync_time = 0
        self.sync_interval = 0.05  # 50ms
        self.ping = 0
        self.last_ping_time = 0
        
        # Démarrer les threads réseau
        self.running = True
        self.network_thread = threading.Thread(target=self._network_loop)
        self.network_thread.daemon = True
        self.network_thread.start()
        
        self.ping_thread = threading.Thread(target=self._ping_loop)
        self.ping_thread.daemon = True
        self.ping_thread.start()
        
        # Charger le fond
        random.seed(time.time()*time.time())
        self.bg_selected = random.choice(["bg_2.png", "backg.png", "bgtree.png", "bg-ile.png", "bgjoconde.png", "bgmatrix.png", "jard.png"])
        
        try:
            bg_path = os.path.join("src", "assets", "backgrounds", self.bg_selected)
            self.bg_image = pygame.image.load(bg_path).convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
            logging.info(f"Background image loaded successfully: {bg_path}")
        except Exception as e:
            logging.error(f"Error loading background image: {e}")
            self.bg_image = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT))
            self.bg_image.fill((50, 50, 80))
        
        self.ground_y = VISIBLE_HEIGHT - 91 if self.bg_selected == "backg.png" else VISIBLE_HEIGHT - 98
        
        # Initialiser les combattants
        fighter_map = {
            "Mitsu": Mitsu,
            "Tank": Tank,
            "Noya": Noya,
            "ThunderStrike": ThunderStrike,
            "Bruiser": Bruiser
        }
        
        fighter_height = VISIBLE_HEIGHT // 5
        
        if fighter_type not in fighter_map:
            logging.warning(f"Invalid fighter type: {fighter_type}, defaulting to Mitsu")
            fighter_type = "Mitsu"
        
        # Créer les combattants (local et distant)
        self.local_fighter = Fighter(1, VISIBLE_WIDTH // 4 - 75, self.ground_y - fighter_height,
                                    fighter_map[fighter_type](), self.ground_y)
        self.remote_fighter = Fighter(2, VISIBLE_WIDTH * 3 // 4 - 75, self.ground_y - fighter_height,
                                     fighter_map["Tank"](), self.ground_y)  # Type par défaut, sera mis à jour
        
        self.fighters = [self.local_fighter, self.remote_fighter]
        
        # Initialiser les contrôleurs
        self.controllers = []
        for i in range(min(1, pygame.joystick.get_count())):  # Un seul contrôleur en multijoueur
            try:
                joy = pygame.joystick.Joystick(i)
                joy.init()
                self.controllers.append(joy)
                logging.info(f"Controller {i} initialized with {joy.get_numaxes()} axes and {joy.get_numbuttons()} buttons.")
            except Exception as e:
                logging.error(f"Error initializing controller {i}: {e}")
        
        # État du jeu
        self.game_state = GameState.WAITING
        self.start_time = time.time()
        self.game_start_time = None
        self.round_time = 99
        self.font = pygame.font.Font(None, 36)
        self.winner = None
        
        # Interface
        self.menu_options = ["Resume", "Quit"]
        self.selected_option = 0
        
        # Sons
        try:
            pygame.mixer.init()
            self.hit_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "hit.wav"))
            self.victory_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "victory.wav"))
            self.menu_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "menu.wav"))
            self.sounds_loaded = True
            logging.info("Sounds loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load sound effects: {e}")
            self.sounds_loaded = False
            self.hit_sound = None
            self.victory_sound = None
            self.menu_sound = None
        
        # Se connecter au serveur
        self._connect_to_server()
    
    def _connect_to_server(self):
        """Établit la connexion avec le serveur."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                # Créer ou rejoindre une salle
                if self.is_host:
                    created_room = self.mp_manager.create_room(self.player_name, self.fighter_type)
                    if created_room:
                        self.room_id = created_room
                        self.connected = True
                        self.status_message = f"Salle créée avec succès. ID: {self.room_id}"
                    else:
                        self.status_message = "Erreur lors de la création de la salle."
                else:
                    joined = self.mp_manager.join_room(self.room_id, self.player_name, self.fighter_type)
                    if joined:
                        self.connected = True
                        self.status_message = f"Connecté à la salle {self.room_id}"
                    else:
                        self.status_message = "Salle non trouvée ou erreur de connexion."
                
                data = {
                    "action": "JOIN_ROOM",
                    "room_id": self.room_id,
                    "client_id": self.client_id,
                    "player_name": self.player_name,
                    "fighter_type": self.fighter_type,
                    "player_uuid": self.client_id  # Utiliser le même UUID pour l'identification
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        self.server_connected = True
                        
                        if self.is_host:
                            self.room_id = response_data.get("room_id")
                            logging.info(f"Room created with ID: {self.room_id}")
                        else:
                            # Mettre à jour le type de combattant de l'adversaire
                            opponent_fighter = response_data.get("host_fighter_type", "Tank")
                            host_uuid = response_data.get("host_uuid")
                            self._update_opponent_fighter(opponent_fighter)
                            logging.info(f"Joined room {self.room_id} with opponent fighter: {opponent_fighter} (UUID: {host_uuid})")
                        
                        # Indiquer que le joueur est prêt
                        self._set_ready(True)
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logging.error(f"Failed to connect to server: {error_msg}")
                except json.JSONDecodeError:
                    logging.error(f"Invalid server response: {response}")
        except Exception as e:
            logging.error(f"Connection error: {e}")
    
    def _update_opponent_fighter(self, fighter_type):
        """Met à jour le type de combattant de l'adversaire."""
        fighter_map = {
            "Mitsu": Mitsu,
            "Tank": Tank,
            "Noya": Noya,
            "ThunderStrike": ThunderStrike,
            "Bruiser": Bruiser
        }
        
        if fighter_type in fighter_map:
            fighter_height = VISIBLE_HEIGHT // 5
            self.remote_fighter = Fighter(2, VISIBLE_WIDTH * 3 // 4 - 75, self.ground_y - fighter_height,
                                         fighter_map[fighter_type](), self.ground_y)
            self.fighters[1] = self.remote_fighter
    
    def _set_ready(self, ready=True):
        """Indique au serveur que le joueur est prêt."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "SET_READY",
                    "room_id": self.room_id,
                    "client_id": self.client_id,
                    "ready": ready
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        logging.info(f"Player ready status set to {ready}")
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logging.error(f"Failed to set ready status: {error_msg}")
                except json.JSONDecodeError:
                    logging.error(f"Invalid server response: {response}")
        except Exception as e:
            logging.error(f"Connection error when setting ready status: {e}")
    
    def _check_opponent_ready(self):
        """Vérifie si l'adversaire est prêt."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "CHECK_OPPONENT_READY",
                    "room_id": self.room_id,
                    "client_id": self.client_id
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        return response_data.get("ready", False)
                except json.JSONDecodeError:
                    logging.error(f"Invalid server response: {response}")
            
            return False
        except Exception as e:
            logging.error(f"Connection error when checking opponent ready: {e}")
            return False
    
    def _send_game_state(self):
        """Envoie l'état du jeu au serveur."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                # Préparer les données d'état du jeu
                game_state = {
                    "position": {
                        "x": self.local_fighter.pos_x,
                        "y": self.local_fighter.pos_y
                    },
                    "velocity": {
                        "x": self.local_fighter.vel_x,
                        "y": self.local_fighter.vel_y
                    },
                    "health": self.local_fighter.health,
                    "stamina": self.local_fighter.stamina,
                    "direction": self.local_fighter.direction,
                    "animation": self.local_fighter.current_animation,
                    "animation_frame": self.local_fighter.animation_frame,
                    "attacking": self.local_fighter.attacking,
                    "blocking": self.local_fighter.blocking,
                    "jumping": self.local_fighter.jumping
                }
                
                data = {
                    "action": "UPDATE_STATE",
                    "room_id": self.room_id,
                    "client_id": self.client_id,
                    "game_state": game_state
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") != "success":
                        error_msg = response_data.get("message", "Unknown error")
                        logging.error(f"Failed to send game state: {error_msg}")
                except json.JSONDecodeError:
                    logging.error(f"Invalid server response: {response}")
        except Exception as e:
            logging.error(f"Connection error when sending game state: {e}")
    
    def _get_opponent_state(self):
        """Récupère l'état du jeu de l'adversaire."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "GET_OPPONENT_STATE",
                    "room_id": self.room_id,
                    "client_id": self.client_id,
                    "player_uuid": self.client_id  # Ajouter l'UUID pour cohérence
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        opponent_state = response_data.get("opponent_state")
                        if opponent_state:
                            self.opponent_connected = True
                            logging.info(f"État de l'adversaire reçu: {opponent_state.get('health', 'N/A')} PV")
                            return opponent_state
                        else:
                            logging.info("Aucun état d'adversaire disponible")
                    else:
                        error_msg = response_data.get("message", "Erreur inconnue")
                        logging.error(f"Échec de récupération de l'état de l'adversaire: {error_msg}")
                except json.JSONDecodeError:
                    logging.error(f"Réponse serveur invalide: {response}")
            
            return None
        except Exception as e:
            logging.error(f"Erreur de connexion lors de la récupération de l'état de l'adversaire: {e}")
            return None
    
    def _update_remote_fighter(self, state):
        """Met à jour l'état du combattant distant."""
        if not state:
            return
        
        if "position" in state:
            self.remote_fighter.pos_x = state["position"]["x"]
            self.remote_fighter.pos_y = state["position"]["y"]
        
        if "velocity" in state:
            self.remote_fighter.vel_x = state["velocity"]["x"]
            self.remote_fighter.vel_y = state["velocity"]["y"]
        
        if "health" in state:
            self.remote_fighter.health = state["health"]
        
        if "stamina" in state:
            self.remote_fighter.stamina = state["stamina"]
        
        if "direction" in state:
            self.remote_fighter.direction = state["direction"]
        
        if "animation" in state:
            self.remote_fighter.current_animation = state["animation"]
        
        if "animation_frame" in state:
            self.remote_fighter.animation_frame = state["animation_frame"]
        
        if "attacking" in state:
            self.remote_fighter.attacking = state["attacking"]
        
        if "blocking" in state:
            self.remote_fighter.blocking = state["blocking"]
        
        if "jumping" in state:
            self.remote_fighter.jumping = state["jumping"]
        
        # Mettre à jour le rectangle de collision
        self.remote_fighter.rect.x = int(self.remote_fighter.pos_x)
        self.remote_fighter.rect.y = int(self.remote_fighter.pos_y)
    
    def _network_loop(self):
        """Boucle principale pour la communication réseau."""
        while self.running:
            try:
                # Vérifier si l'adversaire est prêt
                if self.game_state == GameState.WAITING:
                    opponent_ready = self._check_opponent_ready()
                    logging.info(f"Vérification si l'adversaire est prêt: {opponent_ready}")
                    if opponent_ready:
                        self.game_state = GameState.COUNTDOWN
                        self.start_time = time.time()
                        self.opponent_connected = True
                        logging.info(f"Adversaire prêt! Début du compte à rebours.")
                    else:
                        # Attendre un peu avant de vérifier à nouveau
                        time.sleep(1)
                
                # Synchroniser l'état du jeu
                if self.game_state in [GameState.COUNTDOWN, GameState.PLAYING]:
                    current_time = time.time()
                    
                    if current_time - self.last_sync_time >= self.sync_interval:
                        # Envoyer l'état local
                        self._send_game_state()
                        
                        # Récupérer l'état de l'adversaire
                        opponent_state = self._get_opponent_state()
                        if opponent_state:
                            self._update_remote_fighter(opponent_state)
                            if not self.opponent_connected:
                                self.opponent_connected = True
                                logging.info("Connexion avec l'adversaire établie")
                        
                        self.last_sync_time = current_time
            except Exception as e:
                logging.error(f"Erreur dans la boucle réseau: {e}")
                # Ne pas déconnecter immédiatement, essayer de se reconnecter
                time.sleep(1)
    
    def _set_ready(self, ready=True):
        """Indique au serveur que le joueur est prêt."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "SET_READY",
                    "room_id": self.room_id,
                    "client_id": self.client_id,
                    "player_uuid": self.client_id,  # Ajouter l'UUID pour cohérence
                    "ready": ready
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        logging.info(f"Statut 'prêt' défini à {ready}")
                        # Vérifier immédiatement si l'adversaire est prêt
                        if ready:
                            time.sleep(0.5)  # Petit délai pour laisser le serveur traiter
                            opponent_ready = self._check_opponent_ready()
                            logging.info(f"Vérification immédiate si l'adversaire est prêt: {opponent_ready}")
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logging.error(f"Échec de définition du statut 'prêt': {error_msg}")
                except json.JSONDecodeError:
                    logging.error(f"Réponse serveur invalide: {response}")
        except Exception as e:
            logging.error(f"Erreur de connexion dans set_ready: {e}")
            # Réessayer après un court délai
            time.sleep(1)
            self._set_ready(ready)
    
    def _check_opponent_ready(self):
        """Vérifie si l'adversaire est prêt."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "CHECK_OPPONENT_READY",
                    "room_id": self.room_id,
                    "client_id": self.client_id
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        # Correction: utiliser la clé correcte 'opponent_ready' au lieu de 'ready'
                        return response_data.get("opponent_ready", False)
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logging.error(f"Failed to check opponent ready: {error_msg}")
                except json.JSONDecodeError:
                    logging.error(f"Invalid server response: {response}")
            
            return False
        except Exception as e:
            logging.error(f"Connection error in check_opponent_ready: {e}")
            return False
    
    def _network_loop(self):
        """Boucle principale pour la synchronisation réseau."""
        while self.running:
            try:
                # Vérifier si l'adversaire est connecté
                if self.server_connected and not self.opponent_connected:
                    opponent_ready = self._check_opponent_ready()
                    logging.info(f"Vérification si l'adversaire est prêt: {opponent_ready}")
                    if opponent_ready:
                        self.opponent_connected = True
                        self.game_state = GameState.COUNTDOWN
                        self.start_time = time.time()
                        logging.info(f"Adversaire prêt! Début du compte à rebours.")
                    else:
                        # Attendre un peu avant de vérifier à nouveau
                        time.sleep(1)
                        logging.info("Opponent connected and ready, starting countdown")
                
                # Synchroniser l'état du jeu
                if self.server_connected and self.opponent_connected and self.game_state == GameState.PLAYING:
                    current_time = time.time()
                    if current_time - self.last_sync_time >= self.sync_interval:
                        self._sync_game_state()
                        self.last_sync_time = current_time
                
                time.sleep(0.1)  # Éviter de surcharger le CPU
            except Exception as e:
                logging.error(f"Error in network loop: {e}")
                time.sleep(1)  # Attendre avant de réessayer
    
    def _ping_loop(self):
        """Boucle pour mesurer la latence avec le serveur."""
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    start_time = time.time()
                    s.connect((SERVER_HOST, PING_PORT))
                    s.sendall(b"PING")
                    response = s.recv(1024)
                    if response == b"PONG":
                        self.ping = int((time.time() - start_time) * 1000)  # en ms
                        self.last_ping_time = time.time()
            except Exception as e:
                logging.debug(f"Ping error: {e}")
            
            time.sleep(2)  # Ping toutes les 2 secondes
    
    def _sync_game_state(self):
        """Synchronise l'état du jeu avec le serveur."""
        try:
            # Envoyer l'état du joueur local
            local_state = {
                "pos_x": self.local_fighter.pos_x,
                "pos_y": self.local_fighter.pos_y,
                "vel_x": self.local_fighter.vel_x,
                "vel_y": self.local_fighter.vel_y,
                "health": self.local_fighter.health,
                "stamina": self.local_fighter.stamina,
                "direction": self.local_fighter.direction,
                "animation": self.local_fighter.current_animation,
                "frame": self.local_fighter.animation_frame
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "UPDATE_STATE",
                    "room_id": self.room_id,
                    "client_id": self.client_id,
                    "game_state": local_state
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                s.recv(1024)  # Attendre la confirmation
            
            # Récupérer l'état de l'adversaire
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "GET_OPPONENT_STATE",
                    "room_id": self.room_id,
                    "client_id": self.client_id
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        opponent_state = response_data.get("opponent_state", {})
                        if opponent_state:
                            self._update_remote_fighter(opponent_state)
                except json.JSONDecodeError:
                    logging.error(f"Invalid server response: {response}")
        
        except Exception as e:
            logging.error(f"Error syncing game state: {e}")
    
    def _update_remote_fighter(self, state):
        """Met à jour l'état du combattant distant."""
        if not state:
            return
        
        self.remote_fighter.pos_x = state.get("pos_x", self.remote_fighter.pos_x)
        self.remote_fighter.pos_y = state.get("pos_y", self.remote_fighter.pos_y)
        self.remote_fighter.vel_x = state.get("vel_x", self.remote_fighter.vel_x)
        self.remote_fighter.vel_y = state.get("vel_y", self.remote_fighter.vel_y)
        self.remote_fighter.health = state.get("health", self.remote_fighter.health)
        self.remote_fighter.stamina = state.get("stamina", self.remote_fighter.stamina)
        self.remote_fighter.direction = state.get("direction", self.remote_fighter.direction)
        
        # Mettre à jour l'animation
        new_animation = state.get("animation")
        if new_animation and new_animation != self.remote_fighter.current_animation:
            self.remote_fighter.current_animation = new_animation
            self.remote_fighter.animation_frame = 0
            self.remote_fighter.animation_time = 0
        
        # Mettre à jour le rectangle de collision
        self.remote_fighter.rect.x = int(self.remote_fighter.pos_x)
        self.remote_fighter.rect.y = int(self.remote_fighter.pos_y)
    
    def run(self):
        """Boucle principale du jeu."""
        clock = pygame.time.Clock()
        last_time = time.time()
        
        while self.running:
            # Calculer le delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == GameState.PLAYING:
                            self.game_state = GameState.PAUSED
                        elif self.game_state == GameState.PAUSED:
                            self.game_state = GameState.PLAYING
                    
                    # Contrôles clavier
                    if self.game_state == GameState.PLAYING:
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            self.local_fighter.jump()
                        elif event.key == pygame.K_j:
                            self.local_fighter.attack()
                        elif event.key == pygame.K_k:
                            self.local_fighter.special_attack()
                        elif event.key == pygame.K_l:
                            self.local_fighter.block(True)
                
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_l:
                        self.local_fighter.block(False)
            
            # Contrôles continus du clavier
            if self.game_state == GameState.PLAYING:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.local_fighter.move(-1)
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.local_fighter.move(1)
                else:
                    self.local_fighter.stop()
            
            # Contrôles manette
            if self.controllers and self.game_state == GameState.PLAYING:
                joy = self.controllers[0]
                
                # Mouvement
                x_axis = joy.get_axis(0)
                if abs(x_axis) > 0.2:
                    self.local_fighter.move(1 if x_axis > 0 else -1)
                else:
                    self.local_fighter.stop()
                
                # Boutons
                if joy.get_button(0):  # A - Saut
                    self.local_fighter.jump()
                if joy.get_button(1):  # B - Attaque
                    self.local_fighter.attack()
                if joy.get_button(2):  # X - Attaque spéciale
                    self.local_fighter.special_attack()
                if joy.get_button(3):  # Y - Blocage
                    self.local_fighter.block(True)
                else:
                    self.local_fighter.block(False)
                
                # Pause
                if joy.get_button(7):  # Start
                    if self.game_state == GameState.PLAYING:
                        self.game_state = GameState.PAUSED
                    elif self.game_state == GameState.PAUSED:
                        self.game_state = GameState.PLAYING
            
            # Mettre à jour l'état du jeu
            if self.game_state == GameState.WAITING:
                # Attendre que l'adversaire se connecte
                pass
            
            elif self.game_state == GameState.COUNTDOWN:
                # Compte à rebours avant le début du combat
                elapsed = current_time - self.start_time
                if elapsed >= 3:  # 3 secondes de compte à rebours
                    self.game_state = GameState.PLAYING
                    self.game_start_time = current_time
            
            elif self.game_state == GameState.PLAYING:
                # Mettre à jour les combattants
                self.local_fighter.update(dt, self.remote_fighter)
                
                # Vérifier les conditions de victoire
                if self.local_fighter.health <= 0:
                    self.game_state = GameState.DEFEAT
                    self.winner = self.remote_fighter
                    if self.sounds_loaded:
                        self.victory_sound.play()
                
                elif self.remote_fighter.health <= 0:
                    self.game_state = GameState.VICTORY
                    self.winner = self.local_fighter
                    if self.sounds_loaded:
                        self.victory_sound.play()
                
                # Mettre à jour le temps restant
                if self.game_start_time:
                    elapsed = current_time - self.game_start_time
                    remaining = max(0, self.round_time - int(elapsed))
                    
                    if remaining == 0:
                        # Match nul ou victoire au temps
                        if self.local_fighter.health > self.remote_fighter.health:
                            self.game_state = GameState.VICTORY
                            self.winner = self.local_fighter
                        elif self.local_fighter.health < self.remote_fighter.health:
                            self.game_state = GameState.DEFEAT
                            self.winner = self.remote_fighter
                        else:
                            # Match nul
                            self.game_state = GameState.VICTORY  # On considère un match nul comme une victoire
                            self.winner = self.local_fighter
                        
                        if self.sounds_loaded:
                            self.victory_sound.play()
            
            elif self.game_state == GameState.PAUSED:
                # Menu pause
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_UP] and not self.button_pressed:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    self.button_pressed = True
                    if self.sounds_loaded:
                        self.menu_sound.play()
                
                elif keys[pygame.K_DOWN] and not self.button_pressed:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    self.button_pressed = True
                    if self.sounds_loaded:
                        self.menu_sound.play()
                
                elif keys[pygame.K_RETURN] and not self.button_pressed:
                    self.button_pressed = True
                    
                    if self.menu_options[self.selected_option] == "Resume":
                        self.game_state = GameState.PLAYING
                    elif self.menu_options[self.selected_option] == "Quit":
                        self.running = False
                
                else:
                    self.button_pressed = False
            
            # Dessiner l'écran
            self.screen.blit(self.bg_image, (0, 0))
            
            if self.game_state == GameState.WAITING:
                # Afficher un message d'attente
                waiting_text = self.font.render("En attente d'un adversaire...", True, (255, 255, 255))
                room_text = self.font.render(f"ID de salle: {self.room_id}", True, (255, 255, 255))
                
                self.screen.blit(waiting_text, (VISIBLE_WIDTH // 2 - waiting_text.get_width() // 2, VISIBLE_HEIGHT // 2))
                self.screen.blit(room_text, (VISIBLE_WIDTH // 2 - room_text.get_width() // 2, VISIBLE_HEIGHT // 2 + 40))
            
            elif self.game_state == GameState.COUNTDOWN:
                # Afficher le compte à rebours
                elapsed = current_time - self.start_time
                count = 3 - int(elapsed)
                
                count_text = self.font.render(str(count), True, (255, 255, 255))
                self.screen.blit(count_text, (VISIBLE_WIDTH // 2 - count_text.get_width() // 2, VISIBLE_HEIGHT // 2))
                
                # Dessiner les combattants
                self.local_fighter.draw(self.screen)
                self.remote_fighter.draw(self.screen)
            
            elif self.game_state in [GameState.PLAYING, GameState.PAUSED, GameState.VICTORY, GameState.DEFEAT]:
                # Dessiner les combattants
                self.local_fighter.draw(self.screen)
                self.remote_fighter.draw(self.screen)
                
                # Afficher le temps restant
                if self.game_start_time:
                    elapsed = current_time - self.game_start_time
                    remaining = max(0, self.round_time - int(elapsed))
                    time_text = self.font.render(f"{remaining}", True, (255, 255, 255))
                    self.screen.blit(time_text, (VISIBLE_WIDTH // 2 - time_text.get_width() // 2, 20))
                
                # Afficher le ping
                ping_text = self.font.render(f"Ping: {self.ping} ms", True, (200, 200, 200))
                self.screen.blit(ping_text, (10, 10))
                
                # Menu pause
                if self.game_state == GameState.PAUSED:
                    # Fond semi-transparent
                    overlay = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128))
                    self.screen.blit(overlay, (0, 0))
                    
                    # Titre
                    pause_text = self.font.render("PAUSE", True, (255, 255, 255))
                    self.screen.blit(pause_text, (VISIBLE_WIDTH // 2 - pause_text.get_width() // 2, VISIBLE_HEIGHT // 3))
                    
                    # Options
                    for i, option in enumerate(self.menu_options):
                        color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                        option_text = self.font.render(option, True, color)
                        self.screen.blit(option_text, (VISIBLE_WIDTH // 2 - option_text.get_width() // 2, VISIBLE_HEIGHT // 2 + i * 40))
                
                # Écran de victoire/défaite
                elif self.game_state in [GameState.VICTORY, GameState.DEFEAT]:
                    # Fond semi-transparent
                    overlay = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128))
                    self.screen.blit(overlay, (0, 0))
                    
                    # Message
                    result_text = self.font.render("VICTOIRE !" if self.game_state == GameState.VICTORY else "DÉFAITE...", True, (255, 255, 0) if self.game_state == GameState.VICTORY else (255, 0, 0))
                    self.screen.blit(result_text, (VISIBLE_WIDTH // 2 - result_text.get_width() // 2, VISIBLE_HEIGHT // 3))
                    
                    # Instructions
                    instr_text = self.font.render("Appuyez sur ÉCHAP pour quitter", True, (255, 255, 255))
                    self.screen.blit(instr_text, (VISIBLE_WIDTH // 2 - instr_text.get_width() // 2, VISIBLE_HEIGHT * 2 // 3))
            
            pygame.display.flip()
            clock.tick(60)
        
        # Nettoyer avant de quitter
        self._leave_room()
        pygame.quit()
    
    def _leave_room(self):
        """Quitte la salle de jeu."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                
                data = {
                    "action": "LEAVE_ROOM",
                    "room_id": self.room_id,
                    "client_id": self.client_id
                }
                
                s.sendall(json.dumps(data).encode('utf-8'))
                s.recv(1024)  # Attendre la confirmation
                
                logging.info(f"Left room {self.room_id}")
        except Exception as e:
            logging.error(f"Error leaving room: {e}")

# Fonction principale pour lancer le jeu
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="PythFighter - Mode Multijoueur")
    parser.add_argument("--name", default="Joueur", help="Nom du joueur")
    parser.add_argument("--fighter", default="Mitsu", help="Type de combattant")
    parser.add_argument("--room", help="ID de la salle à rejoindre")
    
    args = parser.parse_args()
    
    game = MultiplayerGame(player_name=args.name, fighter_type=args.fighter, room_id=args.room)
    game.run()

if __name__ == "__main__":
    main()