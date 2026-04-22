import pygame

from config import MAGE_COST
from entities.tower import Tower
from entities.projectile import Projectile


class MageTower(Tower):
    def __init__(self, col, row, x, y) -> None:
        super().__init__(
            col=col,
            row=row,
            x=x,
            y=y,
            damage=22,
            attack_range=100,
            fire_rate=0.8,
            cost=MAGE_COST,
            name="Mage",
        )
        self.splash_radius = 60

    def attack(self, target, enemies: list, projectiles: list) -> None:
        _ = enemies
        projectile = Projectile(
            x=self.x,
            y=self.y,
            target=target,
            speed=250,
            damage=self.damage,
            color=(120, 220, 255),
            radius=7,
            projectile_type="magic",
            splash_radius=self.splash_radius,
        )
        projectiles.append(projectile)

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_base_selection(screen)

        center = (self.x, self.y)

        # Radii scale up with level
        outer_r = 13 + (self.level - 1) * 3    # 13 → 16 → 19
        mid_r = 8 + (self.level - 1) * 3  # 8 → 11 → 14
        core_r = 4 + (self.level - 1) * 2  # 4 →  6 →  8

        body_color = (90, 80, 220)
        pygame.draw.circle(screen, body_color, center, outer_r)
        pygame.draw.circle(screen, (220, 240, 255), center, outer_r, 2)

        pygame.draw.circle(screen, (120, 220, 255), center, mid_r)
        pygame.draw.circle(screen, (220, 255, 255), center, core_r)

        # Level 1: single outer accent ring
        pygame.draw.circle(screen, (150, 120, 255), center, outer_r + 3, 2)

        # Level 2+: second pulsing ring in a brighter colour
        if self.level >= 2:
            pygame.draw.circle(screen, (180, 100, 255), center, outer_r + 6, 1)

        # Level 3: third ring + bright white core dot
        if self.level == 3:
            pygame.draw.circle(screen, (220, 180, 255), center, outer_r + 9, 1)
            pygame.draw.circle(screen, (255, 255, 255), center, 3)
