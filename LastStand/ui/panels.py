import pygame

from config import (
    BG_PANEL,
    BG_CARD,
    BG_PANEL_DARK,
    BUTTON_BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    TEXT_WARNING,
    TEXT_SUCCESS,
    TEXT_DANGER,
    PADDING_MEDIUM,
)


def draw_side_panel(
    screen: pygame.Surface,
    rect: pygame.Rect,
    selected_tower_name: str,
    status_text: str,
    font_small: pygame.font.Font,
    font_medium: pygame.font.Font,
    selected_tower=None,
) -> None:
    pygame.draw.rect(screen, BG_PANEL, rect)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2)

    x = rect.x + PADDING_MEDIUM
    y = rect.y + PADDING_MEDIUM
    card_width = rect.width - (PADDING_MEDIUM * 2)
    gap = 10

    # Card 1: Build menu
    card1_h = 112
    card1 = pygame.Rect(x, y, card_width, card1_h)
    draw_card(screen, card1)
    draw_text(screen, "TOWER FABRICATION", font_medium, TEXT_MAIN, card1.x + 12, card1.y + 10)

    draw_hotline(screen, font_small, card1.x + 12, card1.y + 42, "[1] Archer", "Fast single target", TEXT_WARNING)
    draw_hotline(screen, font_small, card1.x + 12, card1.y + 64, "[2] Mage", "Splash magic burst", TEXT_SUCCESS)
    draw_hotline(screen, font_small, card1.x + 12, card1.y + 86, "[3] Ballista", "Piercing strike", (255, 190, 120))

    # Card 2: Selected tower
    y += card1_h + gap
    card2_h = 154
    card2 = pygame.Rect(x, y, card_width, card2_h)
    draw_card(screen, card2)
    draw_text(screen, "SELECTED UNIT", font_medium, TEXT_MAIN, card2.x + 12, card2.y + 10)

    if selected_tower:
        draw_text(screen, f"Type: {selected_tower.name}", font_small, TEXT_WARNING, card2.x + 12, card2.y + 40)
        draw_text(screen, f"Level: {selected_tower.level}/{selected_tower.max_level}", font_small, TEXT_MUTED, card2.x + 12, card2.y + 62)
        draw_text(screen, f"Damage: {selected_tower.damage}", font_small, TEXT_MUTED, card2.x + 12, card2.y + 84)
        draw_text(screen, f"Range: {selected_tower.attack_range}", font_small, TEXT_MUTED, card2.x + 170, card2.y + 84)
        draw_text(screen, f"Rate: {selected_tower.fire_rate:.2f}", font_small, TEXT_MUTED, card2.x + 12, card2.y + 106)
        draw_text(screen, f"Sell: {selected_tower.sell_value}", font_small, TEXT_DANGER, card2.x + 170, card2.y + 106)

        if selected_tower.can_upgrade():
            upgrade_text = f"Upgrade Cost: {selected_tower.upgrade_cost}"
            upgrade_color = TEXT_SUCCESS
        else:
            upgrade_text = "Upgrade Cost: MAX"
            upgrade_color = TEXT_WARNING

        draw_text(screen, upgrade_text, font_small, upgrade_color, card2.x + 12, card2.y + 128)
    else:
        draw_text(screen, f"Build Mode: {selected_tower_name}", font_small, TEXT_WARNING, card2.x + 12, card2.y + 50)
        draw_text(screen, "Click tower to inspect.", font_small, TEXT_MUTED, card2.x + 12, card2.y + 78)
        draw_text(screen, "Right click empty area to deselect.", font_small, TEXT_MUTED, card2.x + 12, card2.y + 100)

    # Card 3: Actions
    y += card2_h + gap
    card3_h = 84
    card3 = pygame.Rect(x, y, card_width, card3_h)
    draw_card(screen, card3)
    draw_text(screen, "UNIT ACTIONS", font_medium, TEXT_MAIN, card3.x + 12, card3.y + 10)
    draw_text(screen, "[U] Upgrade", font_small, TEXT_SUCCESS, card3.x + 12, card3.y + 44)
    draw_text(screen, "[S] Sell", font_small, TEXT_DANGER, card3.x + 170, card3.y + 44)

    # Card 4: Status console
    y += card3_h + gap
    card4_h = rect.bottom - y - 12
    if card4_h < 90:
        card4_h = 90

    card4 = pygame.Rect(x, y, card_width, card4_h)
    pygame.draw.rect(screen, BG_PANEL_DARK, card4, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER, card4, 2, border_radius=8)
    draw_text(screen, "TACTICAL STATUS", font_medium, TEXT_MAIN, card4.x + 12, card4.y + 10)
    draw_multiline_text(
        screen=screen,
        text=status_text,
        font=font_small,
        color=TEXT_MUTED,
        x=card4.x + 12,
        y=card4.y + 42,
        max_width=card4.width - 24,
        line_height=20,
        max_lines=4,
    )


def draw_card(screen: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(screen, BG_CARD, rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2, border_radius=8)


def draw_text(screen: pygame.Surface, text: str, font: pygame.font.Font, color, x: int, y: int) -> None:
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_hotline(screen, font, x, y, left_text, right_text, left_color):
    left_surface = font.render(left_text, True, left_color)
    right_surface = font.render(f" - {right_text}", True, TEXT_MUTED)
    screen.blit(left_surface, (x, y))
    screen.blit(right_surface, (x + 92, y))


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