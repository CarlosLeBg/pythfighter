import os
import sys
import subprocess
import pygame

def check_pygame_installation():
    try:
        import pygame
    except ImportError:
        print("Pygame non installé. Installation en cours...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, color, start_x, start_y):
        super().__init__()
        self.name = name
        self.color = color
        self.health = 100
        self.velocity = 5
        self.rect = pygame.Rect(start_x, start_y, 50, 50)

    def move(self, dx, dy):
        self.rect.x += dx * self.velocity
        self.rect.y += dy * self.velocity

    def attack(self, opponent):
        damage = 10
        if self.rect.colliderect(opponent.rect):
            opponent.health -= damage
            if opponent.health < 0:
                opponent.health = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        health_text = font.render(f"{self.name}: {self.health}", True, (255, 255, 255))
        surface.blit(health_text, (self.rect.x, self.rect.y - 20))

class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.options = ["Tank", "Assassin", "Sorcier"]
        self.selected = 0

    def draw(self, surface):
        surface.fill((30, 30, 30))
        title = self.font.render("Sélectionnez un personnage", True, (255, 255, 255))
        surface.blit(title, (200, 50))
        for index, option in enumerate(self.options):
            color = (255, 255, 0) if index == self.selected else (255, 255, 255)
            option_text = self.font.render(option, True, color)
            surface.blit(option_text, (250, 150 + index * 60))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.options)
        if keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.options)
        if keys[pygame.K_RETURN]:
            return self.options[self.selected]
        return None

def main():
    check_pygame_installation()
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pyth Fighter")

    global font
    font = pygame.font.Font(None, 36)

    menu = Menu()
    selected_character = None

    while selected_character is None:
        menu.draw(screen)
        pygame.display.flip()
        selected_character = menu.handle_input()

    # Initialisation des personnages sélectionnés
    if selected_character == "Tank":
        player1 = Character("Tank", (0, 255, 0), 100, 400)
        player2 = Character("Assassin", (0, 0, 255), 500, 400)  # En attendant de choisir un second joueur
    elif selected_character == "Assassin":
        player1 = Character("Assassin", (0, 0, 255), 100, 400)
        player2 = Character("Tank", (0, 255, 0), 500, 400)
    else:
        player1 = Character("Sorcier", (255, 0, 0), 100, 400)
        player2 = Character("Tank", (0, 255, 0), 500, 400)

    characters = [player1, player2]

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Mouvements du joueur 1
        if keys[pygame.K_a]:  # Gauche
            player1.move(-1, 0)
        if keys[pygame.K_d]:  # Droite
            player1.move(1, 0)
        if keys[pygame.K_SPACE]:  # Attaque
            player1.attack(player2)

        # Mouvements du joueur 2
        if keys[pygame.K_LEFT]:  # Gauche
            player2.move(-1, 0)
        if keys[pygame.K_RIGHT]:  # Droite
            player2.move(1, 0)
        if keys[pygame.K_RETURN]:  # Attaque
            player2.attack(player1)

        screen.fill((50, 50, 50))  # Couleur de fond
        pygame.draw.rect(screen, (150, 75, 0), (0, 550, 800, 50))  # Sol de l'arène

        for character in characters:
            character.draw(screen)

        # Vérifie si un personnage a perdu
        if player1.health == 0 or player2.health == 0:
            winner_text = font.render(f"{characters[0].name if characters[0].health > 0 else characters[1].name} a gagné !", True, (255, 255, 0))
            screen.blit(winner_text, (300, 250))
            pygame.display.flip()
            pygame.time.wait(2000)  # Attendre 2 secondes avant de quitter
            running = False

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
