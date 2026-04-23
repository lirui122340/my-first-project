from __future__ import annotations

import json
from dataclasses import dataclass

import pygame

from game.config import TILE_SIZE
from game.entities.tank import Tank
from game.entities.wall import Wall


@dataclass
class LevelData:
    player_spawn: tuple[int, int]
    enemy_spawns: list[tuple[int, int]]
    walls: list[Wall]


def _to_px(tile_xy: tuple[int, int]) -> tuple[int, int]:
    x, y = tile_xy
    return x * TILE_SIZE, y * TILE_SIZE


def load_level(path: str) -> LevelData:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    player_spawn = tuple(raw["player_spawn"])
    enemy_spawns = [tuple(x) for x in raw.get("enemy_spawns", [])]

    walls: list[Wall] = []
    for w in raw.get("walls", []):
        x, y = _to_px(tuple(w["pos"]))
        size = w.get("size", [1, 1])
        ww, hh = size[0] * TILE_SIZE, size[1] * TILE_SIZE
        rect = pygame.Rect(x, y, ww, hh)
        walls.append(Wall(rect=rect, breakable=bool(w.get("breakable", False)), hp=int(w.get("hp", 0))))

    return LevelData(player_spawn=player_spawn, enemy_spawns=enemy_spawns, walls=walls)


def spawn_player(level: LevelData) -> Tank:
    x, y = _to_px(level.player_spawn)
    return Tank.player(x + 2, y + 2)


def spawn_enemies(level: LevelData) -> list[Tank]:
    enemies: list[Tank] = []
    for sp in level.enemy_spawns:
        x, y = _to_px(sp)
        enemies.append(Tank.enemy(x + 2, y + 2))
    return enemies

