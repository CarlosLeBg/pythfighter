import os
import sys
import subprocess
import pygame
from game import Game
from launcher import Launcher

# Vérifie et installe automatiquement pygame si nécessaire
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

if __name__ == "__main__":
    main()
