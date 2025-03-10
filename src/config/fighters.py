class Fighter:
    def __init__(self, name, speed, damage, abilities, style, stats, description, combo, lore, color, special, weakness):
        self.name = name
        self.speed = speed
        self.damage = damage
        self.abilities = abilities
        self.style = style
        self.stats = stats
        self.description = description
        self.combo = combo
        self.lore = lore
        self.color = color
        self.special = special
        self.weakness = weakness

class AgileFighter(Fighter):
    def __init__(self):
        super().__init__(
            "Ben (Benjamin)", speed=7, damage=8,
            abilities=["Dodge", "Quick Strike"],
            style="Agile", stats={"Force": 7, "Défense": 4, "Vitesse": 7, "Vie": 100},
            description="Rapide et insaisissable, il excelle dans l'esquive et la contre-attaque.",
            combo=["Esquivez puis frappez rapidement pour un maximum d'impact."],
            lore="Maître du katana, il privilégie la vitesse aux attaques puissantes.",
            color=(0, 200, 255),
            special="Esquive parfaite (réduit les dégâts de 50 % si bien utilisée)",
            weakness="Fragile (3 coups suffisent à briser sa garde)"
        )

class Tank(Fighter):
    def __init__(self):
        super().__init__(
            "Tank (Carl)", speed=4, damage=16,
            abilities=["Shield Bash", "Endurance"],
            style="Defensive", stats={"Force": 10, "Défense": 7, "Vitesse": 4, "Vie": 120},
            description="Massif et résistant, il frappe fort mais se déplace lentement.",
            combo=["Utilisez Shield Bash pour repousser, puis enchaînez une attaque lourde."],
            lore="Un colosse sur le champ de bataille, inébranlable en défense.",
            color=(255, 100, 100),
            special="Bouclier indestructible (absorbe un coup toutes les 10 sec)",
            weakness="Très lent (difficile d'atteindre les cibles mobiles)"
        )

class BurstDamage(Fighter):
    def __init__(self):
        super().__init__(
            "Moinécha", speed=6, damage=7,
            abilities=["Flame Burst", "Inferno"],
            style="Burst", stats={"Force": 7, "Défense": 4, "Vitesse": 6, "Vie": 100},
            description="Un moine du feu, infligeant des brûlures continues à ses ennemis.",
            combo=["Appliquez la brûlure avec Flame Burst, puis terminez avec Inferno."],
            lore="Maîtrisant les flammes, il privilégie les dégâts sur la durée.",
            color=(255, 165, 0),
            special="Brûlure (5 dégâts/s pendant 2s)",
            weakness="Dégâts directs faibles (doit maximiser les brûlures)"
        )

class ThunderStrike(Fighter):
    def __init__(self):
        super().__init__(
            "Timothy", speed=7, damage=8,
            abilities=["Lightning Bolt", "Thunderstorm"],
            style="Elemental", stats={"Force": 8, "Défense": 4, "Vitesse": 7, "Vie": 100},
            description="Maître de l'électricité, capable d'étourdir ses adversaires.",
            combo=["Utilisez Lightning Bolt pour étourdir, puis enchaînez avec Thunderstorm."],
            lore="Né en plein orage, il canalise la foudre pour terrasser ses ennemis.",
            color=(0, 0, 255),
            special="Stun aléatoire (30 % de chance d'étourdir 2s)",
            weakness="Dépendance à la chance (stun incertain)"
        )

class Bruiser(Fighter):
    def __init__(self):
        super().__init__(
            "Rémi", speed=6, damage=9,
            abilities=["Balanced Strike", "Power Up"],
            style="Balanced", stats={"Force": 9, "Défense": 5, "Vitesse": 6, "Vie": 105},
            description="Un combattant équilibré, performant dans toutes les situations.",
            combo=["Activez Power Up, puis enchaînez un Balanced Strike."],
            lore="Guerrier polyvalent, il s’adapte à tous les styles de combat.",
            color=(128, 128, 128),
            special="Boost (10 % dégâts + vitesse pendant 5s)",
            weakness="Aucune stat dominante (moyen partout, mais excelle nulle part)"
        )
