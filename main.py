import pygame
pygame.init()

#generer la fenetre
pygame.display.set_caption("pythfighter")
screen = pygame.display.set_mode((1920, 1080))

#importer l'arriere plan
background=pygame.image.load('nomdufichier.jpg')

running = True

#boucle pour que la fenetre reste eveillé
while running:

    #arrriere plan
    screen.blit(background,(400,300))
    pygame.display.flip()

    #si le joueur ferme cette fentre
    for event in pygame.event.get():
        #que l'evenement est fermeture de fenetre
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Fermeture du jeu")
