import pygame

class Fighter:
    def __init__(self, player_num, x, y, fighter_type):
        self.player_num = player_num
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 50, 100)
        self.hitbox = pygame.Rect(x, y, 40, 90)
        
        # Import fighter stats from fighter_type
        self.name = fighter_type.name
        self.speed = fighter_type.speed
        self.damage = fighter_type.damage
        self.abilities = fighter_type.abilities
        self.color = fighter_type.color
        
        # Combat states
        self.health = 100
        self.special_meter = 0
        self.max_special = 100
        self.attacking = False
        self.blocking = False
        self.special_active = False
        
    def handle_controller_input(self, input_state, opponent_x):
        # Movement
        move_x = input_state['move_x'] * self.speed
        move_y = input_state['move_y'] * self.speed
        
        self.x += move_x
        self.y += move_y
        self.rect.x = self.x
        self.rect.y = self.y
        self.hitbox.x = self.x + 5
        self.hitbox.y = self.y + 5
        
        # Actions
        self.attacking = input_state['attack']
        self.blocking = input_state['block']
        if input_state['special'] and self.special_meter >= self.max_special:
            self.special_active = True
            self.special_meter = 0
            
    def draw(self, screen):
        # Draw fighter
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw health bar
        health_width = 50 * (self.health / 100)
        health_color = (0, 255, 0) if self.health > 50 else (255, 165, 0)
        pygame.draw.rect(screen, health_color, (self.x, self.y - 20, health_width, 10))
        
        # Draw special meter
        special_width = 50 * (self.special_meter / self.max_special)
        pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y - 10, special_width, 5))

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