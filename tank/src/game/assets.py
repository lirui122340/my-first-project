from __future__ import annotations

import pygame


class Assets:
    def __init__(self) -> None:
        self._initialized = False

    def ensure(self) -> None:
        if self._initialized:
            return
        # 占位：后续可以在这里加载图片/音效
        self._initialized = True


assets = Assets()

