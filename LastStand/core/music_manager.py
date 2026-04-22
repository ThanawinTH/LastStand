"""
MusicManager – handles background music for all scenes.

Usage:
    music = MusicManager()
    music.play_menu()          # start screen
    music.play_game()          # in-game
    music.toggle_mute()        # mute / unmute
    music.set_volume(0.5)      # 0.0 – 1.0
"""

import pygame
from pathlib import Path

SOUNDS_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"


class MusicManager:
    VOLUME_DEFAULT = 0.45

    def __init__(self):
        # pygame.mixer must already be initialised (pygame.init() handles it)
        self._muted = False
        self._volume = self.VOLUME_DEFAULT
        self._current = None          # "menu" | "game" | None

        self._files = {
            "menu": SOUNDS_DIR / "music_menu.wav",
            "game": SOUNDS_DIR / "music_game.wav",
        }

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def play_menu(self):
        self._play("menu")

    def play_game(self):
        self._play("game")

    def stop(self):
        pygame.mixer.music.stop()
        self._current = None

    def toggle_mute(self):
        self._muted = not self._muted
        pygame.mixer.music.set_volume(0.0 if self._muted else self._volume)
        return self._muted   # returns new mute state

    @property
    def is_muted(self):
        return self._muted

    def set_volume(self, vol: float):
        self._volume = max(0.0, min(1.0, vol))
        if not self._muted:
            pygame.mixer.music.set_volume(self._volume)

    # ------------------------------------------------------------------ #
    #  Internal                                                            #
    # ------------------------------------------------------------------ #

    def _play(self, track: str):
        if self._current == track:
            return          # already playing the right track

        path = self._files.get(track)
        if path is None or not path.exists():
            return

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.0 if self._muted else self._volume)
            pygame.mixer.music.play(-1)   # loop forever
            self._current = track
        except pygame.error as exc:
            print(f"[MusicManager] Could not play {track}: {exc}")
