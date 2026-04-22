import math
import random
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BG_MAIN,
    BG_PANEL,
    BG_CARD,
    BG_PANEL_DARK,
    BUTTON_BG,
    BUTTON_BG_HOVER,
    BUTTON_BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    GLOW_CYAN,
    GLOW_BLUE,
    GLOW_PURPLE,
)


class StartScreen:
    def __init__(self, screen):
        self.screen = screen

        self.font_title = pygame.font.SysFont("consolas", 64, bold=True)
        self.font_subtitle = pygame.font.SysFont("consolas", 22)
        self.font_button = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 16)

        panel_width = 560
        panel_height = 470
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = 90

        self.main_panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        btn_w = 340
        btn_h = 62
        btn_x = panel_x + (panel_width - btn_w) // 2

        self.buttons = {
            "start": pygame.Rect(btn_x, panel_y + 220, btn_w, btn_h),
            "stats": pygame.Rect(btn_x, panel_y + 300, btn_w, btn_h),
            "exit": pygame.Rect(btn_x, panel_y + 380, btn_w, btn_h),
        }

        self.time = 0.0

        random.seed(42)
        self.stars = []
        for _ in range(80):
            self.stars.append({
                "x": random.randint(0, WINDOW_WIDTH),
                "y": random.randint(0, WINDOW_HEIGHT),
                "r": random.randint(1, 2),
                "phase": random.random() * math.pi * 2,
                "speed": 1.5 + random.random() * 2.0,
            })

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, music=None):
        self.screen.fill(BG_MAIN)

        self.draw_background_fx()
        self.draw_main_panel()
        self.draw_title_block()
        self.draw_buttons()
        self.draw_footer_hint()
        if music is not None:
            self.draw_mute_button(music)

    def draw_background_fx(self):
        self.draw_gradient_vignette()
        self.draw_starfield()
        self.draw_tech_grid()
        self.draw_orb_glows()

    def draw_gradient_vignette(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        # soft top glow
        pygame.draw.rect(overlay, (10, 20, 50, 70), (0, 0, WINDOW_WIDTH, 180))
        # soft center aura
        pygame.draw.circle(
            overlay,
            (0, 180, 255, 20),
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50),
            260,
        )
        # side glows
        pygame.draw.circle(
            overlay,
            (140, 80, 255, 14),
            (200, 160),
            160,
        )
        pygame.draw.circle(
            overlay,
            (60, 220, 255, 16),
            (WINDOW_WIDTH - 180, 220),
            190,
        )

        self.screen.blit(overlay, (0, 0))

    def draw_starfield(self):
        for star in self.stars:
            alpha = 120 + int(100 * (0.5 + 0.5 * math.sin(self.time * star["speed"] + star["phase"])))
            surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surface, (180, 220, 255, alpha), (4, 4), star["r"])
            self.screen.blit(surface, (star["x"], star["y"]))

    def draw_tech_grid(self):
        grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        step = 40
        line_color = (80, 120, 180, 18)

        for x in range(0, WINDOW_WIDTH, step):
            pygame.draw.line(grid_surface, line_color, (x, 0), (x, WINDOW_HEIGHT), 1)

        for y in range(0, WINDOW_HEIGHT, step):
            pygame.draw.line(grid_surface, line_color, (0, y), (WINDOW_WIDTH, y), 1)

        self.screen.blit(grid_surface, (0, 0))

    def draw_orb_glows(self):
        orb_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        pulse1 = 110 + int(20 * math.sin(self.time * 1.8))
        pulse2 = 90 + int(25 * math.sin(self.time * 2.2 + 1.2))

        pygame.draw.circle(
            orb_surface,
            (0, 200, 255, 22),
            (WINDOW_WIDTH // 2, 120),
            pulse1,
        )
        pygame.draw.circle(
            orb_surface,
            (160, 80, 255, 16),
            (WINDOW_WIDTH // 2 + 220, 180),
            pulse2,
        )

        self.screen.blit(orb_surface, (0, 0))

    def draw_main_panel(self):
        panel = self.main_panel

        # outer glow
        glow = pygame.Surface((panel.width + 40, panel.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (80, 180, 255, 20),
            glow.get_rect().inflate(-10, -10),
            border_radius=24,
        )
        self.screen.blit(glow, (panel.x - 20, panel.y - 20))

        # main panel
        pygame.draw.rect(self.screen, BG_PANEL_DARK, panel, border_radius=18)
        pygame.draw.rect(self.screen, BUTTON_BORDER, panel, 2, border_radius=18)

        inner = panel.inflate(-18, -18)
        pygame.draw.rect(self.screen, BG_PANEL, inner, border_radius=16)

        # decorative corner cuts
        self.draw_panel_corners(panel)

        # header stripe
        stripe_rect = pygame.Rect(panel.x + 18, panel.y + 18, panel.width - 36, 10)
        pygame.draw.rect(self.screen, (40, 80, 150), stripe_rect, border_radius=6)

        pulse_width = 120 + int(50 * math.sin(self.time * 2.4))
        pulse_rect = pygame.Rect(panel.x + 18, panel.y + 18, pulse_width, 10)
        pygame.draw.rect(self.screen, GLOW_CYAN, pulse_rect, border_radius=6)

    def draw_panel_corners(self, panel: pygame.Rect):
        color = GLOW_BLUE
        t = 3
        cut = 24

        # top-left
        pygame.draw.line(self.screen, color, (panel.x + 14, panel.y + cut), (panel.x + 14, panel.y + 14), t)
        pygame.draw.line(self.screen, color, (panel.x + 14, panel.y + 14), (panel.x + cut, panel.y + 14), t)

        # top-right
        pygame.draw.line(self.screen, color, (panel.right - 14, panel.y + cut), (panel.right - 14, panel.y + 14), t)
        pygame.draw.line(self.screen, color, (panel.right - 14, panel.y + 14), (panel.right - cut, panel.y + 14), t)

        # bottom-left
        pygame.draw.line(self.screen, color, (panel.x + 14, panel.bottom - cut), (panel.x + 14, panel.bottom - 14), t)
        pygame.draw.line(self.screen, color, (panel.x + 14, panel.bottom - 14), (panel.x + cut, panel.bottom - 14), t)

        # bottom-right
        pygame.draw.line(self.screen, color, (panel.right - 14, panel.bottom - cut), (panel.right - 14, panel.bottom - 14), t)
        pygame.draw.line(self.screen, color, (panel.right - 14, panel.bottom - 14), (panel.right - cut, panel.bottom - 14), t)

    def draw_title_block(self):
        panel = self.main_panel
        center_x = panel.centerx

        glow_surface = self.font_title.render("LAST STAND", True, GLOW_BLUE)
        title_surface = self.font_title.render("LAST STAND", True, GLOW_CYAN)
        subtitle_surface = self.font_subtitle.render("SPACE DUNGEON DEFENSE PROTOCOL", True, TEXT_MUTED)
        caption_surface = self.font_small.render("TACTICAL DEFENSE INTERFACE // v1.0", True, (120, 155, 210))

        glow_rect = glow_surface.get_rect(center=(center_x, panel.y + 88))
        title_rect = title_surface.get_rect(center=(center_x, panel.y + 84))
        subtitle_rect = subtitle_surface.get_rect(center=(center_x, panel.y + 142))
        caption_rect = caption_surface.get_rect(center=(center_x, panel.y + 172))

        # fake bloom
        self.screen.blit(glow_surface, (glow_rect.x - 2, glow_rect.y))
        self.screen.blit(glow_surface, (glow_rect.x + 2, glow_rect.y))
        self.screen.blit(glow_surface, (glow_rect.x, glow_rect.y - 2))
        self.screen.blit(glow_surface, (glow_rect.x, glow_rect.y + 2))

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)
        self.screen.blit(caption_surface, caption_rect)

        # title underline
        line_y = panel.y + 194
        pygame.draw.line(self.screen, (50, 90, 150), (panel.x + 80, line_y), (panel.right - 80, line_y), 2)
        pygame.draw.line(self.screen, GLOW_PURPLE, (panel.centerx - 80, line_y), (panel.centerx + 80, line_y), 2)

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()

        self.draw_button(self.buttons["start"], "START MISSION", mouse_pos, accent=GLOW_CYAN)
        self.draw_button(self.buttons["stats"], "VIEW STATISTICS", mouse_pos, accent=GLOW_PURPLE)
        self.draw_button(self.buttons["exit"], "EXIT SYSTEM", mouse_pos, accent=(255, 120, 120))

    def draw_button(self, rect: pygame.Rect, label: str, mouse_pos, accent):
        hovered = rect.collidepoint(mouse_pos)

        bg = BUTTON_BG_HOVER if hovered else BUTTON_BG
        border = accent if hovered else BUTTON_BORDER

        # glow
        if hovered:
            glow = pygame.Surface((rect.width + 30, rect.height + 30), pygame.SRCALPHA)
            pygame.draw.rect(glow, (accent[0], accent[1], accent[2], 28), glow.get_rect().inflate(-8, -8), border_radius=18)
            self.screen.blit(glow, (rect.x - 15, rect.y - 15))

        pygame.draw.rect(self.screen, bg, rect, border_radius=14)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=14)

        inner = rect.inflate(-10, -10)
        pygame.draw.rect(self.screen, BG_CARD, inner, border_radius=12)

        # accent line
        pygame.draw.rect(self.screen, accent, (rect.x + 14, rect.y + 10, 6, rect.height - 20), border_radius=4)

        text_color = TEXT_MAIN if hovered else (210, 225, 245)
        text_surface = self.font_button.render(label, True, text_color)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def draw_footer_hint(self):
        hint = self.font_small.render("CLICK A COMMAND TO CONTINUE  |  [M] MUTE", True, (110, 145, 205))
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 42)))

    def draw_mute_button(self, music):
        label = "🔇 MUTED" if music.is_muted else "🔊 MUSIC"
        color = (140, 100, 100) if music.is_muted else (80, 180, 120)
        btn_surf = self.font_small.render(label, True, color)
        x = WINDOW_WIDTH - btn_surf.get_width() - 18
        y = WINDOW_HEIGHT - btn_surf.get_height() - 16
        self._mute_btn_rect = pygame.Rect(x - 6, y - 4, btn_surf.get_width() + 12, btn_surf.get_height() + 8)
        pygame.draw.rect(self.screen, (18, 24, 44), self._mute_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, color, self._mute_btn_rect, 1, border_radius=6)
        self.screen.blit(btn_surf, (x, y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    return name
        return None