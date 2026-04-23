from __future__ import annotations

import math

import pygame


def load_font(size: int, name: str | None = None) -> pygame.font.Font:
    return pygame.font.Font(name, size)


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    *,
    color: tuple[int, int, int] = (235, 235, 235),
    font: pygame.font.Font,
    anchor: str = "topleft",
) -> None:
    img = font.render(text, True, color)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(img, rect)


def angle_to_dir(angle_rad: float) -> pygame.Vector2:
    return pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))

