import main
from main import *
import pygame 

class Thunderstrike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.velocity= 5
        self.image = pygame.image.load()
        
pygame.init()
#generation de fenetre de jeu
pygame.display.set_caption("Pythfighter")
screen=pygame.display.set_mode((1920, 1080))

#importation du fond du jeu
background=pygame.image.load('assets/Pixilart_App.jpg')
running = True

while running:
    
    #appliquation du background du jeu
    screen.blit(background, (0,0))
    
    #mettre à jour l'écran
    pygame.display.flip()
    
    # si le joueur ferme la fenetre
    for event in pygame.event.get():
        #fermeture de jeu
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("fermeture")
