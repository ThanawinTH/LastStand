import subprocess
import sys
from pathlib import Path

import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT
from core.scene_manager import SceneManager
from core.game import Game
from core.music_manager import MusicManager
from ui.start_screen import StartScreen

# Absolute path to the project root (where main.py lives)
PROJECT_ROOT = Path(__file__).resolve().parent


def open_stats_dashboard():
    script = PROJECT_ROOT / "dashboard_main.py"
    subprocess.Popen(
        [sys.executable, str(script)],
        cwd=str(PROJECT_ROOT),
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    scene_manager = SceneManager(screen)
    start_screen = StartScreen(screen)
    music = MusicManager()
    game = None

    # Start with menu music
    music.play_menu()

    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            # Global mute toggle: M key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                music.toggle_mute()

        if scene_manager.current_scene == "start":
            music.play_menu()   # switch back if returning from game

            for event in events:
                action = start_screen.handle_event(event)
                if action == "start":
                    scene_manager.start_transition("game")
                elif action == "stats":
                    open_stats_dashboard()
                elif action == "exit":
                    running = False

            start_screen.update(dt)
            start_screen.draw(music)

        elif scene_manager.current_scene == "game":
            if game is None:
                game = Game()
                music.play_game()

            result = game.handle_events(events, music)

            if result == "back_to_menu":
                game = None
                scene_manager.current_scene = "start"
                scene_manager.is_fading_in = True
                scene_manager.fade_alpha = 255

            elif result == "view_stats":
                open_stats_dashboard()

            # สำคัญ: อัปเดต/วาดเฉพาะตอน game ยังมีอยู่
            if game is not None:
                game.update(dt)
                game.draw()

        scene_manager.update(dt)
        scene_manager.draw_fade()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()