import pygame

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
        
        # Combat attributes
        self.health = 100
        self.max_health = 100
        self.special_meter = 0
        self.max_special = 100
        self.x = 0
        self.y = 0
        self.width = 50
        self.height = 100
        self.attacking = False
        self.blocking = False
        self.special_active = False
        self.facing_right = True
        self.hitbox = pygame.Rect(0, 0, self.width, self.height)

    def handle_keyboard_input(self, input_state, opponent_x):
        self.facing_right = self.x < opponent_x
        move_speed = 5 * self.speed / 5

        if input_state["left"]: self.x -= move_speed
        if input_state["right"]: self.x += move_speed
        if input_state["up"]: self.y -= move_speed
        if input_state["down"]: self.y += move_speed

        self.attacking = input_state["attack"]
        self.blocking = input_state["block"]
        if input_state["special"] and self.special_meter >= self.max_special:
            self.special_active = True
            self.special_meter = 0

        self.hitbox.x = self.x - self.width//2
        self.hitbox.y = self.y - self.height//2

    def draw(self, screen):
        # Draw character
        character_rect = pygame.Rect(
            self.x - self.width//2,
            self.y - self.height//2,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, self.color, character_rect)

        # Health bar
        health_width = 100
        health_height = 10
        health_x = self.x - health_width//2
        health_y = self.y - self.height//2 - 20
        
        pygame.draw.rect(screen, (255, 0, 0), 
                        (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, (0, 255, 0),
                        (health_x, health_y, 
                         health_width * (self.health/self.max_health), health_height))

        # Special meter
        special_y = health_y - 15
        pygame.draw.rect(screen, (100, 100, 100),
                        (health_x, special_y, health_width, health_height))
        pygame.draw.rect(screen, (255, 255, 0),
                        (health_x, special_y,
                         health_width * (self.special_meter/self.max_special), health_height))

        # Attack visualization
        if self.attacking:
            attack_rect = pygame.Rect(
                self.x + (self.width//2 if self.facing_right else -self.width*1.5),
                self.y - self.height//4,
                self.width,
                self.height//2
            )
            pygame.draw.rect(screen, (255, 0, 0), attack_rect)
        
        if self.blocking:
            shield_color = (0, 0, 255, 128)
            shield_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(shield_surface, shield_color, 
                           (0, 0, self.width, self.height))
            screen.blit(shield_surface, 
                       (self.x - self.width//2, self.y - self.height//2))

class AgileFighter(Fighter):
    def __init__(self):
        super().__init__(
            name="Menfou (Benjamin)", speed=9, damage=7,
            abilities=["Dodge", "Quick Strike"],
            style="Agile", stats={"Force": 7, "Défense": 3, "Vitesse": 9, "Vie": 95},
            description="Un samouraï rapide et précis, excellent pour esquiver et contre-attaquer.",
            combo_tips=["Esquivez puis enchaînez avec une frappe rapide pour un maximum d'impact."],
            lore="Benjamin est un maître du katana, spécialisé dans la rapidité et les attaques chirurgicales.",
            color=(0, 200, 255),
            special_ability="Esquive parfaite (réduit les dégâts reçus de 50 % si activée au bon moment)",
            weakness="Faible résistance (3 coups pour briser la garde)"
        )

class Tank(Fighter):
    def __init__(self):
        super().__init__(
            name="Tank (Carl)", speed=2, damage=20,
            abilities=["Shield Bash", "Endurance"],
            style="Defensive", stats={"Force": 10, "Défense": 6, "Vitesse": 2, "Vie": 120},
            description="Un guerrier imposant et lent, mais capable d'encaisser et de frapper très fort.",
            combo_tips=["Utilisez Shield Bash pour repousser les ennemis, puis suivez avec une attaque lourde."],
            lore="Carl est un géant sur le champ de bataille, inarrêtable dans sa quête de victoire.",
            color=(255, 100, 100),
            special_ability="Bouclier indestructible (absorbe le prochain coup subi toutes les 10 secondes)",
            weakness="Extrême lenteur (difficile de toucher les cibles rapides)"
        )

class BurstDamage(Fighter):
    def __init__(self):
        super().__init__(
            name="Burst Damage (Moinécha)", speed=6, damage=5,
            abilities=["Flame Burst", "Inferno"],
            style="Burst", stats={"Force": 6, "Défense": 4, "Vitesse": 6, "Vie": 100},
            description="Un moine spécialisé dans les attaques à base de feu, infligeant des brûlures continues.",
            combo_tips=["Appliquez la brûlure avec Flame Burst, puis enchaînez avec Inferno pour maximiser les dégâts."],
            lore="Moinécha utilise le pouvoir des flammes pour anéantir ses ennemis, un maître du contrôle de zone.",
            color=(255, 165, 0),
            special_ability="Inflige des brûlures (5 dégâts par seconde pendant 3 secondes)",
            weakness="Faibles dégâts directs (brûlures nécessaires pour maximiser les dégâts totaux)"
        )

class ThunderStrike(Fighter):
    def __init__(self):
        super().__init__(
            name="Thunder Strike (Timothy)", speed=8, damage=9,
            abilities=["Lightning Bolt", "Thunderstorm"],
            style="Elemental", stats={"Force": 9, "Défense": 4, "Vitesse": 8, "Vie": 100},
            description="Un combattant électrique qui peut paralyser ses adversaires et dominer le combat.",
            combo_tips=["Utilisez Lightning Bolt pour étourdir, puis Thunderstorm pour infliger de lourds dégâts."],
            lore="Timothy, né pendant un orage, canalise l'énergie des éclairs pour terrasser ses adversaires.",
            color=(0, 0, 255),
            special_ability="Stun aléatoire (25 % de chance d'étourdir l'ennemi pendant 2 secondes)",
            weakness="Dépendance à la chance (le stun peut ne pas se produire)"
        )

class Bruiser(Fighter):
    def __init__(self):
        super().__init__(
            name="Bruiser (Rémi)", speed=7, damage=8,
            abilities=["Balanced Strike", "Power Up"],
            style="Balanced", stats={"Force": 8, "Défense": 4, "Vitesse": 7, "Vie": 105},
            description="Un combattant polyvalent, équilibré dans toutes les statistiques.",
            combo_tips=["Activez Power Up pour augmenter vos dégâts, puis frappez avec Balanced Strike."],
            lore="Rémi est un guerrier polyvalent, prêt à affronter n'importe quelle situation avec aplomb.",
            color=(128, 128, 128),
            special_ability="Boost équilibré (augmente les dégâts et la vitesse de 10 % pendant 5 secondes)",
            weakness="Aucune statistique dominante (ne surpasse pas les autres dans un domaine spécifique)"
        )