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
with open('.env', 'r', encoding='utf-8') as env_file:
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

characters = {
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
        weight=100
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
        total_width = (character_count * 300) + ((character_count - 1) * 50)  # 300px par carte + 50px espacement
        self.start_x = (SCREEN_WIDTH - total_width) // 2
        self.card_y = SCREEN_HEIGHT // 2 - 150  # Centré verticalement
        
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
        
        # Difficulté
        diff = self.fonts['normal'].render(data.difficulty, True, TEXT_COLOR)
        card_surface.blit(diff, (width//2 - diff.get_width()//2, y_content))
        y_content += 50
        
        # Stats principales avec barres
        for stat_name, value in list(data.stats.items())[:3]:
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
        
        for stat_name, value in char_data.stats.items():
            # Nom et valeur
            stat_text = self.fonts['normal'].render(f"{stat_name}: {value}", True, TEXT_COLOR)
            surface.blit(stat_text, (20, y))
            
            # Barre
            bar_width = 300
            bar_height = 15
            pygame.draw.rect(surface, (50, 50, 50), (self.detail_panel_width-bar_width-20, y+5, bar_width, bar_height))
            pygame.draw.rect(surface, char_data.color, 
                                       (self.detail_panel_width-bar_width-20, y+5, bar_width * (value/10), bar_height))
            
            y += 40
        
        # Capacités
        y += 20
        pygame.draw.line(surface, TEXT_COLOR, (20, y), (self.detail_panel_width-20, y))
        y += 20
        pygame.draw.line(surface, TEXT_COLOR, (20, y), (self.detail_panel_width-20, y))
        y += 20
        
        title = self.fonts['normal'].render("Capacités Spéciales:", True, TEXT_COLOR)
        surface.blit(title, (20, y))
        y += 40
        
        for ability in char_data.abilities:
            # Nom de la capacité
            name_text = self.fonts['small'].render(f"• {ability.name}", True, TEXT_COLOR)
            surface.blit(name_text, (20, y))
            y += 25
            
            # Description de la capacité
            desc_text = self.fonts['small'].render(f"  {ability.description}", True, TEXT_COLOR)
            surface.blit(desc_text, (40, y))
            y += 25
            
            # Détails de la capacité
            details_text = self.fonts['small'].render(f"  Dégâts: {ability.damage}, CD: {ability.cooldown}s, Mana: {ability.mana_cost}", True, TEXT_COLOR)
            surface.blit(details_text, (40, y))
            y += 30
        
        self.screen.blit(surface, (self.detail_panel_x, 50))

    def draw(self):
        # Fond
        self.screen.fill(BACKGROUND_COLOR)
        
        # Titre
        title_color = PLAYER1_COLOR if self.current_player == "player1" else PLAYER2_COLOR
        title_text = f"Joueur {1 if self.current_player == 'player1' else 2}, choisissez votre personnage!"
        title = self.fonts['title'].render(title_text, True, title_color)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, self.title_y))
        
        # Sous-titre
        subtitle = self.fonts['normal'].render("Survolez pour plus d'informations, cliquez pour sélectionner", 
                                             True, TEXT_COLOR)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, self.subtitle_y))
        
        # Cartes des personnages
        for i, (name, data) in enumerate(FIGHTERS.items()):
            self.draw_character_card(name, data, i)
        
        # Panneau de détails
        self.draw_detail_panel()
        
        # Compte à rebours
        if self.countdown is not None:
            seconds = (self.countdown // FPS) + 1
            countdown = self.fonts['title'].render(str(seconds), True, TEXT_COLOR)
            self.screen.blit(countdown, (SCREEN_WIDTH//2 - countdown.get_width()//2, SCREEN_HEIGHT//2))
        
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.animation_time += 0.05
            self.hovered_character = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and 
                    event.key == pygame.K_ESCAPE and 
                    DEBUG_MODE
                ):
                    return None
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for name, rect in self.card_positions.items():
                        if rect.collidepoint(event.pos):
                            if self.selected[self.current_player] != name:
                                self.selected[self.current_player] = name
                                
                                if self.current_player == "player1" and not self.selected["player2"]:
                                    self.current_player = "player2"
                                elif self.current_player == "player2" and not self.countdown:
                                    self.countdown = 3 * FPS
            
            if self.countdown is not None:
                self.countdown -= 1
                if self.countdown <= 0:
                    return (self.selected["player1"], self.selected["player2"])
            
            self.draw()
            clock.tick(FPS)
        
        return None

def main():
    selector = CharacterSelect()
    result = selector.run()
    
    if result:
        player1, player2 = result
        print(f"Combat: {player1} vs {player2}")
        # Lancement du combat
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()