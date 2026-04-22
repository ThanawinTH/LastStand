import pygame
import math


class Projectile:
    """Base projectile. Moves in a straight line toward its spawn direction."""

    COLOR = (255, 255, 100)
    SIZE = 5
    SPEED = 8

    def __init__(self, x: float, y: float, target, damage: float):
        self.x = x
        self.y = y
        self.damage = damage

        dx = target.x - x
        dy = target.y - y
        dist = math.hypot(dx, dy) or 1
        self.vx = (dx / dist) * self.SPEED
        self.vy = (dy / dist) * self.SPEED

        self.rect = pygame.Rect(int(x), int(y), self.SIZE, self.SIZE)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

    def on_hit(self, enemy, all_enemies: list) -> None:
        """Called when this projectile hits an enemy."""
        enemy.take_damage(self.damage)

    def off_screen(self) -> bool:
        return not (-50 < self.x < 850 and -50 < self.y < 650)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.COLOR, (int(self.x), int(self.y)), self.SIZE)


class Arrow(Projectile):
    """Single-target fast arrow fired by ArcherTower."""
    COLOR = (220, 180, 80)
    SIZE = 4
    SPEED = 10


class MagicBolt(Projectile):
    """Slow, high-damage bolt fired by MageTower. Deals splash damage on hit."""
    COLOR = (160, 80, 220)
    SIZE = 7
    SPEED = 5
    SPLASH_RADIUS = 50

    def on_hit(self, enemy, all_enemies: list) -> None:
        # Splash: damage all enemies within radius
        for e in all_enemies:
            dist = math.hypot(e.x - self.x, e.y - self.y)
            if dist <= self.SPLASH_RADIUS:
                e.take_damage(self.damage)


class Bolt(Projectile):
    """
    Piercing bolt fired by BallistaTower.
    Passes through multiple enemies in a line — handled in game.py by
    NOT removing the projectile on first hit (on_hit returns False to signal
    it should remain active). Damage decreases slightly per enemy pierced.
    """
    COLOR = (200, 150, 80)
    SIZE = 6
    SPEED = 7
    MAX_PIERCE = 3

    def __init__(self, x: float, y: float, target, damage: float):
        super().__init__(x, y, target, damage)
        self.pierced = 0
        self.hit_enemies: set = set()

    def on_hit(self, enemy, all_enemies: list) -> bool:
        """Returns True if the bolt should be removed, False if it pierces."""
        if id(enemy) in self.hit_enemies:
            return False
        self.hit_enemies.add(id(enemy))
        enemy.take_damage(self.damage * (0.8 ** self.pierced))
        self.pierced += 1
        return self.pierced >= self.MAX_PIERCE
