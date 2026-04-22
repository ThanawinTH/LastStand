# Project Description

## 1. Project Overview

- **Project Name:** Last Stand
- **Game Genre:** Tower Defense, Strategy
- **Brief Description:**

  Last Stand is a top-down grid-based tower defense game built with Python and Pygame-CE, themed around a space dungeon. The player places and upgrades towers on a fixed tile map to defend their base from waves of enemies following a preset path. Three distinct tower types — Archer, Mage, and Ballista — each have different stats and attack behaviors, and can be upgraded up to three levels.

  The game features four enemy types with different HP, speed, and armor values, escalating across ten waves. A boss enemy appears on key waves. The player starts with 150 gold and 20 lives; towers are purchased and upgraded with gold earned from kills.

  Beyond the core game, Last Stand includes a **custom map editor** for designing new maps visually, and a **standalone Statistics Dashboard** built with customtkinter and matplotlib that visualizes session performance data logged to CSV.

- **Problem Statement:**

  Tower defense games often feel samey because the player has no visibility into their own tendencies — do they over-invest in upgrades? Do they consistently lose lives on early waves? Last Stand addresses this by pairing the gameplay with a persistent statistics system and dashboard, turning each session into a data point so players can track and improve over time.

- **Target Users:**

  Players who enjoy tactical strategy games with short session times. Also suitable for students or developers interested in seeing how a Pygame game can be paired with a data analytics layer.

- **Key Features:**
  - 3 tower types with 3-level upgrades (damage, range, fire rate scale per level)
  - 4 enemy types (Goblin, Orc, Dark Knight, Boss) with armor and trail/glow visuals
  - 10 configurable waves with escalating enemy counts and compositions
  - Grid-based 18×16 tile map with path, build, spawn, and base tile types
  - Custom visual map editor (`editor_main.py`) for creating new maps
  - Session statistics logged to `data/sessions.csv` after every game
  - Standalone analytics dashboard (`dashboard_main.py`) with 4 charts + summary table
  - Background music with scene-based switching via `MusicManager`
  - Space dungeon visual theme — dark blue/cyan color palette throughout

---

## 2. Concept

### 2.1 Background

Last Stand was designed to explore what a tower defense game feels like when it also acts as a personal performance tracker. Most tower defense games reset completely between sessions with no record of what happened. This project adds a lightweight statistics layer so every session leaves a trace, and the player can look back at a dashboard to understand how they play.

The space dungeon setting was chosen to give the game a distinct visual identity — glowing enemies with trails, cyan tower beams, and a dark blue grid that feels different from typical fantasy tower defense aesthetics.

### 2.2 Objectives

- Build a fully playable tower defense loop with clear win and lose conditions
- Implement a clean inheritance hierarchy for towers and enemies
- Create a custom tile-based map editor that produces JSON map files loadable by the game
- Record meaningful per-session gameplay statistics to CSV in a structured format
- Visualize that data in an external dashboard using customtkinter and matplotlib

---

## 3. UML Class Diagram

The UML class diagram covers all major classes, their key attributes and methods, and relationships (inheritance, association, dependency).

**Key Inheritance Trees:**

- `Tower → ArcherTower / MageTower / BallistaTower`
- `Enemy → Goblin / Orc / DarkKnight / BossEnemy`

---

## 4. Object-Oriented Programming Implementation

- **`Game`** — Top-level controller in `main.py`. Owns the main loop, manages state transitions (start screen → gameplay → game over), and coordinates all subsystems.

- **`Player`** — Holds the player's gold, lives, and session counters (towers_placed, enemies_killed, gold_on_upgrades, lives_lost). Updated by game events rather than controlling a character.

- **`Tower`** _(abstract base)_ — Base class for all towers. Handles targeting logic (furthest enemy along the path within range), attack cooldown timing, upgrade stat scaling, sell value calculation, and selection/range circle drawing.

- **`ArcherTower`** — Fast fire rate, low damage. Fires single-target projectiles.

- **`MageTower`** — Slow fire rate, high damage. Fires single-target projectiles.

- **`BallistaTower`** — Medium fire rate, piercing projectile that passes through multiple enemies in a line.

- **`Enemy`** _(abstract base)_ — Base class for all enemies. Handles waypoint-based pathfinding, armor-reduced damage calculation, HP bar drawing, glow and trail visual effects, and base-reached detection.

- **`Goblin`** — Fast, low HP, no armor.

- **`Orc`** — Slow, high HP, moderate armor.

- **`DarkKnight`** — Medium speed, medium HP, high armor.

- **`BossEnemy`** — Large HP pool with an aura effect, spawns on key waves.

- **`Projectile`** — Moves toward a target enemy per frame, deals damage on contact, removed on hit (or on passing through for Ballista).

- **`WaveManager`** — Controls enemy spawn scheduling across all 10 waves. Reads wave configurations to determine enemy type counts and spawn intervals. Tracks current wave and victory state.

- **`MapLoader`** — Loads tile maps from JSON files. Returns tile type grids and precomputed waypoint paths for enemies to follow.

- **`StatisticsManager`** — Writes session results to `data/sessions.csv` in append mode. Handles file creation, column validation and auto-repair, and ID sequencing across sessions.

- **`SceneManager`** — Manages transitions between the start screen, gameplay, and game-over scenes.

- **`MusicManager`** — Handles background music loading and scene-based track switching using Pygame's mixer.

- **`HUD`** — Draws the top header (wave counter, gold, lives) and the right-side panel (tower selection buttons, upgrade/sell info for selected tower, wave start button).

- **`StartScreen`** — Animated title screen with Play button and the space dungeon visual theme.

- **`StatsDashboardApp`** _(customtkinter)_ — Standalone dashboard window. Loads `sessions.csv` via `StatisticsManager`, computes summary statistics, and renders four matplotlib charts embedded in the UI.

---

## 5. Statistical Data

### 5.1 Data Recording Method

Session data is recorded by `StatisticsManager` at the end of each game (win or loss). The file `data/sessions.csv` is opened in append mode so data accumulates across all sessions without overwriting previous runs. Each row represents one complete game session and is assigned an auto-incrementing `session_id`.

### 5.2 Data Features

| Column             | What It Records                                               |
| ------------------ | ------------------------------------------------------------- |
| `session_id`       | Auto-incrementing unique session identifier                   |
| `waves_survived`   | Number of waves completed before game over (or all 10 on win) |
| `towers_placed`    | Total towers placed during the session                        |
| `enemies_killed`   | Total enemies killed during the session                       |
| `gold_on_upgrades` | Total gold spent on tower upgrades                            |
| `lives_lost`       | Total lives lost to enemies reaching the base                 |
| `result`           | `win` or `lose`                                               |

These features were chosen to cover the four core decisions a player makes each session: how aggressively they build (towers_placed), how well they defend (enemies_killed, waves_survived), how they invest (gold_on_upgrades), and how well they hold the line (lives_lost). Together they provide a complete picture of tactical performance over time.

---

## 6. External Sources

All assets are sourced from open-source or royalty-free repositories. Attribution details are included in the `assets/` folder.
