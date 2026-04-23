from __future__ import annotations

import pygame

from game.config import BG_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE_FONT_SIZE, UI_FONT_SIZE
from game.scenes.base import Scene
from game.utils import draw_text, load_font


class GameOverScene(Scene):
    def __init__(self, manager: object, *, won: bool, stats: dict | None = None) -> None:
        super().__init__(manager)
        self.won = won
        self.stats = stats or {}
        self.title_font = load_font(TITLE_FONT_SIZE)
        self.ui_font = load_font(UI_FONT_SIZE)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.manager.switch("gameplay", {"level_path": "levels/level_01.json"})
            elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                self.manager.switch("menu")

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)
        title = "胜利！" if self.won else "失败"
        draw_text(
            screen,
            title,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90),
            font=self.title_font,
            anchor="center",
            color=(90, 220, 120) if self.won else (240, 90, 90),
        )
        kills = self.stats.get("kills", 0)
        time_s = self.stats.get("time_s", 0.0)
        draw_text(
            screen,
            f"击杀：{kills}    用时：{time_s:.1f}s",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10),
            font=self.ui_font,
            anchor="center",
        )
        draw_text(
            screen,
            "R 重新开始  |  M/Esc 回主菜单",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40),
            font=self.ui_font,
            anchor="center",
        )

