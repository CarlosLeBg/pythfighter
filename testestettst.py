import pygame
import numpy as np

def create_detailed_sprite(character_type):
    sprite_sheet = pygame.Surface((200, 50), pygame.SRCALPHA)
    
    for frame in range(4):
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        
        if character_type == "python":
            color_body = (65, 105, 225)  # Royal Blue
            color_head = (255, 223, 0)   # Golden
        else:
            color_body = (34, 139, 34)   # Forest Green
            color_head = (255, 140, 0)   # Dark Orange
        
        # Body
        pygame.draw.ellipse(surface, color_body, (10, 20, 30, 25))
        
        # Head
        pygame.draw.circle(surface, color_head, (25, 15), 10)
        
        # Eyes
        eye_color = (0, 0, 0)
        pygame.draw.circle(surface, eye_color, (22, 13), 2)
        pygame.draw.circle(surface, eye_color, (28, 13), 2)
        
        # Arms
        arm_angle = np.pi/4 + (frame/4) * np.pi/2
        arm_x = 25 + 15 * np.cos(arm_angle)
        arm_y = 25 + 15 * np.sin(arm_angle)
        pygame.draw.line(surface, color_body, (25, 25), (arm_x, arm_y), 4)
        
        # Legs
        leg_spread = 5 + frame * 2
        pygame.draw.line(surface, color_body, (20, 40), (20-leg_spread, 50), 4)
        pygame.draw.line(surface, color_body, (30, 40), (30+leg_spread, 50), 4)
        
        # Add shading
        for i in range(10):
            pygame.draw.circle(surface, (*color_body, 10), (25, 25), 20-i, 1)
        
        # Add "scales" or "leaves" effect
        for i in range(5):
            y_offset = i * 5
            pygame.draw.arc(surface, (*color_body, 100), (5, 20+y_offset, 40, 10), 0, np.pi, 2)
        
        # Add frame to sprite sheet
        sprite_sheet.blit(surface, (frame * 50, 0))
    
    return sprite_sheet

# Usage
pygame.init()
screen = pygame.display.set_mode((400, 200))

python_sprite = create_detailed_sprite("python")
anaconda_sprite = create_detailed_sprite("anaconda")

# Display sprites
screen.blit(python_sprite, (0, 0))
screen.blit(anaconda_sprite, (0, 100))
pygame.display.flip()

# Keep window open
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()