import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, health, attack, velocity, color, start_x, start_y):
        super().__init__()
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.velocity = velocity
        self.color = color
        
        self.image = pygame.Surface((50, 50))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

    def move(self, x_offset, y_offset):
        self.rect.x += x_offset * self.velocity
        self.rect.y += y_offset * self.velocity

    def attack_target(self, target):
        target.health -= self.attack
        if target.health < 0:
            target.health = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Tank(Character):
    def __init__(self):
        super().__init__("Tank", 120, 8, 4, (255, 0, 0), 100, 300)

class Assassin(Character):
    def __init__(self):
        super().__init__("Assassin", 80, 15, 6, (0, 255, 0), 300, 300)

class Sorcier(Character):
    def __init__(self):
        super().__init__("Sorcier", 70, 12, 5, (0, 0, 255), 500, 300)

class Mage(Character):
    def __init__(self):
        super().__init__("Mage", 75, 10, 5, (128, 0, 128), 700, 300)

class Archer(Character):
    def __init__(self):
        super().__init__("Archer", 65, 14, 7, (0, 128, 0), 900, 300)
