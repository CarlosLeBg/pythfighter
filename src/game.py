import pygame
import subprocess
import sys
import time
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

print(f"Arguments reçus : {sys.argv}")

# Initialisation
pygame.init()

# Récupérer les personnages sélectionnés
fighter_classes = {
    "AgileFighter": AgileFighter,
    "Tank": Tank,
    "BurstDamage": BurstDamage,
    "ThunderStrike": ThunderStrike,
    "Bruiser": Bruiser
}

try:
    selected_fighter_1 = sys.argv[1] if len(sys.argv) > 1 else "AgileFighter"
    selected_fighter_2 = sys.argv[2] if len(sys.argv) > 2 else "Tank"

    print(f"Chargement de {selected_fighter_1} et {selected_fighter_2}")
    
    fighter_1_data = fighter_classes[selected_fighter_1]()
    fighter_2_data = fighter_classes[selected_fighter_2]()

except KeyError as e:
    print(f"Erreur : Personnage inconnu {e}")
    sys.exit(1)


# Configuration de la fenêtre
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brawler")

# Définition des variables
FPS = 60
clock = pygame.time.Clock()
round_over = False

class Fighter():
    def __init__(self, player, x, y, data):
        self.player = player
        self.color = data.color
        self.health = data.stats["Vie"]
        self.damage = data.damage
        self.speed = data.speed
        self.rect = pygame.Rect(x, y, 80, 180)
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.attack_cooldown = 0
        self.alive = True

    def move(self, screen_width, screen_height, target):
        SPEED = self.speed
        GRAVITY = 2
        dx, dy = 0, 0
        key = pygame.key.get_pressed()
        
        if not self.attacking and self.alive:
            if self.player == 1:
                if key[pygame.K_a]: dx = -SPEED
                if key[pygame.K_d]: dx = SPEED
                if key[pygame.K_w] and not self.jump: self.vel_y = -30; self.jump = True
                if key[pygame.K_r]: self.attack(target)
            else:
                if key[pygame.K_LEFT]: dx = -SPEED
                if key[pygame.K_RIGHT]: dx = SPEED
                if key[pygame.K_UP] and not self.jump: self.vel_y = -30; self.jump = True
                if key[pygame.K_KP1]: self.attack(target)

        self.vel_y += GRAVITY
        dy += self.vel_y
        self.rect.x += dx
        self.rect.y += dy
        self.rect.y = min(self.rect.y, screen_height - 110)
        self.jump = self.rect.y < screen_height - 110
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attack_range = pygame.Rect(self.rect.x - 40, self.rect.y, 160, 180)
            if attack_range.colliderect(target.rect):
                target.health -= self.damage
                target.alive = target.health > 0
            self.attack_cooldown = 20

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Création des combattants
fighter_1 = Fighter(1, 200, 310, fighter_1_data)
fighter_2 = Fighter(2, 700, 310, fighter_2_data)

# Boucle du jeu
run = True
while run:
    clock.tick(FPS)
    screen.fill((50, 50, 50))
    pygame.draw.rect(screen, (30, 30, 30), (0, 450, SCREEN_WIDTH, 150))
    
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1)
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()
