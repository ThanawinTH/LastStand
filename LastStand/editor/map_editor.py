import sys
import pygame

from config import (
    FPS,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    GAME_TITLE,
    BG_MAIN,
    BG_PANEL,
    BG_CARD,
    BUTTON_BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    TEXT_SUCCESS,
    TEXT_WARNING,
    TEXT_DANGER,
    MAP_WIDTH,
    MAP_HEIGHT,
    MAP_OFFSET_X,
    MAP_OFFSET_Y,
    SIDE_PANEL_X,
    SIDE_PANEL_Y,
    SIDE_PANEL_WIDTH,
    SIDE_PANEL_HEIGHT,
    HEADER_HEIGHT,
    FOOTER_HEIGHT,
    FOOTER_Y,
    DEFAULT_MAP_JSON,
    TILE_EMPTY,
    TILE_PATH,
    TILE_BUILD,
    TILE_SPAWN,
    TILE_BASE,
    EMPTY_COLOR,
    PATH_COLOR,
    BUILD_COLOR,
    SPAWN_COLOR,
    BASE_COLOR,
    DEFAULT_MAP_IMAGE
)
from core.map_loader import MapLoader
from editor.map_data import create_empty_map_data, set_tile, erase_tile
from editor.map_validator import MapValidator


class MapEditor:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(f"{GAME_TITLE} - Map Editor")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.map_data = create_empty_map_data()
        self.selected_tile_type = TILE_PATH
        self.status_text = "Editor ready."
        self.last_validation_ok = None

        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_medium = pygame.font.SysFont("consolas", 22)
        self.font_large = pygame.font.SysFont("consolas", 30)
        # Load background image (map)
        self.map_image = None
        if DEFAULT_MAP_IMAGE.exists():
            try:
                self.map_image = pygame.image.load(DEFAULT_MAP_IMAGE).convert()
                self.map_image = pygame.transform.scale(
                    self.map_image,
                    (MAP_WIDTH, MAP_HEIGHT)
                )
                self.status_text = f"Loaded map image: {DEFAULT_MAP_IMAGE.name}"
            except Exception as e:
                self.status_text = f"Failed to load map image: {e}"

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button(event)

    def handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_1:
            self.selected_tile_type = TILE_PATH
            self.status_text = "Selected tile type: PATH"

        elif event.key == pygame.K_2:
            self.selected_tile_type = TILE_BUILD
            self.status_text = "Selected tile type: BUILD"

        elif event.key == pygame.K_3:
            self.selected_tile_type = TILE_SPAWN
            self.status_text = "Selected tile type: SPAWN"

        elif event.key == pygame.K_4:
            self.selected_tile_type = TILE_BASE
            self.status_text = "Selected tile type: BASE"

        elif event.key == pygame.K_0:
            self.selected_tile_type = TILE_EMPTY
            self.status_text = "Selected tile type: EMPTY"

        elif event.key == pygame.K_c:
            self.map_data = create_empty_map_data()
            self.last_validation_ok = None
            self.status_text = "Map cleared."

        elif event.key == pygame.K_s:
            try:
                MapLoader.save_map(DEFAULT_MAP_JSON, self.map_data)
                self.status_text = f"Map saved to: {DEFAULT_MAP_JSON.name}"
            except Exception as exc:
                self.status_text = f"Save failed: {exc}"
                self.last_validation_ok = False

        elif event.key == pygame.K_l:
            try:
                self.map_data = MapLoader.load_map(DEFAULT_MAP_JSON)
                self.status_text = f"Map loaded from: {DEFAULT_MAP_JSON.name}"
                self.last_validation_ok = None
            except Exception as exc:
                self.status_text = f"Load failed: {exc}"
                self.last_validation_ok = False

        elif event.key == pygame.K_v:
            ok, message = MapValidator.validate(self.map_data)
            self.last_validation_ok = ok
            self.status_text = message

    def handle_mouse_button(self, event: pygame.event.Event) -> None:
        grid_pos = self.get_grid_pos_from_mouse(event.pos)
        if grid_pos is None:
            return

        col, row = grid_pos

        if event.button == 1:  # Left click = paint selected type
            set_tile(self.map_data, col, row, self.selected_tile_type)
            self.status_text = f"Painted ({col}, {row}) as {self.selected_tile_type.upper()}"
            self.last_validation_ok = None

        elif event.button == 3:  # Right click = erase
            erase_tile(self.map_data, col, row)
            self.status_text = f"Erased tile at ({col}, {row})"
            self.last_validation_ok = None

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self.screen.fill(BG_MAIN)

        self.draw_header()
        self.draw_map_area()
        self.draw_side_panel()
        self.draw_footer()

        pygame.display.flip()

    def draw_header(self) -> None:
        rect = pygame.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(self.screen, BG_PANEL, rect)
        pygame.draw.rect(self.screen, BUTTON_BORDER, rect, 2)

        title = self.font_large.render("MAP EDITOR", True, TEXT_MAIN)
        subtitle = self.font_small.render(
            "Space dungeon grid editor for spawn / build / path / base",
            True,
            TEXT_MUTED,
        )

        self.screen.blit(title, (16, 12))
        self.screen.blit(subtitle, (16, 50))

        selected = self.font_medium.render(
            f"SELECTED: {self.selected_tile_type.upper()}",
            True,
            TEXT_WARNING,
        )
        self.screen.blit(selected, (430, 24))

    def draw_map_area(self) -> None:
        map_rect = pygame.Rect(MAP_OFFSET_X, MAP_OFFSET_Y, MAP_WIDTH, MAP_HEIGHT)
        if self.map_image:
            self.screen.blit(self.map_image, (map_rect.x, map_rect.y))
        else:
            pygame.draw.rect(self.screen, (20, 26, 44), map_rect)
        pygame.draw.rect(self.screen, BUTTON_BORDER, map_rect, 2)

        self.draw_tile_overlay(map_rect)
        self.draw_grid(map_rect)
        self.draw_hover_cell(map_rect)

    def draw_tile_overlay(self, map_rect: pygame.Rect) -> None:
        tile_size = self.map_data["tile_size"]
        cols = self.map_data["cols"]
        rows = self.map_data["rows"]
        grid = self.map_data["grid"]

        color_map = {
            TILE_EMPTY: EMPTY_COLOR,
            TILE_PATH: PATH_COLOR,
            TILE_BUILD: BUILD_COLOR,
            TILE_SPAWN: SPAWN_COLOR,
            TILE_BASE: BASE_COLOR,
        }

        for row in range(rows):
            for col in range(cols):
                tile_type = grid[row][col]
                color = color_map[tile_type]

                cell_rect = pygame.Rect(
                    map_rect.x + col * tile_size,
                    map_rect.y + row * tile_size,
                    tile_size,
                    tile_size,
                )

                if tile_type == TILE_EMPTY:
                    # empty should stay subtle
                    surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    surface.fill((120, 120, 120, 18))
                    self.screen.blit(surface, cell_rect.topleft)
                else:
                    surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    surface.fill((color[0], color[1], color[2], 90))
                    self.screen.blit(surface, cell_rect.topleft)

    def draw_grid(self, map_rect: pygame.Rect) -> None:
        tile_size = self.map_data["tile_size"]
        cols = self.map_data["cols"]
        rows = self.map_data["rows"]

        for col in range(cols + 1):
            x = map_rect.x + col * tile_size
            pygame.draw.line(self.screen, (55, 75, 120), (x, map_rect.y), (x, map_rect.bottom), 1)

        for row in range(rows + 1):
            y = map_rect.y + row * tile_size
            pygame.draw.line(self.screen, (55, 75, 120), (map_rect.x, y), (map_rect.right, y), 1)

    def draw_hover_cell(self, map_rect: pygame.Rect) -> None:
        grid_pos = self.get_grid_pos_from_mouse(pygame.mouse.get_pos())
        if grid_pos is None:
            return

        col, row = grid_pos
        tile_size = self.map_data["tile_size"]

        hover_rect = pygame.Rect(
            map_rect.x + col * tile_size,
            map_rect.y + row * tile_size,
            tile_size,
            tile_size,
        )
        pygame.draw.rect(self.screen, (230, 240, 255), hover_rect, 2)

    def draw_side_panel(self) -> None:
        rect = pygame.Rect(SIDE_PANEL_X, SIDE_PANEL_Y, SIDE_PANEL_WIDTH, SIDE_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, BG_PANEL, rect)
        pygame.draw.rect(self.screen, BUTTON_BORDER, rect, 2)

        x = rect.x + 12
        y = rect.y + 12
        card_width = rect.width - 24

        # Card 1: Controls
        card1 = pygame.Rect(x, y, card_width, 170)
        self.draw_card(card1)
        self.draw_text("PAINT CONTROLS", self.font_medium, TEXT_MAIN, card1.x + 12, card1.y + 10)
        self.draw_text("[1] Path", self.font_small, TEXT_MUTED, card1.x + 12, card1.y + 46)
        self.draw_text("[2] Build", self.font_small, TEXT_MUTED, card1.x + 12, card1.y + 72)
        self.draw_text("[3] Spawn", self.font_small, TEXT_MUTED, card1.x + 12, card1.y + 98)
        self.draw_text("[4] Base", self.font_small, TEXT_MUTED, card1.x + 12, card1.y + 124)
        self.draw_text("[0] Empty", self.font_small, TEXT_MUTED, card1.x + 150, card1.y + 46)

        # Card 2: File actions
        y += 186
        card2 = pygame.Rect(x, y, card_width, 115)
        self.draw_card(card2)
        self.draw_text("FILE ACTIONS", self.font_medium, TEXT_MAIN, card2.x + 12, card2.y + 10)
        self.draw_text("[S] Save JSON", self.font_small, TEXT_MUTED, card2.x + 12, card2.y + 46)
        self.draw_text("[L] Load JSON", self.font_small, TEXT_MUTED, card2.x + 12, card2.y + 72)
        self.draw_text("[V] Validate", self.font_small, TEXT_MUTED, card2.x + 150, card2.y + 46)
        self.draw_text("[C] Clear All", self.font_small, TEXT_MUTED, card2.x + 150, card2.y + 72)

        # Card 3: Map info
        y += 131
        card3 = pygame.Rect(x, y, card_width, 125)
        self.draw_card(card3)
        self.draw_text("MAP INFO", self.font_medium, TEXT_MAIN, card3.x + 12, card3.y + 10)

        hover_pos = self.get_grid_pos_from_mouse(pygame.mouse.get_pos())
        hover_text = f"Hover Cell: {hover_pos}" if hover_pos else "Hover Cell: None"

        self.draw_text(f"Cols x Rows: {self.map_data['cols']} x {self.map_data['rows']}", self.font_small, TEXT_MUTED, card3.x + 12, card3.y + 46)
        self.draw_text(f"Spawn: {self.map_data['spawn']}", self.font_small, TEXT_MUTED, card3.x + 12, card3.y + 70)
        self.draw_text(f"Base: {self.map_data['base']}", self.font_small, TEXT_MUTED, card3.x + 12, card3.y + 94)
        self.draw_text(hover_text, self.font_small, TEXT_WARNING, card3.x + 150, card3.y + 94)

        # Card 4: Status
        y += 141
        card4 = pygame.Rect(x, y, card_width, rect.bottom - y - 12)
        self.draw_card(card4)
        self.draw_text("STATUS", self.font_medium, TEXT_MAIN, card4.x + 12, card4.y + 10)

        status_color = TEXT_MUTED
        if self.last_validation_ok is True:
            status_color = TEXT_SUCCESS
        elif self.last_validation_ok is False:
            status_color = TEXT_DANGER

        self.draw_multiline_text(
            text=self.status_text,
            font=self.font_small,
            color=status_color,
            x=card4.x + 12,
            y=card4.y + 46,
            max_width=card4.width - 24,
            line_height=24,
        )

    def draw_footer(self) -> None:
        rect = pygame.Rect(0, FOOTER_Y, WINDOW_WIDTH, FOOTER_HEIGHT)
        pygame.draw.rect(self.screen, BG_PANEL, rect)
        pygame.draw.rect(self.screen, BUTTON_BORDER, rect, 2)

        lines = [
            "Left Click = Paint selected tile | Right Click = Erase",
            "Paint exactly one SPAWN and one BASE. Connect them using PATH tiles.",
            f"Current output file: {DEFAULT_MAP_JSON.name}",
        ]

        y = rect.y + 14
        for line in lines:
            surface = self.font_small.render(line, True, TEXT_MUTED)
            self.screen.blit(surface, (16, y))
            y += 24

    def get_grid_pos_from_mouse(self, mouse_pos: tuple[int, int]) -> tuple[int, int] | None:
        mx, my = mouse_pos
        tile_size = self.map_data["tile_size"]
        cols = self.map_data["cols"]
        rows = self.map_data["rows"]

        if not (MAP_OFFSET_X <= mx < MAP_OFFSET_X + cols * tile_size):
            return None
        if not (MAP_OFFSET_Y <= my < MAP_OFFSET_Y + rows * tile_size):
            return None

        col = (mx - MAP_OFFSET_X) // tile_size
        row = (my - MAP_OFFSET_Y) // tile_size
        return int(col), int(row)

    def draw_card(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, BG_CARD, rect, border_radius=8)
        pygame.draw.rect(self.screen, BUTTON_BORDER, rect, 2, border_radius=8)

    def draw_text(self, text: str, font: pygame.font.Font, color, x: int, y: int) -> None:
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_multiline_text(
        self,
        text: str,
        font: pygame.font.Font,
        color,
        x: int,
        y: int,
        max_width: int,
        line_height: int,
    ) -> None:
        words = text.split()
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            surface = font.render(test_line, True, color)

            if surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    line_surface = font.render(current_line, True, color)
                    self.screen.blit(line_surface, (x, y))
                    y += line_height
                current_line = word

        if current_line:
            line_surface = font.render(current_line, True, color)
            self.screen.blit(line_surface, (x, y))