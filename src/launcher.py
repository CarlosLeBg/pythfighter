import pygame
import pygame.joystick
import sys

class GameLauncher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter - Launcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.controllers = self.detect_controllers()
        self.selected_option = 0
        self.options = ["Start Game", "Controller Settings", "Keyboard Settings", "Exit"]

    def detect_controllers(self):
        pygame.joystick.init()
        controllers = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            controllers.append(joystick.get_name())
        return controllers

    def draw_menu(self):
        self.screen.fill((50, 50, 50))  # Change to a dark gray background
        title_text = self.font.render("Welcome to Pyth Fighter", True, (255, 255, 255))
        self.screen.blit(title_text, (200, 50))

        for index, option in enumerate(self.options):
            color = (255, 0, 0) if index == self.selected_option else (255, 255, 255)
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, (350, 150 + index * 50))

        if self.controllers:
            controllers_text = self.font.render("Connected Controllers:", True, (255, 255, 255))
            self.screen.blit(controllers_text, (50, 400))
            for i, controller in enumerate(self.controllers):
                controller_text = self.font.render(controller, True, (255, 255, 255))
                self.screen.blit(controller_text, (70, 450 + i * 30))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        self.select_option()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if self.selected_option == 0:  # Start Game
                        self.start_game()  # Call to start the game

            self.draw_menu()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

    def select_option(self):
        if self.selected_option == 0:  # Start Game
            self.start_game()
        elif self.selected_option == 1:  # Controller Settings
            print("Open Controller Settings...")  # Placeholder
        elif self.selected_option == 2:  # Keyboard Settings
            print("Open Keyboard Settings...")  # Placeholder
        elif self.selected_option == 3:  # Exit
            self.running = False

    def start_game(self):
        try:
            import main  # Assure que main.py est dans le même répertoire
            main.main()  # Démarre le jeu
        except Exception as e:
            print(f"Erreur lors du démarrage du jeu : {e}")

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()
