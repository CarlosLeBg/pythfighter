import pygame
import sys
import time
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config.fighters import AgileFighter, Tank, BurstDamage, ThunderStrike, Bruiser

BASE_WIDTH, BASE_HEIGHT = 175, 112
SCALE_FACTOR = 7
VISIBLE_WIDTH = BASE_WIDTH * SCALE_FACTOR
VISIBLE_HEIGHT = BASE_HEIGHT * SCALE_FACTOR

class Fighter:
    def __init__(self, player, x, y, fighter_data):
        self.player = player
        self.name = fighter_data.name
        self.color = fighter_data.color
        self.speed = fighter_data.speed * 1.2
        self.damage = fighter_data.damage
        self.max_health = fighter_data.stats["Vie"]
        self.health = self.max_health
        
        self.max_stamina = 100
        self.stamina = self.max_stamina
        
        self.pos_x = float(x)
        self.pos_y = float(91)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.direction = 1 if player == 1 else -1
        
        self.fighter_width = VISIBLE_WIDTH // 16
        self.fighter_height = VISIBLE_HEIGHT // 4
        self.rect = pygame.Rect(x, 91, self.fighter_width, self.fighter_height)
        self.hitbox = pygame.Rect(x + self.fighter_width//4, 91 + self.fighter_height//4,
                                self.fighter_width//2, self.fighter_height*3//4)
        
        self.on_ground = True
        self.attacking = False
        self.can_attack = True  # New attribute to prevent multiple attacks
        self.blocking = False
        self.attack_cooldown = 0
        self.invincibility_frames = 0
        self.combo_count = 0
        self.last_hit_time = 0

    def draw(self, surface):
        if self.invincibility_frames % 4 < 2:  # Flash when hit
            pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)
        
        bar_width = VISIBLE_WIDTH * 0.4
        bar_height = 20
        health_percentage = max(0, self.health / self.max_health)
        health_color = (int(255 * (1 - health_percentage)),
                       int(255 * health_percentage), 0)
        
        bar_x = 20 if self.player == 1 else VISIBLE_WIDTH - bar_width - 20
        
        pygame.draw.rect(surface, (100, 0, 0),
                        (bar_x, 10, bar_width, bar_height),
                        border_radius=10)
        pygame.draw.rect(surface, health_color,
                        (bar_x, 10, bar_width * health_percentage, bar_height),
                        border_radius=10)
        
        # Draw Stamina bar
        stamina_percentage = max(0, self.stamina / self.max_stamina)
        stamina_color = (0, 0, 255)  # Blue for stamina
        
        pygame.draw.rect(surface, (0, 0, 100),
                        (bar_x, 40, bar_width, bar_height),
                        border_radius=10)
        pygame.draw.rect(surface, stamina_color,
                        (bar_x, 40, bar_width * stamina_percentage, bar_height),
                        border_radius=10)
        
        # Adjusted positions for text
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.name, True, (220, 220, 240))
        health_text = name_font.render(f"{int(self.health)}/{self.max_health}", True, (150, 150, 180))
        combo_text = name_font.render(f"Combo: {self.combo_count}", True, (255, 215, 0))
        
        if self.player == 1:
            surface.blit(name_text, (bar_x, 60))
            surface.blit(health_text, (bar_x + bar_width - 100, 60))
            surface.blit(combo_text, (bar_x, 80))
        else:
            surface.blit(name_text, (bar_x + bar_width - name_text.get_width(), 60))
            surface.blit(health_text, (bar_x, 60))
            surface.blit(combo_text, (bar_x + bar_width - combo_text.get_width(), 80))

    def take_damage(self, damage, current_time):
        if self.invincibility_frames <= 0:
            actual_damage = damage * (0.5 if self.blocking else 1)
            self.health = max(0, self.health - actual_damage)
            self.invincibility_frames = 30
            if current_time - self.last_hit_time < 1.0:
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.last_hit_time = current_time

    def attack(self, opponent_x):
        if self.can_attack and self.attack_cooldown == 0 and not self.blocking and self.stamina >= 10:
            distance = abs(self.rect.centerx - opponent_x)
            if distance < self.rect.width * 2:
                self.attacking = True
                self.can_attack = False  # Prevent multiple attacks
                self.attack_cooldown = 15
                self.stamina -= 10  # Spend stamina on attack

    def reset_attack(self):
        # Reset attack state when cooldown completes
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 0:
                self.attacking = False
                self.can_attack = True

    def block(self):
        self.blocking = True
        self.stamina = max(0, self.stamina - 5)  # Spend stamina while blocking

    def recover_stamina(self):
        if self.stamina < self.max_stamina:
            self.stamina += 0.1  # Slower recovery
        self.stamina = min(self.stamina, self.max_stamina)

    def update_physics(self):
        GRAVITY = 0.4
        GROUND_Y = VISIBLE_HEIGHT - VISIBLE_HEIGHT // 5.4
        MAX_JUMP_HEIGHT = 60

        if not self.on_ground:
            self.vel_y += GRAVITY

        friction = 0.85 if self.on_ground else 0.95
        self.vel_x *= friction

        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        if self.pos_y < MAX_JUMP_HEIGHT:
            self.pos_y = MAX_JUMP_HEIGHT
            self.vel_y = 0

        if self.pos_y + self.rect.height >= GROUND_Y:
            self.pos_y = GROUND_Y - self.rect.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.pos_x = max(0, min(self.pos_x, VISIBLE_WIDTH - self.rect.width))

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        self.hitbox.topleft = (self.rect.x + self.rect.width // 4,
                               self.rect.y + self.rect.height // 4)

        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1

        # Reset attack state
        self.reset_attack()

class Game:
    def __init__(self, player1_type="AgileFighter", player2_type="Tank"):
        pygame.init()
        pygame.joystick.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
        pygame.display.set_caption("PythFighter")
        
        self.bg_image = pygame.image.load(r"src\assets\backgrounds\backg.jpg")
        self.bg_image = pygame.transform.scale(self.bg_image, (VISIBLE_WIDTH, VISIBLE_HEIGHT))
        
        self.controllers = []
        for i in range(min(2, pygame.joystick.get_count())):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.controllers.append(joy)

        fighter_map = {
            "AgileFighter": AgileFighter,
            "Tank": Tank,
            "BurstDamage": BurstDamage,
            "ThunderStrike": ThunderStrike,
            "Bruiser": Bruiser
        }
        GROUND_Y = 91  
        fighter_height = VISIBLE_HEIGHT // 4  

        self.fighters = [
            Fighter(1, VISIBLE_WIDTH//4, GROUND_Y - fighter_height, fighter_map[player1_type]()),
            Fighter(2, VISIBLE_WIDTH*3//4, GROUND_Y - fighter_height, fighter_map[player2_type]())
        ]

        self.clock = pygame.time.Clock()
        self.pause_menu_active = False
        self.show_start_timer = True
        self.start_time = time.time()
        self.game_start_time = None
        self.round_time = 99
        self.font = pygame.font.Font(None, 36)

    def draw_timer(self):
        if self.game_start_time:
            remaining_time = max(0, int(self.round_time - (time.time() - self.game_start_time)))
            timer_text = self.font.render(str(remaining_time), True, (255, 255, 255))
            timer_rect = timer_text.get_rect(center=(VISIBLE_WIDTH//2, 30))
            self.screen.blit(timer_text, timer_rect)
            return remaining_time
        return self.round_time

    def draw_pause_menu(self):
        pause_surface = pygame.Surface((VISIBLE_WIDTH, VISIBLE_HEIGHT), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 128))  # Semi-transparent black

        pause_text = self.font.render("PAUSE", True, (255, 255, 255))
        resume_text = self.font.render("Press ESC to Resume", True, (200, 200, 200))
        
        pause_rect = pause_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2 - 50))
        resume_rect = resume_text.get_rect(center=(VISIBLE_WIDTH//2, VISIBLE_HEIGHT//2 + 50))
        
        self.screen.blit(pause_surface, (0, 0))
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)
        pygame.display.flip()

    def handle_controller_input(self, fighter, controller, current_time):
        deadzone = 0.2
        
        x_axis = controller.get_axis(0)
        if abs(x_axis) > deadzone:
            fighter.vel_x = fighter.speed * 2 * x_axis
            fighter.direction = 1 if x_axis > 0 else -1
        
        if controller.get_button(0) and fighter.on_ground:
            fighter.vel_y = -10
            fighter.on_ground = False
        
        if controller.get_button(2):  # Blocking
            fighter.block()
        
        if controller.get_button(1):  # Attack
            fighter.attack(self.fighters[1 if fighter.player == 1 else 0].rect.centerx)

    def handle_keyboard_input(self, fighter, keys, current_time):
        if fighter.player == 1:
            if keys[pygame.K_a]:
                fighter.vel_x = -fighter.speed * 2
                fighter.direction = -1
            elif keys[pygame.K_d]:
                fighter.vel_x = fighter.speed * 2
                fighter.direction = 1
            
            if keys[pygame.K_w] and fighter.on_ground:
                fighter.vel_y = -10
                fighter.on_ground = False
            
            if keys[pygame.K_LSHIFT]:  # Blocking
                fighter.block()
            
            if keys[pygame.K_r]:  # Attack
                fighter.attack(self.fighters[1].rect.centerx)
        else:
            if keys[pygame.K_LEFT]:
                fighter.vel_x = -fighter.speed * 2
                fighter.direction = -1
            elif keys[pygame.K_RIGHT]:
                fighter.vel_x = fighter.speed * 2
                fighter.direction = 1

            if keys[pygame.K_UP] and fighter.on_ground:
                fighter.vel_y = -10
                fighter.on_ground = False
            
            if keys[pygame.K_RSHIFT]:  # Blocking
                fighter.block()
            
            if keys[pygame.K_RETURN]:  # Attack
                fighter.attack(self.fighters[0].rect.centerx)

    def draw_countdown(self, number):
        font = pygame.font.Font(None, 200)
        text = font.render(str(number), True, (255, 255, 255))
        text_rect = text.get_rect(center=(VISIBLE_WIDTH/2, VISIBLE_HEIGHT/2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)

    def update(self):
        current_time = time.time()
        self.screen.fill((0, 0, 0))  
        self.screen.blit(self.bg_image, (0, 0))  
        
        keys = pygame.key.get_pressed()
        
        # Handle game pause
        if keys[pygame.K_ESCAPE]:
            self.pause_menu_active = not self.pause_menu_active
            pygame.time.delay(200)  # Prevent multiple toggles
        
        if self.pause_menu_active:
            self.draw_pause_menu()
            return

        # Draw and check timer
        remaining_time = self.draw_timer()
        if remaining_time <= 0:
            print("Time's up!")
            pygame.quit()
            sys.exit()

        for fighter in self.fighters:
            fighter.update_physics()
            fighter.recover_stamina() 
            fighter.draw(self.screen)

        # Input handling
        for i, fighter in enumerate(self.fighters):
            if i < len(self.controllers):
                self.handle_controller_input(fighter, self.controllers[i], current_time)
            
            self.handle_keyboard_input(fighter, keys, current_time)

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        # Countdown before game starts
        if self.show_start_timer:
            for i in range(3, 0, -1):
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.bg_image, (0, 0))
                self.draw_countdown(i)
            self.show_start_timer = False
            self.game_start_time = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.game_start_time:
                # Check for first fighter's hit
                if self.fighters[0].hitbox.colliderect(self.fighters[1].hitbox):
                    if self.fighters[0].attacking:
                        self.fighters[1].take_damage(self.fighters[0].damage, time.time())
                    elif self.fighters[1].attacking:
                        self.fighters[0].take_damage(self.fighters[1].damage, time.time())

                # Check for game over conditions
                if self.fighters[0].health <= 0 or self.fighters[1].health <= 0:
                    print("Game Over!")
                    pygame.quit()
                    sys.exit()

                self.update()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        game = Game(sys.argv[1], sys.argv[2])
    else:
        game = Game()
    game.run()
