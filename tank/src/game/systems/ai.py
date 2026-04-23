from __future__ import annotations

import random

import pygame

from game.config import clamp


class SimpleEnemyAI:
    """非常轻量的 AI：
    - 定时随机换方向巡逻
    - 距离玩家较近则朝玩家移动
    """

    def __init__(self) -> None:
        self._timer = 0.0
        self._dir = pygame.Vector2(0, 1)

    def update(self, dt: float, enemy_center: pygame.Vector2, player_center: pygame.Vector2) -> pygame.Vector2:
        self._timer = clamp(self._timer - dt, 0.0, 999.0)
        to_player = player_center - enemy_center
        dist2 = to_player.length_squared()

        if dist2 < (260.0 * 260.0) and dist2 > 0:
            return to_player.normalize()

        if self._timer <= 0.0:
            self._timer = random.uniform(0.6, 1.4)
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self._dir = pygame.Vector2(dx, dy)
        return self._dir


def enemy_should_fire(enemy_center: pygame.Vector2, player_center: pygame.Vector2, facing: pygame.Vector2) -> bool:
    to_player = player_center - enemy_center
    if to_player.length_squared() == 0:
        return False
    dist2 = to_player.length_squared()
    if dist2 > (420.0 * 420.0):
        return False
    dir_to_player = to_player.normalize()
    return dir_to_player.dot(facing) > 0.85

