class Fighter:
    def __init__(self, name, speed, damage, abilities, style, stats, description, combo_tips, lore, color):
        self.name = name
        self.speed = speed
        self.damage = damage
        self.abilities = abilities
        self.style = style
        self.stats = stats
        self.description = description
        self.combo_tips = combo_tips
        self.lore = lore
        self.color = color  # Ajout de la couleur ici

class AgileFighter(Fighter):
    def __init__(self):
        super().__init__(
            "Agile Fighter", speed=10, damage=5,
            abilities=["Dodge", "Quick Strike"],
            style="Agile", stats={"Force": 5, "Défense": 4, "Vitesse": 10},
            description="A fast and nimble fighter, capable of evading attacks and dealing quick strikes.",
            combo_tips=["Quick dodge into a counterattack!", "Use Quick Strike after a successful dodge!"],
            lore="An agile warrior trained in the art of stealth and speed, with roots in the ninja tradition.",
            color=(0, 200, 255)  # Couleur bleu clair pour Agile Fighter
        )

class Tank(Fighter):
    def __init__(self):
        super().__init__(
            "Tank", speed=4, damage=15,
            abilities=["Shield Bash", "Endurance"],
            style="Defensive", stats={"Force": 10, "Défense": 9, "Vitesse": 4},
            description="A heavy-hitting fighter with great defense but slower movement.",
            combo_tips=["Use Shield Bash to create space!", "Endurance helps you take a lot of damage."],
            lore="A warrior trained to withstand even the toughest blows, often seen on the frontlines.",
            color=(255, 100, 100)  # Couleur rouge pour Tank
        )

class BurstDamage(Fighter):
    def __init__(self):
        super().__init__(
            "Burst Damage", speed=7, damage=12,
            abilities=["Flame Burst", "Inferno"],
            style="Burst", stats={"Force": 8, "Défense": 5, "Vitesse": 7},
            description="A fiery fighter who unleashes explosive damage in short bursts.",
            combo_tips=["Use Flame Burst followed by Inferno for massive damage!"],
            lore="Once a fire mage, this fighter channels their flame-based powers into devastating attacks.",
            color=(255, 165, 0)  # Couleur orange pour Burst Damage
        )

class ThunderStrike(Fighter):
    def __init__(self):
        super().__init__(
            "Thunder Strike", speed=8, damage=10,
            abilities=["Lightning Bolt", "Thunderstorm"],
            style="Elemental", stats={"Force": 7, "Défense": 6, "Vitesse": 8},
            description="A fighter who harnesses the power of electricity to strike down foes.",
            combo_tips=["Lightning Bolt stuns enemies, follow up with Thunderstorm!"],
            lore="Born during a violent thunderstorm, this fighter uses the power of the skies to dominate enemies.",
            color=(0, 0, 255)  # Couleur bleu pour Thunder Strike
        )

class Bruiser(Fighter):
    def __init__(self):
        super().__init__(
            "Bruiser", speed=7, damage=8,
            abilities=["Balanced Strike", "Power Up"],
            style="Balanced", stats={"Force": 9, "Défense": 7, "Vitesse": 6},
            description="A balanced fighter with solid stats in all areas, capable of handling any situation.",
            combo_tips=["Use Balanced Strike to close the distance and Power Up to increase damage."],
            lore="A versatile warrior, the Bruiser can adapt to any fight and is known for their resilience.",
            color=(128, 128, 128)  # Couleur gris pour Bruiser (équilibré)
        )
