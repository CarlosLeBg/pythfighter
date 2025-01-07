import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pyth Fighter - Menu de Sélection")

# Couleurs
BACKGROUND_COLOR = (15, 15, 30)
HIGHLIGHT_COLOR = (255, 255, 255)
PLAYER1_COLOR = (0, 200, 255)
PLAYER2_COLOR = (255, 100, 100)

CHARACTER_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255)
]

CHARACTER_POSITIONS = [
    (200, 250),
    (400, 250),
    (600, 250),
    (800, 250),
    (1000, 250),
]

# Variables globales
joysticks = []
player1_selection = 0
player2_selection = 1
ready = [False, False]

# Texte
font = pygame.font.Font(None, 60)

# Initialisation des joysticks
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)

# Afficher un texte centré
def draw_text_centered(text, size, color, y_offset=0):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

# Transition vers le jeu
def start_game(player1, player2):
    screen.fill(BACKGROUND_COLOR)
    draw_text_centered(f"Joueur 1 : Personnage {player1 + 1}", 60, PLAYER1_COLOR, -40)
    draw_text_centered(f"Joueur 2 : Personnage {player2 + 1}", 60, PLAYER2_COLOR, 40)
    pygame.display.flip()
    pygame.time.wait(5000)
    print(f"Personnage Joueur 1 : {player1 + 1}, Joueur 2 : {player2 + 1}")
    sys.exit()  # Simule l'exécution d'un autre code

# Fonction principale
def main():
    global player1_selection, player2_selection, ready
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Détection des périphériques
        keys = pygame.key.get_pressed()

        # Joystick pour Joueur 1
        if len(joysticks) > 0:
            joystick1 = joysticks[0]
            if not ready[0]:
                if joystick1.get_axis(0) < -0.5:  # Gauche
                    player1_selection = (player1_selection - 1) % len(CHARACTER_COLORS)
                if joystick1.get_axis(0) > 0.5:  # Droite
                    player1_selection = (player1_selection + 1) % len(CHARACTER_COLORS)
                if joystick1.get_button(0):  # Bouton A pour valider
                    ready[0] = True

        # Joystick pour Joueur 2
        if len(joysticks) > 1:
            joystick2 = joysticks[1]
            if not ready[1]:
                if joystick2.get_axis(0) < -0.5:  # Gauche
                    player2_selection = (player2_selection - 1) % len(CHARACTER_COLORS)
                if joystick2.get_axis(0) > 0.5:  # Droite
                    player2_selection = (player2_selection + 1) % len(CHARACTER_COLORS)
                if joystick2.get_button(0):  # Bouton A pour valider
                    ready[1] = True

        # Clavier et souris
        if not ready[0]:
            if keys[pygame.K_a]:
                player1_selection = (player1_selection - 1) % len(CHARACTER_COLORS)
            if keys[pygame.K_d]:
                player1_selection = (player1_selection + 1) % len(CHARACTER_COLORS)
            if keys[pygame.K_RETURN]:
                ready[0] = True

        if not ready[1]:
            if keys[pygame.K_LEFT]:
                player2_selection = (player2_selection - 1) % len(CHARACTER_COLORS)
            if keys[pygame.K_RIGHT]:
                player2_selection = (player2_selection + 1) % len(CHARACTER_COLORS)
            if keys[pygame.K_SPACE]:
                ready[1] = True

        # Dessiner les personnages
        for i, (color, pos) in enumerate(zip(CHARACTER_COLORS, CHARACTER_POSITIONS)):
            rect = pygame.Rect(pos[0] - 75, pos[1] - 75, 150, 150)
            pygame.draw.rect(screen, color, rect, border_radius=15)

            # Indicateurs pour les sélections
            if i == player1_selection:
                pygame.draw.rect(screen, PLAYER1_COLOR, rect, 5, border_radius=15)
            if i == player2_selection:
                pygame.draw.rect(screen, PLAYER2_COLOR, rect, 5, border_radius=15)

        # Affichage des statuts des joueurs
        draw_text_centered(f"Joueur 1 : {'Prêt' if ready[0] else 'Choisir'}", 40, PLAYER1_COLOR, -300)
        draw_text_centered(f"Joueur 2 : {'Prêt' if ready[1] else 'Choisir'}", 40, PLAYER2_COLOR, -250)

        # Lancer le jeu si les deux joueurs sont prêts
        if all(ready):
            start_game(player1_selection, player2_selection)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
