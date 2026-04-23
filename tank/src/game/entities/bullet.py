from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import BULLET_COLOR, BULLET_LIFETIME


@dataclass
class Bullet:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: int
    owner: str  # "player" or "enemy"
    ttl: float = BULLET_LIFETIME
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False
            return
        self.pos += self.vel * dt

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pos.x - self.radius),
            int(self.pos.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.pos.x), int(self.pos.y)), self.radius)

