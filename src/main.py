import pygame
from launcher import Launcher

def main():
    try:
        pygame.init()
        launcher = Launcher()
        launcher.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()