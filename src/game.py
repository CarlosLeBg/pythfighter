import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

# Initialisation de Pygame
pygame.init()

# Définition des couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Taille de l'image de fond
bg_image = pygame.image.load("src/assets/backg.jpg")  # Utilise backg.jpg
bg_width, bg_height = bg_image.get_size()

# Configuration de la fenêtre (en fonction de la taille de l'image)
VISIBLE_WIDTH = 1280  # Zone visible
VISIBLE_HEIGHT = 720  # Zone visible
screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
pygame.display.set_caption("Brawler")

# Forcer le redimensionnement de l'image pour qu'elle occupe toute la fenêtre
bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))

# Récupération des personnages à partir de la config
fighter_classes = {
    "AgileFighter": AgileFighter,
    "Tank": Tank,
    "BurstDamage": BurstDamage,
    "ThunderStrike": ThunderStrike,
    "Bruiser": Bruiser
}

# Sélection des personnages
selected_fighter_1 = "AgileFighter"
selected_fighter_2 = "Tank"

fighter_1_data = fighter_classes[selected_fighter_1]()
fighter_2_data = fighter_classes[selected_fighter_2]()

# Configuration du jeu
FPS = 60
clock = pygame.time.Clock()

# Classe Fighter
class Fighter:
    def __init__(self, player, x, y, data):
        self.player = player
        self.name = data.name
        self.speed = data.speed
        self.damage = data.damage
        self.abilities = data.abilities
        self.style = data.style
        self.stats = data.stats
        self.description = data.description
        self.combo_tips = data.combo_tips
        self.lore = data.lore
        self.color = data.color
        self.special_ability = data.special_ability
        self.weakness = data.weakness
        self.health = self.stats["Vie"]
        self.max_health = self.health
        self.rect = pygame.Rect(x, y, 80, 180)
        self.hitbox = pygame.Rect(x + 20, y + 40, 40, 140)
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.attack_cooldown = 0
        self.alive = True

    def move(self, keys, screen_width, screen_height):
        dx, dy = 0, 0
        GRAVITY = 0.5
        JUMP_FORCE = -15
        GROUND_Y = screen_height - 150

        if not self.attacking and self.alive:
            if self.player == 1:
                if keys[pygame.K_a]: dx = -self.speed
                if keys[pygame.K_d]: dx = self.speed
                if keys[pygame.K_w] and not self.jump: self.vel_y = JUMP_FORCE; self.jump = True
                if keys[pygame.K_r]: self.attack()
            else:
                if keys[pygame.K_LEFT]: dx = -self.speed
                if keys[pygame.K_RIGHT]: dx = self.speed
                if keys[pygame.K_UP] and not self.jump: self.vel_y = JUMP_FORCE; self.jump = True
                if keys[pygame.K_KP1]: self.attack()

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.y + dy > GROUND_Y:
            dy = GROUND_Y - self.rect.y
            self.vel_y = 0
            self.jump = False

        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(self.rect.x, screen_width - 80))
        self.rect.y = max(0, self.rect.y)

        self.hitbox.topleft = (self.rect.x + 20, self.rect.y + 40)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_cooldown = 20

    def draw(self, surface, show_hitbox=False):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)
        
        if show_hitbox:  # Afficher la hitbox si activée par F3
            pygame.draw.rect(surface, WHITE, self.hitbox, 1)

        # Amélioration de la barre de vie
        health_bar_width = 200
        health_bar_height = 20
        if self.player == 1:
            pygame.draw.rect(surface, RED, (50, 50, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, GREEN, (50, 50, health_bar_width * (self.health / self.max_health), health_bar_height))
            font = pygame.font.SysFont("Arial", 18)
            health_text = font.render(f"{self.health}/{self.max_health}", True, BLACK)
            surface.blit(health_text, (50 + health_bar_width + 10, 50))
        else:
            pygame.draw.rect(surface, RED, (VISIBLE_WIDTH - 250, 50, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, GREEN, (VISIBLE_WIDTH - 250, 50, health_bar_width * (self.health / self.max_health), health_bar_height))
            font = pygame.font.SysFont("Arial", 18)
            health_text = font.render(f"{self.health}/{self.max_health}", True, BLACK)
            surface.blit(health_text, (VISIBLE_WIDTH - 250 - health_bar_width - 10, 50))

    def use_special_ability(self):
        # Code spécifique pour utiliser l'abilité spéciale
        pass

    def collide_with(self, other):
        return self.hitbox.colliderect(other.hitbox)

# Ajustement de la position initiale des combattants
fighter_1 = Fighter(1, 50, VISIBLE_HEIGHT - 180, fighter_1_data)
fighter_2 = Fighter(2, VISIBLE_WIDTH - 130, VISIBLE_HEIGHT - 180, fighter_2_data)

# Variable pour afficher les hitboxes avec F3
show_hitbox = False

# Main game loop
running = True
while running:
    clock.tick(FPS)

    # Remplir l'écran avec l'arrière-plan redimensionné
    screen.blit(bg_image, (0, 0))

    # Remplir le sol
    pygame.draw.rect(screen, (30, 30, 30), (0, VISIBLE_HEIGHT - 150, VISIBLE_WIDTH, 150))

    # Déplacer et dessiner les combattants
    keys = pygame.key.get_pressed()
    fighter_1.move(keys, VISIBLE_WIDTH, VISIBLE_HEIGHT)
    fighter_2.move(keys, VISIBLE_WIDTH, VISIBLE_HEIGHT)

    # Vérification de la collision entre l'attaque et l'adversaire
    if fighter_1.attacking and fighter_1.collide_with(fighter_2):
        fighter_2.health -= fighter_1.damage  # Infliger des dégâts à l'ennemi
        fighter_1.attacking = False

    if fighter_2.attacking and fighter_2.collide_with(fighter_1):
        fighter_1.health -= fighter_2.damage  # Infliger des dégâts à l'ennemi
        fighter_2.attacking = False

    # Afficher les combattants
    fighter_1.draw(screen, show_hitbox)
    fighter_2.draw(screen, show_hitbox)

    # Gérer les événements de la fenêtre
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:  # Activer/Désactiver l'affichage des hitboxes avec F3
                show_hitbox = not show_hitbox

    # Mettre à jour l'affichage
    pygame.display.update()

pygame.quit()
