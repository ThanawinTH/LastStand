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

        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def load_sessions(self) -> List[Dict]:
        self.ensure_csv_exists()

        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)

    def get_next_session_id(self) -> int:
        rows = self.load_sessions()
        if not rows:
            return 1
        return int(rows[-1]["session_id"]) + 1

    def build_session_data(self, game) -> Dict:
        result = "win" if game.wave_manager.is_victory() else "lose"

        # ถ้าแพ้กลาง wave ให้ถือว่ารอดถึง wave ปัจจุบัน - 1
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