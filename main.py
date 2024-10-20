import os
import sys
import subprocess
from game import Game

try:
    import pygame
except ImportError:
    print("Pygame non installé. Installation en cours...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    print("Fermeture du jeu")

if __name__ == "__main__":
    main()
