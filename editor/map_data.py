from copy import deepcopy

from config import (
    MAP_COLS,
    MAP_ROWS,
    TILE_SIZE,
    TILE_EMPTY,
    TILE_PATH,
    TILE_BUILD,
    TILE_SPAWN,
    TILE_BASE,
    DEFAULT_MAP_NAME,
)


def create_empty_grid() -> list[list[str]]:
    return [[TILE_EMPTY for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]


def create_empty_map_data() -> dict:
    return {
        "map_name": DEFAULT_MAP_NAME,
        "cols": MAP_COLS,
        "rows": MAP_ROWS,
        "tile_size": TILE_SIZE,
        "spawn": None,
        "base": None,
        "grid": create_empty_grid(),
    }


def clone_map_data(map_data: dict) -> dict:
    return deepcopy(map_data)


def find_first_tile_position(grid: list[list[str]], tile_type: str) -> tuple[int, int] | None:
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == tile_type:
                return col, row
    return None


def clear_unique_tile(grid: list[list[str]], tile_type: str) -> None:
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == tile_type:
                grid[row][col] = TILE_EMPTY


def set_tile(map_data: dict, col: int, row: int, tile_type: str) -> None:
    grid = map_data["grid"]

    if tile_type == TILE_SPAWN:
        clear_unique_tile(grid, TILE_SPAWN)
        grid[row][col] = TILE_SPAWN
        map_data["spawn"] = [col, row]

    elif tile_type == TILE_BASE:
        clear_unique_tile(grid, TILE_BASE)
        grid[row][col] = TILE_BASE
        map_data["base"] = [col, row]

    else:
        # If overwriting existing spawn/base, clear stored references
        if grid[row][col] == TILE_SPAWN:
            map_data["spawn"] = None
        elif grid[row][col] == TILE_BASE:
            map_data["base"] = None

        grid[row][col] = tile_type

        # Re-scan in case we changed something important
        spawn_pos = find_first_tile_position(grid, TILE_SPAWN)
        base_pos = find_first_tile_position(grid, TILE_BASE)

        map_data["spawn"] = list(spawn_pos) if spawn_pos else None
        map_data["base"] = list(base_pos) if base_pos else None


def erase_tile(map_data: dict, col: int, row: int) -> None:
    grid = map_data["grid"]

    if grid[row][col] == TILE_SPAWN:
        map_data["spawn"] = None
    elif grid[row][col] == TILE_BASE:
        map_data["base"] = None

    grid[row][col] = TILE_EMPTY