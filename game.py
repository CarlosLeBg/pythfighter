import main
from main import *
import pygame 
pygame.init()
#generation de fenetre de jeu
pygame.display.set_caption("Pythfighter")
pygame.display.set_mode((1920, 1080))

running = True

while running:
    # si le joueur ferme la fenetre
    for event in pygame.event.get():
        #fermeture de jeu
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("fermeture")