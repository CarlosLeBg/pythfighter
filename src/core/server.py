# CE CODE EST SUR LE SERVEUR DISTANT, N'Y TOUCHEZ PAS SURTOUT
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
STATS_PORT = 25570 # Port pour les statistiques

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

# Statistiques
class ServerStats:
    def __init__(self):
        self.total_connections = 0
        self.active_connections = 0
        self.total_rooms_created = 0
        self.active_rooms = 0
        self.total_matches_played = 0
        self.peak_concurrent_users = 0
        self.peak_concurrent_rooms = 0
        self.server_uptime = 0
        self.last_reset = time.time()
        
    def update(self):
        self.active_connections = active_connections
        self.active_rooms = len(rooms)
        self.server_uptime = time.time() - server_start_time
        
        # Mettre à jour les pics
        if self.active_connections > self.peak_concurrent_users:
            self.peak_concurrent_users = self.active_connections
        
        if self.active_rooms > self.peak_concurrent_rooms:
            self.peak_concurrent_rooms = self.active_rooms
    
    def to_dict(self):
        self.update()
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "total_rooms_created": self.total_rooms_created,
            "active_rooms": self.active_rooms,
            "total_matches_played": self.total_matches_played,
            "peak_concurrent_users": self.peak_concurrent_users,
            "peak_concurrent_rooms": self.peak_concurrent_rooms,
            "server_uptime": int(self.server_uptime),
            "last_reset": datetime.fromtimestamp(self.last_reset).strftime('%Y-%m-%d %H:%M:%S')
        }

stats = ServerStats()

class Room:
    def __init__(self, host_id, host_name, host_fighter):
        self.id = str(uuid.uuid4())[:8]  # ID court et unique
        self.host_id = host_id
        self.players = {
            host_id: {
                "name": host_name,
                "fighter_type": host_fighter,
                "ready": False,
                "last_active": time.time(),
                "ip_address": None,
                "uuid": str(uuid.uuid4()),  # Identifiant unique pour chaque joueur
                "score": 0
            }
        }
        self.game_state = {}
        self.created_at = time.time()
        self.last_activity = time.time()
        self.match_history = []
        self.round_number = 0
        self.status = "waiting"  # waiting, playing, finished
        
        stats.total_rooms_created += 1
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
            
            stats.total_matches_played += 1
            logging.info(f"Match terminé dans la salle {self.id}: {result['winner']} a gagné contre {result['loser']} en {result['duration']} secondes")
            
            return True
        return False
    
    def is_empty(self):
        return len(self.players) == 0
    
    def is_stale(self, max_age=3600):  # 1 heure par défaut
        inactive_time = time.time() - self.last_activity
        return inactive_time > max_age or time.time() - self.created_at > max_age * 3
    
    def to_dict(self):
        """Convertit la salle en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "host": self.players[self.host_id]["name"] if self.host_id in self.players else "Inconnu",
            "player_count": len(self.players),
            "status": self.status,
            "created_at": datetime.fromtimestamp(self.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            "last_activity": datetime.fromtimestamp(self.last_activity).strftime('%Y-%m-%d %H:%M:%S'),
            "round_number": self.round_number,
            "match_history_count": len(self.match_history)
        }

def handle_client(client_socket, client_address):
    """Gère les connexions des clients."""
    global active_connections, total_connections
    
    active_connections += 1
    total_connections += 1
    stats.total_connections += 1
    
    connection_time = time.time()
    connection_history.append({
        "ip": client_address[0],
        "port": client_address[1],
        "time": connection_time,
        "datetime": datetime.fromtimestamp(connection_time).strftime('%Y-%m-%d %H:%M:%S')
    })
    
    try:
        client_socket.settimeout(10)  # Timeout de 10 secondes
        data = client_socket.recv(4096).decode('utf-8')
        
        # Simple connexion de test
        if data == "CONNECT":
            client_socket.sendall("CONNECTED".encode('utf-8'))
            logging.info(f"Client connecté pour test depuis {client_address[0]}:{client_address[1]}")
            return
        
        # Traitement des commandes JSON
        try:
            request = json.loads(data)
            action = request.get("action", "")
            
            # Ajouter l'adresse IP à la requête
            request["ip_address"] = client_address[0]
            
            # Vérifier si un UUID est fourni, sinon en générer un
            if "player_uuid" not in request and action in ["CREATE_ROOM", "JOIN_ROOM"]:
                request["player_uuid"] = str(uuid.uuid4())
                logging.info(f"UUID généré pour le client {client_address[0]}: {request['player_uuid']}")
            
            if action == "CREATE_ROOM":
                response = create_room(request)
            elif action == "JOIN_ROOM":
                response = join_room(request)
            elif action == "LEAVE_ROOM":
                response = leave_room(request)
            elif action == "UPDATE_STATE":
                response = update_state(request)
            elif action == "GET_OPPONENT_STATE":
                response = get_opponent_state(request)
            elif action == "SET_READY":
                response = set_ready(request)
            elif action == "CHECK_OPPONENT_READY":
                response = check_opponent_ready(request)
            elif action == "RECORD_MATCH_RESULT":
                response = record_match_result(request)
            elif action == "LIST_ROOMS":
                response = list_rooms(request)
            elif action == "GET_ROOM_INFO":
                response = get_room_info(request)
            else:
                response = {"status": "error", "message": "Action non reconnue"}
            
            client_socket.sendall(json.dumps(response).encode('utf-8'))
            
        except json.JSONDecodeError:
            client_socket.sendall(json.dumps({"status": "error", "message": "Format JSON invalide"}).encode('utf-8'))
    
    except socket.timeout:
        logging.warning(f"Timeout de connexion pour {client_address[0]}:{client_address[1]}")
        try:
            client_socket.sendall(json.dumps({"status": "error", "message": "Timeout de connexion"}).encode('utf-8'))
        except:
            pass
    
    except Exception as e:
        logging.error(f"Erreur lors du traitement de la connexion de {client_address[0]}:{client_address[1]}: {e}")
        try:
            client_socket.sendall(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        except:
            pass
    
    finally:
        client_socket.close()
        active_connections -= 1

def create_room(request):
    """Crée une nouvelle salle de jeu."""
    player_name = request.get("player_name", "Joueur")
    fighter_type = request.get("fighter_type", "Mitsu")
    ip_address = request.get("ip_address")
    player_uuid = request.get("player_uuid", str(uuid.uuid4()))
    
    # Vérifier si le joueur a déjà créé trop de salles (en utilisant UUID au lieu de l'IP)
    existing_rooms = 0
    for room in rooms.values():
        for player in room.players.values():
            if player.get("uuid") == player_uuid:
                existing_rooms += 1
    
    if existing_rooms >= 3:
        return {"status": "error", "message": "Vous avez déjà créé trop de salles"}
    
    player_id = str(uuid.uuid4())
    room = Room(player_id, player_name, fighter_type)
    
    # Ajouter l'adresse IP et l'UUID
    room.players[player_id]["ip_address"] = ip_address
    room.players[player_id]["uuid"] = player_uuid
    
    rooms[room.id] = room
    
    return {
        "status": "success",
        "room_id": room.id,
        "player_id": player_id
    }

def join_room(request):
    """Rejoint une salle existante."""
    room_id = request.get("room_id")
    player_name = request.get("player_name", "Joueur")
    fighter_type = request.get("fighter_type", "Tank")
    ip_address = request.get("ip_address")
    player_uuid = request.get("player_uuid", str(uuid.uuid4()))
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    
    if len(room.players) >= 2:
        return {"status": "error", "message": "Salle pleine"}
    
    # Vérifier si le joueur est déjà dans la salle (même UUID)
    for player in room.players.values():
        if player.get("uuid") == player_uuid:
            return {"status": "error", "message": "Vous ne pouvez pas rejoindre votre propre salle"}
    
    player_id = str(uuid.uuid4())
    success = room.add_player(player_id, player_name, fighter_type, ip_address, player_uuid)
    
    if success:
        logging.info(f"Joueur {player_name} a rejoint la salle {room_id} avec UUID {player_uuid}")
        return {
            "status": "success",
            "player_id": player_id,
            "host_fighter_type": room.get_host_fighter_type(),
            "host_uuid": room.get_host_uuid()
        }
    else:
        return {"status": "error", "message": "Impossible de rejoindre la salle"}

def leave_room(request):
    """Quitte une salle."""
    room_id = request.get("room_id")
    player_id = request.get("player_id")
    
    if not room_id or room_id not in rooms:
        return {"status": "success", "message": "Salle déjà fermée"}
    
    room = rooms[room_id]
    success = room.remove_player(player_id)
    
    if room.is_empty():
        del rooms[room_id]
        logging.info(f"Salle {room_id} fermée (vide)")
    
    return {"status": "success"}

def update_state(request):
    """Met à jour l'état du jeu d'un joueur."""
    room_id = request.get("room_id")
    player_id = request.get("player_id")
    game_state = request.get("game_state", {})
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    success = room.update_player_state(player_id, game_state)
    
    if success:
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Joueur non trouvé dans la salle"}

def get_opponent_state(request):
    """Récupère l'état du jeu de l'adversaire."""
    room_id = request.get("room_id")
    player_id = request.get("player_id")
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    opponent_state = room.get_opponent_state(player_id)
    
    if opponent_state:
        return {
            "status": "success",
            "opponent_state": opponent_state
        }
    else:
        return {
            "status": "success",
            "opponent_state": {}
        }

def set_ready(request):
    """Définit l'état 'prêt' d'un joueur."""
    room_id = request.get("room_id")
    player_id = request.get("player_id")
    ready = request.get("ready", True)
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    success = room.set_player_ready(player_id, ready)
    
    if success:
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Joueur non trouvé dans la salle"}

def check_opponent_ready(request):
    """Vérifie si l'adversaire est prêt."""
    room_id = request.get("room_id")
    player_id = request.get("player_id")
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    ready = room.is_opponent_ready(player_id)
    
    return {
        "status": "success",
        "ready": ready
    }

def record_match_result(request):
    """Enregistre le résultat d'un match."""
    room_id = request.get("room_id")
    winner_id = request.get("winner_id")
    loser_id = request.get("loser_id")
    match_duration = request.get("duration", 0)
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    success = room.record_match_result(winner_id, loser_id, match_duration)
    
    if success:
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Impossible d'enregistrer le résultat"}

def list_rooms(request):
    """Liste les salles disponibles."""
    available_rooms = []
    
    for room_id, room in rooms.items():
        if len(room.players) < 2 and room.status == "waiting":
            room_info = room.to_dict()
            available_rooms.append(room_info)
    
    return {
        "status": "success",
        "rooms": available_rooms
    }

def get_room_info(request):
    """Récupère les informations d'une salle."""
    room_id = request.get("room_id")
    
    if not room_id or room_id not in rooms:
        return {"status": "error", "message": "Salle introuvable"}
    
    room = rooms[room_id]
    
    # Créer une version sécurisée des informations des joueurs
    players_info = []
    for player_id, player in room.players.items():
        players_info.append({
            "name": player["name"],
            "fighter_type": player["fighter_type"],
            "ready": player["ready"],
            "score": player["score"]
        })
    
    return {
        "status": "success",
        "room": room.to_dict(),
        "players": players_info,
        "match_history": room.match_history
    }

def handle_ping(client_socket):
    """Gère les requêtes de ping."""
    try:
        data = client_socket.recv(1024)
        if data == b"PING":
            client_socket.sendall(b"PONG")
    except Exception as e:
        logging.error(f"Erreur lors du traitement du ping: {e}")
    finally:
        client_socket.close()

def handle_stats(client_socket):
    """Gère les requêtes de statistiques."""
    try:
        data = client_socket.recv(1024)
        if data == b"STATS":
            stats_data = stats.to_dict()
            client_socket.sendall(json.dumps(stats_data).encode('utf-8'))
    except Exception as e:
        logging.error(f"Erreur lors du traitement des statistiques: {e}")
    finally:
        client_socket.close()

def clean_stale_rooms():
    """Nettoie les salles inactives."""
    while True:
        try:
            current_time = time.time()
            rooms_to_remove = []
            
            for room_id, room in rooms.items():
                if room.is_stale():
                    rooms_to_remove.append(room_id)
            
            for room_id in rooms_to_remove:
                del rooms[room_id]
                logging.info(f"Salle {room_id} supprimée (inactive)")
            
            # Mettre à jour les statistiques
            stats.update()
            
            time.sleep(300)  # Vérifier toutes les 5 minutes
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage des salles: {e}")
            time.sleep(60)

def signal_handler(sig, frame):
    """Gère l'arrêt propre du serveur."""
    logging.info("Signal d'arrêt reçu, fermeture du serveur...")
    sys.exit(0)

def main():
    """Fonction principale du serveur."""
    # Configurer le gestionnaire de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrer le thread de nettoyage
    cleanup_thread = threading.Thread(target=clean_stale_rooms, daemon=True)
    cleanup_thread.start()
    
    # Socket pour les connexions principales
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    main_socket.bind((HOST, PORT))
    main_socket.listen(10)
    
    # Socket pour les pings
    ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ping_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ping_socket.bind((HOST, PING_PORT))
    ping_socket.listen(10)
    
    # Socket pour les statistiques
    stats_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stats_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    stats_socket.bind((HOST, STATS_PORT))
    stats_socket.listen(5)
    
    logging.info(f"Serveur démarré sur {HOST}:{PORT} (principal), {HOST}:{PING_PORT} (ping) et {HOST}:{STATS_PORT} (stats)")
    
    # Thread pour gérer les pings
    def handle_ping_connections():
        while True:
            try:
                client, addr = ping_socket.accept()
                ping_thread = threading.Thread(target=handle_ping, args=(client,))
                ping_thread.daemon = True
                ping_thread.start()
            except Exception as e:
                logging.error(f"Erreur lors de l'acceptation d'une connexion ping: {e}")
    
    ping_thread = threading.Thread(target=handle_ping_connections, daemon=True)
    ping_thread.start()
    
    # Thread pour gérer les statistiques
    def handle_stats_connections():
        while True:
            try:
                client, addr = stats_socket.accept()
                stats_thread = threading.Thread(target=handle_stats, args=(client,))
                stats_thread.daemon = True
                stats_thread.start()
            except Exception as e:
                logging.error(f"Erreur lors de l'acceptation d'une connexion stats: {e}")
    
    stats_thread = threading.Thread(target=handle_stats_connections, daemon=True)
    stats_thread.start()
    
    # Boucle principale pour les connexions
    try:
        while True:
            client, addr = main_socket.accept()
            logging.info(f"Nouvelle connexion de {addr[0]}:{addr[1]}")
            
            client_thread = threading.Thread(target=handle_client, args=(client, addr))
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        logging.info("Arrêt du serveur...")
    
    finally:
        main_socket.close()
        ping_socket.close()
        stats_socket.close()

if __name__ == "__main__":
    main()