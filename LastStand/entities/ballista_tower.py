from config import BALLISTA_COST
from entities.tower import Tower
from entities.projectile import Projectile
import pygame


class BallistaTower(Tower):
    def __init__(self, col, row, x, y) -> None:
        super().__init__(
            col=col,
            row=row,
            x=x,
            y=y,
            damage=18,
            attack_range=140,
            fire_rate=1.0,
            cost=BALLISTA_COST,
            name="Ballista",
        )
        self.max_pierce_targets = 3
        self.impact_radius = 65

    def attack(self, target, enemies: list, projectiles: list) -> None:
        _ = enemies
        projectile = Projectile(
            x=self.x,
            y=self.y,
            target=target,
            speed=280,
            damage=self.damage,
            color=(255, 180, 90),
            radius=5,
            projectile_type="bolt",
            splash_radius=self.impact_radius,
            max_pierce_targets=self.max_pierce_targets,
        )
        projectiles.append(projectile)

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_base_selection(screen)

        # Body grows with level: 28×20 → 33×25 → 38×30
        bw = 28 + (self.level - 1) * 5
        bh = 20 + (self.level - 1) * 5
        lw = 3 + (self.level - 1)      # cross line width: 3 → 4 → 5

        body_rect = pygame.Rect(self.x - bw // 2, self.y - bh // 2, bw, bh)

        # Body colour deepens slightly on higher levels
        body_color = (130 + (self.level - 1) * 15,
                      100 + (self.level - 1) * 10, 70)
        border_color = (230, 230, 230) if self.level < 3 else (255, 240, 160)

        pygame.draw.rect(screen, body_color, body_rect, border_radius=4)
        pygame.draw.rect(screen, border_color, body_rect, 2, border_radius=4)

        # X cross — widens with level
        hw = bw // 2 - 2
        hh = bh // 2 - 2
        cross_color = (255, 200, 120) if self.level < 3 else (255, 230, 80)
        pygame.draw.line(screen, cross_color, (self.x - hw,
                         self.y - hh), (self.x + hw, self.y + hh), lw)
        pygame.draw.line(screen, cross_color, (self.x - hw,
                         self.y + hh), (self.x + hw, self.y - hh), lw)

        # Level 2+: small corner accent squares
        if self.level >= 2:
            for cx, cy in [(self.x - hw, self.y - hh), (self.x + hw, self.y - hh),
                           (self.x - hw, self.y + hh), (self.x + hw, self.y + hh)]:
                pygame.draw.rect(screen, (255, 220, 100),
                                 pygame.Rect(cx - 2, cy - 2, 4, 4))

        # Level 3: bright outer border glow
        if self.level == 3:
            glow_rect = body_rect.inflate(6, 6)
            pygame.draw.rect(screen, (255, 200, 60),
                             glow_rect, 1, border_radius=6)
