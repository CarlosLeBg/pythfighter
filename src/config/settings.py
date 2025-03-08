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
    FPS = 20

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

    @classmethod
    def calculate_positions(cls, num_cards, center_x=None, center_y=None):
        """
        Calcule les positions des cartes sur l'écran.
        :param num_cards: Nombre total de cartes.
        :param center_x: Centre horizontal (par défaut, milieu de l'écran).
        :param center_y: Centre vertical (par défaut, milieu de l'écran).
        :return: Liste des positions des cartes.
        """
        card_width, card_height = cls.get_card_dimensions()
        total_width = num_cards * card_width + (num_cards - 1) * cls.CARD_SPACING
        center_x = center_x or cls.SCREEN_WIDTH // 2
        center_y = center_y or cls.SCREEN_HEIGHT // 2

        start_x = center_x - total_width // 2
        positions = [
            (start_x + i * (card_width + cls.CARD_SPACING), center_y - card_height // 2)
            for i in range(num_cards)
        ]
        return positions

    @classmethod
    def get_ui_element_position(cls, element_width, element_height, position="center"):
        """
        Retourne la position pour un élément d'interface.
        :param element_width: Largeur de l'élément.
        :param element_height: Hauteur de l'élément.
        :param position: Position sur l'écran ("center", "top-left", "top-right", etc.).
        :return: Tuple (x, y) de la position.
        """
        if position == "center":
            x = (cls.SCREEN_WIDTH - element_width) // 2
            y = (cls.SCREEN_HEIGHT - element_height) // 2
        elif position == "top-left":
            x = 0
            y = 0
        elif position == "top-right":
            x = cls.SCREEN_WIDTH - element_width
            y = 0
        elif position == "bottom-left":
            x = 0
            y = cls.SCREEN_HEIGHT - element_height
        elif position == "bottom-right":
            x = cls.SCREEN_WIDTH - element_width
            y = cls.SCREEN_HEIGHT - element_height
        else:
            raise ValueError("Position non reconnue.")
        return x, y
