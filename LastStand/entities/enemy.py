import math
import pygame


class Enemy:
    def __init__(
        self,
        x: float,
        y: float,
        hp: int,
        speed: float,
        armor: int,
        reward: int,
        name: str,
        body_color: tuple[int, int, int],
        glow_color: tuple[int, int, int],
        radius: int = 10,
        trail_length: int = 5,
        aura_strength: int = 0,
        is_boss: bool = False,
    ) -> None:
        self.x = x
        self.y = y

        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.armor = armor
        self.reward = reward
        self.name = name

        self.body_color = body_color
        self.glow_color = glow_color
        self.radius = radius
        self.trail_length = trail_length
        self.aura_strength = aura_strength
        self.is_boss = is_boss

        self.alive = True
        self.path_index = 0
        self.reached_base = False

        self.visual_time = 0.0
        self.trail: list[tuple[float, float]] = []

    def take_damage(self, amount: int) -> None:
        actual_damage = max(1, amount - self.armor)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, dt: float, path_points: list[tuple[int, int]]) -> None:
        if not self.alive or self.reached_base:
            return

        self.visual_time += dt

        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        if not path_points:
            return

        if self.path_index >= len(path_points):
            self.reached_base = True
            return

        target_x, target_y = path_points[self.path_index]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance < 2:
            self.path_index += 1
            if self.path_index >= len(path_points):
                self.reached_base = True
            return

        if distance > 0:
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return

        self.draw_shadow(screen)
        self.draw_trail(screen)
        self.draw_aura(screen)
        self.draw_body(screen)
        self.draw_hp_bar(screen)

    def draw_shadow(self, screen: pygame.Surface) -> None:
        shadow_w = self.radius * 2
        shadow_h = max(6, self.radius // 2 + 3)
        shadow_rect = pygame.Rect(
            int(self.x - shadow_w // 2),
            int(self.y + self.radius - shadow_h // 2),
            shadow_w,
            shadow_h,
        )
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(
            shadow_surface,
            (0, 0, 0, 90 if not self.is_boss else 130),
            shadow_surface.get_rect(),
        )
        screen.blit(shadow_surface, shadow_rect.topleft)

    def draw_trail(self, screen: pygame.Surface) -> None:
        if len(self.trail) < 2:
            return

        for i, (tx, ty) in enumerate(self.trail):
            alpha_ratio = (i + 1) / len(self.trail)
            r = max(2, int(self.radius * 0.45 * alpha_ratio))
            surface = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            alpha = int(40 + 60 * alpha_ratio)
            pygame.draw.circle(
                surface,
                (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha),
                (surface.get_width() // 2, surface.get_height() // 2),
                r,
            )
            screen.blit(surface, (int(tx - surface.get_width() // 2), int(ty - surface.get_height() // 2)))

    def draw_aura(self, screen: pygame.Surface) -> None:
        if self.aura_strength <= 0:
            return

        pulse = math.sin(self.visual_time * 5.0) * 3.0
        aura_radius = int(self.radius + self.aura_strength + pulse)

        surface = pygame.Surface((aura_radius * 2 + 8, aura_radius * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(
            surface,
            (self.glow_color[0], self.glow_color[1], self.glow_color[2], 35),
            (surface.get_width() // 2, surface.get_height() // 2),
            aura_radius,
        )
        screen.blit(surface, (int(self.x - surface.get_width() // 2), int(self.y - surface.get_height() // 2)))

    def draw_body(self, screen: pygame.Surface) -> None:
        pulse = 1 if math.sin(self.visual_time * 8.0) > 0 else 0
        center = (int(self.x), int(self.y))

        pygame.draw.circle(screen, self.body_color, center, self.radius)
        pygame.draw.circle(screen, self.glow_color, center, self.radius, 2 + pulse)

        # eye/core glow
        eye_r = max(2, self.radius // 4)
        pygame.draw.circle(screen, (255, 240, 180), center, eye_r)

    def draw_hp_bar(self, screen: pygame.Surface) -> None:
        if self.is_boss:
            bar_width = 54
            bar_height = 8
            y_offset = self.radius + 16
        else:
            bar_width = 28
            bar_height = 5
            y_offset = self.radius + 10

        bar_x = int(self.x - bar_width // 2)
        bar_y = int(self.y - y_offset)

        pygame.draw.rect(screen, (45, 18, 18), (bar_x, bar_y, bar_width, bar_height))
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        fill_w = int(bar_width * hp_ratio)

        fill_color = (120, 255, 170) if not self.is_boss else (255, 120, 120)
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_w, bar_height))
        pygame.draw.rect(screen, (240, 240, 255), (bar_x, bar_y, bar_width, bar_height), 1)