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
        self.image.fill(self.color)  # Utilisation de la couleur pour représenter le personnage
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
            print(f"{self.name} a été éliminé.")

    def is_alive(self):
        return self.health > 0

class Tank(Character):
    def __init__(self):
        super().__init__(
            name="Tank",
            health=120,
            attack=10,
            velocity=4,
            color=(255, 0, 0),  # Rouge
            start_x=100,
            start_y=200
        )

class Assassin(Character):
    def __init__(self):
        super().__init__(
            name="Assassin",
            health=100,
            attack=8,
            velocity=12,
            color=(0, 255, 0),  # Vert
            start_x=200,
            start_y=200
        )

class Sorcier(Character):
    def __init__(self):
        super().__init__(
            name="Sorcier",
            health=90,
            attack=12,
            velocity=6,
            color=(0, 0, 255),  # Bleu
            start_x=300,
            start_y=200
        )

class Mage(Character):
    def __init__(self):
        super().__init__(
            name="Mage",
            health=80,
            attack=15,
            velocity=5,
            color=(128, 0, 128),  # Violet
            start_x=400,
            start_y=200
        )

class Archer(Character):
    def __init__(self):
        super().__init__(
            name="Archer",
            health=90,
            attack=10,
            velocity=7,
            color=(0, 128, 0),  # Vert foncé
            start_x=500,
            start_y=200
        )
