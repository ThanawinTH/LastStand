import random
import pygame

from config import *
from core.map_loader import MapLoader
from core.wave_manager import WaveManager
from data.statistics_manager import StatisticsManager
from entities.player import Player
from entities.goblin import Goblin
from entities.orc import Orc
from entities.dark_knight import DarkKnight
from entities.boss_enemy import BossEnemy
from entities.archer_tower import ArcherTower
from entities.mage_tower import MageTower
from entities.ballista_tower import BallistaTower
from ui.hud import draw_header, draw_footer
from ui.panels import draw_side_panel


class Game:
    def __init__(self) -> None:
        pygame.display.set_caption(GAME_TITLE)

        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player()
        self.stats = StatisticsManager()
        self.session_saved = False

        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_medium = pygame.font.SysFont("consolas", 22)
        self.font_large = pygame.font.SysFont("consolas", 30)
        self.font_xlarge = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_huge = pygame.font.SysFont("consolas", 54, bold=True)

        self.selected_tower_name = "Archer"
        self.selected_tower_type = "archer"
        self.selected_tower = None
        self.build_mode_active = False
        self.status_text = "Loading map..."

        self.map_data = None
        self.map_image = None
        self.path_cells = []
        self.path_points = []

        self.enemies = []
        self.towers = []
        self.projectiles = []

        self.wave_manager = WaveManager(MAX_WAVES)
        self.boss_spawned_this_wave = False

        # endgame panel ยกขึ้นและสูงขึ้น
        panel_w = 480
        panel_h = 360
        panel_x = WINDOW_WIDTH // 2 - panel_w // 2
        panel_y = WINDOW_HEIGHT // 2 - 180

        self.end_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        btn_w = 360
        btn_h = 52
        btn_x = WINDOW_WIDTH // 2 - btn_w // 2

        self.end_buttons = {
            "restart": pygame.Rect(btn_x, panel_y + 140, btn_w, btn_h),
            "menu": pygame.Rect(btn_x, panel_y + 206, btn_w, btn_h),
            "stats": pygame.Rect(btn_x, panel_y + 272, btn_w, btn_h),
        }

        # Pause & live-stats overlay state
        self.paused = False
        self.stats_panel_open = False
        self._music = None          # set by handle_events each frame
        self._mute_btn_rect   = pygame.Rect(0, 0, 0, 0)
        self._pause_btn_rect  = pygame.Rect(0, 0, 0, 0)
        self._stats_btn_rect  = pygame.Rect(0, 0, 0, 0)

        self.load_map()
        self.wave_manager.start_first_wave()

    def load_map(self) -> None:
        try:
            self.map_data = MapLoader.load_map(DEFAULT_MAP_JSON)

            if DEFAULT_MAP_IMAGE.exists():
                img = pygame.image.load(DEFAULT_MAP_IMAGE).convert()
                self.map_image = pygame.transform.scale(img, (MAP_WIDTH, MAP_HEIGHT))

            self.path_cells = MapLoader.build_path_points(self.map_data)
            self.path_points = MapLoader.path_to_pixel_points(
                self.path_cells,
                TILE_SIZE,
                MAP_OFFSET_X,
                MAP_OFFSET_Y,
            )

            if not self.path_points:
                self.status_text = "Path build failed."
            else:
                self.status_text = f"Map loaded | Path length: {len(self.path_points)}"

        except Exception as exc:
            self.status_text = f"Map load error: {exc}"

    def handle_events(self, events, music=None):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if self.wave_manager.is_victory() or self.wave_manager.is_game_over():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.end_buttons["restart"].collidepoint(event.pos):
                        self.reset_game()
                        return None
                    if self.end_buttons["menu"].collidepoint(event.pos):
                        return "back_to_menu"
                    if self.end_buttons["stats"].collidepoint(event.pos):
                        return "view_stats"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

                elif event.key == pygame.K_p:
                    self.paused = not self.paused

                elif event.key == pygame.K_TAB:
                    self.stats_panel_open = not self.stats_panel_open

                elif event.key == pygame.K_1:
                    self.enter_build_mode("archer", "Archer")

                elif event.key == pygame.K_2:
                    self.enter_build_mode("mage", "Mage")

                elif event.key == pygame.K_3:
                    self.enter_build_mode("ballista", "Ballista")

                elif event.key == pygame.K_u:
                    self.try_upgrade_selected_tower()

                elif event.key == pygame.K_s:
                    self.try_sell_selected_tower()

                elif event.key == pygame.K_ESCAPE:
                    self.exit_build_mode()
                    self.clear_selected_tower()
                    self.status_text = "Selection/build mode cleared."

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if music is not None and self._mute_btn_rect.collidepoint(event.pos):
                        music.toggle_mute()
                    elif self._pause_btn_rect.collidepoint(event.pos):
                        self.paused = not self.paused
                    elif self._stats_btn_rect.collidepoint(event.pos):
                        self.stats_panel_open = not self.stats_panel_open
                    else:
                        self.handle_left_click(event.pos)
                elif event.button == 3:
                    self.exit_build_mode()
                    self.clear_selected_tower()
                    self.status_text = "Selection/build mode cleared."

        self._music = music
        return None

    def enter_build_mode(self, tower_type: str, tower_name: str) -> None:
        self.selected_tower_type = tower_type
        self.selected_tower_name = tower_name
        self.build_mode_active = True
        self.clear_selected_tower()
        self.status_text = f"Build mode: {tower_name}"

    def handle_left_click(self, mouse_pos: tuple[int, int]) -> None:
        if self.wave_manager.is_victory() or self.wave_manager.is_game_over():
            return

        clicked_tower = self.get_tower_at_mouse(mouse_pos)
        if clicked_tower is not None:
            self.exit_build_mode()
            self.select_tower(clicked_tower)
            return

        grid_pos = self.get_grid_pos_from_mouse(mouse_pos)
        if grid_pos is None:
            self.exit_build_mode()
            self.clear_selected_tower()
            self.status_text = "Selection/build mode cleared."
            return

        col, row = grid_pos
        tile = self.map_data["grid"][row][col]

        if self.build_mode_active:
            self.try_place_tower_by_grid(col, row)
            return

        if tile != TILE_BUILD:
            self.clear_selected_tower()
            self.status_text = "No tower selected."
        else:
            self.status_text = "Press 1 / 2 / 3 to enter build mode."

    def update(self, dt: float) -> None:
        if self.wave_manager.is_victory() or self.wave_manager.is_game_over():
            if not self.session_saved:
                self.stats.save_session(self)
                self.session_saved = True
            self.update_projectiles(dt)
            return

        if self.paused:
            return

        self.update_wave_logic(dt)

        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)

        self.update_projectiles(dt)
        self.update_enemies(dt)
        self.cleanup_enemies()

        if self.player.lives <= 0:
            self.wave_manager.set_game_over()
            self.status_text = "Base destroyed. Game Over."

    def update_wave_logic(self, dt: float) -> None:
        if self.wave_manager.state == WaveManager.PREPARING:
            started = self.wave_manager.update_preparing(dt)
            if started:
                self.boss_spawned_this_wave = False
                if self.wave_manager.current_wave in (5, 10):
                    self.status_text = f"Wave {self.wave_manager.current_wave} started! Boss incoming..."
                else:
                    self.status_text = f"Wave {self.wave_manager.current_wave} started!"
            else:
                if self.wave_manager.current_wave in (5, 10):
                    self.status_text = (
                        f"CAUTION - Boss Wave {self.wave_manager.current_wave} in "
                        f"{max(0, self.wave_manager.prep_timer):.1f}s"
                    )
                else:
                    self.status_text = (
                        f"Preparing Wave {self.wave_manager.current_wave}... "
                        f"{max(0, self.wave_manager.prep_timer):.1f}s"
                    )
            return

        if self.wave_manager.state == WaveManager.IN_WAVE:
            if self.wave_manager.can_spawn_enemy() and self.wave_manager.update_spawn_timer(dt):
                self.spawn_enemy()

            if self.should_spawn_boss() and not self.boss_spawned_this_wave:
                self.spawn_boss()
                self.boss_spawned_this_wave = True

            if self.wave_manager.is_wave_cleared(len(self.enemies)):
                prev_wave = self.wave_manager.current_wave
                self.wave_manager.start_next_wave_or_finish()

                if self.wave_manager.is_victory():
                    self.status_text = "All 10 waves cleared. Victory!"
                else:
                    self.status_text = f"Wave {prev_wave} cleared. Prepare for Wave {self.wave_manager.current_wave}."

    def should_spawn_boss(self) -> bool:
        return self.wave_manager.current_wave in (5, 10)

    def spawn_enemy(self) -> None:
        if not self.path_points:
            return

        start_x, start_y = self.path_points[0]
        wave = self.wave_manager.current_wave

        if wave < 3:
            enemy = Goblin(start_x, start_y)
        elif wave < 6:
            enemy = random.choice([
                Goblin(start_x, start_y),
                Orc(start_x, start_y),
            ])
        else:
            enemy = random.choice([
                Goblin(start_x, start_y),
                Orc(start_x, start_y),
                DarkKnight(start_x, start_y),
            ])

        wave_bonus_hp = (wave - 1) * 6
        wave_bonus_speed = (wave - 1) * 1.2

        enemy.max_hp += wave_bonus_hp
        enemy.hp += wave_bonus_hp
        enemy.speed += wave_bonus_speed

        self.enemies.append(enemy)
        self.wave_manager.register_spawn()

    def spawn_boss(self) -> None:
        if not self.path_points:
            return

        start_x, start_y = self.path_points[0]
        boss = BossEnemy(start_x, start_y)

        if self.wave_manager.current_wave == 10:
            boss.max_hp += 180
            boss.hp += 180
            boss.speed += 10
            boss.reward += 70

        self.enemies.append(boss)
        self.status_text = f"BOSS ENTERED THE DUNGEON - Wave {self.wave_manager.current_wave}"

    def update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            enemy.update(dt, self.path_points)

    def update_projectiles(self, dt: float) -> None:
        remaining = []
        for projectile in self.projectiles:
            projectile.update(dt, self.enemies)
            if projectile.alive:
                remaining.append(projectile)
        self.projectiles = remaining

    def cleanup_enemies(self) -> None:
        remaining = []

        for enemy in self.enemies:
            if enemy.reached_base:
                damage = 3 if getattr(enemy, "is_boss", False) else 1
                self.player.lose_life(damage)
                if getattr(enemy, "is_boss", False):
                    self.status_text = f"BOSS reached base! Lives left: {self.player.lives}"
                else:
                    self.status_text = f"{enemy.name} reached base! Lives left: {self.player.lives}"
                continue

            if not enemy.alive:
                self.player.earn_gold(enemy.reward)
                self.player.enemies_killed += 1
                if getattr(enemy, "is_boss", False):
                    self.status_text = f"Boss defeated! (+{enemy.reward} gold)"
                else:
                    self.status_text = f"Killed {enemy.name} (+{enemy.reward} gold)"
                continue

            remaining.append(enemy)

        self.enemies = remaining

    def reset_game(self) -> None:
        self.enemies.clear()
        self.towers.clear()
        self.projectiles.clear()

        self.player.lives = PLAYER_START_LIVES
        self.player.lives_lost = 0
        self.player.gold = PLAYER_START_GOLD
        self.player.towers_placed = 0
        self.player.gold_on_upgrades = 0
        self.player.enemies_killed = 0

        self.selected_tower = None
        self.build_mode_active = False
        self.boss_spawned_this_wave = False
        self.session_saved = False

        self.wave_manager = WaveManager(MAX_WAVES)
        self.wave_manager.start_first_wave()

        self.status_text = "Game reset."

    def try_place_tower_by_grid(self, col: int, row: int) -> None:
        if self.map_data is None:
            self.status_text = "Map not loaded."
            return

        if self.wave_manager.is_victory() or self.wave_manager.is_game_over():
            return

        tile = self.map_data["grid"][row][col]

        if tile != TILE_BUILD:
            self.status_text = "Can only build on BUILD tiles"
            return

        for tower in self.towers:
            if tower.col == col and tower.row == row:
                self.status_text = "Tile already occupied"
                return

        if self.selected_tower_type == "archer":
            cost = ARCHER_COST
        elif self.selected_tower_type == "mage":
            cost = MAGE_COST
        else:
            cost = BALLISTA_COST

        if not self.player.can_afford(cost):
            self.status_text = "Not enough gold"
            return

        x = MAP_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = MAP_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2

        if self.selected_tower_type == "archer":
            tower = ArcherTower(col, row, x, y)
        elif self.selected_tower_type == "mage":
            tower = MageTower(col, row, x, y)
        else:
            tower = BallistaTower(col, row, x, y)

        self.player.spend_gold(tower.cost)
        self.player.towers_placed += 1
        self.towers.append(tower)
        self.select_tower(tower)
        self.exit_build_mode()
        self.status_text = f"Placed {tower.name} at ({col}, {row})"

    def try_upgrade_selected_tower(self) -> None:
        if self.selected_tower is None:
            self.status_text = "No tower selected."
            return

        if not self.selected_tower.can_upgrade():
            self.status_text = f"{self.selected_tower.name} is already max level."
            return

        cost = self.selected_tower.upgrade_cost
        if not self.player.can_afford(cost):
            self.status_text = "Not enough gold to upgrade."
            return

        self.player.spend_gold(cost)
        self.player.record_upgrade_spending(cost)
        self.selected_tower.upgrade()
        self.status_text = f"Upgraded {self.selected_tower.name} to level {self.selected_tower.level}"

    def try_sell_selected_tower(self) -> None:
        if self.selected_tower is None:
            self.status_text = "No tower selected."
            return

        sell_value = self.selected_tower.sell_value
        tower_name = self.selected_tower.name

        self.player.earn_gold(sell_value)
        self.towers.remove(self.selected_tower)
        self.selected_tower = None

        for tower in self.towers:
            tower.is_selected = False

        self.status_text = f"Sold {tower_name} for {sell_value} gold."

    def select_tower(self, tower) -> None:
        self.selected_tower = tower
        for t in self.towers:
            t.is_selected = False
        tower.is_selected = True
        self.status_text = f"Selected {tower.name} (Lv {tower.level})"

    def clear_selected_tower(self) -> None:
        self.selected_tower = None
        for tower in self.towers:
            tower.is_selected = False

    def exit_build_mode(self) -> None:
        self.build_mode_active = False

    def get_tower_at_mouse(self, mouse_pos: tuple[int, int]):
        for tower in reversed(self.towers):
            if tower.contains_point(mouse_pos):
                return tower
        return None

    def get_grid_pos_from_mouse(self, mouse_pos: tuple[int, int]) -> tuple[int, int] | None:
        mx, my = mouse_pos

        if not (MAP_OFFSET_X <= mx < MAP_OFFSET_X + MAP_WIDTH):
            return None
        if not (MAP_OFFSET_Y <= my < MAP_OFFSET_Y + MAP_HEIGHT):
            return None

        col = (mx - MAP_OFFSET_X) // TILE_SIZE
        row = (my - MAP_OFFSET_Y) // TILE_SIZE
        return int(col), int(row)

    def can_place_selected_tower_on_hover(self) -> tuple[bool, tuple[int, int] | None]:
        if not self.build_mode_active:
            return False, None

        mouse_pos = pygame.mouse.get_pos()
        grid_pos = self.get_grid_pos_from_mouse(mouse_pos)
        if grid_pos is None or self.map_data is None:
            return False, None

        col, row = grid_pos
        tile = self.map_data["grid"][row][col]

        if tile != TILE_BUILD:
            return False, grid_pos

        for tower in self.towers:
            if tower.col == col and tower.row == row:
                return False, grid_pos

        return True, grid_pos

    def draw_build_cursor_preview(self) -> None:
        if not self.build_mode_active:
            return

        if self.wave_manager.is_victory() or self.wave_manager.is_game_over():
            return

        grid_pos = self.get_grid_pos_from_mouse(pygame.mouse.get_pos())
        if grid_pos is None:
            return

        can_place, _ = self.can_place_selected_tower_on_hover()

        col, row = grid_pos
        center_x = MAP_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        center_y = MAP_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2

        if self.selected_tower_type == "archer":
            preview_range = 110
            color = (255, 230, 120)
        elif self.selected_tower_type == "mage":
            preview_range = 100
            color = (120, 220, 255)
        else:
            preview_range = 140
            color = (255, 180, 90)

        range_color = color if can_place else (255, 90, 90)
        outline_color = color if can_place else (255, 120, 120)

        preview_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(
            preview_surface,
            (range_color[0], range_color[1], range_color[2], 35),
            (center_x - MAP_OFFSET_X, center_y - MAP_OFFSET_Y),
            preview_range,
        )
        self.screen.blit(preview_surface, (MAP_OFFSET_X, MAP_OFFSET_Y))

        cell_rect = pygame.Rect(
            MAP_OFFSET_X + col * TILE_SIZE,
            MAP_OFFSET_Y + row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )
        pygame.draw.rect(self.screen, outline_color, cell_rect, 2)

        if self.selected_tower_type == "archer":
            points = [(center_x, center_y - 10), (center_x + 8, center_y + 6), (center_x - 8, center_y + 6)]
            pygame.draw.polygon(self.screen, outline_color, points, 2)
        elif self.selected_tower_type == "mage":
            pygame.draw.circle(self.screen, outline_color, (center_x, center_y), 12, 2)
            pygame.draw.circle(self.screen, outline_color, (center_x, center_y), 5, 2)
        else:
            pygame.draw.rect(self.screen, outline_color, pygame.Rect(center_x - 12, center_y - 8, 24, 16), 2)
            pygame.draw.line(self.screen, outline_color, (center_x - 10, center_y - 6), (center_x + 10, center_y + 6), 2)
            pygame.draw.line(self.screen, outline_color, (center_x - 10, center_y + 6), (center_x + 10, center_y - 6), 2)

    def draw_overlay_message(self) -> None:
        if self.wave_manager.is_victory() or self.wave_manager.is_game_over():
            return

        if self.wave_manager.state != WaveManager.PREPARING:
            return

        is_boss_wave = self.wave_manager.current_wave in (5, 10)
        countdown_text = f"{max(0, self.wave_manager.prep_timer):.1f}s"

        if is_boss_wave:
            warning_text = f"CAUTION - BOSS WAVE {self.wave_manager.current_wave}"
            countdown_label = f"Incoming in {countdown_text}"
            color = (255, 120, 160)

            warning_surface = self.font_xlarge.render(warning_text, True, color)
            warning_rect = warning_surface.get_rect(center=(MAP_OFFSET_X + MAP_WIDTH // 2, MAP_OFFSET_Y + 36))

            bg1 = warning_rect.inflate(34, 16)
            pygame.draw.rect(self.screen, (24, 10, 20), bg1, border_radius=12)
            pygame.draw.rect(self.screen, color, bg1, 2, border_radius=12)
            self.screen.blit(warning_surface, warning_rect)

            countdown_surface = self.font_large.render(countdown_label, True, (255, 220, 220))
            countdown_rect = countdown_surface.get_rect(center=(MAP_OFFSET_X + MAP_WIDTH // 2, MAP_OFFSET_Y + 86))

            bg2 = countdown_rect.inflate(24, 12)
            pygame.draw.rect(self.screen, (18, 14, 28), bg2, border_radius=10)
            pygame.draw.rect(self.screen, (255, 170, 210), bg2, 2, border_radius=10)
            self.screen.blit(countdown_surface, countdown_rect)
        else:
            text = f"Wave {self.wave_manager.current_wave} starts in {countdown_text}"
            color = (255, 220, 120)

            surface = self.font_large.render(text, True, color)
            rect = surface.get_rect(center=(MAP_OFFSET_X + MAP_WIDTH // 2, MAP_OFFSET_Y + 42))

            bg_rect = rect.inflate(24, 14)
            pygame.draw.rect(self.screen, (10, 18, 34), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (90, 180, 255), bg_rect, 2, border_radius=10)
            self.screen.blit(surface, rect)

    def draw_endgame_panel(self) -> None:
        if not (self.wave_manager.is_victory() or self.wave_manager.is_game_over()):
            return

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel = self.end_panel_rect
        pygame.draw.rect(self.screen, (14, 20, 36), panel, border_radius=18)
        pygame.draw.rect(self.screen, (90, 180, 255), panel, 2, border_radius=18)

        title = "VICTORY" if self.wave_manager.is_victory() else "GAME OVER"
        title_color = (120, 255, 170) if self.wave_manager.is_victory() else (255, 120, 120)

        title_surface = self.font_huge.render(title, True, title_color)
        self.screen.blit(title_surface, title_surface.get_rect(center=(panel.centerx, panel.y + 52)))

        detail = self.font_small.render(
            "Choose your next action",
            True,
            (190, 210, 240),
        )
        self.screen.blit(detail, detail.get_rect(center=(panel.centerx, panel.y + 98)))

        self.draw_menu_button(self.end_buttons["restart"], "RESTART")
        self.draw_menu_button(self.end_buttons["menu"], "BACK TO MENU")
        self.draw_menu_button(self.end_buttons["stats"], "VIEW STATS")

    def draw_menu_button(self, rect: pygame.Rect, text: str) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        bg = (36, 52, 90) if hovered else (28, 40, 70)
        border = (120, 220, 255) if hovered else (90, 180, 255)

        pygame.draw.rect(self.screen, bg, rect, border_radius=12)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=12)

        label = self.font_medium.render(text, True, (230, 240, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw(self) -> None:
        self.screen.fill(BG_MAIN)

        draw_header(
            screen=self.screen,
            player=self.player,
            current_wave=self.wave_manager.current_wave,
            title="LAST STAND",
            subtitle="SPACE DUNGEON DEFENSE PROTOCOL",
            font_small=self.font_small,
            font_medium=self.font_medium,
            font_large=self.font_large,
            wave_state=self.wave_manager.state,
        )

        map_rect = pygame.Rect(MAP_OFFSET_X, MAP_OFFSET_Y, MAP_WIDTH, MAP_HEIGHT)

        if self.map_image:
            self.screen.blit(self.map_image, (map_rect.x, map_rect.y))
        else:
            pygame.draw.rect(self.screen, (20, 26, 44), map_rect)

        pygame.draw.rect(self.screen, (80, 180, 255), map_rect, 2)

        if DEBUG_DRAW_PATH and self.path_points:
            pygame.draw.lines(self.screen, (255, 100, 100), False, self.path_points, 4)
            for p in self.path_points:
                pygame.draw.circle(self.screen, (255, 200, 200), p, 4)

        for tower in self.towers:
            tower.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        self.draw_build_cursor_preview()
        self.draw_overlay_message()

        side_rect = pygame.Rect(
            SIDE_PANEL_X,
            SIDE_PANEL_Y,
            SIDE_PANEL_WIDTH,
            SIDE_PANEL_HEIGHT,
        )
        draw_side_panel(
            screen=self.screen,
            rect=side_rect,
            selected_tower_name=self.selected_tower_name,
            status_text=self.status_text,
            font_small=self.font_small,
            font_medium=self.font_medium,
            selected_tower=self.selected_tower,
        )

        footer_rect = pygame.Rect(0, FOOTER_Y, WINDOW_WIDTH, FOOTER_HEIGHT)

        mode_text = "BUILD MODE" if self.build_mode_active else "NORMAL MODE"
        boss_text = " | BOSS WAVE" if self.wave_manager.current_wave in (5, 10) else ""

        footer_text = (
            f"{mode_text}{boss_text} | "
            f"Wave {self.wave_manager.current_wave}/{MAX_WAVES} | "
            f"Spawned {self.wave_manager.enemies_spawned}/{self.wave_manager.enemies_to_spawn} | "
            f"Alive {len(self.enemies)} | "
            f"Projectiles {len(self.projectiles)} | "
            f"[1][2][3] Build  [U] Upgrade  [S] Sell  [R] Reset  [P] Pause  [TAB] Stats  [ESC] Clear"
        )

        draw_footer(
            screen=self.screen,
            rect=footer_rect,
            text=footer_text,
            font_small=self.font_small,
            font_medium=self.font_medium,
        )

        self.draw_endgame_panel()
        self.draw_top_buttons()
        if self.stats_panel_open:
            self.draw_stats_panel()
        if self.paused and not (self.wave_manager.is_victory() or self.wave_manager.is_game_over()):
            self.draw_pause_overlay()
        pygame.display.flip()

    # ------------------------------------------------------------------ #
    #  Control button row  (header row 2, right half)                     #
    # ------------------------------------------------------------------ #
    def draw_top_buttons(self) -> None:
        music = getattr(self, '_music', None)
        is_muted   = music.is_muted if music else False

        # Button definitions: (attr, label, accent_color, active)
        defs = [
            ("_pause_btn_rect",
             "RESUME" if self.paused else "PAUSE",
             (255, 210, 80) if self.paused else (80, 180, 255),
             self.paused),
            ("_stats_btn_rect",
             "STATS  ON" if self.stats_panel_open else "STATS OFF",
             (100, 255, 170) if self.stats_panel_open else (80, 180, 255),
             self.stats_panel_open),
            ("_mute_btn_rect",
             "MUSIC OFF" if is_muted else "MUSIC  ON",
             (220, 90, 90)  if is_muted else (80, 200, 130),
             is_muted),
        ]

        # Layout: evenly distribute 3 buttons across the side-panel width
        # in header row 2  (y = 62 … 110)
        btn_area_x = SIDE_PANEL_X + 8
        btn_area_w = SIDE_PANEL_WIDTH - 16
        btn_h      = 36
        btn_y      = 62 + (HEADER_HEIGHT - 62 - btn_h) // 2   # vertically centered
        n          = len(defs)
        gap        = 8
        btn_w      = (btn_area_w - gap * (n - 1)) // n

        mouse_pos = pygame.mouse.get_pos()

        for i, (attr, label, accent, active) in enumerate(defs):
            bx = btn_area_x + i * (btn_w + gap)
            btn = pygame.Rect(bx, btn_y, btn_w, btn_h)
            setattr(self, attr, btn)

            hovered = btn.collidepoint(mouse_pos)
            bg   = (30, 44, 80)  if (hovered or active) else (18, 26, 52)
            border_col = accent

            pygame.draw.rect(self.screen, bg, btn, border_radius=8)
            pygame.draw.rect(self.screen, border_col, btn, 2, border_radius=8)

            # Keybind badge (left side)
            keys = ["P", "TAB", "M"]
            badge_w = 30 if keys[i] != "TAB" else 36
            badge_rect = pygame.Rect(bx + 6, btn_y + (btn_h - 20) // 2, badge_w, 20)
            pygame.draw.rect(self.screen, border_col, badge_rect, border_radius=4)
            key_surf = self.font_small.render(keys[i], True, (10, 14, 28))
            self.screen.blit(key_surf, key_surf.get_rect(center=badge_rect.center))

            # Label text
            lbl_surf = self.font_small.render(label, True, accent if active else (180, 200, 240))
            lx = bx + badge_w + 14
            self.screen.blit(lbl_surf, lbl_surf.get_rect(midleft=(lx, btn_y + btn_h // 2)))

    # ------------------------------------------------------------------ #
    #  Pause overlay                                                       #
    # ------------------------------------------------------------------ #
    def draw_pause_overlay(self) -> None:
        overlay = pygame.Surface(
            (MAP_WIDTH, MAP_HEIGHT + FOOTER_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((8, 10, 22, 175))
        self.screen.blit(overlay, (MAP_OFFSET_X, MAP_OFFSET_Y))

        font_big  = pygame.font.SysFont("consolas", 52, bold=True)
        font_hint = self.font_small

        cx = MAP_OFFSET_X + MAP_WIDTH // 2
        cy = MAP_OFFSET_Y + MAP_HEIGHT // 2

        # Glow ring
        pygame.draw.circle(self.screen, (40, 100, 200), (cx, cy), 90, 2)
        pygame.draw.circle(self.screen, (20, 60, 140),  (cx, cy), 94, 1)

        pause_surf = font_big.render("⏸  PAUSED", True, (230, 240, 255))
        hint_surf  = font_hint.render("Press  [P]  or  click  [P] PAUSE  to resume", True, (130, 160, 210))

        self.screen.blit(pause_surf, pause_surf.get_rect(center=(cx, cy - 18)))
        self.screen.blit(hint_surf,  hint_surf.get_rect(center=(cx, cy + 44)))

    # ------------------------------------------------------------------ #
    #  Live stats overlay panel                                            #
    # ------------------------------------------------------------------ #
    def draw_stats_panel(self) -> None:
        pw, ph = 310, 360
        px = MAP_OFFSET_X + MAP_WIDTH - pw - 12
        py = MAP_OFFSET_Y + 12

        # Background
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill((12, 18, 38, 215))
        self.screen.blit(panel_surf, (px, py))
        pygame.draw.rect(self.screen, (80, 180, 255), (px, py, pw, ph), 2, border_radius=10)

        # Title bar
        title_surf = self.font_medium.render("LIVE  STATISTICS", True, (80, 220, 255))
        self.screen.blit(title_surf, title_surf.get_rect(centerx=px + pw // 2, y=py + 12))
        pygame.draw.line(self.screen, (50, 120, 200), (px + 12, py + 40), (px + pw - 12, py + 40), 1)

        wm = self.wave_manager

        # Derive kill efficiency
        enemies_to_now = sum(
            5 + (w - 1) * 2 for w in range(1, wm.current_wave + 1)
        )
        kill_pct = (
            round(self.player.enemies_killed / enemies_to_now * 100)
            if enemies_to_now > 0 else 0
        )

        rows = [
            ("Wave",          f"{wm.current_wave} / {wm.max_waves}",            (230, 240, 255)),
            ("Wave State",    wm.state.upper(),                                  (255, 210, 80)  if wm.state == "preparing" else
                                                                                 (120, 255, 170) if wm.state == "in_wave"   else
                                                                                 (255, 120, 120)),
            ("Enemies Alive", str(len(self.enemies)),                            (255, 170, 80)),
            ("Spawned",       f"{wm.enemies_spawned} / {wm.enemies_to_spawn}",  (180, 200, 255)),
            ("─" * 28,        "",                                                (50, 90, 160)),
            ("Gold",          str(self.player.gold),                             (255, 215, 80)),
            ("Lives Left",    str(self.player.lives),                            (255, 110, 110) if self.player.lives <= 5 else (120, 255, 170)),
            ("Lives Lost",    str(self.player.lives_lost),                       (255, 130, 130)),
            ("Score",         str(self.player.score),                            (130, 220, 255)),
            ("─" * 28,        "",                                                (50, 90, 160)),
            ("Towers Placed", str(self.player.towers_placed),                   (160, 130, 255)),
            ("Active Towers", str(len(self.towers)),                             (160, 130, 255)),
            ("Kills",         str(self.player.enemies_killed),                   (120, 255, 170)),
            ("Kill Rate",     f"{kill_pct}%",                                    (120, 255, 170)),
            ("Gold→Upgrades", str(self.player.gold_on_upgrades),                (255, 200, 80)),
        ]

        ry = py + 52
        row_h = 19
        for label, value, color in rows:
            if value == "" and label.startswith("─"):
                pygame.draw.line(self.screen, (50, 90, 160),
                                 (px + 12, ry + 6), (px + pw - 12, ry + 6), 1)
            else:
                lbl_s = self.font_small.render(label, True, (150, 170, 210))
                val_s = self.font_small.render(value, True, color)
                self.screen.blit(lbl_s, (px + 14, ry))
                self.screen.blit(val_s, (px + pw - val_s.get_width() - 14, ry))
            ry += row_h

        # Pause hint at bottom if paused
        if self.paused:
            p_surf = self.font_small.render("⏸  Game is paused", True, (255, 210, 80))
            self.screen.blit(p_surf, p_surf.get_rect(centerx=px + pw // 2, y=py + ph - 24))