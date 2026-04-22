import pygame

from entities.enemy import Enemy


class Orc(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x=x,
            y=y,
            hp=80,
            speed=45.0,
            armor=1,
            reward=15,
            name="Orc",
            body_color=(90, 135, 70),
            glow_color=(160, 230, 120),
            radius=13,
            trail_length=4,
            aura_strength=4,
            is_boss=False,
        )

    def draw_body(self, screen: pygame.Surface) -> None:
        center = (int(self.x), int(self.y))

        pygame.draw.circle(screen, self.body_color, center, self.radius)
        pygame.draw.circle(screen, self.glow_color, center, self.radius, 2)

        # armor plate
        chest = pygame.Rect(int(self.x - 7), int(self.y - 5), 14, 12)
        pygame.draw.rect(screen, (80, 90, 100), chest, border_radius=3)
        pygame.draw.rect(screen, (180, 220, 180), chest, 1, border_radius=3)

        # eyes
        pygame.draw.circle(screen, (255, 245, 180), (int(self.x - 4), int(self.y - 2)), 2)
        pygame.draw.circle(screen, (255, 245, 180), (int(self.x + 4), int(self.y - 2)), 2)