import socket
import json
import threading
import time
import logging
import pygame
import random

# Configuration des adresses
HOST = '194.9.172.146'  # Adresse IP du serveur
PORT = 25568            # Port pour les connexions
PING_PORT = 25569       # Port pour les pings

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MultiplayerManager:
    """Gestionnaire de connexion multijoueur pour PythFighter."""
    
    def __init__(self):
        self.connected = False
        self.room_id = None
        self.player_id = None
        self.opponent_data = {}
        self.last_ping_time = 0
        self.ping_value = 0
        self.keep_alive = False
        self.ping_thread = None
        self.game_state = {}
        self.is_host = False
        self.opponent_ready = False
        self.match_data = {
            "player1_type": "Mitsu",
            "player2_type": "Tank"
        }
    
    def connect_to_server(self):
        """Établit une connexion avec le serveur."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((HOST, PORT))
                s.sendall(b"CONNECT")
                response = s.recv(1024).decode('utf-8')
                if "CONNECTED" in response:
                    self.connected = True
                    logging.info("Connexion au serveur établie")
                    return True
                else:
                    logging.error(f"Échec de connexion: {response}")
                    return False
        except Exception as e:
            logging.error(f"Erreur de connexion: {e}")
            return False
    
    def create_room(self, player_name, fighter_type):
        """Crée une nouvelle salle de jeu."""
        if not self.connected:
            if not self.connect_to_server():
                return False
        
        try:
            data = {
                "action": "CREATE_ROOM",
                "player_name": player_name,
                "fighter_type": fighter_type
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                try:
                    response_data = json.loads(response)
                    
                    if response_data.get("status") == "success":
                        self.room_id = response_data.get("room_id")
                        self.player_id = response_data.get("player_id")
                        self.is_host = True
                        self.match_data["player1_type"] = fighter_type
                        self._start_ping_thread()
                        logging.info(f"Salle créée avec succès. ID: {self.room_id}")
                        return self.room_id
                    else:
                        logging.error(f"Échec de création de salle: {response}")
                        return None
                except json.JSONDecodeError:
                    logging.error(f"Réponse invalide du serveur: {response}")
                    return None
        except Exception as e:
            logging.error(f"Erreur lors de la création de salle: {e}")
            return None
    
    def join_room(self, room_id, player_name, fighter_type):
        """Rejoint une salle existante."""
        if not self.connected:
            if not self.connect_to_server():
                return False
        
        try:
            data = {
                "action": "JOIN_ROOM",
                "room_id": room_id,
                "player_name": player_name,
                "fighter_type": fighter_type
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                try:
                    response_data = json.loads(response)
                    
                    if response_data.get("status") == "success":
                        self.room_id = room_id
                        self.player_id = response_data.get("player_id")
                        self.is_host = False
                        self.match_data["player2_type"] = fighter_type
                        self.match_data["player1_type"] = response_data.get("host_fighter_type", "Mitsu")
                        self._start_ping_thread()
                        logging.info(f"Salle rejointe avec succès. ID: {self.room_id}")
                        return True
                    else:
                        logging.error(f"Échec pour rejoindre la salle: {response}")
                        return False
                except json.JSONDecodeError:
                    logging.error(f"Réponse invalide du serveur: {response}")
                    return False
        except Exception as e:
            logging.error(f"Erreur lors de la tentative de rejoindre la salle: {e}")
            return False
    
    def send_game_state(self, game_state):
        """Envoie l'état actuel du jeu au serveur."""
        if not self.room_id or not self.player_id:
            return False
        
        try:
            data = {
                "action": "UPDATE_STATE",
                "room_id": self.room_id,
                "player_id": self.player_id,
                "game_state": game_state
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                return "success" in response.lower()
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'état du jeu: {e}")
            return False
    
    def get_opponent_state(self):
        """Récupère l'état du jeu de l'adversaire."""
        if not self.room_id or not self.player_id:
            return None
        
        try:
            data = {
                "action": "GET_OPPONENT_STATE",
                "room_id": self.room_id,
                "player_id": self.player_id
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        self.opponent_data = response_data.get("opponent_state", {})
                        return self.opponent_data
                    return None
                except json.JSONDecodeError:
                    logging.error("Réponse invalide du serveur")
                    return None
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'état de l'adversaire: {e}")
            return None
    
    def check_opponent_ready(self):
        """Vérifie si l'adversaire est prêt à jouer."""
        if not self.room_id or not self.player_id:
            return False
        
        try:
            data = {
                "action": "CHECK_OPPONENT_READY",
                "room_id": self.room_id,
                "player_id": self.player_id
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                try:
                    response_data = json.loads(response)
                    if response_data.get("status") == "success":
                        self.opponent_ready = response_data.get("ready", False)
                        return self.opponent_ready
                    return False
                except json.JSONDecodeError:
                    return False
        except Exception as e:
            logging.error(f"Erreur lors de la vérification de l'état de l'adversaire: {e}")
            return False
    
    def set_ready(self, ready=True):
        """Indique au serveur que le joueur est prêt."""
        if not self.room_id or not self.player_id:
            return False
        
        try:
            data = {
                "action": "SET_READY",
                "room_id": self.room_id,
                "player_id": self.player_id,
                "ready": ready
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                return "success" in response.lower()
        except Exception as e:
            logging.error(f"Erreur lors de la définition de l'état prêt: {e}")
            return False
    
    def leave_room(self):
        """Quitte la salle actuelle."""
        if not self.room_id or not self.player_id:
            return True
        
        try:
            data = {
                "action": "LEAVE_ROOM",
                "room_id": self.room_id,
                "player_id": self.player_id
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((HOST, PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
                
            self._stop_ping_thread()
            self.room_id = None
            self.player_id = None
            self.is_host = False
            self.opponent_ready = False
            logging.info("Salle quittée avec succès")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la tentative de quitter la salle: {e}")
            return False
    
    def _start_ping_thread(self):
        """Démarre un thread pour envoyer des pings réguliers."""
        self.keep_alive = True
        self.ping_thread = threading.Thread(target=self._ping_loop)
        self.ping_thread.daemon = True
        self.ping_thread.start()
    
    def _stop_ping_thread(self):
        """Arrête le thread de ping."""
        self.keep_alive = False
        if self.ping_thread:
            self.ping_thread.join(timeout=1)
    
    def _ping_loop(self):
        """Boucle d'envoi de pings réguliers."""
        while self.keep_alive:
            self._send_ping()
            time.sleep(2)
    
    def _send_ping(self):
        """Envoie un ping au serveur et mesure le temps de réponse."""
        try:
            start_time = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((HOST, PING_PORT))
                s.sendall(b"PING")
                response = s.recv(1024)
                if response == b"PONG":
                    self.ping_value = int((time.time() - start_time) * 1000)
                    self.last_ping_time = time.time()
        except Exception as e:
            logging.error(f"Erreur de ping: {e}")
            self.ping_value = 999


class MultiplayerGame:
    """Gère une partie en mode multijoueur."""
    
    def __init__(self, game_instance, is_host=False):
        self.game = game_instance
        self.mp_manager = MultiplayerManager()
        self.is_host = is_host
        self.last_sync_time = 0
        self.sync_interval = 0.05  # 50ms
        self.game_started = False
        self.countdown_done = False
    
    def start_game(self, room_id=None, player_name="Player", fighter_type="Mitsu"):
        """Démarre une partie multijoueur."""
        if room_id:
            # Rejoindre une salle existante
            success = self.mp_manager.join_room(room_id, player_name, fighter_type)
            if not success:
                return False
            self.is_host = False
        else:
            # Créer une nouvelle salle
            room_id = self.mp_manager.create_room(player_name, fighter_type)
            if not room_id:
                return False
            self.is_host = True
        
        # Indiquer que le joueur est prêt
        self.mp_manager.set_ready(True)
        return True
    
    def update(self):
        """Met à jour l'état du jeu multijoueur."""
        current_time = time.time()
        
        # Vérifier si l'adversaire est prêt
        if not self.game_started:
            opponent_ready = self.mp_manager.check_opponent_ready()
            if opponent_ready:
                self.game_started = True
                # Configurer les personnages en fonction des données du match
                if self.is_host:
                    self.game.fighters[0].name = self.mp_manager.match_data["player1_type"]
                    self.game.fighters[1].name = self.mp_manager.match_data["player2_type"]
                else:
                    self.game.fighters[0].name = self.mp_manager.match_data["player2_type"]
                    self.game.fighters[1].name = self.mp_manager.match_data["player1_type"]
                return
        
        # Synchroniser les états du jeu
        if current_time - self.last_sync_time >= self.sync_interval:
            # Préparer l'état du jeu local
            local_fighter = self.game.fighters[0] if self.is_host else self.game.fighters[1]
            game_state = {
                "position": {
                    "x": local_fighter.pos_x,
                    "y": local_fighter.pos_y
                },
                "velocity": {
                    "x": local_fighter.vel_x,
                    "y": local_fighter.vel_y
                },
                "health": local_fighter.health,
                "stamina": local_fighter.stamina,
                "attacking": local_fighter.attacking,
                "blocking": local_fighter.blocking,
                "animation": local_fighter.current_animation,
                "direction": local_fighter.direction
            }
            
            # Envoyer l'état local
            self.mp_manager.send_game_state(game_state)
            
            # Récupérer l'état de l'adversaire
            opponent_state = self.mp_manager.get_opponent_state()
            if opponent_state:
                # Mettre à jour l'état de l'adversaire
                remote_fighter = self.game.fighters[1] if self.is_host else self.game.fighters[0]
                if "position" in opponent_state:
                    remote_fighter.pos_x = opponent_state["position"]["x"]
                    remote_fighter.pos_y = opponent_state["position"]["y"]
                    remote_fighter.rect.x = int(remote_fighter.pos_x)
                    remote_fighter.rect.y = int(remote_fighter.pos_y)
                
                if "velocity" in opponent_state:
                    remote_fighter.vel_x = opponent_state["velocity"]["x"]
                    remote_fighter.vel_y = opponent_state["velocity"]["y"]
                
                if "health" in opponent_state:
                    remote_fighter.health = opponent_state["health"]
                
                if "stamina" in opponent_state:
                    remote_fighter.stamina = opponent_state["stamina"]
                
                if "attacking" in opponent_state:
                    remote_fighter.attacking = opponent_state["attacking"]
                
                if "blocking" in opponent_state:
                    remote_fighter.blocking = opponent_state["blocking"]
                
                if "animation" in opponent_state:
                    remote_fighter.current_animation = opponent_state["animation"]
                
                if "direction" in opponent_state:
                    remote_fighter.direction = opponent_state["direction"]
            
            self.last_sync_time = current_time
    
    def end_game(self):
        """Termine la partie multijoueur."""
        self.mp_manager.leave_room()
        self.game_started = False
        self.countdown_done = False