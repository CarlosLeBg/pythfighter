import pygame
from abc import ABC, abstractmethod

class Character(pygame.sprite.Sprite, ABC):
    def __init__(self, name, health, attack, velocity, color, start_x, start_y):
        super().__init__()
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_power = attack
        self.velocity = velocity
        self.color = color
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.image = None
        self.animation_frames = []
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_time = 0

    def load_sprite(self, sprite_sheet_path):
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        for i in range(4):  # Assuming 4 frames of animation
            frame = sprite_sheet.subsurface((i * 50, 0, 50, 50))
            self.animation_frames.append(frame)
        self.image = self.animation_frames[0]

    def move(self, x_offset, y_offset):
        self.rect.x += x_offset * self.velocity
        self.rect.y += y_offset * self.velocity

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def is_alive(self):
        return self.health > 0

    def perform_attack(self, target):
        if target.is_alive():
            target.take_damage(self.attack_power)
            print(f"{self.name} attacks {target.name} for {self.attack_power} damage!")

    @abstractmethod
    def special_ability(self):
        pass

    def update(self):
        self.animation_time += 1
        if self.animation_time >= self.animation_speed * 60:  # 60 FPS
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

class Tank(Character):
    def __init__(self):
        super().__init__("Tank", 200, 10, 4, (0, 128, 255), 100, 300)

    def special_ability(self):
        self.health = min(self.max_health, self.health + 20)
        print(f"{self.name} uses Shield Bash and recovers 20 HP!")

class Assassin(Character):
    def __init__(self):
        super().__init__("Assassin", 100, 15, 8, (255, 0, 0), 200, 300)

    def special_ability(self):
        self.attack_power *= 2
        print(f"{self.name} uses Shadow Strike, doubling attack power for the next attack!")

class Sorcerer(Character):
    def __init__(self):
        super().__init__("Sorcerer", 90, 12, 6, (128, 0, 128), 300, 300)

    def special_ability(self):
        print(f"{self.name} casts Arcane Burst, dealing area damage!")
        # Implement area damage logic here

class Archer(Character):
    def __init__(self):
        super().__init__("Archer", 100, 10, 7, (0, 255, 0), 400, 300)

    def special_ability(self):
        print(f"{self.name} uses Precise Shot, increasing accuracy!")
        # Implement increased accuracy logic here