import math
import pygame

from entities.enemy import Enemy


class BossEnemy(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x=x,
            y=y,
            hp=260,
            speed=38.0,
            armor=5,
            reward=80,
            name="Boss",
            body_color=(120, 40, 40),
            glow_color=(255, 100, 180),
            radius=20,
            trail_length=8,
            aura_strength=12,
            is_boss=True,
        )

    def draw_aura(self, screen: pygame.Surface) -> None:
        pulse1 = math.sin(self.visual_time * 4.0) * 4.0
        pulse2 = math.sin(self.visual_time * 6.0 + 1.2) * 3.0

        for extra, alpha in [(pulse1, 35), (pulse2 + 10, 22)]:
            aura_radius = int(self.radius + self.aura_strength + extra)
            surface = pygame.Surface((aura_radius * 2 + 12, aura_radius * 2 + 12), pygame.SRCALPHA)
            pygame.draw.circle(
                surface,
                (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha),
                (surface.get_width() // 2, surface.get_height() // 2),
                aura_radius,
            )
            screen.blit(surface, (int(self.x - surface.get_width() // 2), int(self.y - surface.get_height() // 2)))

    def draw_body(self, screen: pygame.Surface) -> None:
        center = (int(self.x), int(self.y))

        pygame.draw.circle(screen, self.body_color, center, self.radius)
        pygame.draw.circle(screen, self.glow_color, center, self.radius, 3)

        # crown / spikes
        spikes = [
            (self.x - 12, self.y - 10),
            (self.x - 6, self.y - 24),
            (self.x, self.y - 11),
            (self.x + 6, self.y - 24),
            (self.x + 12, self.y - 10),
        ]
        pygame.draw.lines(screen, (255, 160, 200), False, spikes, 3)

        # eyes
        pygame.draw.circle(screen, (255, 240, 210), (int(self.x - 5), int(self.y - 2)), 3)
        pygame.draw.circle(screen, (255, 240, 210), (int(self.x + 5), int(self.y - 2)), 3)

        # chest sigil
        pygame.draw.circle(screen, (255, 120, 180), (int(self.x), int(self.y + 6)), 4)
        pygame.draw.circle(screen, (255, 220, 235), (int(self.x), int(self.y + 6)), 1)