import pygame


class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = "start"
        self.fade_alpha = 255
        self.fade_speed = 400
        self.is_fading_in = True
        self.is_fading_out = False
        self.next_scene = None

    def update(self, dt):
        if self.is_fading_in:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.is_fading_in = False

        if self.is_fading_out:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.is_fading_out = False
                self.switch_scene()

    def draw_fade(self):
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface(self.screen.get_size())
            fade_surface.set_alpha(int(self.fade_alpha))
            fade_surface.fill((0, 0, 0))
            self.screen.blit(fade_surface, (0, 0))

    def start_transition(self, next_scene):
        self.is_fading_out = True
        self.next_scene = next_scene

    def switch_scene(self):
        self.current_scene = self.next_scene
        self.is_fading_in = True