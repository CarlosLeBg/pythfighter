# items.py
class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 255, 0))  # Jaune
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def apply_health(self, character):
        character.health += 20
        if character.health > character.max_health:
            character.health = character.max_health
