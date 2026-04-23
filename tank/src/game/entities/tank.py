from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import (
    ENEMY_COLOR,
    ENEMY_HP,
    ENEMY_SPEED,
    FIRE_COOLDOWN_ENEMY,
    FIRE_COOLDOWN_PLAYER,
    HIT_FLASH_TIME,
    MAX_ENEMY_BULLETS,
    MAX_PLAYER_BULLETS,
    PLAYER_COLOR,
    PLAYER_MAX_HP,
    PLAYER_SPEED,
    clamp,
)


def _axis_to_dir(dx: int, dy: int) -> pygame.Vector2:
    v = pygame.Vector2(dx, dy)
    if v.length_squared() > 0:
        v = v.normalize()
    return v


@dataclass
class Tank:
    kind: str  # "player" or "enemy"
    rect: pygame.Rect
    facing: pygame.Vector2
    hp: int
    speed: float
    fire_cd: float
    max_bullets: int

    fire_timer: float = 0.0
    hit_flash: float = 0.0
    alive: bool = True

    @staticmethod
    def player(x: int, y: int) -> "Tank":
        return Tank(
            kind="player",
            rect=pygame.Rect(x, y, 28, 28),
            facing=pygame.Vector2(0, -1),
            hp=PLAYER_MAX_HP,
            speed=PLAYER_SPEED,
            fire_cd=FIRE_COOLDOWN_PLAYER,
            max_bullets=MAX_PLAYER_BULLETS,
        )

    @staticmethod
    def enemy(x: int, y: int) -> "Tank":
        return Tank(
            kind="enemy",
            rect=pygame.Rect(x, y, 28, 28),
            facing=pygame.Vector2(0, 1),
            hp=ENEMY_HP,
            speed=ENEMY_SPEED,
            fire_cd=FIRE_COOLDOWN_ENEMY,
            max_bullets=MAX_ENEMY_BULLETS,
        )

    def color(self) -> tuple[int, int, int]:
        if self.hit_flash > 0:
            return (255, 255, 255)
        return PLAYER_COLOR if self.kind == "player" else ENEMY_COLOR

    def update_timers(self, dt: float) -> None:
        self.fire_timer = clamp(self.fire_timer - dt, 0.0, 999.0)
        self.hit_flash = clamp(self.hit_flash - dt, 0.0, 999.0)

    def take_hit(self, dmg: int = 1) -> None:
        if not self.alive:
            return
        self.hp -= dmg
        self.hit_flash = HIT_FLASH_TIME
        if self.hp <= 0:
            self.alive = False

    def set_facing_from_move(self, move: pygame.Vector2) -> None:
        if move.length_squared() == 0:
            return
        self.facing = pygame.Vector2(move.x, move.y)
        if self.facing.length_squared() > 0:
            self.facing = self.facing.normalize()

    def desired_move_from_keys(self, keys: pygame.key.ScancodeWrapper) -> pygame.Vector2:
        dx = (1 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0) - (
            1 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 0
        )
        dy = (1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0) - (
            1 if keys[pygame.K_w] or keys[pygame.K_UP] else 0
        )
        return _axis_to_dir(dx, dy)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color(), self.rect)
        # 炮口方向线
        cx, cy = self.rect.center
        end = (int(cx + self.facing.x * 18), int(cy + self.facing.y * 18))
        pygame.draw.line(screen, (20, 20, 20), (cx, cy), end, 3)

