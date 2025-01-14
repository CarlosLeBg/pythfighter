import os
from dotenv import load_dotenv
from pathlib import Path

# Chargement des variables d'environnement
load_dotenv()

class GameSettings:
    # Chemins
    BASE_DIR = Path(__file__).resolve().parent.parent
    ASSETS_DIR = BASE_DIR / os.getenv('ASSETS_PATH', 'assets/')
    SOUNDS_DIR = BASE_DIR / os.getenv('SOUNDS_PATH', 'assets/sounds/')
    IMAGES_DIR = BASE_DIR / os.getenv('IMAGES_PATH', 'assets/images/')
    FONTS_DIR = BASE_DIR / os.getenv('FONTS_PATH', 'assets/fonts/')

    # Configuration de l'écran
    SCREEN_WIDTH = int(os.getenv('SCREEN_WIDTH', 1920))
    SCREEN_HEIGHT = int(os.getenv('SCREEN_HEIGHT', 1080))
    FPS = int(os.getenv('FPS', 60))
    
    # Mode debug
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Configuration du son
    SOUND_ENABLED = os.getenv('SOUND_ENABLED', 'True').lower() == 'true'
    MUSIC_VOLUME = float(os.getenv('MUSIC_VOLUME', 0.7))
    SFX_VOLUME = float(os.getenv('SFX_VOLUME', 0.8))
    
    @staticmethod
    def parse_color(color_str):
        """Convertit une chaîne RGB en tuple de couleur."""
        try:
            return tuple(map(int, color_str.split(',')))
        except:
            return (255, 255, 255)  # Couleur par défaut en cas d'erreur
    
    # Couleurs
    BACKGROUND_COLOR = parse_color(os.getenv('BACKGROUND_COLOR', '15,15,35'))
    PLAYER1_COLOR = parse_color(os.getenv('PLAYER1_COLOR', '0,200,255'))
    PLAYER2_COLOR = parse_color(os.getenv('PLAYER2_COLOR', '255,100,100'))
    TEXT_COLOR = parse_color(os.getenv('TEXT_COLOR', '255,255,255'))
    
    # Configuration de l'interface
    UI_SCALE = 1.0
    CARD_WIDTH = 300
    CARD_HEIGHT = 400
    CARD_SPACING = 50
    ANIMATION_SPEED = 0.05
    HOVER_ALPHA = 30
    
    @classmethod
    def get_card_dimensions(cls):
        """Retourne les dimensions des cartes ajustées à l'échelle UI."""
        return (
            int(cls.CARD_WIDTH * cls.UI_SCALE),
            int(cls.CARD_HEIGHT * cls.UI_SCALE)
        )