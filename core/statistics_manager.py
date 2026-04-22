import csv
from pathlib import Path
from typing import Dict, List

from config import SESSIONS_CSV


class StatisticsManager:
    FIELDNAMES = [
        "session_id",
        "waves_survived",
        "towers_placed",
        "enemies_killed",
        "gold_on_upgrades",
        "lives_lost",
        "result",
    ]

    def __init__(self, csv_path: Path = SESSIONS_CSV) -> None:
        self.csv_path = Path(csv_path)
        self.ensure_csv_exists()

    def ensure_csv_exists(self) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            self._write_fresh_file()
            return

        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames or []

            if any(name not in fieldnames for name in self.FIELDNAMES):
                self._repair_file()
        except Exception:
            self._write_fresh_file()

    def _write_fresh_file(self) -> None:
        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writeheader()

    def _repair_file(self) -> None:
        old_rows = []

        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for index, row in enumerate(reader, start=1):
                    normalized = {
                        "session_id": row.get("session_id") or str(index),
                        "waves_survived": row.get("waves_survived", 0),
                        "towers_placed": row.get("towers_placed", 0),
                        "enemies_killed": row.get("enemies_killed", 0),
                        "gold_on_upgrades": row.get("gold_on_upgrades", 0),
                        "lives_lost": row.get("lives_lost", 0),
                        "result": row.get("result", ""),
                    }
                    old_rows.append(normalized)
        except Exception:
            old_rows = []

        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(old_rows)

    def load_sessions(self) -> List[Dict]:
        self.ensure_csv_exists()

        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        normalized_rows = []
        for index, row in enumerate(rows, start=1):
            normalized_rows.append({
                "session_id": row.get("session_id") or str(index),
                "waves_survived": row.get("waves_survived", 0),
                "towers_placed": row.get("towers_placed", 0),
                "enemies_killed": row.get("enemies_killed", 0),
                "gold_on_upgrades": row.get("gold_on_upgrades", 0),
                "lives_lost": row.get("lives_lost", 0),
                "result": row.get("result", ""),
            })

        return normalized_rows

    def get_next_session_id(self) -> int:
        rows = self.load_sessions()
        if not rows:
            return 1

        last_id = 0
        for row in rows:
            try:
                last_id = max(last_id, int(row.get("session_id", 0)))
            except (TypeError, ValueError):
                continue

        return last_id + 1

    def build_session_data(self, game) -> Dict:
        result = "win" if game.wave_manager.is_victory() else "lose"

        if result == "lose":
            waves_survived = max(0, game.wave_manager.current_wave - 1)
        else:
            waves_survived = game.wave_manager.current_wave

        return {
            "session_id": self.get_next_session_id(),
            "waves_survived": waves_survived,
            "towers_placed": game.player.towers_placed,
            "enemies_killed": game.player.enemies_killed,
            "gold_on_upgrades": game.player.gold_on_upgrades,
            "lives_lost": game.player.lives_lost,
            "result": result,
        }

    def save_session(self, game) -> None:
        self.ensure_csv_exists()
        row = self.build_session_data(game)

        with open(self.csv_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writerow(row)