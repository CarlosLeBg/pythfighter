import pygame
from characters import Tank, Assassin, Sorcier

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

    def load_assets(self):
        try:
            self.background = pygame.image.load('src/background.png')
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image d'arrière-plan : {e}")
            pygame.quit()
            sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_controls(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player1.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.player1.move(1, 0)
        if keys[pygame.K_UP]:
            self.player1.move(0, -1)
        if keys[pygame.K_DOWN]:
            self.player1.move(0, 1)

        if keys[pygame.K_a]:
            self.player2.move(-1, 0)
        if keys[pygame.K_d]:
            self.player2.move(1, 0)
        if keys[pygame.K_w]:
            self.player2.move(0, -1)
        if keys[pygame.K_s]:
            self.player2.move(0, 1)

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
        self.screen.blit(self.background, (0, 0))
        self.characters.draw(self.screen)
        pygame.display.flip()
