import pygame
pygame.init()

#generer la fenetre
pygame.display.set_caption("pythfighter")
pygame.display.set_mode((1920, 1080))

running = True

#boucle pour que la fenetre reste eveillé
while running:
    #si le joueur ferme cette fentre
    for event in pygame.event.get():
        #que l'evenement est fermeture de fenetre
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

