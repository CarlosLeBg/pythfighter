import pygame
import sys
import time
from math import sin
from dataclasses import dataclass
from typing import List, Dict, Tuple
from config.settings import GameSettings
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser
from position_manager import PositionManager  # Import du gestionnaire de positions

# Chargement des paramètres
SETTINGS = GameSettings()

# Configuration de l'écran
SCREEN_WIDTH = SETTINGS.SCREEN_WIDTH
SCREEN_HEIGHT = SETTINGS.SCREEN_HEIGHT
FPS = SETTINGS.FPS
DEBUG_MODE = SETTINGS.DEBUG_MODE

# Autres couleurs
TEXT_COLOR = SETTINGS.TEXT_COLOR
HOVER_COLOR = (255, 255, 255, SETTINGS.HOVER_ALPHA)

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
    difficulty: str  # Ajout de la difficulté
    stats: Dict[str, int]

    def __post_init__(self):
        self.difficulty = self.difficulty or "Moyenne"  # Si la difficulté n'est pas définie, par défaut "Moyenne"

FIGHTERS = {
    "AgileFighter": AgileFighter(),
    "Tank": Tank(),
    "BurstDamage": BurstDamage(),
    "ThunderStrike": ThunderStrike(),
    "Bruiser": Bruiser()
}

class CharacterSelect:
    def __init__(self):
        pygame.init()

        # Initialisation de l'écran et du gestionnaire de positions
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.position_manager = PositionManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        pygame.display.set_caption("Pyth Fighter - Sélection des Personnages")

        # Initialisation
        self.selected = {"player1": None, "player2": None}
        self.current_player = "player1"
        self.countdown = 5
        self.animation_time = 0
        self.hovered_character = None

        # Chargement des polices
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 48),
            'normal': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }

        # Mise à jour des positions des cartes des personnages
        self.position_manager.update_card_positions(FIGHTERS)

    def draw_character_card(self, name, data, index):
        card_rect = self.position_manager.card_positions[name]
        # Récupération des coordonnées
        x, y = card_rect.x, card_rect.y

        # Animation de flottement
        y_offset = sin(self.animation_time * 3) * 5
        y = y + y_offset

        # Création de la carte
        card_surface = pygame.Surface((SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), pygame.SRCALPHA)
        hover = card_rect.collidepoint(pygame.mouse.get_pos())

        # Couleur de fond
        base_color = data.color
        alpha = 230 if hover else 200
        pygame.draw.rect(card_surface, (*base_color, alpha), (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), border_radius=20)

        # Effet de survol
        if hover:
            self.hovered_character = name
            pygame.draw.rect(card_surface, (*HOVER_COLOR[:3], 50), (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), border_radius=20)

        # Bordure de sélection
        if name == self.selected['player1']:
            pygame.draw.rect(card_surface, SETTINGS.PLAYER1_COLOR, (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), 4, border_radius=20)
        elif name == self.selected['player2']:
            pygame.draw.rect(card_surface, SETTINGS.PLAYER2_COLOR, (0, 0, SETTINGS.CARD_WIDTH, SETTINGS.CARD_HEIGHT), 4, border_radius=20)

        # Contenu de la carte
        y_content = 20

        # Nom
        text = self.fonts['subtitle'].render(name, True, TEXT_COLOR)
        card_surface.blit(text, (SETTINGS.CARD_WIDTH // 2 - text.get_width() // 2, y_content))
        y_content += 50

        # Style
        style = self.fonts['normal'].render(f"Style: {data.style}", True, TEXT_COLOR)
        card_surface.blit(style, (SETTINGS.CARD_WIDTH // 2 - style.get_width() // 2, y_content))
        y_content += 40

        # Stats principales avec barres
        for stat_name, value in list(getattr(data, 'stats', {}).items())[:3]:
            # Nom de la stat
            stat_text = self.fonts['small'].render(stat_name, True, TEXT_COLOR)
            card_surface.blit(stat_text, (20, y_content))

            # Barre de progression
            bar_width = SETTINGS.CARD_WIDTH - 40
            bar_height = 10
            pygame.draw.rect(card_surface, (50, 50, 50), (20, y_content + 20, bar_width, bar_height))
            pygame.draw.rect(card_surface, TEXT_COLOR, (20, y_content + 20, bar_width * (value / 10), bar_height))

            y_content += 40

        # Affichage de la carte
        self.screen.blit(card_surface, (x, y))

    def draw_detail_panel(self):
        if not self.hovered_character:
            return

        char_data = FIGHTERS[self.hovered_character]
        panel_rect = self.position_manager.get_detail_panel_position()
        surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)

        # Fond semi-transparent
        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, panel_rect.width, panel_rect.height), border_radius=15)

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
        pygame.draw.line(surface, TEXT_COLOR, (20, y), (panel_rect.width - 20, y))
        y += 20

        for stat_name, value in getattr(char_data, 'stats', {}).items():
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
        self.screen.blit(surface, panel_rect.topleft)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        start_time = time.time()

        while running:
            self.animation_time += clock.get_time() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for char_name, char_rect in self.position_manager.card_positions.items():
                        if char_rect.collidepoint(event.pos):
                            self.selected[self.current_player] = char_name
                            self.current_player = "player2" if self.current_player == "player1" else "player1"
                            break

            self.screen.fill((0, 0, 0))  # Fond noir

            # Dessin du texte en haut
            title_text = self.fonts['title'].render("Sélectionnez un Personnage", True, TEXT_COLOR)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))

            # Dessin des cartes des personnages
            for index, char_name in enumerate(FIGHTERS):
                self.draw_character_card(char_name, FIGHTERS[char_name], index)

            # Dessin du panneau de détails
            self.draw_detail_panel()

            # Rafraîchir l'écran
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Exécution du jeu
if __name__ == "__main__":
    game = CharacterSelect()
    game.run()
