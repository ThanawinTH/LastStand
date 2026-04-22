from config import ARCHER_COST
from entities.tower import Tower
from entities.projectile import Projectile
import pygame


class ArcherTower(Tower):
    def __init__(self, col, row, x, y) -> None:
        super().__init__(
            col=col,
            row=row,
            x=x,
            y=y,
            damage=12,
            attack_range=110,
            fire_rate=1.5,
            cost=ARCHER_COST,
            name="Archer",
        )

    def attack(self, target, enemies: list, projectiles: list) -> None:
        _ = enemies
        projectile = Projectile(
            x=self.x,
            y=self.y,
            target=target,
            speed=360,
            damage=self.damage,
            color=(255, 230, 120),
            radius=4,
            projectile_type="arrow",
        )
        projectiles.append(projectile)

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_base_selection(screen)

        center = (self.x, self.y)

        # Scale size and color intensity with level
        radius = 13 + (self.level - 1) * 3        # 13 → 16 → 19
        tip_h = 10 + (self.level - 1) * 4        # 10 → 14 → 18  (arrow height)
        base_w = 8 + (self.level - 1) * 3  # 8 → 11 → 14  (arrow half-width)

        body_color = (80 + (self.level - 1) * 20,  150, 230)
        ring_color = (220, 240, 255)

        pygame.draw.circle(screen, body_color, center, radius)
        pygame.draw.circle(screen, ring_color, center, radius, 2)

        # Level 2+: add a second decorative ring
        if self.level >= 2:
            pygame.draw.circle(screen, (255, 220, 80), center, radius + 3, 1)

        # Level 3: add a bright outer glow ring
        if self.level == 3:
            pygame.draw.circle(screen, (255, 255, 160), center, radius + 6, 1)

        # Arrow / triangle — grows with level
        arrow_points = [
            (self.x,          self.y - tip_h),
            (self.x + base_w, self.y + tip_h // 2),
            (self.x - base_w, self.y + tip_h // 2),
        ]
        arrow_color = (255, 230, 120) if self.level < 3 else (255, 255, 100)
        pygame.draw.polygon(screen, arrow_color, arrow_points)
        pygame.draw.polygon(screen, (255, 250, 220), arrow_points, 2)
