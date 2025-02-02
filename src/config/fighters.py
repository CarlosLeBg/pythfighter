import pygame
import math

class Fighter:
    def __init__(self, name, speed, damage, abilities, style, stats, description, combo_tips, lore, color, special_ability, weakness):
        self.name = name
        self.speed = speed
        self.damage = damage
        self.abilities = abilities
        self.style = style
        self.stats = stats
        self.description = description
        self.combo_tips = combo_tips
        self.lore = lore
        self.color = color
        self.special_ability = special_ability
        self.weakness = weakness
        
        # Fighting properties
        self.x = 0
        self.y = 0
        self.width = 50
        self.height = 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = 100
        self.max_special = 100
        self.special_meter = 0
        self.attacking = False
        self.blocking = False
        self.special_active = False
        self.facing_right = True
        
        # Create rectangles for collision
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_controller_input(self, input_state, opponent_x):
        # Movement
        self.velocity_x = input_state['move_x'] * self.speed
        
        # Update facing direction
        if self.velocity_x > 0:
            self.facing_right = True
        elif self.velocity_x < 0:
            self.facing_right = False
        
        # Update position
        self.x += self.velocity_x
        self.rect.x = self.x
        self.hitbox.x = self.x
        
        # Actions
        if input_state['attack']:
            self.attacking = True
        if input_state['block']:
            self.blocking = True
        else:
            self.blocking = False
        if input_state['special'] and self.special_meter >= self.max_special:
            self.special_active = True
            self.special_meter = 0

    def draw(self, screen):
        # Draw character rectangle
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw health bar
        health_width = 50
        health_height = 5
        health_x = self.x
        health_y = self.y - 10
        health_fill = (self.health / 100) * health_width
        
        pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, health_fill, health_height))
        
        # Draw special meter
        special_y = self.y - 20
        special_fill = (self.special_meter / self.max_special) * health_width
        pygame.draw.rect(screen, (0, 0, 255), (health_x, special_y, special_fill, health_height))
        
        # Visual feedback for actions
        if self.attacking:
            attack_rect = pygame.Rect(
                self.x + (self.width if self.facing_right else -20),
                self.y + 20,
                20,
                20
            )
            pygame.draw.rect(screen, (255, 255, 0), attack_rect)
        
        if self.blocking:
            pygame.draw.rect(screen, (200, 200, 200), 
                           (self.x + (0 if self.facing_right else self.width - 5),
                            self.y,
                            5,
                            self.height))

    def activate_special(self):
        self.special_active = True

    def deactivate_special(self):
        self.special_active = False

class AgileFighter(Fighter):
    def __init__(self):
        super().__init__(
            "Menfou (Benjamin)", speed=9, damage=7,
            abilities=["Dodge", "Quick Strike"],
            style="Agile", stats={"Force": 7, "Défense": 3, "Vitesse": 9, "Vie": 95},
            description="Un samouraï rapide et précis, excellent pour esquiver et contre-attaquer.",
            combo_tips=["Esquivez puis enchaînez avec une frappe rapide pour un maximum d'impact."],
            lore="Benjamin est un maître du katana, spécialisé dans la rapidité et les attaques chirurgicales.",
            color=(0, 200, 255),
            special_ability="Esquive parfaite (réduit les dégâts reçus de 50 % si activée au bon moment)",
            weakness="Faible résistance (3 coups pour briser la garde)"
        )
        self.hitbox = pygame.Rect(0, 0, 45, 95)

class Tank(Fighter):
    def __init__(self):
        super().__init__(
            "Tank (Carl)", speed=2, damage=20,
            abilities=["Shield Bash", "Endurance"],
            style="Defensive", stats={"Force": 10, "Défense": 6, "Vitesse": 2, "Vie": 120},
            description="Un guerrier imposant et lent, mais capable d'encaisser et de frapper très fort.",
            combo_tips=["Utilisez Shield Bash pour repousser les ennemis, puis suivez avec une attaque lourde."],
            lore="Carl est un géant sur le champ de bataille, inarrêtable dans sa quête de victoire.",
            color=(255, 100, 100),
            special_ability="Bouclier indestructible (absorbe le prochain coup subi toutes les 10 secondes)",
            weakness="Extrême lenteur (difficile de toucher les cibles rapides)"
        )
        self.hitbox = pygame.Rect(0, 0, 60, 120)

class BurstDamage(Fighter):
    def __init__(self):
        super().__init__(
            "Burst Damage (Moinécha)", speed=6, damage=5,
            abilities=["Flame Burst", "Inferno"],
            style="Burst", stats={"Force": 6, "Défense": 4, "Vitesse": 6, "Vie": 100},
            description="Un moine spécialisé dans les attaques à base de feu, infligeant des brûlures continues.",
            combo_tips=["Appliquez la brûlure avec Flame Burst, puis enchaînez avec Inferno pour maximiser les dégâts."],
            lore="Moinécha utilise le pouvoir des flammes pour anéantir ses ennemis, un maître du contrôle de zone.",
            color=(255, 165, 0),
            special_ability="Inflige des brûlures (5 dégâts par seconde pendant 3 secondes)",
            weakness="Faibles dégâts directs (brûlures nécessaires pour maximiser les dégâts totaux)"
        )
        self.hitbox = pygame.Rect(0, 0, 50, 100)

class ThunderStrike(Fighter):
    def __init__(self):
        super().__init__(
            "Thunder Strike (Timothy)", speed=8, damage=9,
            abilities=["Lightning Bolt", "Thunderstorm"],
            style="Elemental", stats={"Force": 9, "Défense": 4, "Vitesse": 8, "Vie": 100},
            description="Un combattant électrique qui peut paralyser ses adversaires et dominer le combat.",
            combo_tips=["Utilisez Lightning Bolt pour étourdir, puis Thunderstorm pour infliger de lourds dégâts."],
            lore="Timothy, né pendant un orage, canalise l'énergie des éclairs pour terrasser ses adversaires.",
            color=(0, 0, 255),
            special_ability="Stun aléatoire (25 % de chance d'étourdir l'ennemi pendant 2 secondes)",
            weakness="Dépendance à la chance (le stun peut ne pas se produire)"
        )
        self.hitbox = pygame.Rect(0, 0, 50, 100)

class Bruiser(Fighter):
    def __init__(self):
        super().__init__(
            "Bruiser (Rémi)", speed=7, damage=8,
            abilities=["Balanced Strike", "Power Up"],
            style="Balanced", stats={"Force": 8, "Défense": 4, "Vitesse": 7, "Vie": 105},
            description="Un combattant polyvalent, équilibré dans toutes les statistiques.",
            combo_tips=["Activez Power Up pour augmenter vos dégâts, puis frappez avec Balanced Strike."],
            lore="Rémi est un guerrier polyvalent, prêt à affronter n'importe quelle situation avec aplomb.",
            color=(128, 128, 128),
            special_ability="Boost équilibré (augmente les dégâts et la vitesse de 10 % pendant 5 secondes)",
            weakness="Aucune statistique dominante (ne surpasse pas les autres dans un domaine spécifique)"
        )
        self.hitbox = pygame.Rect(0, 0, 50, 100)
