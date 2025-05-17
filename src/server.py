# Serveur PythFighter avec support UUID
import socket
import threading
import json
import time
import uuid
import logging
import os
import signal
import sys
from datetime import datetime
from collections import deque

# Configuration du serveur
HOST = '0.0.0.0'  # Écoute sur toutes les interfaces
PORT = 25568      # Port principal
PING_PORT = 25569 # Port pour les pings

# Configuration du logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"server_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Stockage des salles et des joueurs
rooms = {}
player_states = {}
active_connections = 0
total_connections = 0
connection_history = deque(maxlen=100)  # Garde les 100 dernières connexions
server_start_time = time.time()

class Room:
    def __init__(self, host_id, host_name, host_fighter, host_uuid=None):
        self.id = str(uuid.uuid4())[:8]  # ID court et unique
        self.host_id = host_id
        self.players = {
            host_id: {
                "name": host_name,
                "fighter_type": host_fighter,
                "ready": False,
                "last_active": time.time(),
                "ip_address": None,
                "uuid": host_uuid or str(uuid.uuid4()),  # Utiliser l'UUID fourni ou en générer un nouveau
                "score": 0
            }
        }
        self.game_state = {}
        self.created_at = time.time()
        self.last_activity = time.time()
        self.match_history = []
        self.round_number = 0
        self.status = "waiting"  # waiting, playing, finished
        
        logging.info(f"Nouvelle salle créée: {self.id} par {host_name} avec UUID {self.players[host_id]['uuid']}")
    
    def add_player(self, player_id, player_name, fighter_type, ip_address=None, player_uuid=None):
        if len(self.players) >= 2:
            return False
        
        self.players[player_id] = {
            "name": player_name,
            "fighter_type": fighter_type,
            "ready": False,
            "last_active": time.time(),
            "ip_address": ip_address,
            "uuid": player_uuid or str(uuid.uuid4()),  # Utiliser l'UUID fourni ou en générer un nouveau
            "score": 0
        }
        self.last_activity = time.time()
        return True
    
    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            self.last_activity = time.time()
            return True
        return False
    
    def update_player_state(self, player_id, game_state):
        if player_id in self.players:
            self.game_state[player_id] = game_state
            self.players[player_id]["last_active"] = time.time()
            self.last_activity = time.time()
            return True
        return False
    
    def get_opponent_state(self, player_id):
        for pid in self.players:
            if pid != player_id and pid in self.game_state:
                return self.game_state[pid]
        return None
    
    def set_player_ready(self, player_id, ready=True):
        if player_id in self.players:
            self.players[player_id]["ready"] = ready
            self.last_activity = time.time()
            
            # Si les deux joueurs sont prêts, commencer le match
            if ready and len(self.players) == 2:
                all_ready = all(player["ready"] for player in self.players.values())
                if all_ready and self.status == "waiting":
                    self.status = "playing"
                    self.round_number += 1
                    logging.info(f"Match commencé dans la salle {self.id}, round {self.round_number}")
            
            return True
        return False
    
    def is_opponent_ready(self, player_id):
        for pid, player in self.players.items():
            if pid != player_id:
                return player.get("ready", False)
        return False
    
    def get_opponent_id(self, player_id):
        for pid in self.players:
            if pid != player_id:
                return pid
        return None
    
    def get_host_fighter_type(self):
        return self.players[self.host_id]["fighter_type"]
    
    def get_host_uuid(self):
        return self.players[self.host_id]["uuid"]
    
    def record_match_result(self, winner_id, loser_id, match_duration):
        """Enregistre le résultat d'un match."""
        if winner_id in self.players and loser_id in self.players:
            result = {
                "winner": self.players[winner_id]["name"],
                "loser": self.players[loser_id]["name"],
                "winner_fighter": self.players[winner_id]["fighter_type"],
                "loser_fighter": self.players[loser_id]["fighter_type"],
                "duration": match_duration,
                "timestamp": time.time(),
                "round": self.round_number
            }
            
            self.match_history.append(result)
            self.players[winner_id]["score"] += 1
            self.status = "waiting"
            
            logging.info(f"Match terminé dans la salle {self.id}: {result['winner']} a gagné contre {result['loser']} en {result['duration']} secondes")
            
            return True
        return False
    
    def is_empty(self):
        return len(self.players) == 0

def handle_client(client_socket, client_address):
    global active_connections, total_connections
    
    active_connections += 1
    total_connections += 1
    connection_time = time.time()
    connection_history.append({
        "ip": client_address[0],
        "port": client_address[1],
        "time": connection_time
    })
    
    logging.info(f"Nouvelle connexion de {client_address[0]}:{client_address[1]}")
    
    try:
        data = client_socket.recv(1024).decode('utf-8')
        
        if data == "CONNECT":
            client_socket.send("CONNECTED".encode('utf-8'))
            return
        
        try:
            request = json.loads(data)
            action = request.get("action")
            
            if action == "CREATE_ROOM":
                player_name = request.get("player_name", "Joueur")
                fighter_type = request.get("fighter_type", "Mitsu")
                player_uuid = request.get("player_uuid", str(uuid.uuid4()))
                
                player_id = str(uuid.uuid4())
                room = Room(player_id, player_name, fighter_type, player_uuid)
                rooms[room.id] = room
                
                response = {
                    "status": "success",
                    "room_id": room.id,
                    "player_id": player_id
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
                logging.info(f"Salle créée: {room.id} par {player_name} avec UUID {player_uuid}")
            
            elif action == "JOIN_ROOM":
                room_id = request.get("room_id")
                player_name = request.get("player_name", "Joueur")
                fighter_type = request.get("fighter_type", "Mitsu")
                player_uuid = request.get("player_uuid", str(uuid.uuid4()))
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                player_id = str(uuid.uuid4())
                
                # Vérifier si la salle est pleine
                if len(room.players) >= 2:
                    response = {"status": "error", "message": "Salle pleine"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                # Ajouter le joueur à la salle
                room.add_player(player_id, player_name, fighter_type, client_address[0], player_uuid)
                
                response = {
                    "status": "success",
                    "room_id": room_id,
                    "player_id": player_id,
                    "host_fighter_type": room.get_host_fighter_type(),
                    "host_uuid": room.get_host_uuid()
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
                logging.info(f"Joueur {player_name} avec UUID {player_uuid} a rejoint la salle {room_id}")
            
            elif action == "UPDATE_STATE":
                room_id = request.get("room_id")
                player_id = request.get("player_id")
                game_state = request.get("game_state", {})
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                if player_id not in room.players:
                    response = {"status": "error", "message": "Joueur non trouvé dans cette salle"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room.update_player_state(player_id, game_state)
                response = {"status": "success"}
                client_socket.send(json.dumps(response).encode('utf-8'))
            
            elif action == "GET_OPPONENT_STATE":
                room_id = request.get("room_id")
                player_id = request.get("player_id")
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                if player_id not in room.players:
                    response = {"status": "error", "message": "Joueur non trouvé dans cette salle"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                opponent_state = room.get_opponent_state(player_id)
                response = {
                    "status": "success",
                    "opponent_state": opponent_state
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
            
            elif action == "SET_READY":
                room_id = request.get("room_id")
                player_id = request.get("player_id")
                ready = request.get("ready", True)
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                if player_id not in room.players:
                    response = {"status": "error", "message": "Joueur non trouvé dans cette salle"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room.set_player_ready(player_id, ready)
                response = {"status": "success"}
                client_socket.send(json.dumps(response).encode('utf-8'))
            
            elif action == "CHECK_OPPONENT_READY":
                room_id = request.get("room_id")
                player_id = request.get("player_id")
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                if player_id not in room.players:
                    response = {"status": "error", "message": "Joueur non trouvé dans cette salle"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                opponent_ready = room.is_opponent_ready(player_id)
                response = {
                    "status": "success",
                    "opponent_ready": opponent_ready
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
            
            elif action == "RECORD_MATCH_RESULT":
                room_id = request.get("room_id")
                winner_id = request.get("winner_id")
                loser_id = request.get("loser_id")
                match_duration = request.get("match_duration", 0)
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                success = room.record_match_result(winner_id, loser_id, match_duration)
                
                if success:
                    response = {"status": "success"}
                else:
                    response = {"status": "error", "message": "Impossible d'enregistrer le résultat"}
                
                client_socket.send(json.dumps(response).encode('utf-8'))
            
            elif action == "LEAVE_ROOM":
                room_id = request.get("room_id")
                player_id = request.get("player_id")
                
                if room_id not in rooms:
                    response = {"status": "error", "message": "Salle introuvable"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room = rooms[room_id]
                if player_id not in room.players:
                    response = {"status": "error", "message": "Joueur non trouvé dans cette salle"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    return
                
                room.remove_player(player_id)
                
                # Si la salle est vide, la supprimer
                if room.is_empty():
                    del rooms[room_id]
                    logging.info(f"Salle {room_id} supprimée car vide")
                
                response = {"status": "success"}
                client_socket.send(json.dumps(response).encode('utf-8'))
                logging.info(f"Joueur {player_id} a quitté la salle {room_id}")
            
            else:
                response = {"status": "error", "message": "Action non reconnue"}
                client_socket.send(json.dumps(response).encode('utf-8'))
        
        except json.JSONDecodeError:
            response = {"status": "error", "message": "Format JSON invalide"}
            client_socket.send(json.dumps(response).encode('utf-8'))
    
    except Exception as e:
        logging.error(f"Erreur lors du traitement de la requête: {e}")
    
    finally:
        client_socket.close()
        active_connections -= 1

def handle_ping(client_socket, client_address):
    try:
        start_time = time.time()
        client_socket.send(str(start_time).encode('utf-8'))
        client_socket.close()
    except Exception as e:
        logging.error(f"Erreur lors du ping: {e}")
        client_socket.close()

def clean_inactive_rooms():
    """Nettoie les salles inactives."""
    current_time = time.time()
    inactive_threshold = 300  # 5 minutes
    
    rooms_to_remove = []
    for room_id, room in rooms.items():
        if current_time - room.last_activity > inactive_threshold:
            rooms_to_remove.append(room_id)
    
    for room_id in rooms_to_remove:
        del rooms[room_id]
        logging.info(f"Salle {room_id} supprimée pour inactivité")

def main_server():
    """Serveur principal pour les connexions de jeu."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        logging.info(f"Serveur principal démarré sur {HOST}:{PORT}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
    
    except Exception as e:
        logging.error(f"Erreur du serveur principal: {e}")
    
    finally:
        server_socket.close()

def ping_server():
    """Serveur de ping pour mesurer la latence."""
    ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ping_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        ping_socket.bind((HOST, PING_PORT))
        ping_socket.listen(5)
        logging.info(f"Serveur de ping démarré sur {HOST}:{PING_PORT}")
        
        while True:
            client_socket, client_address = ping_socket.accept()
            ping_thread = threading.Thread(target=handle_ping, args=(client_socket, client_address))
            ping_thread.daemon = True
            ping_thread.start()
    
    except Exception as e:
        logging.error(f"Erreur du serveur de ping: {e}")
    
    finally:
        ping_socket.close()

def cleanup_thread():
    """Thread pour nettoyer les salles inactives."""
    while True:
        try:
            clean_inactive_rooms()
            time.sleep(60)  # Vérifier toutes les minutes
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage: {e}")

def signal_handler(sig, frame):
    """Gestionnaire de signal pour arrêter proprement le serveur."""
    logging.info("Arrêt du serveur...")
    sys.exit(0)

if __name__ == "__main__":
    # Enregistrer les gestionnaires de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrer le thread de nettoyage
    cleanup = threading.Thread(target=cleanup_thread)
    cleanup.daemon = True
    cleanup.start()
    
    # Démarrer le serveur de ping dans un thread séparé
    ping_thread = threading.Thread(target=ping_server)
    ping_thread.daemon = True
    ping_thread.start()
    
    # Démarrer le serveur principal
    main_server()