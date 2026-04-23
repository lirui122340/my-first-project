from __future__ import annotations

import pygame

from game.config import BG_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE_FONT_SIZE, UI_FONT_SIZE
from game.scenes.base import Scene
from game.utils import draw_text, load_font


class MenuScene(Scene):
    def __init__(self, manager: object) -> None:
        super().__init__(manager)
        self.title_font = load_font(TITLE_FONT_SIZE)
        self.ui_font = load_font(UI_FONT_SIZE)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.manager.switch("gameplay", {"level_path": "levels/level_01.json"})
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)
        draw_text(
            screen,
            "TANK BATTLE",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80),
            font=self.title_font,
            anchor="center",
        )
        draw_text(
            screen,
            "按 Enter/Space 开始  |  Esc 退出",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10),
            font=self.ui_font,
            anchor="center",
        )

