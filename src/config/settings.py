from pathlib import Path

class GameSettings:
    # Chemins
    BASE_DIR = Path(__file__).resolve().parent.parent
    ASSETS_DIR = BASE_DIR / 'assets/'
    SOUNDS_DIR = ASSETS_DIR / 'sounds/'
    IMAGES_DIR = ASSETS_DIR / 'images/'
    FONTS_DIR = ASSETS_DIR / 'fonts/'
    LOGO_PATH = ASSETS_DIR / 'logo-bg.png'

    # Configuration de l'écran
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    FPS = 60

    # Mode debug
    DEBUG_MODE = False

    # Configuration du son
    SOUND_ENABLED = True
    MUSIC_VOLUME = 0.7
    SFX_VOLUME = 0.8

    @staticmethod
    def parse_color(color_str):
        """Convertit une chaîne RGB en tuple de couleur."""
        try:
            return tuple(map(int, color_str.split(',')))
        except ValueError:
            return (255, 255, 255)  # Couleur par défaut en cas d'erreur

    # Couleurs
    BACKGROUND_COLOR = (15, 15, 35)
    PLAYER1_COLOR = (0, 200, 255)
    PLAYER2_COLOR = (255, 100, 100)
    TEXT_COLOR = (255, 255, 255)

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
