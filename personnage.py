import pygame

# la j'ai creer les differentes classe potentiel avec les differences de pv, de vitesse etc...

#création d'un joueur
class Tank(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.health = 150
        self.max_health = 150
        self.attack = 12
        self.velocity = 5
        self.image = pygame.image.load('nomdufichier')
        self.rect = self.image.get_rect()
        self.rect.x = 1000
        self.rect.y=200



#création d'un joueur
class Assassin(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 9
        self.velocity = 10
        self.image = pygame.image.load('nomdufichier')
        self.rect = self.image.get_rect()
        self.rect.x = 1000
        self.rect.y=200



#création d'un joueur
class Sorcier(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 90
        self.attack = 15
        self.velocity = 7
        self.image = pygame.image.load('nomdufichier')
        self.rect = self.image.get_rect()
        self.rect.x = 1000
        self.rect.y=200
