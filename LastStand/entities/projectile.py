import math
import pygame


class Projectile:
    def __init__(
        self,
        x: float,
        y: float,
        target,
        speed: float,
        damage: int,
        color: tuple[int, int, int],
        radius: int,
        projectile_type: str,
        splash_radius: int = 0,
        max_pierce_targets: int = 0,
    ) -> None:
        self.x = x
        self.y = y

        self.target = target
        self.speed = speed
        self.damage = damage
        self.color = color
        self.radius = radius
        self.projectile_type = projectile_type

        self.splash_radius = splash_radius
        self.max_pierce_targets = max_pierce_targets

        self.alive = True

    def update(self, dt: float, enemies: list) -> None:
        if not self.alive:
            return

        if self.target is None or not self.target.alive:
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.speed * dt or dist < 4:
            self.on_hit(enemies)
            self.alive = False
            return

        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def on_hit(self, enemies: list) -> None:
        if self.projectile_type == "arrow":
            if self.target.alive:
                self.target.take_damage(self.damage)

        elif self.projectile_type == "magic":
            for enemy in enemies:
                if not enemy.alive:
                    continue
                dx = enemy.x - self.target.x
                dy = enemy.y - self.target.y
                dist = math.hypot(dx, dy)
                if dist <= self.splash_radius:
                    enemy.take_damage(self.damage)

        elif self.projectile_type == "bolt":
            candidates = []
            for enemy in enemies:
                if not enemy.alive:
                    continue
                dx = enemy.x - self.target.x
                dy = enemy.y - self.target.y
                dist = math.hypot(dx, dy)
                if dist <= self.splash_radius:
                    candidates.append(enemy)

            candidates.sort(key=lambda e: e.path_index, reverse=True)
            hit_list = candidates[:self.max_pierce_targets] if self.max_pierce_targets > 0 else candidates

            for enemy in hit_list:
                enemy.take_damage(self.damage)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return

        if self.projectile_type == "arrow":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 245, 200), (int(self.x), int(self.y)), self.radius, 1)

        elif self.projectile_type == "magic":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (220, 255, 255), (int(self.x), int(self.y)), max(2, self.radius - 2))

        elif self.projectile_type == "bolt":
            rect = pygame.Rect(int(self.x) - 5, int(self.y) - 2, 10, 4)
            pygame.draw.rect(screen, self.color, rect, border_radius=2)
            pygame.draw.rect(screen, (255, 235, 200), rect, 1, border_radius=2)