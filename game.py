import pygame
from player import Thunderstrike

class Game:
    def __init__(self):
        self.player = Thunderstrike()

class Thunderstrike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.velocity = 5
        self.image = pygame.image.load('assets/player_image.png')  # Assurez-vous que le chemin de l'image est correct
        self.rect = self.image.get_rect()

pygame.init()

pygame.display.set_caption("Pythfighter")
screen = pygame.display.set_mode((1920, 1080))

try:
    background = pygame.image.load('assets/Pixilart_App.jpg')
except pygame.error as e:
    print(f"Erreur lors du chargement de l'image de fond : {e}")
    pygame.quit()
    exit()

game = Game()

running = True
while running:
    screen.blit(background, (0, 0))
    screen.blit(game.player.image, game.player.rect)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
<<<<<<< HEAD
print("Fermeture du jeu")
=======
print("Fermeture du jeu")
>>>>>>> 4cbb1d559d6f785b60f608b0f9155873abff85c9
