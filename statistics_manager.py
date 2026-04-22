import csv
import os
import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = "session_log.csv"
FIELDNAMES = ["waves_survived", "towers_placed", "enemies_killed",
              "gold_on_upgrades", "lives_lost"]


class StatisticsManager:
    """
    Collects per-session gameplay data, saves it to CSV, and generates graphs.

    Counters are incremented by Game throughout a session. At game end,
    end_session() is called with the final values, save_csv() appends the row,
    and show_graphs() renders matplotlib visualisations.
    """

    def __init__(self):
        # Live counters incremented by Game during play
        self.towers_placed: int = 0
        self.enemies_killed: int = 0
        self.gold_on_upgrades: int = 0

        # Populated at end_session()
        self._session: dict = {}

    # ----------------------------------------------------------------- record
    def end_session(self, waves_survived: int, towers_placed: int,
                    enemies_killed: int, gold_on_upgrades: int,
                    lives_lost: int) -> None:
        self._session = {
            "waves_survived": waves_survived,
            "towers_placed": towers_placed,
            "enemies_killed": enemies_killed,
            "gold_on_upgrades": gold_on_upgrades,
            "lives_lost": lives_lost,
        }

    def save_csv(self) -> None:
        """Append one row to session_log.csv. Create file with header if new."""
        file_exists = os.path.isfile(CSV_PATH)
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(self._session)

    # ------------------------------------------------------------------ graphs
    def show_graphs(self) -> None:
        """Load all session data from CSV and display 5 matplotlib charts."""
        if not os.path.isfile(CSV_PATH):
            print("No session data found.")
            return

        df = pd.read_csv(CSV_PATH)
        if df.empty:
            print("Session log is empty.")
            return

        fig, axes = plt.subplots(2, 3, figsize=(15, 9))
        fig.suptitle("Last Stand — Session Statistics", fontsize=16, fontweight="bold")

        # 1. Histogram of waves survived
        axes[0, 0].hist(df["waves_survived"], bins=range(0, 12), color="#4C8FBF",
                        edgecolor="white", align="left")
        axes[0, 0].set_title("Waves Survived Distribution")
        axes[0, 0].set_xlabel("Waves Survived")
        axes[0, 0].set_ylabel("Sessions")
        axes[0, 0].set_xticks(range(0, 11))

        # 2. Bar chart of towers placed per session
        session_ids = range(1, len(df) + 1)
        axes[0, 1].bar(session_ids, df["towers_placed"], color="#6BAF72", edgecolor="white")
        axes[0, 1].set_title("Towers Placed per Session")
        axes[0, 1].set_xlabel("Session")
        axes[0, 1].set_ylabel("Towers Placed")

        # 3. Line graph of enemies killed over sessions
        axes[0, 2].plot(session_ids, df["enemies_killed"],
                        marker="o", color="#BF7940", linewidth=2)
        axes[0, 2].set_title("Enemies Killed over Sessions")
        axes[0, 2].set_xlabel("Session")
        axes[0, 2].set_ylabel("Enemies Killed")

        # 4. Scatter: gold on upgrades vs waves survived
        axes[1, 0].scatter(df["gold_on_upgrades"], df["waves_survived"],
                           color="#9B59B6", alpha=0.7, edgecolors="white", s=80)
        axes[1, 0].set_title("Upgrade Spending vs Waves Survived")
        axes[1, 0].set_xlabel("Gold Spent on Upgrades")
        axes[1, 0].set_ylabel("Waves Survived")

        # 5. Line graph of lives lost over sessions
        #    (line graph suits sequential session data; tracks improvement over time)
        axes[1, 1].plot(session_ids, df["lives_lost"],
                        marker="s", color="#E74C3C", linewidth=2)
        axes[1, 1].set_title("Lives Lost over Sessions")
        axes[1, 1].set_xlabel("Session")
        axes[1, 1].set_ylabel("Lives Lost")

        # 6. Summary text panel
        axes[1, 2].axis("off")
        summary = (
            f"Total sessions:  {len(df)}\n\n"
            f"Waves survived\n"
            f"  Mean:  {df['waves_survived'].mean():.1f}\n"
            f"  Max:   {df['waves_survived'].max()}\n\n"
            f"Lives lost\n"
            f"  Mean:  {df['lives_lost'].mean():.1f}\n"
            f"  Max:   {df['lives_lost'].max()}\n\n"
            f"Enemies killed\n"
            f"  Total: {df['enemies_killed'].sum()}\n\n"
            f"Gold on upgrades\n"
            f"  Mean:  {df['gold_on_upgrades'].mean():.0f}"
        )
        axes[1, 2].text(0.1, 0.9, summary, transform=axes[1, 2].transAxes,
                        fontsize=12, verticalalignment="top", fontfamily="monospace",
                        bbox=dict(boxstyle="round", facecolor="#F0F0F0", alpha=0.8))
        axes[1, 2].set_title("Summary")

        plt.tight_layout()
        plt.show()
