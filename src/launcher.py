import pygame
import sys

class GameLauncher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter - Launcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.running = True
        self.selected_option = 0
        self.options = ["Start Game", "Controller Settings", "Keyboard Settings", "Exit"]
        self.background_color = (30, 30, 30)
        self.highlight_color = (255, 0, 0)
        self.default_color = (255, 255, 255)

    def draw_menu(self):
        self.screen.fill(self.background_color)
        title_text = self.font.render("Welcome to Pyth Fighter", True, self.default_color)
        self.screen.blit(title_text, (200, 50))

        for index, option in enumerate(self.options):
            color = self.highlight_color if index == self.selected_option else self.default_color
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, (350, 150 + index * 70))

        instructions_text = self.font.render("Use UP/DOWN to navigate, ENTER to select.", True, self.default_color)
        self.screen.blit(instructions_text, (50, 500))
        
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

            self.draw_menu()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

    def select_option(self):
        if self.selected_option == 0:  # Start Game
            self.start_game()
        elif self.selected_option == 1:  # Controller Settings
            print("Controller Settings Not Implemented Yet.")
        elif self.selected_option == 2:  # Keyboard Settings
            print("Keyboard Settings Not Implemented Yet.")
        elif self.selected_option == 3:  # Exit
            self.running = False

    def start_game(self):
        try:
            print("Starting the game...")
            import main
            main.main()
        except Exception as e:
            print(f"Error starting the game: {e}")

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()
