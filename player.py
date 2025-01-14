import pygame

class Thunderstrike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.velocity = 5
        self.image = pygame.image.load('assets/player_image.png')  # Assurez-vous que le chemin de l'image est correct
        self.rect = self.image.get_rect()

def update_health_bar(self, surface):
    #dessiner barre de vie
    pygame.draw.rect(surface, (60, 63, 60), [1000,1000,self.max_health,1000])
    pygame.draw.rect(surface, (95,95,248), [1000,1000,self.health,1000])
    


