# Visualisation

## Overview

Last Stand records a row of session data to `data/sessions.csv` after every game. The **Statistics Dashboard** (`dashboard_main.py`) reads this file and presents five visualizations — four charts and one summary table — inside a customtkinter window. The dashboard can be launched independently of the game at any time.

To open the dashboard:

```sh
python dashboard_main.py
```

---

## Data Source

All visualizations are driven by `data/sessions.csv`, which is written by `StatisticsManager` in `core/statistics_manager.py`. Each row records one complete game session:

| Column             | Type | Description                               |
| ------------------ | ---- | ----------------------------------------- |
| `session_id`       | int  | Auto-incrementing session number          |
| `waves_survived`   | int  | Waves completed before game over (max 10) |
| `towers_placed`    | int  | Total towers placed during the session    |
| `enemies_killed`   | int  | Total enemies killed                      |
| `gold_on_upgrades` | int  | Total gold spent on tower upgrades        |
| `lives_lost`       | int  | Lives lost to enemies reaching the base   |
| `result`           | str  | `win` or `lose`                           |

Data accumulates across all sessions in append mode — no session is ever overwritten.

---

## Dashboard Layout

The dashboard window is `1320×860 px`, built with **customtkinter** (dark mode). It is divided into four sections from top to bottom:

1. **Header** — Title, subtitle, Refresh button, Open CSV button
2. **Summary Cards** — Four key aggregate stats at a glance
3. **Summary Table** — Min / Mean / Max / Std for all numeric columns
4. **Chart Grid** — 2×2 grid of matplotlib charts

---

## Summary Cards

Four metric cards displayed horizontally below the header, each showing a single aggregate value computed from all sessions:

| Card               | Value                                        |
| ------------------ | -------------------------------------------- |
| **Total Sessions** | Count of all rows in the CSV                 |
| **Avg Waves**      | Mean of `waves_survived` across all sessions |
| **Avg Kills**      | Mean of `enemies_killed` across all sessions |
| **Avg Lives Lost** | Mean of `lives_lost` across all sessions     |

---

## Summary Table

A text block showing `min`, `mean`, `max`, and `std` for all five numeric columns:

- `waves_survived`
- `towers_placed`
- `enemies_killed`
- `gold_on_upgrades`
- `lives_lost`

Values are rounded to two decimal places. This table gives a quick statistical profile of overall playstyle across all sessions.

**Example output:**

```
               waves_survived  towers_placed  enemies_killed  gold_on_upgrades  lives_lost
min                       1.0            3.0            12.0               0.0         0.0
mean                      6.4            8.2            54.6              87.5         4.3
max                      10.0           14.0           103.0             240.0        14.0
std                       2.8            2.9            25.1              73.2         3.9
```

---

## Chart 1 — Towers Placed per Session

**Type:** Bar chart
**X-axis:** Session ID
**Y-axis:** Number of towers placed

Shows how tower placement count changes from session to session. A consistent upward trend typically indicates a player building more confidently over time. Flat or declining values may suggest over-reliance on upgrades instead of placement.

---

## Chart 2 — Enemies Killed per Session

**Type:** Line chart with markers
**X-axis:** Session ID
**Y-axis:** Enemies killed

Tracks kill counts across sessions. Rising values over time indicate improving tower placement and coverage. Sharp drops often correlate with sessions where the player lost early and did not survive enough waves to rack up kills.

---

## Chart 3 — Upgrade Spending vs Waves Survived

**Type:** Scatter plot
**X-axis:** Gold spent on upgrades
**Y-axis:** Waves survived

Each point is one session. This chart explores the relationship between upgrade investment and survival. A cluster toward the upper-right would suggest that upgrading towers consistently helps survive more waves. Points scattered along the left edge (low spending, variable waves) indicate players who rely on volume placement rather than upgrades.

---

## Chart 4 — Lives Lost per Session

**Type:** Line chart with markers
**X-axis:** Session ID
**Y-axis:** Lives lost

Tracks how many lives the player lost per session. Ideally this number trends downward as the player improves. Sudden spikes often indicate a wave composition that caught the player off guard or a session where early gold was spent poorly.

---

## Refreshing the Dashboard

Clicking the **Refresh** button restarts the dashboard window and reloads the CSV from disk. This is useful if you just finished a session and want to see your new data without closing and reopening manually.

Clicking **Open CSV** opens `data/sessions.csv` directly using the system default application (Excel, Numbers, or a text editor depending on OS).

---

## Implementation Notes

- Charts are rendered using `matplotlib` and embedded in the customtkinter window via `FigureCanvasTkAgg`
- Each `plt.Figure` is closed with `plt.close(fig)` after embedding to prevent memory accumulation
- If the CSV is empty or missing, all charts display a "No data" message and cards show zeroed values
- Missing or malformed columns are auto-repaired by `StatisticsManager._repair_file()` before loading
