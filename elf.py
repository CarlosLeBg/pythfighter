import pygame
from controller_manager import DualSense
import sys

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre de jeu
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jeu avec Manette")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Chargement des personnages
characters = [
    {"name": "Guerrier", "color": RED, "speed": 5, "attack_power": 10},
    {"name": "Mage", "color": BLUE, "speed": 4, "attack_power": 15},
    {"name": "Archer", "color": GREEN, "speed": 6, "attack_power": 8},
    {"name": "Tank", "color": YELLOW, "speed": 3, "attack_power": 20},
    {"name": "Assassin", "color": PURPLE, "speed": 7, "attack_power": 12},
]

# Index du personnage sélectionné
selected_character = 0

# Initialisation du DualSense
try:
    controller = DualSense()
except Exception as e:
    print(f"Erreur : {e}")
    sys.exit(1)

# Fonction principale du jeu
def game_loop():
    global selected_character
    clock = pygame.time.Clock()
    running = True
    character_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]

    while running:
        screen.fill(WHITE)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Gestion des inputs de la manette
        for btn, state in controller.buttons.items():
            if state:  # Si un bouton est pressé
                if btn == "cross":  # Exemple d'action : attaque
                    print(f"{characters[selected_character]['name']} attaque!")
                elif btn == "circle":  # Exemple d'action : changer de personnage
                    selected_character = (selected_character + 1) % len(characters)
                    print(f"Personnage sélectionné : {characters[selected_character]['name']}")

        # Mouvement via les sticks
        move_x = controller.sticks['left_x']['value'] * characters[selected_character]["speed"]
        move_y = controller.sticks['left_y']['value'] * characters[selected_character]["speed"]
        character_position[0] += move_x
        character_position[1] += move_y

        # Contrainte des bords de l'écran
        character_position[0] = max(0, min(SCREEN_WIDTH, character_position[0]))
        character_position[1] = max(0, min(SCREEN_HEIGHT, character_position[1]))

        # Dessin du personnage
        pygame.draw.circle(
            screen,
            characters[selected_character]["color"],
            (int(character_position[0]), int(character_position[1])),
            20
        )

        # Mise à jour de l'écran
        pygame.display.flip()
        clock.tick(60)

    # Arrêt propre
    pygame.quit()
    controller.stop()

# Lancement du jeu
if __name__ == "__main__":
    game_loop()
