import pygame

pygame.init()

# Paramètres de la fenêtre de jeu
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jeu avec Manette")

# Classe du joueur
class Player:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.hit_box = (self.x + 20, self.y + 20)  # La hitbox est définie dans la classe Player

# Classe pour la barre de vie
class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

    def draw(self, surface):  # Méthode pour dessiner la barre de vie
        ratio = self.hp / self.max_hp
        # Dessine le fond de la barre de vie (rouge)
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        # Dessine la barre de vie (verte) 
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))

# Création de la barre de vie
health_bar = HealthBar(250, 200, 300, 40, 100)

# Boucle principale du jeu
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mise à jour de l'affichage
    screen.fill((0, 0, 0))  # Efface l'écran en noir
    health_bar.draw(screen)  # Dessine la barre de vie

    pygame.display.flip()  # Met à jour l'écran

pygame.quit()
print("Fermeture du jeu")