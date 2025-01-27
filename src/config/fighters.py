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
        self.special_ability = special_ability  # Nouvelle capacité spéciale
        self.weakness = weakness  # Nouveau point faible


class AgileFighter(Fighter):
    def __init__(self):
        super().__init__(
            "Menfou (Benjamin)", speed=10, damage=7,
            abilities=["Dodge", "Quick Strike"],
            style="Agile", stats={"Force": 7, "Défense": 3, "Vitesse": 10, "Vie": 100},
            description="Un samouraï rapide et précis, capable d'infliger des dégâts normaux avec une garde légère.",
            combo_tips=["Esquivez puis contre-attaquez avec une frappe rapide !"],
            lore="Un samouraï entraîné dans les arts martiaux, Benjamin est rapide comme l'éclair.",
            color=(0, 200, 255),
            special_ability="Esquive rapide",
            weakness="Garde fragile (3 coups suffisent à la briser)"
        )


class Tank(Fighter):
    def __init__(self):
        super().__init__(
            "Tank (Carl)", speed=3, damage=18,
            abilities=["Shield Bash", "Endurance"],
            style="Defensive", stats={"Force": 10, "Défense": 5, "Vitesse": 3, "Vie": 100},
            description="Un guerrier lourd et lent, mais infligeant des dégâts massifs et encaissant facilement.",
            combo_tips=["Utilisez Endurance pour encaisser les coups, puis contre-attaquez !"],
            lore="Carl est un guerrier puissant et invincible en défense.",
            color=(255, 100, 100),
            special_ability="Endurance massive",
            weakness="Lenteur extrême"
        )


class BurstDamage(Fighter):
    def __init__(self):
        super().__init__(
            "Burst Damage (Moinécha)", speed=7, damage=6,
            abilities=["Flame Burst", "Inferno"],
            style="Burst", stats={"Force": 6, "Défense": 4, "Vitesse": 7, "Vie": 100},
            description="Un moine des flammes infligeant des brûlures continues malgré de faibles dégâts directs.",
            combo_tips=["Utilisez Flame Burst pour appliquer la brûlure, puis suivez avec Inferno pour maximiser les dégâts."],
            lore="Moinécha a maîtrisé l'art des flammes pour terrasser ses ennemis.",
            color=(255, 165, 0),
            special_ability="Applique des brûlures",
            weakness="Faibles dégâts initiaux"
        )


class ThunderStrike(Fighter):
    def __init__(self):
        super().__init__(
            "Thunder Strike (Timothy)", speed=8, damage=10,
            abilities=["Lightning Bolt", "Thunderstorm"],
            style="Elemental", stats={"Force": 7, "Défense": 4, "Vitesse": 8, "Vie": 100},
            description="Un combattant électrisant, capable de paralyser ses ennemis grâce à un stun aléatoire.",
            combo_tips=["Utilisez Lightning Bolt pour étourdir, puis enchaînez avec Thunderstorm !"],
            lore="Timothy canalise la puissance des orages pour anéantir ses adversaires.",
            color=(0, 0, 255),
            special_ability="Stun aléatoire",
            weakness="Dépendance à la chance"
        )


class Bruiser(Fighter):
    def __init__(self):
        super().__init__(
            "Bruiser (Rémi)", speed=7, damage=8,
            abilities=["Balanced Strike", "Power Up"],
            style="Balanced", stats={"Force": 9, "Défense": 4, "Vitesse": 7, "Vie": 100},
            description="Un combattant équilibré avec des statistiques solides dans tous les domaines.",
            combo_tips=["Activez Power Up avant de frapper avec Balanced Strike pour maximiser l'impact."],
            lore="Rémi est un guerrier polyvalent, adapté à toutes les situations de combat.",
            color=(128, 128, 128),
            special_ability="Équilibre parfait",
            weakness="Aucune force dominante"
        )
