import main
from main import *
import pygame 
from player import Thunderstrike

class Game:
    def __init__(self):
        #générer notre joueur
        self.player = Thunderstrike()

pygame.init()
#generation de fenetre de jeu
pygame.display.set_caption("Pythfighter")
screen=pygame.display.set_mode((1920, 1080))

#importation du fond du jeu
background=pygame.image.load('assets/Pixilart_App.jpg')

#charger notre jeu
game= Game()

running = True
while running:
    
    #appliquation du background du jeu
    screen.blit(background, (0,0))
    
    #appliquer image du joueur
    screen.blit(game.player.image, game.player.rect)
    
    #mettre à jour l'écran
    pygame.display.flip()
    
    # si le joueur ferme la fenetre
    for event in pygame.event.get():
        #fermeture de jeu
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("fermeture")