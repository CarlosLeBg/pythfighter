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

def main():
    check_pygame_installation()
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pyth Fighter")

    # Couleurs des personnages
    colors = {
        "Tank": (0, 255, 0),     # Vert
        "Assassin": (0, 0, 255), # Bleu
        "Sorcier": (255, 0, 0)   # Rouge
    }

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))  # Couleur de fond

        # Dessiner les personnages sous forme de rectangles colorés
        pygame.draw.rect(screen, colors["Tank"], (100, 300, 50, 50))     # Tank
        pygame.draw.rect(screen, colors["Assassin"], (200, 300, 50, 50))  # Assassin
        pygame.draw.rect(screen, colors["Sorcier"], (300, 300, 50, 50))   # Sorcier

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
