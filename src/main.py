import pygame
from launcher import Launcher

def main():
    pygame.init()
    launcher = Launcher()
    launcher.run()
    pygame.quit()

if __name__ == "__main__":
    main()
