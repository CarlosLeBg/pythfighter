import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, health, attack, velocity, color, start_x, start_y):
        super().__init__()
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_power = attack
        self.velocity = velocity
        self.color = color

        self.image = pygame.Surface((50, 50))  # Represent characters as colored squares
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

    def move(self, x_offset, y_offset):
        self.rect.x += x_offset * self.velocity
        self.rect.y += y_offset * self.velocity

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0  # Prevent negative health

    def is_alive(self):
        return self.health > 0

    def perform_attack(self, target):
        if target.is_alive():
            target.take_damage(self.attack_power)
            print(f"{self.name} attacks {target.name} for {self.attack_power} damage!")

class Tank(Character):
    def __init__(self):
        super().__init__(
            name="Tank",
            health=200,
            attack=10,
            velocity=4,
            color=(0, 128, 255),  # Blue color
            start_x=100,
            start_y=300
        )

class Assassin(Character):
    def __init__(self):
        super().__init__(
            name="Assassin",
            health=100,
            attack=15,
            velocity=8,
            color=(255, 0, 0),  # Red color
            start_x=200,
            start_y=300
        )

class Sorcerer(Character):
    def __init__(self):
        super().__init__(
            name="Sorcerer",
            health=90,
            attack=12,
            velocity=6,
            color=(128, 0, 128),  # Purple color
            start_x=300,
            start_y=300
        )

class Archer:
    def __init__(self):
        self.health = 100
        self.attack_damage = 10
        self.rect = pygame.Rect(0, 0, 50, 50)  # Example size and position
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))  # Green color for the archer

    def perform_attack(self, opponent):
        opponent.health -= self.attack_damage
        print(f"Archer attacks! Opponent's health is now {opponent.health}")
