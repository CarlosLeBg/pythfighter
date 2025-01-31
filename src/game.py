import pygame
import sys
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
VISIBLE_WIDTH = SCREEN_WIDTH * 0.8  # Ajuster la largeur visible
VISIBLE_HEIGHT = SCREEN_HEIGHT * 0.8  # Ajuster la hauteur visible
screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
pygame.display.set_caption("Brawler")

# Charger l'image de fond et la redimensionner
bg_image = pygame.image.load("src/assets/backg.jpg")
bg_image = pygame.transform.scale(bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))

# Définition des couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Récupération des personnages à partir de la config
fighter_classes = {
    "AgileFighter": AgileFighter,
    "Tank": Tank,
    "BurstDamage": BurstDamage,
    "ThunderStrike": ThunderStrike,
    "Bruiser": Bruiser
}

# Configuration du jeu
FPS = 60
clock = pygame.time.Clock()

class Fighter:
    def __init__(self, name, speed, damage, abilities, style, stats, description, combo_tips, lore, color, special_ability, weakness):
        self.name = name
        self.speed = speed
        self.damage = damage
        self.abilities = abilities
        self.style = style
        self.stats = stats
        self.description = description
        self.combo_tips = combo_tips
        self.lore = lore
        self.color = color
        self.special_ability = special_ability
        self.weakness = weakness

        self.health = self.stats["Vie"]
        self.max_health = self.health
        self.rect = pygame.Rect(0, 0, 80, 180)
        self.hitbox = pygame.Rect(self.rect.x + 20, self.rect.y + 40, 40, 140)
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.attack_cooldown = 0
        self.alive = True

    def move(self, keys, screen_width, screen_height):
        dx, dy = 0, 0
        GRAVITY = 0.5
        JUMP_FORCE = -15
        GROUND_Y = screen_height - 150  # Y du sol ajusté

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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def draw(self, surface):
        # Dessiner le personnage sans les bordures
        pygame.draw.rect(surface, self.color, self.rect)

        # Dessiner la barre de santé sans bordures
        health_bar_width = 200
        health_bar_height = 20
        if self.player == 1:
            pygame.draw.rect(surface, RED, (50, 50, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, GREEN, (50, 50, health_bar_width * (self.health / self.max_health), health_bar_height))
        else:
            pygame.draw.rect(surface, RED, (SCREEN_WIDTH - 250, 50, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, GREEN, (SCREEN_WIDTH - 250, 50, health_bar_width * (self.health / self.max_health), health_bar_height))

# Sélection des personnages à partir des arguments passés
selected_fighter_1 = "AgileFighter"
selected_fighter_2 = "Tank"

fighter_1_data = fighter_classes[selected_fighter_1]()
fighter_2_data = fighter_classes[selected_fighter_2]()

fighter_1 = Fighter(**fighter_1_data.__dict__)
fighter_1.player = 1
fighter_2 = Fighter(**fighter_2_data.__dict__)
fighter_2.player = 2

# Ajouter un effet d'écran cassé avec des bords colorés
def draw_broken_screen(surface, width, height):
    # Cacher les bords avec une couleur (ex: rouge)
    color = RED  # Tu peux changer cette couleur selon ton envie
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, width, 10))  # Haut
    pygame.draw.rect(surface, color, pygame.Rect(0, height - 10, width, 10))  # Bas
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, 10, height))  # Gauche
    pygame.draw.rect(surface, color, pygame.Rect(width - 10, 0, 10, height))  # Droite

# Function to check for victory
def check_victory():
    if not fighter_1.alive:
        return 2
    elif not fighter_2.alive:
        return 1
    return None

# Main game loop
running = True
while running:
    clock.tick(FPS)

    # Remplir l'écran avec le fond
    screen.blit(bg_image, (0, 0))

    # Simuler un écran cassé avec des bords colorés
    draw_broken_screen(screen, VISIBLE_WIDTH, VISIBLE_HEIGHT)

    # Remplir le sol
    pygame.draw.rect(screen, (30, 30, 30), (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))

    # Déplacer et dessiner les combattants
    keys = pygame.key.get_pressed()
    fighter_1.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
    fighter_2.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
    fighter_1.draw(screen)
    fighter_2.draw(screen) # type: ignore

    # Vérifier la victoire
    winner = check_victory()
    if winner:
        # Afficher le message de victoire
        font = pygame.font.SysFont(None, 55)
        win_text = "Player 1 Wins!" if winner == 1 else "Player 2 Wins!"
        text = font.render(win_text, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.delay(2000)
        running = False

    # Mettre à jour l'affichage
    pygame.display.update()

    # Gérer les événements de la fenêtre
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
