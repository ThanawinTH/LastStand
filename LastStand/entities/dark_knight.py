import math
import pygame

from entities.enemy import Enemy


class DarkKnight(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x=x,
            y=y,
            hp=65,
            speed=60.0,
            armor=4,
            reward=20,
            name="Dark Knight",
            body_color=(70, 60, 95),
            glow_color=(180, 120, 255),
            radius=12,
            trail_length=6,
            aura_strength=6,
            is_boss=False,
        )

    def draw_body(self, screen: pygame.Surface) -> None:
        center = (int(self.x), int(self.y))

        pygame.draw.circle(screen, self.body_color, center, self.radius)
        pygame.draw.circle(screen, self.glow_color, center, self.radius, 2)

        # dark helm
        helm = pygame.Rect(int(self.x - 7), int(self.y - 8), 14, 12)
        pygame.draw.rect(screen, (35, 35, 55), helm, border_radius=3)
        pygame.draw.rect(screen, (180, 120, 255), helm, 1, border_radius=3)

        # visor glow
        pygame.draw.line(screen, (255, 180, 255), (int(self.x - 4), int(self.y - 2)), (int(self.x + 4), int(self.y - 2)), 2)

        # small orbit aura
        angle = self.visual_time * 4
        ox = int(self.x + math.cos(angle) * (self.radius + 4))
        oy = int(self.y + math.sin(angle) * (self.radius + 4))
        pygame.draw.circle(screen, (220, 180, 255), (ox, oy), 2)