import pygame 

class Thunderstrike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.velocity= 5
        self.image = pygame.image.load()
        self.rect =self.image.get.rect()
        
pygame.init()
#generation de fenetre de jeu
pygame.display.set_caption("Pythfighter")
screen=pygame.display.set_mode((1920, 1080))

#importation du fond du jeu
background=pygame.image.load('assets/logo-bg.png')
#charger le joueur
player=Thunderstrike()

running = True
while running:
    
    #appliquation du background du jeu
    screen.blit(background, (0,0))
    
    #appliquer image du joueur
    
    #mettre à jour l'écran
    pygame.display.flip()
    
    # si le joueur ferme la fenetre
    for event in pygame.event.get():
        #fermeture de jeu
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("fermeture")