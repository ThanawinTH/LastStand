import pygame

from config import (
    WINDOW_WIDTH,
    HEADER_HEIGHT,
    BG_PANEL,
    BG_CARD,
    BUTTON_BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    TEXT_WARNING,
    TEXT_SUCCESS,
    TEXT_DANGER,
)


def draw_header(
    screen: pygame.Surface,
    player,
    current_wave: int,
    title: str,
    subtitle: str,
    font_small: pygame.font.Font,
    font_medium: pygame.font.Font,
    font_large: pygame.font.Font,
    wave_state: str = "",
) -> None:
    rect = pygame.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
    pygame.draw.rect(screen, BG_PANEL, rect)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2)

    # ── Row 1 (y 6-56): title left, info cards right ─────────────────────
    title_surface = font_large.render(title, True, TEXT_MAIN)
    screen.blit(title_surface, (18, 8))

    card_h   = 46
    card_w   = 108
    gap      = 8
    start_x  = 310
    info_y   = 6

    draw_info_card(screen, pygame.Rect(start_x + 0 * (card_w + gap), info_y, card_w, card_h), "GOLD",  str(player.gold),  font_small, font_medium, TEXT_WARNING)
    draw_info_card(screen, pygame.Rect(start_x + 1 * (card_w + gap), info_y, card_w, card_h), "LIVES", str(player.lives), font_small, font_medium, TEXT_DANGER if player.lives <= 5 else TEXT_MAIN)
    draw_info_card(screen, pygame.Rect(start_x + 2 * (card_w + gap), info_y, card_w, card_h), "WAVE",  str(current_wave), font_small, font_medium, TEXT_MAIN)

    state_text = wave_state.upper() if wave_state else "UNKNOWN"
    if wave_state == "preparing":
        state_color = TEXT_WARNING
    elif wave_state == "in_wave":
        state_color = TEXT_SUCCESS
    elif wave_state in ("victory", "game_over"):
        state_color = TEXT_SUCCESS if wave_state == "victory" else TEXT_DANGER
    else:
        state_color = TEXT_MUTED

    draw_info_card(
        screen,
        pygame.Rect(start_x + 3 * (card_w + gap), info_y, 138, card_h),
        "STATE", state_text,
        font_small, font_medium, state_color,
    )

    # ── Divider ───────────────────────────────────────────────────────────
    div_y = 58
    pygame.draw.line(screen, BUTTON_BORDER, (8, div_y), (WINDOW_WIDTH - 8, div_y), 1)

    # ── Row 2 (y 62-110): subtitle left, empty right (buttons drawn by Game) ─
    subtitle_surface = font_small.render(subtitle, True, TEXT_MUTED)
    screen.blit(subtitle_surface, (18, 66))


def draw_footer(
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font_small: pygame.font.Font,
    font_medium: pygame.font.Font,
) -> None:
    _ = font_medium

    pygame.draw.rect(screen, BG_PANEL, rect)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2)

    console_rect = pygame.Rect(rect.x + 14, rect.y + 10, rect.width - 28, rect.height - 20)
    pygame.draw.rect(screen, BG_CARD, console_rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER, console_rect, 2, border_radius=8)

    label = font_small.render("SYSTEM CONSOLE", True, TEXT_MUTED)
    screen.blit(label, (console_rect.x + 12, console_rect.y + 6))

    draw_multiline_text(
        screen=screen,
        text=text,
        font=font_small,
        color=TEXT_MAIN,
        x=console_rect.x + 12,
        y=console_rect.y + 30,
        max_width=console_rect.width - 24,
        line_height=20,
        max_lines=2,
    )


def draw_info_card(
    screen: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    value: str,
    font_small: pygame.font.Font,
    font_medium: pygame.font.Font,
    value_color,
) -> None:
    pygame.draw.rect(screen, BG_CARD, rect, border_radius=10)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2, border_radius=10)

    label_surface = font_small.render(label, True, TEXT_MUTED)
    value_surface = font_medium.render(value, True, value_color)

    screen.blit(label_surface, (rect.x + 10, rect.y + 6))
    screen.blit(value_surface, (rect.x + 10, rect.y + 24))


def draw_multiline_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color,
    x: int,
    y: int,
    max_width: int,
    line_height: int,
    max_lines: int | None = None,
) -> None:
    words = text.split()
    current_line = ""
    lines_drawn = 0

    for word in words:
        test_line = f"{current_line} {word}".strip()
        surface = font.render(test_line, True, color)

        if surface.get_width() <= max_width:
            current_line = test_line
        else:
            if current_line:
                if max_lines is not None and lines_drawn >= max_lines:
                    return
                line_surface = font.render(current_line, True, color)
                screen.blit(line_surface, (x, y))
                y += line_height
                lines_drawn += 1
            current_line = word

    if current_line:
        if max_lines is not None and lines_drawn >= max_lines:
            return
        line_surface = font.render(current_line, True, color)
        screen.blit(line_surface, (x, y))