import pygame
import sys
import os
import json
import random
import math
import socket
import threading
import uuid
from enum import Enum

# Ajout du chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.fighters import Mitsu, Tank, Noya, ThunderStrike, Bruiser
from core.game import Fighter, GameState, VISIBLE_WIDTH, VISIBLE_HEIGHT, load_image

# Constantes - Style Street Fighter
LOBBY_BG_COLOR = (20, 20, 30)  # Bleu foncé
WATER_COLOR = (0, 100, 180)    # Bleu plus profond
WATER_HIGHLIGHT = (80, 180, 255)  # Reflets plus vifs
BUTTON_COLOR = (220, 50, 50)   # Rouge Street Fighter
BUTTON_HOVER_COLOR = (255, 80, 80)  # Rouge plus vif
TEXT_COLOR = (255, 255, 255)   # Blanc pur
TITLE_COLOR = (255, 220, 0)    # Or plus vif
INPUT_BG_COLOR = (40, 40, 60)  # Fond sombre
INPUT_ACTIVE_COLOR = (60, 60, 100)  # Bleu foncé actif

# Fichier pour stocker les données du joueur
PLAYER_DATA_FILE = "player_data.json"

# Ajouter au .gitignore
def update_gitignore():
    gitignore_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".gitignore")
    
    # Créer le fichier s'il n'existe pas
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("player_data.json\n")
        return
    
    # Vérifier si player_data.json est déjà dans .gitignore
    with open(gitignore_path, "r") as f:
        content = f.read()
    
    if "player_data.json" not in content:
        with open(gitignore_path, "a") as f:
            f.write("\n# Données du joueur local\nplayer_data.json\n")

class LobbyState(Enum):
    MAIN_MENU = 0
    CHARACTER_SELECT = 1
    CREATE_ROOM = 2
    JOIN_ROOM = 3
    WAITING_ROOM = 4
    GAME = 5

class WaterEffect:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0
        self.waves = []
        self.generate_waves()
        
    def generate_waves(self):
        self.waves = []
        for i in range(10):
            self.waves.append({
                'amplitude': random.uniform(2, 8),
                'frequency': random.uniform(0.01, 0.05),
                'speed': random.uniform(0.5, 2.0),
                'phase': random.uniform(0, math.pi * 2)
            })
    
    def update(self):
        self.time += 0.016  # ~60fps
        
    def draw(self, surface, y_position):
        # Dessiner le fond de l'eau
        water_rect = pygame.Rect(0, y_position, self.width, self.height - y_position)
        pygame.draw.rect(surface, WATER_COLOR, water_rect)
        
        # Dessiner la surface de l'eau avec des vagues
        points = []
        for x in range(0, self.width + 10, 10):
            y = y_position
            for wave in self.waves:
                y += wave['amplitude'] * math.sin(wave['frequency'] * x + self.time * wave['speed'] + wave['phase'])
            points.append((x, y))
        
        # Ajouter les points du bas pour fermer le polygone
        points.append((self.width, self.height))
        points.append((0, self.height))
        
        # Dessiner le polygone de l'eau
        pygame.draw.polygon(surface, WATER_COLOR, points)
        
        # Dessiner les reflets sur l'eau
        for i in range(len(points) - 3):
            if i % 3 == 0:
                highlight_pos = (points[i][0], points[i][1] + 5)
                pygame.draw.circle(surface, WATER_HIGHLIGHT, highlight_pos, random.randint(1, 3), 1)

class Button:
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=10)
        
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Effet de brillance quand survolé
        if self.hovered:
            glow = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*BUTTON_HOVER_COLOR, 100), 
                            pygame.Rect(5, 5, self.rect.width, self.rect.height), 
                            border_radius=12)
            glow_rect = glow.get_rect(center=self.rect.center)
            surface.blit(glow, (glow_rect.x, glow_rect.y), special_flags=pygame.BLEND_ADD)
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            if self.action:
                return self.action()
        return None

class InputBox:
    def __init__(self, x, y, width, height, font, text='', placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = text
        self.placeholder = placeholder
        self.active = False
        self.color = INPUT_BG_COLOR
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = INPUT_ACTIVE_COLOR if self.active else INPUT_BG_COLOR
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=5)
        
        if self.text:
            text_surf = self.font.render(self.text, True, TEXT_COLOR)
        else:
            text_surf = self.font.render(self.placeholder, True, (150, 150, 150))
            
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)

class Lobby:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        pygame.display.set_caption("PythFighter - Lobby")
        self.clock = pygame.time.Clock()
        
        self.state = LobbyState.MAIN_MENU
        self.water_effect = WaterEffect(VISIBLE_WIDTH, VISIBLE_HEIGHT)
        
        # Chargement des polices
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        
        # Chargement des personnages
        self.available_fighters = [Mitsu, Tank, Noya, ThunderStrike, Bruiser]
        self.selected_fighter_index = 0
        self.selected_fighter = None
        self.fighter_preview = None
        
        # Données du joueur
        self.player_name = ""
        self.load_player_data()
        
        # Données de la salle
        self.room_code = ""
        self.is_host = False
        self.opponent_name = ""
        self.opponent_fighter = None
        
        # Éléments d'interface
        self.buttons = []
        self.input_boxes = []
        self.setup_main_menu()
        
        # Réseau
        self.socket = None
        self.connected = False
        self.server_thread = None
        
        # Mise à jour du .gitignore
        update_gitignore()
        
    def load_player_data(self):
        if os.path.exists(PLAYER_DATA_FILE):
            try:
                with open(PLAYER_DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.player_name = data.get("name", "")
                    fighter_name = data.get("fighter", "")
                    
                    # Trouver l'index du combattant sauvegardé
                    for i, fighter_class in enumerate(self.available_fighters):
                        fighter_instance = fighter_class()
                        if fighter_instance.name == fighter_name:
                            self.selected_fighter_index = i
                            break
            except:
                pass
    
    def save_player_data(self):
        # Instancier la classe du combattant pour obtenir le nom
        fighter_class = self.available_fighters[self.selected_fighter_index]
        fighter_instance = fighter_class()
        fighter_name = fighter_instance.name
        data = {
            "name": self.player_name,
            "fighter": fighter_name
        }
        with open(PLAYER_DATA_FILE, "w") as f:
            json.dump(data, f)
    
    def setup_main_menu(self):
        self.buttons = []
        self.input_boxes = []
        
        # Boutons du menu principal
        center_x = VISIBLE_WIDTH // 2
        button_width = 300
        button_height = 60
        spacing = 20
        
        start_y = VISIBLE_HEIGHT // 2
        
        self.buttons.append(Button(
            center_x - button_width // 2,
            start_y,
            button_width,
            button_height,
            "Sélectionner Personnage",
            self.button_font,
            lambda: self.change_state(LobbyState.CHARACTER_SELECT)
        ))
        
        self.buttons.append(Button(
            center_x - button_width // 2,
            start_y + button_height + spacing,
            button_width,
            button_height,
            "Créer un Salon",
            self.button_font,
            lambda: self.change_state(LobbyState.CREATE_ROOM)
        ))
        
        self.buttons.append(Button(
            center_x - button_width // 2,
            start_y + 2 * (button_height + spacing),
            button_width,
            button_height,
            "Rejoindre un Salon",
            self.button_font,
            lambda: self.change_state(LobbyState.JOIN_ROOM)
        ))
        
        self.buttons.append(Button(
            center_x - button_width // 2,
            start_y + 3 * (button_height + spacing),
            button_width,
            button_height,
            "Quitter",
            self.button_font,
            lambda: sys.exit()
        ))
        
        # Champ de saisie pour le nom du joueur
        name_input = InputBox(
            center_x - button_width // 2,
            start_y - button_height - spacing,
            button_width,
            button_height,
            self.button_font,
            self.player_name,
            "Entrez votre nom"
        )
        self.input_boxes.append(name_input)
    
    def setup_character_select(self):
        self.buttons = []
        
        # Boutons pour naviguer entre les personnages
        self.buttons.append(Button(
            50,
            VISIBLE_HEIGHT // 2,
            80,
            80,
            "<",
            self.subtitle_font,
            self.prev_fighter
        ))
        
        self.buttons.append(Button(
            VISIBLE_WIDTH - 130,
            VISIBLE_HEIGHT // 2,
            80,
            80,
            ">",
            self.subtitle_font,
            self.next_fighter
        ))
        
        # Bouton de confirmation
        self.buttons.append(Button(
            VISIBLE_WIDTH // 2 - 150,
            VISIBLE_HEIGHT - 150,
            300,
            60,
            "Confirmer",
            self.button_font,
            lambda: self.change_state(LobbyState.MAIN_MENU)
        ))
        
        # Bouton retour
        self.buttons.append(Button(
            50,
            50,
            150,
            50,
            "Retour",
            self.button_font,
            lambda: self.change_state(LobbyState.MAIN_MENU)
        ))
        
        # Créer le fighter pour la prévisualisation
        self.update_fighter_preview()
    
    def setup_create_room(self):
        self.buttons = []
        
        # Générer un code de salle aléatoire
        self.room_code = str(uuid.uuid4())[:8].upper()
        self.is_host = True
        
        # Bouton pour démarrer le serveur
        self.buttons.append(Button(
            VISIBLE_WIDTH // 2 - 150,
            VISIBLE_HEIGHT - 150,
            300,
            60,
            "Créer le salon",
            self.button_font,
            self.start_server
        ))
        
        # Bouton retour
        self.buttons.append(Button(
            50,
            50,
            150,
            50,
            "Retour",
            self.button_font,
            lambda: self.change_state(LobbyState.MAIN_MENU)
        ))
    
    def setup_join_room(self):
        self.buttons = []
        self.input_boxes = []
        
        # Champ pour entrer le code de salon
        room_input = InputBox(
            VISIBLE_WIDTH // 2 - 200,
            VISIBLE_HEIGHT // 2,
            400,
            60,
            self.button_font,
            "",
            "Entrez le code du salon"
        )
        self.input_boxes.append(room_input)
        
        # Bouton pour rejoindre
        self.buttons.append(Button(
            VISIBLE_WIDTH // 2 - 150,
            VISIBLE_HEIGHT // 2 + 100,
            300,
            60,
            "Rejoindre",
            self.button_font,
            self.join_server
        ))
        
        # Bouton retour
        self.buttons.append(Button(
            50,
            50,
            150,
            50,
            "Retour",
            self.button_font,
            lambda: self.change_state(LobbyState.MAIN_MENU)
        ))
    
    def setup_waiting_room(self):
        self.buttons = []
        
        # Bouton pour démarrer la partie (uniquement pour l'hôte)
        if self.is_host:
            self.buttons.append(Button(
                VISIBLE_WIDTH // 2 - 150,
                VISIBLE_HEIGHT - 150,
                300,
                60,
                "Démarrer la partie",
                self.button_font,
                self.start_game
            ))
        
        # Bouton pour quitter le salon
        self.buttons.append(Button(
            50,
            50,
            200,
            50,
            "Quitter le salon",
            self.button_font,
            self.leave_room
        ))
    
    def change_state(self, new_state):
        self.state = new_state
        
        if new_state == LobbyState.MAIN_MENU:
            self.setup_main_menu()
        elif new_state == LobbyState.CHARACTER_SELECT:
            self.setup_character_select()
        elif new_state == LobbyState.CREATE_ROOM:
            self.setup_create_room()
        elif new_state == LobbyState.JOIN_ROOM:
            self.setup_join_room()
        elif new_state == LobbyState.WAITING_ROOM:
            self.setup_waiting_room()
    
    def update_fighter_preview(self):
        # Instancier la classe du combattant pour obtenir un objet avec des attributs
        fighter_class = self.available_fighters[self.selected_fighter_index]
        fighter_instance = fighter_class()
        self.selected_fighter = fighter_instance
        
        # Créer une instance du combattant pour l'affichage
        self.fighter_preview = Fighter(1, VISIBLE_WIDTH // 2 - 100, VISIBLE_HEIGHT // 2 - 200, fighter_instance, VISIBLE_HEIGHT - 100)
    
    def next_fighter(self):
        self.selected_fighter_index = (self.selected_fighter_index + 1) % len(self.available_fighters)
        self.update_fighter_preview()
        self.save_player_data()
    
    def prev_fighter(self):
        self.selected_fighter_index = (self.selected_fighter_index - 1) % len(self.available_fighters)
        self.update_fighter_preview()
        self.save_player_data()
    
    def start_server(self):
        # Vérifier que le joueur a un nom
        if not self.player_name:
            return
        
        try:
            # Générer un UUID unique pour cette session
            self.player_uuid = str(uuid.uuid4())
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('0.0.0.0', 5555))
            self.socket.listen(1)
            
            # Démarrer un thread pour accepter les connexions
            self.server_thread = threading.Thread(target=self.accept_connections)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.change_state(LobbyState.WAITING_ROOM)
        except Exception as e:
            print(f"Erreur lors de la création du serveur: {e}")
    
    def accept_connections(self):
        try:
            client, addr = self.socket.accept()
            self.connected = True
            
            # Envoyer les informations du joueur avec UUID
            player_data = {
                "name": self.player_name,
                "fighter": self.selected_fighter.name,
                "uuid": self.player_uuid  # Envoyer l'UUID unique
            }
            client.send(json.dumps(player_data).encode())
            
            # Recevoir les informations de l'adversaire
            opponent_data = json.loads(client.recv(1024).decode())
            self.opponent_name = opponent_data.get("name", "Adversaire")
            self.opponent_uuid = opponent_data.get("uuid", str(uuid.uuid4()))  # Récupérer l'UUID de l'adversaire
            
            # Trouver le combattant de l'adversaire
            fighter_name = opponent_data.get("fighter", "")
            for fighter_class in self.available_fighters:
                fighter_instance = fighter_class()
                if fighter_instance.name == fighter_name:
                    self.opponent_fighter = fighter_instance
                    break
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            self.connected = False
    
    def join_server(self):
        # Vérifier que le joueur a un nom et un code de salon
        if not self.player_name or not self.input_boxes[0].text:
            return
        
        self.room_code = self.input_boxes[0].text
        self.is_host = False
        
        try:
            # Générer un UUID unique pour cette session
            self.player_uuid = str(uuid.uuid4())
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Utiliser l'adresse IP du serveur ou localhost pour les tests
            server_address = os.environ.get('SERVER_HOST', 'localhost')
            self.socket.connect((server_address, 5555))  # Utilise l'adresse du serveur configurée
            
            # Envoyer les informations du joueur avec UUID
            player_data = {
                "name": self.player_name,
                "fighter": self.selected_fighter.name,
                "uuid": self.player_uuid  # Envoyer l'UUID unique
            }
            self.socket.send(json.dumps(player_data).encode())
            
            # Recevoir les informations de l'adversaire
            opponent_data = json.loads(self.socket.recv(1024).decode())
            self.opponent_name = opponent_data.get("name", "Hôte")
            self.opponent_uuid = opponent_data.get("uuid", str(uuid.uuid4()))  # Récupérer l'UUID de l'adversaire
            
            # Trouver le combattant de l'adversaire
            fighter_name = opponent_data.get("fighter", "")
            for fighter_class in self.available_fighters:
                fighter_instance = fighter_class()
                if fighter_instance.name == fighter_name:
                    self.opponent_fighter = fighter_instance
                    break
            
            self.connected = True
            self.change_state(LobbyState.WAITING_ROOM)
        except Exception as e:
            print(f"Erreur de connexion: {e}")
    
    def leave_room(self):
        if self.socket:
            self.socket.close()
        
        self.connected = False
        self.socket = None
        self.server_thread = None
        self.change_state(LobbyState.MAIN_MENU)
    
    def start_game(self):
        # Démarrer la partie (à implémenter)
        pass
    
    def draw_main_menu(self):
        # Titre style Street Fighter
        title_text = self.title_font.render("PYTHFIGHTER", True, TITLE_COLOR)
        title_shadow = self.title_font.render("PYTHFIGHTER", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, 100))
        
        # Effet de glow pour le titre (plus intense)
        glow_surf = pygame.Surface((title_text.get_width() + 30, title_text.get_height() + 30), pygame.SRCALPHA)
        glow_color = (*TITLE_COLOR, 150)
        pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=20)
        glow_rect = glow_surf.get_rect(center=title_rect.center)
        
        # Effet de contour style arcade
        outline_surf = pygame.Surface((title_text.get_width() + 8, title_text.get_height() + 8), pygame.SRCALPHA)
        outline_color = (255, 50, 50, 200)  # Rouge vif
        pygame.draw.rect(outline_surf, outline_color, outline_surf.get_rect(), border_radius=15)
        outline_rect = outline_surf.get_rect(center=title_rect.center)
        
        # Affichage avec effets multiples
        self.screen.blit(outline_surf, outline_rect)
        self.screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_ADD)
        self.screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        self.screen.blit(title_text, title_rect)
        
        # Sous-titre
        if self.player_name:
            subtitle = f"Bienvenue, {self.player_name}!"
        else:
            subtitle = "Entrez votre nom pour commencer"
        
        subtitle_text = self.subtitle_font.render(subtitle, True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(VISIBLE_WIDTH // 2, 180))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Dessiner les boutons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Dessiner les champs de saisie
        for input_box in self.input_boxes:
            input_box.draw(self.screen)
    
    def draw_character_select(self):
        # Titre avec style Street Fighter
        title_text = self.subtitle_font.render("SÉLECTION DU COMBATTANT", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, 80))
        
        # Effet de contour pour le titre
        outline_surf = pygame.Surface((title_text.get_width() + 8, title_text.get_height() + 8), pygame.SRCALPHA)
        outline_color = (255, 50, 50, 200)  # Rouge vif
        pygame.draw.rect(outline_surf, outline_color, outline_surf.get_rect(), border_radius=15)
        outline_rect = outline_surf.get_rect(center=title_rect.center)
        
        self.screen.blit(outline_surf, outline_rect)
        self.screen.blit(title_text, title_rect)
        
        # Afficher le personnage sélectionné
        if self.fighter_preview:
            # Fond pour le personnage
            character_bg = pygame.Surface((300, 400), pygame.SRCALPHA)
            pygame.draw.rect(character_bg, (40, 40, 60, 200), character_bg.get_rect(), border_radius=20)
            self.screen.blit(character_bg, (VISIBLE_WIDTH // 2 - 150, VISIBLE_HEIGHT // 2 - 250))
            
            # Nom du personnage avec effet
            name_text = self.subtitle_font.render(self.selected_fighter.name, True, TITLE_COLOR)
            name_shadow = self.subtitle_font.render(self.selected_fighter.name, True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 - 200))
            
            # Effet de glow pour le nom
            glow_surf = pygame.Surface((name_text.get_width() + 20, name_text.get_height() + 20), pygame.SRCALPHA)
            glow_color = (*TITLE_COLOR, 150)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=10)
            glow_rect = glow_surf.get_rect(center=name_rect.center)
            
            self.screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_ADD)
            self.screen.blit(name_shadow, (name_rect.x + 2, name_rect.y + 2))
            self.screen.blit(name_text, name_rect)
            
            # Statistiques du personnage
            stats_y = VISIBLE_HEIGHT // 2 - 150
            stats = [
                f"Santé: {self.selected_fighter.health}",
                f"Attaque: {self.selected_fighter.attack_power}",
                f"Défense: {self.selected_fighter.defense}",
                f"Vitesse: {self.selected_fighter.speed}"
            ]
            
            for stat in stats:
                stat_text = self.text_font.render(stat, True, TEXT_COLOR)
                stat_rect = stat_text.get_rect(center=(VISIBLE_WIDTH // 2, stats_y))
                self.screen.blit(stat_text, stat_rect)
                stats_y += 30
            
            # Dessiner le personnage
            self.fighter_preview.draw(self.screen)
            
            # Description du personnage
            desc_bg = pygame.Surface((600, 120), pygame.SRCALPHA)
            pygame.draw.rect(desc_bg, (40, 40, 60, 200), desc_bg.get_rect(), border_radius=15)
            self.screen.blit(desc_bg, (VISIBLE_WIDTH // 2 - 300, VISIBLE_HEIGHT - 200))
            
            description = self.selected_fighter.description if hasattr(self.selected_fighter, 'description') else "Un combattant mystérieux..."
            
            # Wrap text
            words = description.split(' ')
            lines = []
            line = ""
            for word in words:
                test_line = line + word + " "
                if self.text_font.size(test_line)[0] < 580:
                    line = test_line
                else:
                    lines.append(line)
                    line = word + " "
            lines.append(line)
            
            desc_y = VISIBLE_HEIGHT - 180
            for line in lines:
                desc_text = self.text_font.render(line, True, TEXT_COLOR)
                desc_rect = desc_text.get_rect(midleft=(VISIBLE_WIDTH // 2 - 280, desc_y))
                self.screen.blit(desc_text, desc_rect)
                desc_y += 25
        
        # Dessiner les boutons
        for button in self.buttons:
            button.draw(self.screen)
    
    def draw_create_room(self):
        # Titre
        title_text = self.subtitle_font.render("Créer un Salon", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Afficher le code de salon
        code_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
        pygame.draw.rect(code_bg, (40, 40, 60, 200), code_bg.get_rect(), border_radius=15)
        self.screen.blit(code_bg, (VISIBLE_WIDTH // 2 - 200, VISIBLE_HEIGHT // 2 - 150))
        
        code_title = self.text_font.render("Code du salon:", True, TEXT_COLOR)
        code_title_rect = code_title.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 - 130))
        self.screen.blit(code_title, code_title_rect)
        
        code_text = self.subtitle_font.render(self.room_code, True, TITLE_COLOR)
        code_rect = code_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 - 90))
        self.screen.blit(code_text, code_rect)
        
        # Instructions
        instructions = [
            "1. Partagez ce code avec votre ami",
            "2. Attendez qu'il rejoigne votre salon",
            "3. Démarrez la partie quand vous êtes prêts"
        ]
        
        instr_y = VISIBLE_HEIGHT // 2
        for instr in instructions:
            instr_text = self.text_font.render(instr, True, TEXT_COLOR)
            instr_rect = instr_text.get_rect(center=(VISIBLE_WIDTH // 2, instr_y))
            self.screen.blit(instr_text, instr_rect)
            instr_y += 40
        
        # Afficher le personnage sélectionné
        if self.selected_fighter:
            fighter_name = self.selected_fighter.name
            fighter_text = self.text_font.render(f"Votre personnage: {fighter_name}", True, TEXT_COLOR)
            fighter_rect = fighter_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 + 150))
            self.screen.blit(fighter_text, fighter_rect)
        
        # Dessiner les boutons
        for button in self.buttons:
            button.draw(self.screen)
    
    def draw_join_room(self):
        # Titre
        title_text = self.subtitle_font.render("Rejoindre un Salon", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instr_text = self.text_font.render("Entrez le code du salon que vous souhaitez rejoindre:", True, TEXT_COLOR)
        instr_rect = instr_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 - 100))
        self.screen.blit(instr_text, instr_rect)
        
        # Afficher le personnage sélectionné
        if self.selected_fighter:
            fighter_name = self.selected_fighter.name
            fighter_text = self.text_font.render(f"Votre personnage: {fighter_name}", True, TEXT_COLOR)
            fighter_rect = fighter_text.get_rect(center=(VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2 + 150))
            self.screen.blit(fighter_text, fighter_rect)
        
        # Dessiner les boutons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Dessiner les champs de saisie
        for input_box in self.input_boxes:
            input_box.draw(self.screen)
    
    def draw_waiting_room(self):
        # Titre
        title_text = self.subtitle_font.render("Salle d'Attente", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(VISIBLE_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Code du salon
        code_text = self.text_font.render(f"Code du salon: {self.room_code}", True, TEXT_COLOR)
        code_rect = code_text.get_rect(center=(VISIBLE_WIDTH // 2, 130))
        self.screen.blit(code_text, code_rect)
        
        # Statut de connexion
        status_color = (0, 255, 0) if self.connected else (255, 0, 0)
        status_text = self.text_font.render(
            "Connecté" if self.connected else "En attente de connexion...",
            True, status_color
        )
        status_rect = status_text.get_rect(center=(VISIBLE_WIDTH // 2, 170))
        self.screen.blit(status_text, status_rect)
        
        # Afficher les joueurs
        player_bg = pygame.Surface((300, 400), pygame.SRCALPHA)
        pygame.draw.rect(player_bg, (40, 40, 60, 200), player_bg.get_rect(), border_radius=20)
        self.screen.blit(player_bg, (VISIBLE_WIDTH // 4 - 150, VISIBLE_HEIGHT // 2 - 150))
        
        player_title = self.text_font.render("Vous", True, TITLE_COLOR)
        player_title_rect = player_title.get_rect(center=(VISIBLE_WIDTH // 4, VISIBLE_HEIGHT // 2 - 130))
        self.screen.blit(player_title, player_title_rect)
        
        player_name = self.text_font.render(self.player_name, True, TEXT_COLOR)
        player_name_rect = player_name.get_rect(center=(VISIBLE_WIDTH // 4, VISIBLE_HEIGHT // 2 - 100))
        self.screen.blit(player_name, player_name_rect)
        
        if self.selected_fighter:
            fighter_name = self.text_font.render(self.selected_fighter.name, True, TEXT_COLOR)
            fighter_name_rect = fighter_name.get_rect(center=(VISIBLE_WIDTH // 4, VISIBLE_HEIGHT // 2 - 70))
            self.screen.blit(fighter_name, fighter_name_rect)
        
        # Afficher l'adversaire s'il est connecté
        opponent_bg = pygame.Surface((300, 400), pygame.SRCALPHA)
        pygame.draw.rect(opponent_bg, (40, 40, 60, 200), opponent_bg.get_rect(), border_radius=20)
        self.screen.blit(opponent_bg, (VISIBLE_WIDTH * 3 // 4 - 150, VISIBLE_HEIGHT // 2 - 150))
        
        opponent_title = self.text_font.render("Adversaire", True, TITLE_COLOR)
        opponent_title_rect = opponent_title.get_rect(center=(VISIBLE_WIDTH * 3 // 4, VISIBLE_HEIGHT // 2 - 130))
        self.screen.blit(opponent_title, opponent_title_rect)
        
        if self.connected and self.opponent_name:
            opponent_name = self.text_font.render(self.opponent_name, True, TEXT_COLOR)
            opponent_name_rect = opponent_name.get_rect(center=(VISIBLE_WIDTH * 3 // 4, VISIBLE_HEIGHT // 2 - 100))
            self.screen.blit(opponent_name, opponent_name_rect)
            
            if self.opponent_fighter:
                fighter_name = self.text_font.render(self.opponent_fighter.name, True, TEXT_COLOR)
                fighter_name_rect = fighter_name.get_rect(center=(VISIBLE_WIDTH * 3 // 4, VISIBLE_HEIGHT // 2 - 70))
                self.screen.blit(fighter_name, fighter_name_rect)
        else:
            waiting_text = self.text_font.render("En attente...", True, (150, 150, 150))
            waiting_rect = waiting_text.get_rect(center=(VISIBLE_WIDTH * 3 // 4, VISIBLE_HEIGHT // 2 - 100))
            self.screen.blit(waiting_text, waiting_rect)
        
        # Dessiner les boutons
        for button in self.buttons:
            button.draw(self.screen)
    
    def draw_particles(self):
        # Effet de particules pour l'ambiance
        for _ in range(5):
            x = random.randint(0, VISIBLE_WIDTH)
            y = random.randint(0, VISIBLE_HEIGHT)
            size = random.randint(1, 3)
            alpha = random.randint(50, 150)
            color = (255, 255, 255, alpha)
            
            particle = pygame.Surface((size, size), pygame.SRCALPHA)
            particle.fill(color)
            self.screen.blit(particle, (x, y))
    
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Gérer les boutons
                for button in self.buttons:
                    result = button.handle_event(event)
                    if result is not None:
                        # Si le bouton a une action, l'exécuter
                        pass
                
                # Gérer les champs de saisie
                for input_box in self.input_boxes:
                    result = input_box.handle_event(event)
                    if result is not None and input_box == self.input_boxes[0] and self.state == LobbyState.MAIN_MENU:
                        # Mettre à jour le nom du joueur
                        self.player_name = result
                        self.save_player_data()
            
            # Mettre à jour les boutons
            for button in self.buttons:
                button.update(mouse_pos)
            
            # Mettre à jour l'effet d'eau
            self.water_effect.update()
            
            # Dessiner le fond
            self.screen.fill(LOBBY_BG_COLOR)
            
            # Dessiner les étoiles en arrière-plan
            for _ in range(100):
                x = random.randint(0, VISIBLE_WIDTH)
                y = random.randint(0, VISIBLE_HEIGHT)
                size = random.randint(1, 3)
                brightness = random.randint(100, 255)
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (x, y), size)
            
            # Dessiner l'effet d'eau
            water_y = int(VISIBLE_HEIGHT * 0.7)
            self.water_effect.draw(self.screen, water_y)
            
            # Dessiner les particules
            self.draw_particles()
            
            # Dessiner l'interface selon l'état
            if self.state == LobbyState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == LobbyState.CHARACTER_SELECT:
                self.draw_character_select()
            elif self.state == LobbyState.CREATE_ROOM:
                self.draw_create_room()
            elif self.state == LobbyState.JOIN_ROOM:
                self.draw_join_room()
            elif self.state == LobbyState.WAITING_ROOM:
                self.draw_waiting_room()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Classe pour gérer le jeu en réseau
class NetworkGame:
    def __init__(self, socket, is_host, player_fighter, opponent_fighter):
        self.socket = socket
        self.is_host = is_host
        self.player_fighter = player_fighter
        self.opponent_fighter = opponent_fighter
        self.game_state = None
        
    def start_game(self):
        # Initialiser le jeu
        self.game_state = GameState()
        
        # Ajouter les combattants
        player_num = 1 if self.is_host else 2
        opponent_num = 2 if self.is_host else 1
        
        self.game_state.add_fighter(player_num, self.player_fighter)
        self.game_state.add_fighter(opponent_num, self.opponent_fighter)
        
        # Démarrer la boucle de jeu
        self.run_game()
    
    def send_game_state(self):
        # Envoyer l'état du jeu au client
        pass
    
    def receive_game_state(self):
        # Recevoir l'état du jeu du serveur
        pass
    
    def run_game(self):
        # Boucle principale du jeu en réseau
        pass

    def run(self):
        running = True
        while running:
            # Gestion du temps
            dt = self.clock.tick(60) / 1000
            
            # Mise à jour de l'effet d'eau
            self.water_effect.update()
            
            # Fond avec dégradé
            self.screen.fill(LOBBY_BG_COLOR)
            
            # Dessiner l'effet d'eau
            water_y = VISIBLE_HEIGHT - VISIBLE_HEIGHT // 3
            self.water_effect.draw(self.screen, water_y)
            
            # Gestion des événements
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Gestion des boutons
                for button in self.buttons:
                    button.update(mouse_pos)
                    result = button.handle_event(event)
                    if result is not None:
                        # Une action a été déclenchée
                        pass
                
                # Gestion des champs de saisie
                for input_box in self.input_boxes:
                    result = input_box.handle_event(event)
                    if result is not None and self.state == LobbyState.MAIN_MENU:
                        self.player_name = result
                        self.save_player_data()
            
            # Affichage en fonction de l'état
            if self.state == LobbyState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == LobbyState.CHARACTER_SELECT:
                self.draw_character_select()
            elif self.state == LobbyState.CREATE_ROOM:
                self.draw_create_room()
            elif self.state == LobbyState.JOIN_ROOM:
                self.draw_join_room()
            elif self.state == LobbyState.WAITING_ROOM:
                self.draw_waiting_room()
            
            # Mise à jour de l'écran
            pygame.display.flip()
        
        pygame.quit()

# Fonction principale
def main():
    lobby = Lobby()
    lobby.run()

if __name__ == "__main__":
    main()