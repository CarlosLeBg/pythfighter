from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class SpecialMove:
    name: str
    description: str
    damage: int
    cooldown: float
    mana_cost: int

@dataclass
class Fighter:
    name: str
    color: Tuple[int, int, int]
    stats: Dict[str, int]
    abilities: List[SpecialMove]
    description: str
    difficulty: str
    style: str
    strengths: List[str]
    weaknesses: List[str]
    combo_tips: List[str]
    lore: str
    height: int
    weight: int

# Définition des capacités spéciales
SPECIAL_MOVES = {
    "berserk_rage": SpecialMove(
        name="Rage Berserk",
        description="Augmente les dégâts de 50% pendant 5 secondes",
        damage=0,
        cooldown=15.0,
        mana_cost=50
    ),
    "divine_shield": SpecialMove(
        name="Bouclier Divin",
        description="Immunité totale pendant 2 secondes",
        damage=0,
        cooldown=20.0,
        mana_cost=75
    ),
    "arcane_burst": SpecialMove(
        name="Nova Arcanique",
        description="Explosion magique qui repousse les ennemis",
        damage=120,
        cooldown=8.0,
        mana_cost=60
    ),
    "precise_shot": SpecialMove(
        name="Tir Précis",
        description="Tir à distance avec 100% de chances de coup critique",
        damage=150,
        cooldown=12.0,
        mana_cost=40
    ),
    "fortress": SpecialMove(
        name="Forteresse",
        description="Augmente la défense de 100% mais réduit la vitesse de 50%",
        damage=0,
        cooldown=25.0,
        mana_cost=80
    )
}

# Définition des personnages
FIGHTERS = {
    "Berserk": Fighter(
        name="Berserk",
        color=(255, 50, 50),
        stats={
            "Force": 9,
            "Vitesse": 7,
            "Défense": 4,
            "Portée": 6,
            "Magie": 3,
            "Endurance": 8,
            "Technique": 5
        },
        abilities=[
            SPECIAL_MOVES["berserk_rage"],
            SpecialMove("Sprint Furieux", "Dash rapide avec dégâts", 75, 6.0, 30),
            SpecialMove("Cri de Guerre", "Étourdit les ennemis proches", 50, 10.0, 45)
        ],
        description="Guerrier furieux spécialisé dans les dégâts rapprochés",
        difficulty="★★★☆☆",
        style="Corps à corps agressif",
        strengths=[
            "Dégâts explosifs",
            "Excellent dans les combos",
            "Pression constante"
        ],
        weaknesses=[
            "Faible défense",
            "Vulnérable à distance",
            "Consomme beaucoup d'énergie"
        ],
        combo_tips=[
            "Commencez par un Sprint Furieux pour vous rapprocher",
            "Enchaînez avec des coups rapides",
            "Utilisez la Rage en finisher"
        ],
        lore="Ancien gladiateur maudit par une entité démoniaque, le Berserk puise sa force dans sa rage intérieure.",
        height=185,
        weight=95
    ),
    
    "Guardian": Fighter(
        name="Guardian",
        color=(50, 255, 50),
        stats={
            "Force": 6,
            "Vitesse": 5,
            "Défense": 9,
            "Portée": 4,
            "Magie": 6,
            "Endurance": 7,
            "Technique": 8
        },
        abilities=[
            SPECIAL_MOVES["divine_shield"],
            SpecialMove("Aura Protectrice", "Réduit les dégâts de zone", 0, 15.0, 55),
            SpecialMove("Contre-Attaque", "Renvoie 50% des dégâts", 0, 8.0, 40)
        ],
        description="Protecteur résistant avec d'excellentes capacités défensives",
        difficulty="★★☆☆☆",
        style="Défensif tactique",
        strengths=[
            "Excellente survie",
            "Bon contre les attaques à distance",
            "Contrôle de zone"
        ],
        weaknesses=[
            "Mobilité limitée",
            "Dégâts modérés",
            "Vulnérable aux combos rapides"
        ],
        combo_tips=[
            "Utilisez Contre-Attaque face aux attaques lourdes",
            "Le Bouclier Divin peut sauver vos alliés",
            "L'Aura Protectrice est parfaite en équipe"
        ],
        lore="Ancien chevalier d'élite ayant juré de protéger les innocents, le Guardian incarne la justice et la protection.",
        height=190,
        weight=100
    ),
}