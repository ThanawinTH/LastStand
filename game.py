import pygame
import sys
from player import Player
from enemies import Goblin, Orc, DarkKnight
from towers import ArcherTower, MageTower, BallistaTower
from statistics_manager import StatisticsManager

# Map waypoints (x, y) enemies follow
WAYPOINTS = [
    (0, 300), (200, 300), (200, 150), (400, 150),
    (400, 450), (600, 450), (600, 300), (800, 300)
]

# Valid tile positions for tower placement (grid cells adjacent to path)
VALID_TILES = {
    (100, 220), (100, 380), (300, 70), (300, 220),
    (500, 370), (500, 520), (700, 220), (700, 380),
}

TOWER_COST = {
    "archer": 50,
    "mage": 80,
    "ballista": 65,
}

UPGRADE_COST = 60

WAVE_DEFINITIONS = [
    [Goblin] * 5,
    [Goblin] * 5 + [Orc] * 2,
    [Goblin] * 6 + [Orc] * 3,
    [Goblin] * 4 + [Orc] * 3 + [DarkKnight] * 1,
    [Goblin] * 6 + [Orc] * 4 + [DarkKnight] * 2,
    [Goblin] * 8 + [Orc] * 4 + [DarkKnight] * 3,
    [Goblin] * 6 + [Orc] * 6 + [DarkKnight] * 4,
    [Goblin] * 8 + [Orc] * 6 + [DarkKnight] * 5,
    [Goblin] * 10 + [Orc] * 8 + [DarkKnight] * 6,
    [Goblin] * 12 + [Orc] * 10 + [DarkKnight] * 8,
]

HP_SCALE_PER_WAVE = 0.15  # +15% hp each wave


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Last Stand")
        self.clock = pygame.time.Clock()

        self.player = Player(gold=150, lives=10)
        self.towers = []
        self.enemies = []
        self.projectiles = []

        self.current_wave = 0
        self.wave_queue = []       # enemies waiting to spawn this wave
        self.spawn_timer = 0
        self.spawn_interval = 90  # frames between spawns
        self.wave_active = False
        self.game_over = False
        self.victory = False

        self.selected_tower_type = None  # "archer" / "mage" / "ballista"
        self.selected_tower = None       # a placed Tower for upgrade

        self.stats = StatisticsManager()
        self.font = pygame.font.SysFont("Arial", 18)

    # ------------------------------------------------------------------ loop
    def run(self):
        while not self.game_over and not self.victory:
            dt = self.clock.tick(60)
            self._handle_events()
            self._update()
            self._draw()

        self.stats.end_session(
            waves_survived=self.current_wave,
            towers_placed=self.stats.towers_placed,
            enemies_killed=self.stats.enemies_killed,
            gold_on_upgrades=self.stats.gold_on_upgrades,
            lives_lost=10 - self.player.lives
        )
        self.stats.save_csv()
        self.stats.show_graphs()
        pygame.quit()

    # ---------------------------------------------------------- event handling
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_tower_type = "archer"
                    self.selected_tower = None
                elif event.key == pygame.K_2:
                    self.selected_tower_type = "mage"
                    self.selected_tower = None
                elif event.key == pygame.K_3:
                    self.selected_tower_type = "ballista"
                    self.selected_tower = None
                elif event.key == pygame.K_ESCAPE:
                    self.selected_tower_type = None
                    self.selected_tower = None
                elif event.key == pygame.K_SPACE:
                    self._start_next_wave()
                elif event.key == pygame.K_u:
                    self._try_upgrade()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos)

    def _handle_click(self, pos):
        # Check if clicked an existing tower (select for upgrade)
        for tower in self.towers:
            if tower.rect.collidepoint(pos):
                self.selected_tower = tower
                self.selected_tower_type = None
                return

        # Otherwise try to place a new tower
        if self.selected_tower_type:
            snap = self._snap_to_tile(pos)
            if snap and snap not in [t.pos for t in self.towers]:
                cost = TOWER_COST[self.selected_tower_type]
                if self.player.spend_gold(cost):
                    tower = self._make_tower(self.selected_tower_type, snap)
                    self.towers.append(tower)
                    self.stats.towers_placed += 1

    def _snap_to_tile(self, pos):
        for tile in VALID_TILES:
            tx, ty = tile
            if abs(pos[0] - tx) < 40 and abs(pos[1] - ty) < 40:
                return tile
        return None

    def _make_tower(self, kind, pos):
        if kind == "archer":
            return ArcherTower(pos)
        elif kind == "mage":
            return MageTower(pos)
        elif kind == "ballista":
            return BallistaTower(pos)

    def _try_upgrade(self):
        if self.selected_tower and self.selected_tower.level < 2:
            if self.player.spend_gold(UPGRADE_COST):
                self.selected_tower.upgrade()
                self.stats.gold_on_upgrades += UPGRADE_COST

    # ------------------------------------------------------------- wave logic
    def _start_next_wave(self):
        if self.wave_active or self.current_wave >= len(WAVE_DEFINITIONS):
            return
        enemy_classes = WAVE_DEFINITIONS[self.current_wave]
        hp_mult = 1 + HP_SCALE_PER_WAVE * self.current_wave
        self.wave_queue = [cls(WAYPOINTS, hp_mult) for cls in enemy_classes]
        self.wave_active = True
        self.spawn_timer = 0
        self.current_wave += 1

    def _spawn_next(self):
        if self.wave_queue:
            self.enemies.append(self.wave_queue.pop(0))

    # ----------------------------------------------------------------- update
    def _update(self):
        # Spawning
        if self.wave_active:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self._spawn_next()
                self.spawn_timer = 0
            if not self.wave_queue and not self.enemies:
                self.wave_active = False
                if self.current_wave >= len(WAVE_DEFINITIONS):
                    self.victory = True

        # Enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.reached_end:
                self.player.lose_life()
                self.enemies.remove(enemy)
                if self.player.lives <= 0:
                    self.game_over = True
            elif enemy.is_dead():
                self.player.earn_gold(enemy.reward)
                self.stats.enemies_killed += 1
                self.enemies.remove(enemy)

        # Towers attack
        for tower in self.towers:
            new_proj = tower.update(self.enemies)
            if new_proj:
                self.projectiles.extend(new_proj if isinstance(new_proj, list) else [new_proj])

        # Projectiles
        for proj in self.projectiles[:]:
            proj.update()
            for enemy in self.enemies[:]:
                if proj.rect.colliderect(enemy.rect):
                    hit_others = proj.on_hit(enemy, self.enemies)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break
            if proj.off_screen():
                if proj in self.projectiles:
                    self.projectiles.remove(proj)

    # ------------------------------------------------------------------- draw
    def _draw(self):
        self.screen.fill((34, 85, 34))   # green map background

        # Draw path
        pygame.draw.lines(self.screen, (180, 140, 80), False, WAYPOINTS, 40)

        # Draw valid tile markers
        for tile in VALID_TILES:
            pygame.draw.rect(self.screen, (60, 120, 60),
                             (*[t - 20 for t in tile], 40, 40), 2)

        for enemy in self.enemies:
            enemy.draw(self.screen)
        for tower in self.towers:
            tower.draw(self.screen, selected=(tower is self.selected_tower))
        for proj in self.projectiles:
            proj.draw(self.screen)

        self._draw_ui()
        pygame.display.flip()

    def _draw_ui(self):
        gold_surf = self.font.render(f"Gold: {self.player.gold}", True, (255, 215, 0))
        lives_surf = self.font.render(f"Lives: {self.player.lives}", True, (255, 100, 100))
        wave_surf = self.font.render(f"Wave: {self.current_wave}/{len(WAVE_DEFINITIONS)}", True, (255, 255, 255))
        self.screen.blit(gold_surf, (10, 10))
        self.screen.blit(lives_surf, (10, 32))
        self.screen.blit(wave_surf, (10, 54))

        hint = self.font.render("[1]Archer [2]Mage [3]Ballista  [SPACE]Start Wave  [U]Upgrade  [ESC]Deselect",
                                True, (200, 200, 200))
        self.screen.blit(hint, (10, 575))

        if self.selected_tower:
            t = self.selected_tower
            info = self.font.render(
                f"Selected: {type(t).__name__} | Lvl {t.level} | DMG {t.damage} | RNG {t.range}"
                + ("" if t.level >= 2 else f"  [U] Upgrade ({UPGRADE_COST}g)"),
                True, (255, 255, 100))
            self.screen.blit(info, (10, 555))

        if self.game_over:
            self._draw_centered("GAME OVER", (255, 50, 50), 48)
        if self.victory:
            self._draw_centered("VICTORY!", (255, 215, 0), 48)

    def _draw_centered(self, text, color, size):
        f = pygame.font.SysFont("Arial", size, bold=True)
        s = f.render(text, True, color)
        self.screen.blit(s, s.get_rect(center=(400, 300)))
