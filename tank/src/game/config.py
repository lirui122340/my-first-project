from __future__ import annotations

import pygame

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Tank Battle"
FPS = 60

BG_COLOR = (20, 20, 24)

TILE_SIZE = 32

PLAYER_COLOR = (80, 200, 120)
ENEMY_COLOR = (220, 80, 80)
WALL_COLOR = (110, 110, 120)
BULLET_COLOR = (240, 240, 100)

PLAYER_SPEED = 200.0
ENEMY_SPEED = 140.0

BULLET_SPEED = 420.0
BULLET_LIFETIME = 2.2

FIRE_COOLDOWN_PLAYER = 0.25
FIRE_COOLDOWN_ENEMY = 0.7

PLAYER_MAX_HP = 5
ENEMY_HP = 2

MAX_PLAYER_BULLETS = 3
MAX_ENEMY_BULLETS = 2

HIT_FLASH_TIME = 0.10

FONT_NAME = None  # default
UI_FONT_SIZE = 20
TITLE_FONT_SIZE = 48


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def vec2(x: float, y: float) -> pygame.Vector2:
    return pygame.Vector2(x, y)

