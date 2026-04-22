# Last Stand

## Space Dungeon Tower Defense

- **Game Genre:** Tower Defense, Strategy
- **Engine:** Python + Pygame-CE

Last Stand is a top-down grid-based tower defense game set in a space dungeon. You strategically place and upgrade towers to defend your base from waves of enemies moving along a fixed path. Each session tracks your performance — kills, towers placed, gold spent on upgrades, and lives lost — and stores it in a CSV that feeds a live analytics dashboard.

The game also ships with a standalone **Statistics Dashboard** (customtkinter + matplotlib) where you can review your performance across all sessions with charts and summary statistics.

---

## Installation

To clone this project:

```sh
git clone https://github.com/your-repo/LastStand.git
cd LastStand
```

To create and run a Python virtual environment:

**Windows:**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirement.txt
```

**Mac / Linux:**

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

---

## Running Guide

After activating the virtual environment, run the game with:

**Windows:**

```bat
python main.py
```

**Mac / Linux:**

```sh
python3 main.py
```

To open the Statistics Dashboard separately:

**Windows:**

```bat
python dashboard_main.py
```

**Mac / Linux:**

```sh
python3 dashboard_main.py
```

---

## Tutorial / Usage

### Controls

| Key / Action          | Function                             |
| --------------------- | ------------------------------------ |
| `1`                   | Select Archer Tower                  |
| `2`                   | Select Mage Tower                    |
| `3`                   | Select Ballista Tower                |
| `Left Click`          | Place selected tower on a build tile |
| `U`                   | Upgrade selected tower               |
| `S`                   | Sell selected tower                  |
| `ESC` / `Right Click` | Deselect / cancel placement          |
| `R`                   | Restart game                         |

### How to Play

1. Launch the game and click **Play** on the start screen
2. Select a tower type using keys `1`, `2`, or `3`
3. Click on any highlighted **build tile** on the map to place it
4. Enemies spawn from the top and follow the path toward your base
5. Towers attack enemies automatically when they enter range
6. Earn gold from kills — use it to place or upgrade more towers
7. Survive all **10 waves** to win; lose all lives and it's game over

### Tips

- Ballista Towers pierce through multiple enemies — great on long straight paths
- Upgrade early towers to maximize gold efficiency
- Use Mage Towers behind Archer Towers for high-damage support
- Check the Statistics Dashboard after your sessions to spot patterns in your play style

---

## Game Features

- **3 Tower Types** — Archer (fast), Mage (high damage), Ballista (piercing)
- **3-Level Upgrade System** — Towers gain damage, range, and fire rate each level
- **4 Enemy Types** — Goblin, Orc, Dark Knight, Boss
- **10 Waves** — Escalating enemy counts and compositions
- **Grid-Based Map** — 18×16 tile map with path, build, spawn, and base tiles
- **Custom Map Editor** — Visual editor for creating and saving new maps (`editor_main.py`)
- **Statistics Logging** — Session data saved to `data/sessions.csv` automatically
- **Analytics Dashboard** — Separate customtkinter app with 4 charts and a summary table
- **Space Dungeon Theme** — Consistent dark blue/cyan color palette across all UI

---

## Project Structure

```
TowerDefenseMing/
│
├── core/               # Game loop, wave manager, scene manager, stats logger, music
├── entities/           # Tower and Enemy class hierarchy + projectiles
├── ui/                 # HUD, panels, start screen, stats dashboard, theme
├── editor/             # Map editor logic
├── data/               # sessions.csv + map JSON/PNG files
├── assets/             # Images and sounds
├── config.py           # Global constants (window size, colors, game balance)
├── main.py             # Game entry point
├── editor_main.py      # Map editor entry point
└── dashboard_main.py   # Statistics dashboard entry point
```

---

## Known Bugs

None known at this time.

---

## Unfinished Works

All planned features have been implemented.

---

## External Sources

All assets are from open-source or royalty-free sources. See `assets/` folder for individual attributions.
