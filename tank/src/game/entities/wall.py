from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import WALL_COLOR


@dataclass
class Wall:
    rect: pygame.Rect
    breakable: bool = False
    hp: int = 0

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, WALL_COLOR, self.rect)

