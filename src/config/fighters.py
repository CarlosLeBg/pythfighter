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
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 50, 100)
        self.special_active = False  # ✅ Ajout pour éviter l'erreur

    def activate_special(self):
        """Active la capacité spéciale du personnage."""
        self.special_active = True

    def deactivate_special(self):
        """Désactive la capacité spéciale du personnage."""
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
