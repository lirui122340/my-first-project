from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Scene:
    manager: object

    def handle_event(self, event: pygame.event.Event) -> None:  # pragma: no cover
        pass

    def update(self, dt: float) -> None:  # pragma: no cover
        pass

    def render(self, screen: pygame.Surface) -> None:  # pragma: no cover
        pass

