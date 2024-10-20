import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, health, attack, velocity, image_file, start_x, start_y):
        super().__init__()
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.velocity = velocity
        
        # Chargement de l'image avec gestion des erreurs
        try:
            self.image = pygame.image.load(image_file).convert_alpha()
        except pygame.error:
            print(f"Erreur : Impossible de charger l'image '{image_file}' pour le personnage {name}")
            self.image = pygame.Surface((50, 50))  # Image par défaut en cas d'erreur

        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

    def move(self, x_offset, y_offset):
        """Déplace le personnage selon les offsets donnés."""
        self.rect.x += x_offset * self.velocity
        self.rect.y += y_offset * self.velocity

    def take_damage(self, damage):
        """Réduit la santé du personnage."""
        self.health -= damage
        if self.health < 0:
            self.health = 0  # Empêcher les points de vie négatifs
            print(f"{self.name} a été éliminé.")

    def is_alive(self):
        """Vérifie si le personnage est encore en vie."""
        return self.health > 0


# Création des différents personnages en utilisant la classe Character
class Tank(Character):
    def __init__(self):
        super().__init__(
            name="Tank",
            health=150,
            attack=12,
            velocity=5,
            image_file='tank_image.png',
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
            image_file='assassin_image.png',
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
            image_file='sorcier_image.png',
            start_x=1000,
            start_y=200
        )
