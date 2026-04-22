import pygame
from projectiles import Arrow, MagicBolt, Bolt


class Tower:
    """
    Base class for all towers.

    Defines shared attributes: position, damage, range, fire_rate, level.
    Provides shared methods: find_target(), upgrade(), draw().
    Subclasses override attack() and set their own base stats.
    No 'type' attribute is used — the class itself determines behaviour.
    """

    BASE_DAMAGE: float = 20.0
    BASE_RANGE: int = 120
    BASE_FIRE_RATE: int = 60   # frames between shots (higher = slower)
    COLOR: tuple = (150, 150, 150)
    SIZE: int = 24

    UPGRADE_DAMAGE_MULT: float = 1.5
    UPGRADE_RANGE_MULT: float = 1.3

    def __init__(self, pos: tuple[int, int]):
        self.pos = pos
        self.x, self.y = pos
        self.damage = float(self.BASE_DAMAGE)
        self.range = self.BASE_RANGE
        self.fire_rate = self.BASE_FIRE_RATE
        self.level = 1
        self._cooldown = 0

        self.rect = pygame.Rect(self.x - self.SIZE // 2,
                                self.y - self.SIZE // 2,
                                self.SIZE, self.SIZE)

    # ---------------------------------------------------------- shared methods
    def find_target(self, enemies: list):
        """
        Return the enemy with the highest path_progress that is within range.
        This targets enemies closest to the castle first.
        """
        best = None
        best_progress = -1
        for enemy in enemies:
            dist = ((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2) ** 0.5
            if dist <= self.range and enemy.path_progress > best_progress:
                best = enemy
                best_progress = enemy.path_progress
        return best

    def upgrade(self) -> None:
        """Increase damage and range. Maximum level is 2."""
        if self.level < 2:
            self.damage *= self.UPGRADE_DAMAGE_MULT
            self.range = int(self.range * self.UPGRADE_RANGE_MULT)
            self.level = 2

    def update(self, enemies: list):
        """Called every frame. Returns a projectile if firing, else None."""
        if self._cooldown > 0:
            self._cooldown -= 1
            return None
        target = self.find_target(enemies)
        if target:
            self._cooldown = self.fire_rate
            return self.attack(target, enemies)
        return None

    def attack(self, target, enemies: list):
        """Subclasses implement this to return the appropriate projectile."""
        raise NotImplementedError

    def draw(self, surface: pygame.Surface, selected: bool = False) -> None:
        color = (255, 215, 0) if selected else self.COLOR
        pygame.draw.rect(surface, color, self.rect)

        # Range ring when selected
        if selected:
            pygame.draw.circle(surface, (255, 255, 255),
                               (self.x, self.y), self.range, 1)

        # Level pip
        if self.level == 2:
            pygame.draw.circle(surface, (255, 215, 0),
                               (self.x + self.SIZE // 2 - 4,
                                self.y - self.SIZE // 2 + 4), 4)


# ═══════════════════════════════════════════════════════════ concrete towers

class ArcherTower(Tower):
    """
    High attack speed, low damage per hit.
    Best against fast, low-HP enemies like Goblins.
    Fires a single-target Arrow projectile.
    """
    BASE_DAMAGE = 15.0
    BASE_RANGE = 130
    BASE_FIRE_RATE = 25     # fires frequently
    COLOR = (180, 120, 60)  # wood brown

    def attack(self, target, enemies: list):
        return Arrow(self.x, self.y, target, self.damage)


class MageTower(Tower):
    """
    Slow attack speed, high damage with splash.
    Best against armored or clustered enemies.
    Fires a MagicBolt that deals area damage on impact.
    """
    BASE_DAMAGE = 60.0
    BASE_RANGE = 110
    BASE_FIRE_RATE = 90     # fires slowly
    COLOR = (100, 60, 180)  # purple

    def attack(self, target, enemies: list):
        return MagicBolt(self.x, self.y, target, self.damage)


class BallistaTower(Tower):
    """
    Medium attack speed and damage.
    Fires a piercing Bolt that passes through up to 3 enemies in a line.
    Best placed in corridors where enemies stack up.
    """
    BASE_DAMAGE = 35.0
    BASE_RANGE = 150
    BASE_FIRE_RATE = 55
    COLOR = (120, 90, 60)   # dark wood

    def attack(self, target, enemies: list):
        return Bolt(self.x, self.y, target, self.damage)
