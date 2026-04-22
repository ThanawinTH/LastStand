import pygame
import math


class Enemy:
    """
    Base class for all enemy units.

    Defines shared attributes (hp, speed, armor, reward) and shared movement
    logic (path following via waypoints). Subclasses set their own stat values
    and may override move() or on_death() for unique behaviour.
    No 'type' attribute is used — the class itself determines behaviour.
    """

    BASE_HP: int = 100
    BASE_SPEED: float = 2.0
    ARMOR: float = 0.0       # damage reduction 0.0–1.0
    REWARD: int = 10
    COLOR: tuple = (200, 200, 200)
    SIZE: int = 16

    def __init__(self, waypoints: list[tuple], hp_multiplier: float = 1.0):
        self.waypoints = waypoints
        self.hp = int(self.BASE_HP * hp_multiplier)
        self.max_hp = self.hp
        self.speed = self.BASE_SPEED
        self.armor = self.ARMOR
        self.reward = self.REWARD

        # Start at first waypoint
        self.x, self.y = float(waypoints[0][0]), float(waypoints[0][1])
        self.waypoint_index = 1
        self.reached_end = False

        self.rect = pygame.Rect(int(self.x) - self.SIZE // 2,
                                int(self.y) - self.SIZE // 2,
                                self.SIZE, self.SIZE)
        # Progress along path — used by tower targeting
        self.path_progress: float = 0.0

    # ----------------------------------------------------------------- update
    def update(self) -> None:
        if self.reached_end or self.is_dead():
            return
        self.move()
        self.rect.center = (int(self.x), int(self.y))

    def move(self) -> None:
        """Move toward the next waypoint. Advance when close enough."""
        if self.waypoint_index >= len(self.waypoints):
            self.reached_end = True
            return

        target_x, target_y = self.waypoints[self.waypoint_index]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.x, self.y = float(target_x), float(target_y)
            self.waypoint_index += 1
            self.path_progress = self.waypoint_index
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            # Fractional progress between waypoints
            self.path_progress = self.waypoint_index - (dist / 100.0)

    # ----------------------------------------------------------------- combat
    def take_damage(self, amount: float) -> None:
        """Apply damage after armor reduction."""
        effective = amount * (1.0 - self.armor)
        self.hp -= effective

    def is_dead(self) -> bool:
        return self.hp <= 0

    def on_death(self) -> None:
        """Hook for subclasses to add death effects (e.g. split, explode)."""
        pass

    # ------------------------------------------------------------------- draw
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.COLOR, self.rect)

        # HP bar above enemy
        bar_w = self.SIZE + 4
        bar_x = self.rect.x - 2
        bar_y = self.rect.y - 7
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (180, 0, 0), (bar_x, bar_y, bar_w, 4))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_w * ratio), 4))


# ═══════════════════════════════════════════════════════════ concrete enemies

class Goblin(Enemy):
    """
    Very fast, low HP. Rushes past towers before they can fire often.
    Overwhelms unprepared defences through sheer speed.
    """
    BASE_HP = 60
    BASE_SPEED = 3.5
    ARMOR = 0.0
    REWARD = 8
    COLOR = (100, 200, 80)   # bright green
    SIZE = 12


class Orc(Enemy):
    """
    Slow, very high HP. Soaks enormous damage; requires sustained fire.
    High reward compensates for the difficulty in killing it.
    """
    BASE_HP = 300
    BASE_SPEED = 1.2
    ARMOR = 0.0
    REWARD = 20
    COLOR = (80, 120, 60)    # dark green
    SIZE = 22


class DarkKnight(Enemy):
    """
    Medium speed with heavy armor that reduces all incoming damage by 40%.
    Requires high-damage towers (Mage) to be dealt with efficiently.
    """
    BASE_HP = 180
    BASE_SPEED = 2.0
    ARMOR = 0.40             # 40% damage reduction
    REWARD = 15
    COLOR = (50, 50, 80)     # dark blue-grey
    SIZE = 18
