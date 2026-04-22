from pathlib import Path

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"

DATA_DIR = BASE_DIR / "data"
MAPS_DIR = DATA_DIR / "maps"
SESSIONS_CSV = DATA_DIR / "sessions.csv"

# =========================
# GAME / WINDOW
# =========================
GAME_TITLE = "Last Stand"
FPS = 60

# =========================
# MAP CONFIG
# =========================
TILE_SIZE = 32
MAP_COLS = 18
MAP_ROWS = 16

MAP_WIDTH = MAP_COLS * TILE_SIZE   # 576
MAP_HEIGHT = MAP_ROWS * TILE_SIZE  # 512

# =========================
# UI LAYOUT
# =========================
HEADER_HEIGHT = 116
FOOTER_HEIGHT = 100

# เพิ่มพื้นที่ฝั่งขวา
SIDE_PANEL_WIDTH = 430

WINDOW_WIDTH = MAP_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = HEADER_HEIGHT + MAP_HEIGHT + FOOTER_HEIGHT

MAP_OFFSET_X = 0
MAP_OFFSET_Y = HEADER_HEIGHT

SIDE_PANEL_X = MAP_WIDTH
SIDE_PANEL_Y = HEADER_HEIGHT
SIDE_PANEL_HEIGHT = MAP_HEIGHT

FOOTER_Y = HEADER_HEIGHT + MAP_HEIGHT

# =========================
# SPACING / FONT
# =========================
PADDING_SMALL = 8
PADDING_MEDIUM = 12
PADDING_LARGE = 18

FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 22
FONT_SIZE_LARGE = 30

# =========================
# SPACE DUNGEON THEME
# =========================
BG_MAIN = (10, 12, 24)
BG_PANEL = (18, 24, 44)
BG_PANEL_DARK = (12, 16, 30)
BG_CARD = (24, 32, 58)

GRID_LINE = (70, 90, 140)
GLOW_BLUE = (80, 180, 255)
GLOW_CYAN = (60, 220, 255)
GLOW_PURPLE = (160, 90, 255)

TEXT_MAIN = (230, 240, 255)
TEXT_MUTED = (150, 170, 210)
TEXT_WARNING = (255, 210, 100)
TEXT_DANGER = (255, 110, 110)
TEXT_SUCCESS = (120, 255, 170)

BUTTON_BG = (28, 38, 70)
BUTTON_BG_HOVER = (40, 56, 96)
BUTTON_BORDER = (90, 180, 255)

PATH_COLOR = (255, 200, 80)
BUILD_COLOR = (80, 200, 120)
SPAWN_COLOR = (80, 220, 255)
BASE_COLOR = (255, 120, 180)
EMPTY_COLOR = (120, 120, 120)

# =========================
# GAME BALANCE (INITIAL)
# =========================
PLAYER_START_GOLD = 150
PLAYER_START_LIVES = 20

ARCHER_COST = 50
MAGE_COST = 70
BALLISTA_COST = 90

MAX_WAVES = 10

# =========================
# MAP TILE TYPES
# =========================
TILE_EMPTY = "empty"
TILE_PATH = "path"
TILE_BUILD = "build"
TILE_SPAWN = "spawn"
TILE_BASE = "base"

VALID_TILE_TYPES = {
    TILE_EMPTY,
    TILE_PATH,
    TILE_BUILD,
    TILE_SPAWN,
    TILE_BASE,
}

# =========================
# DEFAULT MAP FILE
# =========================
DEFAULT_MAP_NAME = "map01"
DEFAULT_MAP_IMAGE = MAPS_DIR / "map01.png"
DEFAULT_MAP_JSON = MAPS_DIR / "map01.json"

# =========================
# DEBUG
# =========================
DEBUG_DRAW_PATH = True