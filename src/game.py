import pygame
import subprocess
import sys
import time
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
import pygame.freetype  # Pour les polices de texte avancées
import pygame_gui       # Pour une interface utilisateur

print(f"Arguments reçus : {sys.argv}")

# Initialisation
pygame.init()

# Charger l'image de fond
bg_image = pygame.image.load("src/assets/bg.jpg")

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


# Configuration de la fenêtre en plein écran
SCREEN_WIDTH = 1920  # Largeur d'écran en plein écran
SCREEN_HEIGHT = 1080  # Hauteur d'écran en plein écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Brawler")

# Définition des variables
FPS = 60
clock = pygame.time.Clock()
round_over = False

# Initialisation du gestionnaire d'interface (UI)
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

class Fighter():
    def __init__(self, player, x, y, data):
        self.player = player
        self.color = data.color
        self.health = data.stats["Vie"]
        self.max_health = self.health  # Sauvegarder la santé maximale
        self.damage = data.damage
        self.speed = data.speed
        self.rect = pygame.Rect(x, y, 80, 180)
        self.hitbox = pygame.Rect(x + 20, y + 20, 40, 160)  # Hitbox plus détaillée
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

        # Limites de déplacement
        max_x = screen_width - self.rect.width
        max_y = screen_height - 150  # Pour éviter que les personnages tombent en dessous du sol
        
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

        # Limiter les déplacements dans les dimensions de l'écran
        self.rect.x += dx
        self.rect.y += dy

        # Empêcher les personnages de sortir de l'écran
        self.rect.x = max(0, min(self.rect.x, max_x))
        self.rect.y = min(self.rect.y, max_y)  # Le personnage ne peut pas tomber sous le sol
        
        self.jump = self.rect.y < max_y
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attack_range = pygame.Rect(self.rect.x - 40, self.rect.y, 160, 180)
            if attack_range.colliderect(target.hitbox):  # Utiliser la hitbox du personnage cible
                target.health -= self.damage
                target.alive = target.health > 0
            self.attack_cooldown = 20

    def draw(self, surface):
        # Dessiner le personnage avec un contour plus détaillé
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)  # Contour noir autour du personnage
        
        # Dessiner la hitbox pour déboguer
        pygame.draw.rect(surface, (255, 255, 255), self.hitbox, 1)  # Hitbox en blanc

        # Dessiner la barre de vie en haut à gauche pour le joueur 1 et en haut à droite pour le joueur 2
        health_bar_width = 200
        health_bar_height = 20
        if self.player == 1:
            pygame.draw.rect(surface, (255, 0, 0), (50, 50, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, (0, 255, 0), (50, 50, health_bar_width * (self.health / self.max_health), health_bar_height))
        else:
            pygame.draw.rect(surface, (255, 0, 0), (SCREEN_WIDTH - 250, 50, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, (0, 255, 0), (SCREEN_WIDTH - 250, 50, health_bar_width * (self.health / self.max_health), health_bar_height))

# Création des combattants
fighter_1 = Fighter(1, 200, SCREEN_HEIGHT - 300, fighter_1_data)  # Positionner un peu au-dessus du bas de l'écran
fighter_2 = Fighter(2, 700, SCREEN_HEIGHT - 300, fighter_2_data)  # Positionner un peu au-dessus du bas de l'écran

# Boucle du jeu
run = True
while run:
    clock.tick(FPS)
    
    # Afficher le fond
    bg_image_resized = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Adapter l'arrière-plan à la taille de la fenêtre
    screen.blit(bg_image_resized, (0, 0))
    
    # Dessiner le sol
    pygame.draw.rect(screen, (30, 30, 30), (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))
    
    # Mouvements et dessins des combattants
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1)
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    # Mise à jour de l'interface (UI)
    manager.update(clock.get_time())

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        manager.process_events(event)

pygame.quit()
