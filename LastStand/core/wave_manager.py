class WaveManager:
    PREPARING = "preparing"
    IN_WAVE = "in_wave"
    VICTORY = "victory"
    GAME_OVER = "game_over"

    def __init__(self, max_waves: int) -> None:
        self.max_waves = max_waves
        self.current_wave = 0

        self.state = self.PREPARING
        self.prep_timer = 3.0

        self.spawn_interval = 1.0
        self.spawn_timer = 0.0

        self.enemies_to_spawn = 0
        self.enemies_spawned = 0

    def start_first_wave(self) -> None:
        self.current_wave = 1
        self.state = self.PREPARING
        self.prep_timer = 3.0
        self._configure_wave(self.current_wave)

    def _configure_wave(self, wave_number: int) -> None:
        # ปรับความยากแบบค่อย ๆ เพิ่ม
        self.enemies_to_spawn = 5 + (wave_number - 1) * 2
        self.enemies_spawned = 0
        self.spawn_timer = 0.0
        self.spawn_interval = max(0.35, 1.0 - (wave_number - 1) * 0.05)

    def update_preparing(self, dt: float) -> bool:
        if self.state != self.PREPARING:
            return False

        self.prep_timer -= dt
        if self.prep_timer <= 0:
            self.state = self.IN_WAVE
            return True
        return False

    def can_spawn_enemy(self) -> bool:
        return (
            self.state == self.IN_WAVE
            and self.enemies_spawned < self.enemies_to_spawn
        )

    def update_spawn_timer(self, dt: float) -> bool:
        if self.state != self.IN_WAVE:
            return False

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            return True
        return False

    def register_spawn(self) -> None:
        self.enemies_spawned += 1

    def is_wave_spawn_finished(self) -> bool:
        return self.enemies_spawned >= self.enemies_to_spawn

    def is_wave_cleared(self, alive_enemy_count: int) -> bool:
        return self.is_wave_spawn_finished() and alive_enemy_count == 0

    def start_next_wave_or_finish(self) -> None:
        if self.current_wave >= self.max_waves:
            self.state = self.VICTORY
            return

        self.current_wave += 1
        self.state = self.PREPARING
        self.prep_timer = 3.0
        self._configure_wave(self.current_wave)

    def set_game_over(self) -> None:
        self.state = self.GAME_OVER

    def is_victory(self) -> bool:
        return self.state == self.VICTORY

    def is_game_over(self) -> bool:
        return self.state == self.GAME_OVER