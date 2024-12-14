import main
from main import *
import pygame 
<<<<<<< HEAD
from player import Thunderstrike

class Game:
    def __init__(self):
        #générer notre joueur
        self.player = Thunderstrike()

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
pygame.init()
#generation de fenetre de jeu
pygame.display.set_caption("Pythfighter")
screen=pygame.display.set_mode((1920, 1080))

#importation du fond du jeu
background=pygame.image.load('assets/Pixilart_App.jpg')
<<<<<<< HEAD

#charger notre jeu
game= Game()
=======
#charger le joueur
player=Thunderstrike()
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402

running = True
while running:
    
    #appliquation du background du jeu
    screen.blit(background, (0,0))
    
    #appliquer image du joueur
<<<<<<< HEAD
    screen.blit(game.player.image, game.player.rect)
=======
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402
    
    #mettre à jour l'écran
    pygame.display.flip()
    
    # si le joueur ferme la fenetre
    for event in pygame.event.get():
        #fermeture de jeu
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
<<<<<<< HEAD
            print("fermeture")
=======
            print("fermeture")
>>>>>>> eb338d57aa69c41f521d1f33b8e3bc419fcf3402
