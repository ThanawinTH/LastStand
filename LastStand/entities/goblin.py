import pygame

from entities.enemy import Enemy


class Goblin(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x=x,
            y=y,
            hp=35,
            speed=90.0,
            armor=0,
            reward=8,
            name="Goblin",
            body_color=(170, 70, 70),
            glow_color=(255, 120, 120),
            radius=9,
            trail_length=5,
            aura_strength=3,
            is_boss=False,
        )

    def draw_body(self, screen: pygame.Surface) -> None:
        center = (int(self.x), int(self.y))

        pygame.draw.circle(screen, self.body_color, center, self.radius)
        pygame.draw.circle(screen, self.glow_color, center, self.radius, 2)

        # horns / sharp head
        horn1 = [(self.x - 5, self.y - 7), (self.x - 1, self.y - 14), (self.x + 1, self.y - 6)]
        horn2 = [(self.x + 5, self.y - 7), (self.x + 1, self.y - 14), (self.x - 1, self.y - 6)]
        pygame.draw.polygon(screen, (255, 180, 180), horn1)
        pygame.draw.polygon(screen, (255, 180, 180), horn2)

        # glowing eyes
        pygame.draw.circle(screen, (255, 240, 180), (int(self.x - 3), int(self.y - 1)), 2)
        pygame.draw.circle(screen, (255, 240, 180), (int(self.x + 3), int(self.y - 1)), 2)