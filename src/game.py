import pygame
from characters import Tank, Assassin
from keyboard_controls import KeyboardControls
from controller_controls import ControllerControls

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("Pyth Fighter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.characters = pygame.sprite.Group()
        self.player1 = Tank()
        self.player2 = Assassin()
        self.characters.add(self.player1)
        self.characters.add(self.player2)
        self.load_assets()
        self.keyboard_controls = KeyboardControls(self.player1)
        self.controller_controls = ControllerControls(self.player2)

    def load_assets(self):
        pass  # Pas d'assets pour l'instant

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_controls(self):
        keys = pygame.key.get_pressed()
        self.keyboard_controls.update(keys)
        self.controller_controls.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.handle_controls()
            self.update()
            self.draw()
            self.clock.tick(60)

    def update(self):
        self.characters.update()

    def draw(self):
        self.screen.fill((0, 0, 0))  # Effacer l'écran avec une couleur noire
        self.characters.draw(self.screen)
        pygame.display.flip()
