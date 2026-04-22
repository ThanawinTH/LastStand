import pygame
import math


class Tower:
    def __init__(
        self,
        col: int,
        row: int,
        x: int,
        y: int,
        damage: int,
        attack_range: int,
        fire_rate: float,
        cost: int,
        name: str,
    ) -> None:
        self.col = col
        self.row = row

        self.x = x
        self.y = y

        self.damage = damage
        self.attack_range = attack_range
        self.fire_rate = fire_rate
        self.cost = cost
        self.name = name

        self.level = 1
        self.max_level = 3
        self.upgrade_cost = int(cost * 0.75)
        self.sell_value = int(cost * 0.60)

        self.cooldown = 1.0 / fire_rate
        self.timer = 0.0

        self.is_selected = False

    def update(self, dt: float, enemies: list, projectiles: list) -> None:
        self.timer += dt

        if self.timer >= self.cooldown:
            target = self.find_target(enemies)
            if target:
                self.attack(target, enemies, projectiles)
                self.timer = 0.0

    def find_target(self, enemies: list):
        target = None
        best_progress = -1

        for enemy in enemies:
            if not enemy.alive:
                continue

            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.hypot(dx, dy)

            if dist > self.attack_range:
                continue

            if enemy.path_index > best_progress:
                best_progress = enemy.path_index
                target = enemy

        return target

    def attack(self, target, enemies: list, projectiles: list) -> None:
        raise NotImplementedError

    def can_upgrade(self) -> bool:
        return self.level < self.max_level

    def upgrade(self) -> bool:
        if not self.can_upgrade():
            return False

        self.level += 1
        self.damage += 5
        self.attack_range += 12
        self.fire_rate += 0.15

        self.cooldown = 1.0 / self.fire_rate
        self.sell_value += int(self.upgrade_cost * 0.60)
        self.upgrade_cost += 35
        return True

    def contains_point(self, mouse_pos: tuple[int, int]) -> bool:
        mx, my = mouse_pos
        dx = mx - self.x
        dy = my - self.y
        return math.hypot(dx, dy) <= 18

    def draw_base_selection(self, screen: pygame.Surface) -> None:
        if self.is_selected:
            pygame.draw.circle(screen, (120, 220, 255), (self.x, self.y), self.attack_range, 1)
            pygame.draw.circle(screen, (255, 255, 120), (self.x, self.y), 18, 2)

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_base_selection(screen)
        pygame.draw.circle(screen, (100, 200, 255), (self.x, self.y), 12)
        pygame.draw.circle(screen, (220, 240, 255), (self.x, self.y), 12, 2)