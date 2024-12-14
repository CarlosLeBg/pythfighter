<<<<<<< HEAD
import main
from main import *
import pygame 
<<<<<<< HEAD
=======
import pygame
>>>>>>> 8720023afd4022c50b41d013531ea11d4bea7b87
from player import Thunderstrike

class Game:
    def __init__(self):
        # Générer notre joueur
        self.player = Thunderstrike()

<<<<<<< HEAD
=======

class Thunderstrike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.velocity= 5
        self.image = pygame.image.load()
        self.rect =self.image.get.rect()
        
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402
=======
# Initialiser Pygame
>>>>>>> 8720023afd4022c50b41d013531ea11d4bea7b87
pygame.init()

# Génération de la fenêtre de jeu
pygame.display.set_caption("Pythfighter")
screen = pygame.display.set_mode((1920, 1080))

<<<<<<< HEAD
#importation du fond du jeu
background=pygame.image.load('assets/Pixilart_App.jpg')
<<<<<<< HEAD

#charger notre jeu
game= Game()
=======
#charger le joueur
player=Thunderstrike()
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402
=======
# Importation du fond du jeu
try:
    background = pygame.image.load('assets/Pixilart_App.jpg')
except pygame.error as e:
    print(f"Erreur lors du chargement de l'image de fond : {e}")
    pygame.quit()
    exit()

# Charger notre jeu
game = Game()
>>>>>>> 8720023afd4022c50b41d013531ea11d4bea7b87

# Boucle principale
running = True
while running:
<<<<<<< HEAD
    
    #appliquation du background du jeu
    screen.blit(background, (0,0))
    
    #appliquer image du joueur
<<<<<<< HEAD
    screen.blit(game.player.image, game.player.rect)
=======
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402
    
    #mettre à jour l'écran
=======
    # Appliquer le background du jeu
    screen.blit(background, (0, 0))

    # Appliquer l'image du joueur
    screen.blit(game.player.image, game.player.rect)

    # Mettre à jour l'écran
>>>>>>> 8720023afd4022c50b41d013531ea11d4bea7b87
    pygame.display.flip()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
<<<<<<< HEAD
            pygame.quit()
<<<<<<< HEAD
            print("fermeture")
=======
            print("fermeture")
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402
=======

# Quitter Pygame proprement
pygame.quit()
print("Fermeture du jeu")
>>>>>>> 8720023afd4022c50b41d013531ea11d4bea7b87
