import os
import sys
import subprocess

# Vérifie et installe automatiquement pygame si nécessaire
try:
    import pygame
except ImportError:
    print("Pygame non installé. Installation en cours...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

def main():
    # Initialisation de pygame
    pygame.init()

    # Générer la fenêtre
    pygame.display.set_caption("Pyth Fighter")
    screen = pygame.display.set_mode((1920, 1080))

    # Importer l'arrière-plan
    try:
        background = pygame.image.load('background.png')
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image d'arrière-plan : {e}")
        pygame.quit()
        sys.exit()

    running = True

    # Boucle principale du jeu
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Si le joueur ferme la fenêtre
                running = False

        # Affichage de l'arrière-plan
        screen.blit(background, (0, 0))
        pygame.display.flip()

    # Fermeture propre de pygame
    pygame.quit()
    print("Fermeture du jeu")

if __name__ == "__main__":
    main()
