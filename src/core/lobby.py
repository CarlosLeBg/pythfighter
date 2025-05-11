import pygame
import sys
import os
import random
import json
import time
import uuid
from math import sin, cos
import socket
import threading

# Ajouter le chemin du projet au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import GameSettings
from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser
from core.game_multi import MultiplayerGame

# Configuration
SETTINGS = GameSettings()
SCREEN_WIDTH = SETTINGS.SCREEN_WIDTH
SCREEN_HEIGHT = SETTINGS.SCREEN_HEIGHT

# Couleurs
BLUE = (0, 120, 255)
LIGHT_BLUE = (0, 180, 255)
DARK_BLUE = (0, 60, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
LIGHT_GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Configuration du serveur
SERVER_HOST = '194.9.172.146'
SERVER_PORT = 25568

# Fichier pour stocker les données du joueur
PLAYER_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "player_data.json")

class WaterEffect:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0
        self.wave_height = 20
        self.wave_length = 0.02
        self.wave_speed = 0.05
        self.water_color = BLUE
        self.water_alpha = 180
        self.water_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
    def update(self):
        self.time += self.wave_speed
        
    def draw(self, screen, y_position):
        self.water_surface.fill((0, 0, 0, 0))
        
        # Dessiner l'eau avec un effet de vague
        points = []
        for x in range(0, self.width + 10, 10):
            y = sin(self.time + x * self.wave_length) * self.wave_height
            points.append((x, y + 50))
        
        # Ajouter les points du bas pour fermer le polygone
        points.append((self.width, self.height))
        points.append((0, self.height))
        
        # Dessiner le polygone d'eau
        pygame.draw.polygon(self.water_surface, (*self.water_color, self.water_alpha), points)
        
        # Ajouter des reflets
        for i in range(10):
            x = random.randint(0, self.width)
            y = random.randint(50, 150)
            size = random.randint(2, 5)
            pygame.draw.circle(self.water_surface, (255, 255, 255, 100), (x, y), size)
        
        screen.blit(self.water_surface, (0, y_position))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(1, 3)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-2, -0.5)
        self.lifetime = random.uniform(30, 60)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size *= 0.98
        
    def draw(self, screen):
        alpha = min(255, self.lifetime * 4)
        pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))

class CharacterDisplay:
    def __init__(self, fighter_type="Mitsu"):
        self.fighter_type = fighter_type
        self.animations = {}
        self.current_frame = 0
        self.animation_time = 0
        self.animation_speed = 0.1
        self.width = 300
        self.height = 300
        self.load_animations()
        
    def load_animations(self):
        # Charger les animations du personnage
        self.animations = {
            "idle": self._load_animation("idle", 4)
        }
        
    def _load_animation(self, animation_name, frames):
        animation_frames = []
        for i in range(frames):
            frame_path = os.path.join("src", "assets", "fighters", self.fighter_type.lower(), f"{animation_name}_{i+1}.png")
            try:
                if os.path.exists(frame_path):
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frame = pygame.transform.scale(frame, (self.width, self.height))
                    animation_frames.append(frame)
                else:
                    # Image de remplacement
                    fallback = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    fallback.fill((255, 0, 255, 128))
                    animation_frames.append(fallback)
            except Exception as e:
                print(f"Erreur lors du chargement de l'animation: {e}")
                fallback = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                fallback.fill((255, 0, 255, 128))
                animation_frames.append(fallback)
        return animation_frames
    
    def update(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations["idle"])
    
    def draw(self, screen, x, y):
        if "idle" in self.animations and self.animations["idle"]:
            screen.blit(self.animations["idle"][self.current_frame], (x - self.width // 2, y - self.height))

class LobbyScreen:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Configurer l'écran
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PythFighter - Lobby Multijoueur")
        
        # Charger les polices
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 48)
        self.normal_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Charger le fond
        try:
            bg_path = os.path.join("src", "assets", "backgrounds", "lobby_bg.png")
            if os.path.exists(bg_path):
                self.bg_image = pygame.image.load(bg_path).convert_alpha()
                self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.bg_image.fill((30, 30, 50))
        except Exception as e:
            print(f"Erreur lors du chargement du fond: {e}")
            self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_image.fill((30, 30, 50))
        
        # Initialiser les effets
        self.water_effect = WaterEffect(SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        self.particles = []
        
        # Initialiser le personnage
        self.character = CharacterDisplay("Mitsu")
        
        # Variables pour l'interface
        self.input_box = pygame.Rect(SCREEN_WIDTH - 400, SCREEN_HEIGHT - 200, 300, 40)
        self.input_text = ""
        self.input_active = False
        self.error_message = ""
        self.success_message = ""
        self.message_time = 0
        
        # Boutons
        self.create_button = pygame.Rect(SCREEN_WIDTH - 400, SCREEN_HEIGHT - 140, 140, 50)
        self.join_button = pygame.Rect(SCREEN_WIDTH - 230, SCREEN_HEIGHT - 140, 140, 50)
        
        # Données du joueur
        self.player_name = self.load_player_data().get("name", "")
        if not self.player_name:
            self.player_name = f"Joueur{random.randint(1000, 9999)}"
            self.save_player_data({"name": self.player_name})
        
        # Sélection du personnage
        self.fighters = ["Mitsu", "Tank", "Noya", "ThunderStrike", "Bruiser"]
        self.selected_fighter = "Mitsu"
        self.fighter_buttons = []
        for i, fighter in enumerate(self.fighters):
            self.fighter_buttons.append(pygame.Rect(SCREEN_WIDTH - 400 + i * 60, SCREEN_HEIGHT - 80, 50, 50))
        
        # Horloge pour le timing
        self.clock = pygame.time.Clock()
        self.running = True
    
    def load_player_data(self):
        """Charge les données du joueur depuis le fichier"""
        if os.path.exists(PLAYER_DATA_FILE):
            try:
                with open(PLAYER_DATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des données du joueur: {e}")
        return {}
    
    def save_player_data(self, data):
        """Sauvegarde les données du joueur dans le fichier"""
        try:
            with open(PLAYER_DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données du joueur: {e}")
    
    def create_room(self):
        """Crée une nouvelle salle de jeu"""
        try:
            data = {
                "action": "CREATE_ROOM",
                "player_name": self.player_name,
                "fighter_type": self.selected_fighter
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        room_id = response_data.get("room_id")
                        player_id = response_data.get("player_id")
                        self.success_message = f"Salle créée! ID: {room_id}"
                        self.message_time = time.time()
                        
                        # Lancer le jeu multijoueur
                        game = MultiplayerGame(self.player_name, self.selected_fighter)
                        return True, room_id
                    else:
                        self.error_message = f"Erreur: {response_data.get('message', 'Erreur inconnue')}"
                        self.message_time = time.time()
                except json.JSONDecodeError:
                    self.error_message = "Réponse invalide du serveur"
                    self.message_time = time.time()
        except Exception as e:
            self.error_message = f"Erreur de connexion: {e}"
            self.message_time = time.time()
        
        return False, None
    
    def join_room(self, room_id):
        """Rejoint une salle existante"""
        if not room_id:
            self.error_message = "Veuillez entrer un ID de salle"
            self.message_time = time.time()
            return False
        
        try:
            data = {
                "action": "JOIN_ROOM",
                "room_id": room_id,
                "player_name": self.player_name,
                "fighter_type": self.selected_fighter
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((SERVER_HOST, SERVER_PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        player_id = response_data.get("player_id")
                        self.success_message = f"Salle rejointe avec succès!"
                        self.message_time = time.time()
                        
                        # Lancer le jeu multijoueur
                        game = MultiplayerGame(self.player_name, self.selected_fighter, room_id)
                        return True
                    else:
                        self.error_message = f"Erreur: {response_data.get('message', 'Erreur inconnue')}"
                        self.message_time = time.time()
                except json.JSONDecodeError:
                    self.error_message = "Réponse invalide du serveur"
                    self.message_time = time.time()
        except Exception as e:
            self.error_message = f"Erreur de connexion: {e}"
            self.message_time = time.time()
        
        return False
    
    def run(self):
        """Boucle principale du lobby"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Vérifier si l'utilisateur a cliqué sur la zone de saisie
                    if self.input_box.collidepoint(event.pos):
                        self.input_active = True
                    else:
                        self.input_active = False
                    
                    # Vérifier si l'utilisateur a cliqué sur un bouton
                    if self.create_button.collidepoint(event.pos):
                        success, room_id = self.create_room()
                        if success:
                            self.input_text = room_id
                    
                    elif self.join_button.collidepoint(event.pos):
                        self.join_room(self.input_text)
                    
                    # Vérifier si l'utilisateur a cliqué sur un bouton de personnage
                    for i, button in enumerate(self.fighter_buttons):
                        if button.collidepoint(event.pos) and i < len(self.fighters):
                            self.selected_fighter = self.fighters[i]
                            self.character = CharacterDisplay(self.selected_fighter)
                
                elif event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.join_room(self.input_text)
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            # Limiter la longueur du texte
                            if len(self.input_text) < 20:
                                self.input_text += event.unicode
            
            # Mettre à jour les effets
            self.water_effect.update()
            self.character.update(dt)
            
            # Mettre à jour les particules
            for particle in self.particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.particles.remove(particle)
            
            # Ajouter de nouvelles particules
            if random.random() < 0.1:
                x = random.randint(0, SCREEN_WIDTH)
                y = SCREEN_HEIGHT // 2 + random.randint(0, 100)
                color = (random.randint(0, 100), random.randint(100, 200), random.randint(200, 255))
                self.particles.append(Particle(x, y, color))
            
            # Dessiner l'écran
            self.draw()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
        
        pygame.quit()
    
    def draw(self):
        """Dessine l'interface du lobby"""
        # Dessiner le fond
        self.screen.blit(self.bg_image, (0, 0))
        
        # Dessiner l'eau
        self.water_effect.draw(self.screen, SCREEN_HEIGHT // 2)
        
        # Dessiner les particules
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Dessiner le personnage
        self.character.draw(self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        # Dessiner le titre
        title_text = self.title_font.render("PYTH FIGHTER", True, WHITE)
        subtitle_text = self.subtitle_font.render("Mode Multijoueur", True, LIGHT_BLUE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        self.screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 120))
        
        # Dessiner le panneau de connexion
        panel_rect = pygame.Rect(SCREEN_WIDTH - 450, SCREEN_HEIGHT - 250, 400, 230)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, LIGHT_BLUE, panel_rect, 2, border_radius=10)
        
        # Dessiner le nom du joueur
        name_text = self.normal_font.render(f"Joueur: {self.player_name}", True, WHITE)
        self.screen.blit(name_text, (SCREEN_WIDTH - 430, SCREEN_HEIGHT - 240))
        
        # Dessiner la zone de saisie
        pygame.draw.rect(self.screen, WHITE if self.input_active else LIGHT_GRAY, self.input_box, 2)
        input_label = self.normal_font.render("ID de salle:", True, WHITE)
        self.screen.blit(input_label, (self.input_box.x - 150, self.input_box.y + 10))
        
        # Dessiner le texte de saisie
        input_surface = self.normal_font.render(self.input_text, True, WHITE)
        self.screen.blit(input_surface, (self.input_box.x + 10, self.input_box.y + 10))
        
        # Dessiner les boutons
        pygame.draw.rect(self.screen, GREEN, self.create_button, border_radius=5)
        pygame.draw.rect(self.screen, ORANGE, self.join_button, border_radius=5)
        
        create_text = self.normal_font.render("Créer", True, BLACK)
        join_text = self.normal_font.render("Rejoindre", True, BLACK)
        
        self.screen.blit(create_text, (self.create_button.x + self.create_button.width // 2 - create_text.get_width() // 2, 
                                      self.create_button.y + self.create_button.height // 2 - create_text.get_height() // 2))
        self.screen.blit(join_text, (self.join_button.x + self.join_button.width // 2 - join_text.get_width() // 2, 
                                    self.join_button.y + self.join_button.height // 2 - join_text.get_height() // 2))
        
        # Dessiner les boutons de sélection de personnage
        fighter_label = self.normal_font.render("Personnage:", True, WHITE)
        self.screen.blit(fighter_label, (SCREEN_WIDTH - 430, SCREEN_HEIGHT - 80))
        
        for i, button in enumerate(self.fighter_buttons):
            color = LIGHT_BLUE if self.fighters[i] == self.selected_fighter else GRAY
            pygame.draw.rect(self.screen, color, button, border_radius=5)
            fighter_text = self.small_font.render(self.fighters[i][0], True, WHITE)
            self.screen.blit(fighter_text, (button.x + button.width // 2 - fighter_text.get_width() // 2, 
                                          button.y + button.height // 2 - fighter_text.get_height() // 2))
        
        # Afficher les messages d'erreur ou de succès
        if self.error_message and time.time() - self.message_time < 3:
            error_surface = self.normal_font.render(self.error_message, True, (255, 0, 0))
            self.screen.blit(error_surface, (SCREEN_WIDTH // 2 - error_surface.get_width() // 2, SCREEN_HEIGHT - 50))
        
        if self.success_message and time.time() - self.message_time < 3:
            success_surface = self.normal_font.render(self.success_message, True, (0, 255, 0))
            self.screen.blit(success_surface, (SCREEN_WIDTH // 2 - success_surface.get_width() // 2, SCREEN_HEIGHT - 50))

def main():
    lobby = LobbyScreen()
    lobby.run()

if __name__ == "__main__":
    main()