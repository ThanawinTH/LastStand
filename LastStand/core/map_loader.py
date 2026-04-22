import json
from pathlib import Path
from collections import deque

from config import TILE_PATH, TILE_BASE


class MapLoader:
    @staticmethod
    def load_map(json_path: Path) -> dict:
        if not json_path.exists():
            raise FileNotFoundError(f"Map file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_map(json_path: Path, map_data: dict) -> None:
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(map_data, file, indent=4, ensure_ascii=False)

    # =========================
    # 🔥 NEW: BUILD PATH POINTS
    # =========================
    @staticmethod
    def build_path_points(map_data: dict) -> list[tuple[int, int]]:
        grid = map_data["grid"]
        spawn = tuple(map_data["spawn"])
        base = tuple(map_data["base"])

        rows = len(grid)
        cols = len(grid[0])

        queue = deque([spawn])
        visited = {spawn}
        parent = {}

        def neighbors(c, r):
            for dc, dr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc, nr = c + dc, r + dr
                if 0 <= nc < cols and 0 <= nr < rows:
                    yield nc, nr

        # BFS หาเส้นทาง
        while queue:
            c, r = queue.popleft()

            if (c, r) == base:
                break

            for nc, nr in neighbors(c, r):
                if (nc, nr) in visited:
                    continue

                tile = grid[nr][nc]
                if tile in {TILE_PATH, TILE_BASE}:
                    visited.add((nc, nr))
                    parent[(nc, nr)] = (c, r)
                    queue.append((nc, nr))

        # reconstruct path
        path = []
        current = base

        while current != spawn:
            path.append(current)
            current = parent.get(current)
            if current is None:
                return []

        path.append(spawn)
        path.reverse()

        return path

    # =========================
    # convert grid -> pixel points
    # =========================
    @staticmethod
    def path_to_pixel_points(path, tile_size, offset_x, offset_y):
        points = []
        for col, row in path:
            x = offset_x + col * tile_size + tile_size // 2
            y = offset_y + row * tile_size + tile_size // 2
            points.append((x, y))
        return points