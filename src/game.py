import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.velocity = 5
        self.image = pygame.image.load('assets/player.png')
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 500

class Game:
    def __init__(self):
        # générer joueur
        self.player = Player()

def damage(self, amount):
    # infliger dégats
    self.health -=amount
    # vérifier si un nouveau nb de pt de vie inférieur ou égal à 0
    if self.health <= 0:
        self.rect.x = 1000
        self.health = self.max_health

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

    #actualiser barre de vie du joueur
    game.player.update_health_bar(screen)
            

pygame.quit()
print("Fermeture du jeu")