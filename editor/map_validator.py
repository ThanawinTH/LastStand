from collections import deque

from config import (
    VALID_TILE_TYPES,
    TILE_PATH,
    TILE_SPAWN,
    TILE_BASE,
)


class MapValidator:
    @staticmethod
    def validate(map_data: dict) -> tuple[bool, str]:
        required_keys = {"map_name", "cols", "rows", "tile_size", "spawn", "base", "grid"}
        if not required_keys.issubset(set(map_data.keys())):
            return False, "Map data is missing required keys."

        cols = map_data["cols"]
        rows = map_data["rows"]
        grid = map_data["grid"]
        spawn = map_data["spawn"]
        base = map_data["base"]

        if not isinstance(grid, list) or len(grid) != rows:
            return False, "Grid row count does not match map rows."

        for row_data in grid:
            if not isinstance(row_data, list) or len(row_data) != cols:
                return False, "Grid column count does not match map cols."

            for cell in row_data:
                if cell not in VALID_TILE_TYPES:
                    return False, f"Invalid tile type found: {cell}"

        spawn_count = 0
        base_count = 0

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == TILE_SPAWN:
                    spawn_count += 1
                elif grid[r][c] == TILE_BASE:
                    base_count += 1

        if spawn_count != 1:
            return False, f"Map must contain exactly 1 spawn tile, found {spawn_count}."

        if base_count != 1:
            return False, f"Map must contain exactly 1 base tile, found {base_count}."

        if spawn is None:
            return False, "Spawn reference is missing."
        if base is None:
            return False, "Base reference is missing."

        spawn_col, spawn_row = spawn
        base_col, base_row = base

        if not MapValidator._is_in_bounds(spawn_col, spawn_row, cols, rows):
            return False, "Spawn reference is out of bounds."
        if not MapValidator._is_in_bounds(base_col, base_row, cols, rows):
            return False, "Base reference is out of bounds."

        if grid[spawn_row][spawn_col] != TILE_SPAWN:
            return False, "Spawn reference does not match grid content."

        if grid[base_row][base_col] != TILE_BASE:
            return False, "Base reference does not match grid content."

        has_route = MapValidator._has_valid_route(grid, spawn, base)
        if not has_route:
            return False, "No connected route from spawn to base through path tiles."

        return True, "Map data is valid."

    @staticmethod
    def _is_in_bounds(col: int, row: int, cols: int, rows: int) -> bool:
        return 0 <= col < cols and 0 <= row < rows

    @staticmethod
    def _has_valid_route(grid: list[list[str]], spawn: list[int], base: list[int]) -> bool:
        cols = len(grid[0])
        rows = len(grid)

        start = tuple(spawn)
        goal = tuple(base)

        queue = deque([start])
        visited = {start}

        def neighbors(col: int, row: int) -> list[tuple[int, int]]:
            result = []
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nc = col + dc
                nr = row + dr
                if 0 <= nc < cols and 0 <= nr < rows:
                    result.append((nc, nr))
            return result

        while queue:
            col, row = queue.popleft()

            if (col, row) == goal:
                return True

            for nc, nr in neighbors(col, row):
                if (nc, nr) in visited:
                    continue

                tile = grid[nr][nc]
                if tile in {TILE_PATH, TILE_BASE}:
                    visited.add((nc, nr))
                    queue.append((nc, nr))

        return False