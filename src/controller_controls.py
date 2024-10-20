import pygame

class ControllerControls:
    def __init__(self, player):
        self.player = player
        pygame.joystick.init()  # Initialiser les manettes
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def update(self):
        if self.controller.get_init():
            left_x = self.controller.get_axis(0)
            left_y = self.controller.get_axis(1)

            if left_x < -0.5:
                self.player.move(-1, 0)
            elif left_x > 0.5:
                self.player.move(1, 0)

            if left_y < -0.5:
                self.player.move(0, -1)
            elif left_y > 0.5:
                self.player.move(0, 1)
