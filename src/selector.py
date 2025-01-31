import pygame
import sys
import time
import math
from abc import ABC, abstractmethod
from math import sin, cos
from dataclasses import dataclass
from typing import List, Dict, Tuple
from config.settings import GameSettings
from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

FIGHTERS = {
    'AgileFighter': AgileFighter(),
    'Tank': Tank(),
    'BurstDamage': BurstDamage(),
    'ThunderStrike': ThunderStrike(),
    'Bruiser': Bruiser()
}
from position_manager import PositionManager
from particle_system import ParticleSystem

SETTINGS = GameSettings()
SCREEN_WIDTH = SETTINGS.SCREEN_WIDTH
SCREEN_HEIGHT = SETTINGS.SCREEN_HEIGHT
FPS = SETTINGS.FPS

# Enhanced colors
BACKGROUND_COLOR = (15, 15, 25)
TEXT_COLOR = (230, 230, 230)
HOVER_COLOR = (255, 255, 255, 200)
CARD_SHADOW_COLOR = (0, 0, 0, 120)
GRADIENT_TOP = (40, 40, 60)
GRADIENT_BOTTOM = (15, 15, 25)

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
    difficulty: str

class Animation(ABC):
    def __init__(self, duration=1.0, loop=True):
        self.duration = duration
        self.loop = loop
        self.time = 0
        
    @abstractmethod
    def update(self, dt):
        pass
        
    def reset(self):
        self.time = 0

class SineWave(Animation):
    def __init__(self, amplitude, frequency=1.0, **kwargs):
        super().__init__(**kwargs)
        self.amplitude = amplitude
        self.frequency = frequency
        
    def update(self, dt):
        self.time += dt
        if self.loop:
            t = (self.time * self.frequency) % self.duration
        else:
            t = min(self.time * self.frequency, self.duration)
        return math.sin(t * math.pi * 2) * self.amplitude

class Spring(Animation):
    def __init__(self, start=0, end=1, stiffness=10.0, damping=0.8, **kwargs):
        super().__init__(loop=False, **kwargs)
        self.pos = start
        self.vel = 0
        self.target = end
        self.stiffness = stiffness
        self.damping = damping
        
    def update(self, dt):
        force = (self.target - self.pos) * self.stiffness
        self.vel += force * dt
        self.vel *= (1 - self.damping * dt)
        self.pos += self.vel * dt
        return self.pos

class AnimationManager:
    def __init__(self):
        self.animations = {}
        
    def add(self, name, animation):
        self.animations[name] = animation
        
    def update(self, dt):
        return {name: anim.update(dt) for name, anim in self.animations.items()}

class CharacterSelect:
    def __init__(self):
        # Chargement des polices
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 48),
            'normal': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }
        
        # Calcul des positions centrées
        self.calculate_layout()
        
        self.animations = {
            'hover': AnimationManager(),
            'card': AnimationManager(),
            'stats': AnimationManager()
        }
        
        # Card animations
        self.animations['card'].add('float', SineWave(2, 0.5))  # Réduire l'amplitude
        # Désactiver l'animation de secousse
        # self.animations['card'].add('shake', SineWave(1, 1.3))  # Réduire l'amplitude ou commenter cette ligne
        
        # Stat bar animations
        self.animations['stats'].add('fill', Spring(0, 1, stiffness=15))
        
        # Hover effects
        self.animations['hover'].add('scale', Spring(1, 1.05, stiffness=20))  # Réduire l'amplitude
        self.animations['hover'].add('glow', SineWave(0.2, 2))  # Réduire l'amplitude

        self.particles = ParticleSystem()  # Initialiser ParticleSystem

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
        card_rect = self.position_manager.card_positions[name]
        hover = card_rect.collidepoint(pygame.mouse.get_pos())
        
        dt = 1/FPS
        anim_values = {
            'card': self.animations['card'].update(dt),
            'hover': self.animations['hover'].update(dt) if hover else {'scale': 1, 'glow': 0}
        }
        
        # Apply animations
        y_offset = anim_values['card']['float']
        x_offset = anim_values['card'].get('shake', 0) if hover else 0  # Utiliser get pour éviter KeyError
        scale = anim_values['hover']['scale']
        glow_intensity = anim_values['hover']['glow']
        
        # Scale card size based on hover
        card_width = int(SETTINGS.CARD_WIDTH * scale)
        card_height = int(SETTINGS.CARD_HEIGHT * scale)
        
        # Dessiner la carte du personnage avec la couleur de base et le style
        base_color = data.color
        style = self.fonts['normal'].render(f"Style: {data.style}", True, TEXT_COLOR)
        difficulty = self.fonts['normal'].render(f"Difficulté: {data.difficulty}", True, TEXT_COLOR)
        # Ajoutez ici le code pour dessiner la carte du personnage

    def draw_detail_panel(self):
        if not self.hovered_character:
            return
            
        dt = 1/FPS
        anim_values = self.animations['stats'].update(dt)
        
        # Utilisation de anim_values['fill'] pour les barres de statistiques
        # Ajoutez ici le code pour dessiner le panneau de détails

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for char_name, char_rect in self.position_manager.card_positions.items():
                        if char_rect.collidepoint(event.pos):
                            self.selected[self.current_player] = char_name
                            self.current_player = "player2" if self.current_player == "player1" else "player1"
                            break
                            
            # Draw everything
            self.draw_gradient_background()
            self.particles.update()
            self.particles.draw(screen)
            
            for char_name in FIGHTERS:
                self.draw_character_card(char_name, FIGHTERS[char_name])
                
            self.draw_detail_panel()
            self.draw_player_prompts()
            
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CharacterSelect()
    game.run()