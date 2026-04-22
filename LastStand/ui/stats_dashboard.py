import subprocess
import sys
from pathlib import Path

# Ensure the project root is on sys.path so relative imports work
# regardless of where the script is launched from
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import customtkinter as ctk
import pandas as pd
from pandas.errors import EmptyDataError
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from config import SESSIONS_CSV
from data.statistics_manager import StatisticsManager


class StatsDashboardApp(ctk.CTk):
    EXPECTED_COLUMNS = [
        "session_id",
        "waves_survived",
        "towers_placed",
        "enemies_killed",
        "gold_on_upgrades",
        "lives_lost",
        "result",
    ]

    def __init__(self) -> None:
        super().__init__()

        self.title("Last Stand - Statistics Dashboard")
        self.geometry("1320x860")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.stats_manager = StatisticsManager()
        self.df = self.load_data()

        self.build_ui()

    def load_data(self) -> pd.DataFrame:
        self.stats_manager.ensure_csv_exists()

        if not SESSIONS_CSV.exists() or SESSIONS_CSV.stat().st_size == 0:
            return pd.DataFrame(columns=self.EXPECTED_COLUMNS)

        try:
            df = pd.read_csv(SESSIONS_CSV)
        except EmptyDataError:
            return pd.DataFrame(columns=self.EXPECTED_COLUMNS)

        if df.empty:
            return pd.DataFrame(columns=self.EXPECTED_COLUMNS)

        for col in self.EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = 0 if col != "result" else ""

        numeric_cols = [
            "session_id",
            "waves_survived",
            "towers_placed",
            "enemies_killed",
            "gold_on_upgrades",
            "lives_lost",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["result"] = df["result"].fillna("").astype(str)
        return df[self.EXPECTED_COLUMNS]

    def build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self, corner_radius=16)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="LAST STAND ANALYTICS",
            font=("Consolas", 30, "bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 4))

        subtitle = ctk.CTkLabel(
            header,
            text="Space dungeon tactical performance dashboard",
            font=("Consolas", 16),
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=16, pady=12)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="Refresh",
            width=120,
            command=self.refresh_dashboard,
            font=("Consolas", 16, "bold"),
        )
        refresh_btn.pack(side="left", padx=6)

        open_csv_btn = ctk.CTkButton(
            btn_frame,
            text="Open CSV",
            width=120,
            command=self.open_csv_file,
            font=("Consolas", 16, "bold"),
        )
        open_csv_btn.pack(side="left", padx=6)

        summary = ctk.CTkFrame(self, corner_radius=16)
        summary.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        summary.grid_columnconfigure((0, 1, 2, 3), weight=1)

        stats = self.get_summary_stats()
        self.make_summary_card(summary, 0, "Total Sessions", stats["total_sessions"])
        self.make_summary_card(summary, 1, "Avg Waves", stats["avg_waves"])
        self.make_summary_card(summary, 2, "Avg Kills", stats["avg_kills"])
        self.make_summary_card(summary, 3, "Avg Lives Lost", stats["avg_lives_lost"])

        table_frame = ctk.CTkFrame(self, corner_radius=16)
        table_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        table_frame.grid_columnconfigure(0, weight=1)

        table_label = ctk.CTkLabel(
            table_frame,
            text="SUMMARY TABLE (MIN / MEAN / MAX / STD)",
            font=("Consolas", 18, "bold"),
        )
        table_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        self.summary_table = ctk.CTkTextbox(table_frame, height=150, font=("Consolas", 15))
        self.summary_table.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        self.fill_summary_table()

        self.body = ctk.CTkFrame(self, corner_radius=16)
        self.body.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.body.grid_columnconfigure((0, 1), weight=1)
        self.body.grid_rowconfigure((0, 1), weight=1)

        self.render_charts()

    def make_summary_card(self, parent, column, label_text, value_text):
        card = ctk.CTkFrame(parent, corner_radius=14)
        card.grid(row=0, column=column, sticky="ew", padx=10, pady=10)

        label = ctk.CTkLabel(card, text=label_text, font=("Consolas", 15))
        label.pack(anchor="w", padx=14, pady=(12, 2))

        value = ctk.CTkLabel(card, text=value_text, font=("Consolas", 24, "bold"))
        value.pack(anchor="w", padx=14, pady=(0, 12))

    def get_summary_stats(self):
        if self.df.empty:
            return {
                "total_sessions": "0",
                "avg_waves": "0.00",
                "avg_kills": "0.00",
                "avg_lives_lost": "0.00",
            }

        return {
            "total_sessions": str(len(self.df)),
            "avg_waves": f"{self.df['waves_survived'].mean():.2f}",
            "avg_kills": f"{self.df['enemies_killed'].mean():.2f}",
            "avg_lives_lost": f"{self.df['lives_lost'].mean():.2f}",
        }

    def fill_summary_table(self):
        self.summary_table.configure(state="normal")
        self.summary_table.delete("0.0", "end")

        if self.df.empty:
            self.summary_table.insert("0.0", "No data available yet.")
            self.summary_table.configure(state="disabled")
            return

        cols = [
            "waves_survived",
            "towers_placed",
            "enemies_killed",
            "gold_on_upgrades",
            "lives_lost",
        ]

        stats_df = self.df[cols].agg(["min", "mean", "max", "std"])
        stats_df = stats_df.fillna(0).round(2)

        text = stats_df.to_string()
        self.summary_table.insert("0.0", text)
        self.summary_table.configure(state="disabled")

    def render_charts(self):
        self.add_chart_frame(self.body, 0, 0, "Towers Placed per Session", self.plot_towers_chart)
        self.add_chart_frame(self.body, 0, 1, "Enemies Killed per Session", self.plot_kills_chart)
        self.add_chart_frame(self.body, 1, 0, "Upgrade Spending vs Waves Survived", self.plot_scatter_chart)
        self.add_chart_frame(self.body, 1, 1, "Lives Lost per Session", self.plot_lives_chart)

    def add_chart_frame(self, parent, row, col, title, plot_func):
        frame = ctk.CTkFrame(parent, corner_radius=14)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(frame, text=title, font=("Consolas", 16, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        chart_container = ctk.CTkFrame(frame, corner_radius=10)
        chart_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        chart_container.grid_rowconfigure(0, weight=1)
        chart_container.grid_columnconfigure(0, weight=1)

        fig = plot_func()
        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        plt.close(fig)

    def plot_towers_chart(self):
        fig = plt.Figure(figsize=(5.2, 3.0), dpi=100)
        ax = fig.add_subplot(111)

        if self.df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return fig

        ax.bar(self.df["session_id"], self.df["towers_placed"])
        ax.set_xlabel("Session ID")
        ax.set_ylabel("Towers Placed")
        ax.grid(True, axis="y", alpha=0.3)
        return fig

    def plot_kills_chart(self):
        fig = plt.Figure(figsize=(5.2, 3.0), dpi=100)
        ax = fig.add_subplot(111)

        if self.df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return fig

        ax.plot(self.df["session_id"], self.df["enemies_killed"], marker="o")
        ax.set_xlabel("Session ID")
        ax.set_ylabel("Enemies Killed")
        ax.grid(True, alpha=0.3)
        return fig

    def plot_scatter_chart(self):
        fig = plt.Figure(figsize=(5.2, 3.0), dpi=100)
        ax = fig.add_subplot(111)

        if self.df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return fig

        ax.scatter(self.df["gold_on_upgrades"], self.df["waves_survived"])
        ax.set_xlabel("Gold on Upgrades")
        ax.set_ylabel("Waves Survived")
        ax.grid(True, alpha=0.3)
        return fig

    def plot_lives_chart(self):
        fig = plt.Figure(figsize=(5.2, 3.0), dpi=100)
        ax = fig.add_subplot(111)

        if self.df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return fig

        ax.plot(self.df["session_id"], self.df["lives_lost"], marker="o")
        ax.set_xlabel("Session ID")
        ax.set_ylabel("Lives Lost")
        ax.grid(True, alpha=0.3)
        return fig

    def refresh_dashboard(self):
        self.destroy()
        app = StatsDashboardApp()
        app.mainloop()

    def open_csv_file(self):
        csv_path = Path(SESSIONS_CSV)
        if not csv_path.exists():
            return

        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", str(csv_path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(csv_path)])
            else:
                subprocess.Popen(["xdg-open", str(csv_path)])
        except Exception:
            pass