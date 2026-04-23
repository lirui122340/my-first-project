from __future__ import annotations

import os

import pygame

from game.config import (
    BG_COLOR,
    BULLET_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_FONT_SIZE,
)
from game.entities.bullet import Bullet
from game.entities.tank import Tank
from game.entities.wall import Wall
from game.scenes.base import Scene
from game.systems.physics import bullet_hits_rect, move_rect_with_collisions
from game.systems.spawn import load_level, spawn_player, spawn_player2
from game.utils import draw_text, load_font


class GameplayScene(Scene):
    def __init__(self, manager: object, *, level_path: str) -> None:
        super().__init__(manager)
        self.ui_font = load_font(UI_FONT_SIZE)

        self.paused = False
        self.kills = 0
        self.time_s = 0.0

        # 允许从 src/ 启动时也能找到 levels/
        if not os.path.exists(level_path):
            level_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", level_path)
            level_path = os.path.normpath(level_path)

        self.level = load_level(level_path)
        # 双人对战：两个玩家
        self.p1 = spawn_player(self.level)
        self.p2 = spawn_player2(self.level)

        self.walls: list[Wall] = list(self.level.walls)
        self.bullets: list[Bullet] = []

        self._solid_rects = self._build_solids()

    def _build_solids(self) -> list[pygame.Rect]:
        solids = [w.rect for w in self.walls]
        # 屏幕边界（用很厚的墙）
        solids.append(pygame.Rect(-9999, -9999, 9999, SCREEN_HEIGHT + 19998))
        solids.append(pygame.Rect(SCREEN_WIDTH, -9999, 9999, SCREEN_HEIGHT + 19998))
        solids.append(pygame.Rect(-9999, -9999, SCREEN_WIDTH + 19998, 9999))
        solids.append(pygame.Rect(-9999, SCREEN_HEIGHT, SCREEN_WIDTH + 19998, 9999))
        return solids

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if not self.paused:
                if event.key == pygame.K_SPACE:
                    self._try_fire(self.p1)
                elif event.key == pygame.K_RCTRL:
                    self._try_fire(self.p2)

    def _try_fire(self, tank: Tank) -> None:
        if tank.fire_timer > 0 or not tank.alive:
            return
        owned = [b for b in self.bullets if b.alive and b.owner == tank.kind]
        if len(owned) >= tank.max_bullets:
            return

        cx, cy = tank.rect.center
        dirv = tank.facing
        if dirv.length_squared() == 0:
            dirv = pygame.Vector2(0, -1)
        vel = dirv.normalize() * BULLET_SPEED
        self.bullets.append(Bullet(pos=pygame.Vector2(cx, cy), vel=vel, radius=4, owner=tank.kind))
        tank.fire_timer = tank.fire_cd

    def update(self, dt: float) -> None:
        if self.paused:
            return

        self.time_s += dt
        self.p1.update_timers(dt)
        self.p2.update_timers(dt)

        self._update_players(dt)
        self._update_bullets(dt)
        self._resolve_end_conditions()

    def _update_players(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        # P1：WASD
        move1 = self.p1.desired_move_from_keys(keys, scheme="wasd")
        self.p1.set_facing_from_move(move1)
        delta1 = move1 * self.p1.speed * dt
        self.p1.rect = move_rect_with_collisions(self.p1.rect, delta1, self._solid_rects)

        # P2：方向键
        move2 = self.p2.desired_move_from_keys(keys, scheme="arrows")
        self.p2.set_facing_from_move(move2)
        delta2 = move2 * self.p2.speed * dt
        self.p2.rect = move_rect_with_collisions(self.p2.rect, delta2, self._solid_rects)

    def _update_bullets(self, dt: float) -> None:
        for b in self.bullets:
            b.update(dt)
            if not b.alive:
                continue

            br = b.rect()
            # 子弹 vs 墙
            hit_wall = False
            for w in self.walls:
                if br.colliderect(w.rect):
                    hit_wall = True
                    if w.breakable:
                        w.hp -= 1
                    b.alive = False
                    break
            if hit_wall:
                continue

            # 子弹 vs 玩家（PVP）
            if b.owner != "p1" and self.p1.alive and bullet_hits_rect(br, self.p1.rect):
                self.p1.take_hit(1)
                b.alive = False
                continue
            if b.owner != "p2" and self.p2.alive and bullet_hits_rect(br, self.p2.rect):
                self.p2.take_hit(1)
                b.alive = False
                continue

        # 清理可破坏墙
        before = len(self.walls)
        self.walls = [w for w in self.walls if not (w.breakable and w.hp <= 0)]
        if len(self.walls) != before:
            self._solid_rects = self._build_solids()

        # 清理死亡子弹
        self.bullets = [b for b in self.bullets if b.alive]

    def _resolve_end_conditions(self) -> None:
        if not self.p1.alive and not self.p2.alive:
            self.manager.switch("gameover", {"won": False, "stats": {"kills": 0, "time_s": self.time_s}})
            return
        if not self.p1.alive:
            self.manager.switch("gameover", {"won": False, "stats": {"kills": 0, "time_s": self.time_s}})
            return
        if not self.p2.alive:
            self.manager.switch("gameover", {"won": True, "stats": {"kills": 0, "time_s": self.time_s}})
            return

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)
        for w in self.walls:
            w.draw(screen)
        for b in self.bullets:
            b.draw(screen)
        if self.p1.alive:
            self.p1.draw(screen)
        if self.p2.alive:
            self.p2.draw(screen)

        draw_text(screen, f"P1 HP: {self.p1.hp}", (12, 10), font=self.ui_font)
        draw_text(screen, f"P2 HP: {self.p2.hp}", (SCREEN_WIDTH - 12, 10), font=self.ui_font, anchor="topright")

        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "已暂停", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20), font=self.ui_font, anchor="center")
            draw_text(
                screen,
                "Esc 继续",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 14),
                font=self.ui_font,
                anchor="center",
            )

