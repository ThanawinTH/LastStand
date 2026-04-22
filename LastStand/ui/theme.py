import pygame

from config import BG_PANEL, BG_CARD, BUTTON_BORDER, TEXT_MAIN


def draw_panel(screen: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(screen, BG_PANEL, rect)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2)


def draw_card(screen: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(screen, BG_CARD, rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2, border_radius=8)


def draw_label(screen: pygame.Surface, text: str, font: pygame.font.Font, color, x: int, y: int) -> None:
    surface = font.render(text, True, color if color else TEXT_MAIN)
    screen.blit(surface, (x, y))