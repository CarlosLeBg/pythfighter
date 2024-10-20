import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, health, attack, velocity, image_file, start_x, start_y):
        super().__init__()
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.velocity = velocity
        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

    def move(self, x_offset, y_offset):
        self.rect.x += x_offset * self.velocity
        self.rect.y += y_offset * self.velocity

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

class Tank(Character):
    def __init__(self):
        super().__init__(
            name="Tank",
            health=150,
            attack=12,
            velocity=5,
            image_file='src/tank_image.png',
            start_x=1000,
            start_y=200
        )

class Assassin(Character):
    def __init__(self):
        super().__init__(
            name="Assassin",
            health=100,
            attack=9,
            velocity=10,
            image_file='src/assassin_image.png',
            start_x=1000,
            start_y=200
        )

class Sorcier(Character):
    def __init__(self):
        super().__init__(
            name="Sorcier",
            health=90,
            attack=15,
            velocity=7,
            image_file='src/sorcier_image.png',
            start_x=1000,
            start_y=200
        )
