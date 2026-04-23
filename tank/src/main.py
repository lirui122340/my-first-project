from __future__ import annotations

import sys

import pygame

from game.config import (
    BG_COLOR,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SCREEN_WIDTH,
)
from game.scenes.gameover import GameOverScene
from game.scenes.gameplay import GameplayScene
from game.scenes.menu import MenuScene


class SceneManager:
    def __init__(self) -> None:
        self._scene = MenuScene(self)

    def switch(self, scene_name: str, payload: dict | None = None) -> None:
        payload = payload or {}
        if scene_name == "menu":
            self._scene = MenuScene(self)
        elif scene_name == "gameplay":
            self._scene = GameplayScene(self, **payload)
        elif scene_name == "gameover":
            self._scene = GameOverScene(self, **payload)
        else:
            raise ValueError(f"Unknown scene: {scene_name}")

    def handle_event(self, event: pygame.event.Event) -> None:
        self._scene.handle_event(event)

    def update(self, dt: float) -> None:
        self._scene.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        self._scene.render(screen)


def main() -> int:
    pygame.init()
    pygame.display.set_caption(SCREEN_TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    manager = SceneManager()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            manager.handle_event(event)

        manager.update(dt)
        screen.fill(BG_COLOR)
        manager.render(screen)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

