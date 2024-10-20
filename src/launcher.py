import pygame
import pygame.joystick
import sys

class GameLauncher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pyth Fighter - Launcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.running = True
        self.controllers = self.detect_controllers()
        self.selected_option = 0
        self.options = ["Start Game", "Controller Settings", "Keyboard Settings", "Exit"]
        self.background_color = (30, 30, 30)
        self.highlight_color = (255, 0, 0)
        self.default_color = (255, 255, 255)

    def detect_controllers(self):
        pygame.joystick.init()
        controllers = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            controllers.append(joystick.get_name())
        return controllers

    def draw_menu(self):
        self.screen.fill(self.background_color)
        title_text = self.font.render("Welcome to Pyth Fighter", True, self.default_color)
        self.screen.blit(title_text, (200, 50))

        for index, option in enumerate(self.options):
            color = self.highlight_color if index == self.selected_option else self.default_color
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, (350, 150 + index * 70))

        if self.controllers:
            controllers_text = self.font.render("Connected Controllers:", True, self.default_color)
            self.screen.blit(controllers_text, (50, 400))
            for i, controller in enumerate(self.controllers):
                controller_text = self.font.render(controller, True, self.default_color)
                self.screen.blit(controller_text, (70, 450 + i * 40))

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
                elif event.type == pygame.JOYBUTTONDOWN:
                    if self.selected_option == 0:  # Start Game
                        self.start_game()

            self.draw_menu()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

    def select_option(self):
        if self.selected_option == 0:  # Start Game
            self.start_game()
        elif self.selected_option == 1:  # Controller Settings
            self.open_controller_settings()
        elif self.selected_option == 2:  # Keyboard Settings
            self.open_keyboard_settings()
        elif self.selected_option == 3:  # Exit
            self.running = False

    def start_game(self):
        try:
            import main
            main.main()
        except Exception as e:
            print(f"Error starting the game: {e}")

    def open_controller_settings(self):
        print("Opening Controller Settings...")  # Placeholder
        # Logic for controller settings can be implemented here

    def open_keyboard_settings(self):
        print("Opening Keyboard Settings...")  # Placeholder
        # Logic for keyboard settings can be implemented here

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()
