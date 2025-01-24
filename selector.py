# -*- coding: utf-8 -*-
import pygame
import sys
from math import sin
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Tuple, Dict, List
import codecs

# Chargement des variables d'environnement
with open('src\config\.env', 'r', encoding='utf-8') as env_file:
    load_dotenv(stream=env_file)

# Configuration depuis .env
SCREEN_WIDTH = int(os.getenv('SCREEN_WIDTH', 1920))
SCREEN_HEIGHT = int(os.getenv('SCREEN_HEIGHT', 1080))
FPS = int(os.getenv('FPS', 60))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Conversion des couleurs depuis .env
def parse_color(color_str):
    return tuple(map(int, color_str.split(',')))

BACKGROUND_COLOR = parse_color(os.getenv('BACKGROUND_COLOR', '15,15,35'))
PLAYER1_COLOR = parse_color(os.getenv('PLAYER1_COLOR', '0,200,255'))
PLAYER2_COLOR = parse_color(os.getenv('PLAYER2_COLOR', '255,100,100'))

# Autres couleurs
TEXT_COLOR = (255, 255, 255)
HOVER_COLOR = (255, 255, 255, 30)

# Définition des personnages
@dataclass
class Character:
    name: str
    description: str
    abilities: List[str]
    combo_tips: List[str]
    lore: str
    height: int
    weight: int
    color: Tuple[int, int, int]
    style: str
    stats: Dict[str, int]

FIGHTERS = {
    "Guardian": Character(
        name="Guardian",
        description="Un défenseur robuste avec une grande capacité de blocage.",
        abilities=[
            "Bouclier Divin",
            "Contre-Attaque",
            "Aura Protectrice"
        ],
        combo_tips=[
            "Utilisez Contre-Attaque face aux attaques lourdes",
            "Le Bouclier Divin peut sauver vos alliés",
            "L'Aura Protectrice est parfaite en équipe"
        ],
        lore="Ancien chevalier d'élite ayant juré de protéger les innocents, le Guardian incarne la justice et la protection.",
        height=190,
        weight=100,
        color=(0, 0, 255),
        style="Défensif",
        stats = {"Force": 7, "Défense": 9, "Vitesse": 4}
    ),
}

class CharacterSelect:
    def __init__(self):
        pygame.init()

        # Configuration de l'écran
        if DEBUG_MODE:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

        pygame.display.set_caption("Pyth Fighter - Sélection des Personnages")

        # État du jeu
        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.countdown = None
        self.animation_time = 0
        self.hovered_character = None
        self.card_positions = {}

        # Chargement des polices
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 48),
            'normal': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }

        # Calcul des positions centrées
        self.calculate_layout()

    def calculate_layout(self):
        # Position des cartes
        character_count = len(FIGHTERS)
        total_width = (character_count * 300) + ((character_count - 1) * 50)
        self.start_x = (SCREEN_WIDTH - total_width) // 2
        self.card_y = SCREEN_HEIGHT // 2 - 150

        # Position du panneau de détails
        self.detail_panel_width = 500
        self.detail_panel_x = SCREEN_WIDTH - self.detail_panel_width - 20

        # Calcul des positions des éléments UI
        self.title_y = 50
        self.subtitle_y = 120

    def draw_character_card(self, name, data, index):
        width, height = 300, 400
        x = self.start_x + (width + 50) * index
        base_y = self.card_y

        # Animation de flottement
        y_offset = sin(self.animation_time * 3) * 5
        y = base_y + y_offset

        # Création de la carte
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        hover = pygame.Rect(x, y, width, height).collidepoint(pygame.mouse.get_pos())

        # Couleur de fond
        base_color = data.color
        alpha = 230 if hover else 200
        pygame.draw.rect(card_surface, (*base_color, alpha), (0, 0, width, height), border_radius=20)

        # Effet de survol
        if hover:
            self.hovered_character = name
            pygame.draw.rect(card_surface, (*HOVER_COLOR[:3], 50), (0, 0, width, height), border_radius=20)

        # Bordure de sélection
        if name == self.selected['player1']:
            pygame.draw.rect(card_surface, PLAYER1_COLOR, (0, 0, width, height), 4, border_radius=20)
        elif name == self.selected['player2']:
            pygame.draw.rect(card_surface, PLAYER2_COLOR, (0, 0, width, height), 4, border_radius=20)

        # Contenu de la carte
        y_content = 20

        # Nom
        text = self.fonts['subtitle'].render(name, True, TEXT_COLOR)
        card_surface.blit(text, (width//2 - text.get_width()//2, y_content))
        y_content += 50

        # Style
        style = self.fonts['normal'].render(f"Style: {data.style}", True, TEXT_COLOR)
        card_surface.blit(style, (width//2 - style.get_width()//2, y_content))
        y_content += 40

        # Stats principales avec barres
        for stat_name, value in list(getattr(data, 'stats', {}).items())[:3]:
            # Nom de la stat
            stat_text = self.fonts['small'].render(stat_name, True, TEXT_COLOR)
            card_surface.blit(stat_text, (20, y_content))

            # Barre de progression
            bar_width = width - 40
            bar_height = 10
            pygame.draw.rect(card_surface, (50, 50, 50), (20, y_content + 20, bar_width, bar_height))
            pygame.draw.rect(card_surface, TEXT_COLOR, (20, y_content + 20, bar_width * (value/10), bar_height))

            y_content += 40

        # Affichage de la carte
        self.screen.blit(card_surface, (x, y))
        self.card_positions[name] = pygame.Rect(x, y, width, height)

    def draw_detail_panel(self):
        if not self.hovered_character:
            return

        char_data = FIGHTERS[self.hovered_character]
        panel_height = SCREEN_HEIGHT - 100
        surface = pygame.Surface((self.detail_panel_width, panel_height), pygame.SRCALPHA)

        # Fond semi-transparent
        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, self.detail_panel_width, panel_height), border_radius=15)

        y = 20
        # Titre
        title = self.fonts['title'].render(self.hovered_character, True, TEXT_COLOR)
        surface.blit(title, (20, y))
        y += 60

        # Description
        desc = self.fonts['normal'].render(char_data.description, True, TEXT_COLOR)
        surface.blit(desc, (20, y))
        y += 50

        # Stats détaillées
        y += 20
        pygame.draw.line(surface, TEXT_COLOR, (20, y), (self.detail_panel_width-20, y))
        y += 20

        for stat_name, value in getattr(char_data, 'stats', {}).items():
            pass
                    # Nom de la stat
            stat_text = self.fonts['normal'].render(f"{stat_name}: {value}", True, TEXT_COLOR)
            surface.blit(stat_text, (20, y))
            y += 40
        
        # Afficher les capacités
        abilities_title = self.fonts['subtitle'].render("Capacités :", True, TEXT_COLOR)
        surface.blit(abilities_title, (20, y))
        y += 40
        
        for ability in char_data.abilities:
            ability_text = self.fonts['small'].render(f"- {ability}", True, TEXT_COLOR)
            surface.blit(ability_text, (20, y))
            y += 30
        
        # Ajouter un espacement
        y += 20
        
        # Conseils pour combos
        combo_title = self.fonts['subtitle'].render("Conseils de Combo :", True, TEXT_COLOR)
        surface.blit(combo_title, (20, y))
        y += 40
        
        for tip in char_data.combo_tips:
            tip_text = self.fonts['small'].render(f"- {tip}", True, TEXT_COLOR)
            surface.blit(tip_text, (20, y))
            y += 30
        
        # Ajouter un espacement
        y += 20
        
        # Lore du personnage
        lore_title = self.fonts['subtitle'].render("Histoire :", True, TEXT_COLOR)
        surface.blit(lore_title, (20, y))
        y += 40
        
        lore_text = self.fonts['small'].render(char_data.lore, True, TEXT_COLOR)
        surface.blit(lore_text, (20, y))
        
        # Afficher le panneau de détails sur l'écran principal
        self.screen.blit(surface, (self.detail_panel_x, 50))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.animation_time += clock.get_time() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for char_name, char_rect in self.card_positions.items():
                        if char_rect.collidepoint(event.pos):
                            self.selected[self.current_player] = char_name
                            self.current_player = "player2" if self.current_player == "player1" else "player1"
                            break
            
            # Mise à jour de l'écran
            self.screen.fill(BACKGROUND_COLOR)
            for index, (char_name, char_data) in enumerate(FIGHTERS.items()):
                self.draw_character_card(char_name, char_data, index)
            
            self.draw_detail_panel()
            
            # Afficher les titres
            title = self.fonts['title'].render("Sélection des personnages", True, TEXT_COLOR)
            self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, self.title_y))
            
            subtitle = self.fonts['subtitle'].render(
                f"Joueur actuel : {self.current_player.upper()}", True, TEXT_COLOR
            )
            self.screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, self.subtitle_y))
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = CharacterSelect()
    game.run()
