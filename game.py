import pygame
from player import Thunderstrike

class Game:
    def __init__(self):
        # Générer notre joueur
        self.player = Thunderstrike()

# Initialiser Pygame
pygame.init()

# Génération de la fenêtre de jeu
pygame.display.set_caption("Pythfighter")
screen = pygame.display.set_mode((1920, 1080))

# Importation du fond du jeu
try:
    background = pygame.image.load('assets/Pixilart_App.jpg')
except pygame.error as e:
    print(f"Erreur lors du chargement de l'image de fond : {e}")
    pygame.quit()
    exit()

# Charger notre jeu
game = Game()

# Boucle principale
running = True
while running:
    # Appliquer le background du jeu
    screen.blit(background, (0, 0))

    # Appliquer l'image du joueur
    screen.blit(game.player.image, game.player.rect)

    # Mettre à jour l'écran
    pygame.display.flip()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quitter Pygame proprement
pygame.quit()
print("Fermeture du jeu")
