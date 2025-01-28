import pygame
import random

class Particle:
    def __init__(self, pos, vel, color, lifetime):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.color = color
        self.lifetime = lifetime
        self.age = 0

    def update(self, dt):
        self.pos += self.vel * dt
        self.age += dt

    def draw(self, surface):
        if self.age < self.lifetime:
            alpha = max(0, 255 - (self.age / self.lifetime) * 255)
            color = (*self.color, alpha)
            pygame.draw.circle(surface, color, self.pos, 3)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, pos, vel, color, lifetime):
        self.particles.append(Particle(pos, vel, color, lifetime))

    def update(self):
        dt = 1 / 60  # Assuming 60 FPS
        self.particles = [p for p in self.particles if p.age < p.lifetime]
        for particle in self.particles:
            particle.update(dt)

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)