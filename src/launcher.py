import pygame
from game import Game
from character import Tank, Assassin, Sorcier, Mage, Archer

class Launcher:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 800))
        pygame.display.set_caption("Pyth Fighter - Launcher")
        self.clock = pygame.time.Clock()
        self.running = True
        self.characters = [Tank(), Assassin(), Sorcier(), Mage(), Archer()]
        self.selected_character1 = None
        self.selected_character2 = None
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 50)
        self.instructions_font = pygame.font.SysFont("Arial", 20)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw_menu()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Gestion des sélections de personnages pour les deux joueurs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and self.selected_character1 is None:
                    self.selected_character1 = self.characters[0]
                elif event.key == pygame.K_2 and self.selected_character1 is None:
                    self.selected_character1 = self.characters[1]
                elif event.key == pygame.K_3 and self.selected_character1 is None:
                    self.selected_character1 = self.characters[2]
                elif event.key == pygame.K_4 and self.selected_character1 is None:
                    self.selected_character1 = self.characters[3]
                elif event.key == pygame.K_5 and self.selected_character1 is None:
                    self.selected_character1 = self.characters[4]

                elif event.key == pygame.K_1 and self.selected_character1 is not None and self.selected_character2 is None:
                    self.selected_character2 = self.characters[0]
                elif event.key == pygame.K_2 and self.selected_character1 is not None and self.selected_character2 is None:
                    self.selected_character2 = self.characters[1]
                elif event.key == pygame.K_3 and self.selected_character1 is not None and self.selected_character2 is None:
                    self.selected_character2 = self.characters[2]
                elif event.key == pygame.K_4 and self.selected_character1 is not None and self.selected_character2 is None:
                    self.selected_character2 = self.characters[3]
                elif event.key == pygame.K_5 and self.selected_character1 is not None and self.selected_character2 is None:
                    self.selected_character2 = self.characters[4]

                elif event.key == pygame.K_RETURN and self.selected_character1 and self.selected_character2:
                    self.start_game()

    def draw_menu(self):
        self.screen.fill((50, 50, 50))
        title_surface = self.title_font.render("Pyth Fighter - Choisissez vos personnages", True, (255, 255, 255))
        self.screen.blit(title_surface, (200, 50))

        # Instructions
        instructions = [
            "Joueur 1: Choisissez votre personnage (1-5)",
            "Joueur 2: Choisissez votre personnage (1-5) après Joueur 1",
            "Appuyez sur Entrée pour lancer le combat"
        ]
        for i, text in enumerate(instructions):
            instruction_surface = self.instructions_font.render(text, True, (200, 200, 200))
            self.screen.blit(instruction_surface, (50, 150 + i * 30))

        # Affichage des personnages disponibles
        for i, character in enumerate(self.characters):
            character_info = f"{i + 1}. {character.name} (HP: {character.max_health}, ATK: {character.attack})"
            character_surface = self.font.render(character_info, True, (255, 255, 255))
            self.screen.blit(character_surface, (100, 300 + i * 50))

        # Affichage des choix actuels des joueurs
        if self.selected_character1:
            selected1_surface = self.font.render(f"Joueur 1 a choisi: {self.selected_character1.name}", True, (0, 255, 0))
            self.screen.blit(selected1_surface, (600, 300))
        if self.selected_character2:
            selected2_surface = self.font.render(f"Joueur 2 a choisi: {self.selected_character2.name}", True, (0, 0, 255))
            self.screen.blit(selected2_surface, (600, 350))

    def start_game(self):
        game = Game(self.selected_character1, self.selected_character2)
        game.run()
