from __future__ import annotations

import os
from dataclasses import dataclass

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
from game.systems.ai import SimpleEnemyAI, enemy_should_fire
from game.systems.physics import bullet_hits_rect, move_rect_with_collisions
from game.systems.spawn import load_level, spawn_enemies, spawn_player
from game.utils import draw_text, load_font


@dataclass
class EnemyController:
    ai: SimpleEnemyAI


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
        self.player = spawn_player(self.level)
        self.enemies = spawn_enemies(self.level)
        self.enemy_ctrl = {id(e): EnemyController(ai=SimpleEnemyAI()) for e in self.enemies}
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
            if not self.paused and event.key == pygame.K_SPACE:
                self._try_fire(self.player)

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
        self.player.update_timers(dt)
        for e in self.enemies:
            e.update_timers(dt)

        self._update_player(dt)
        self._update_enemies(dt)
        self._update_bullets(dt)
        self._resolve_end_conditions()

    def _update_player(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = self.player.desired_move_from_keys(keys)
        self.player.set_facing_from_move(move)
        delta = move * self.player.speed * dt
        self.player.rect = move_rect_with_collisions(self.player.rect, delta, self._solid_rects)

    def _update_enemies(self, dt: float) -> None:
        pc = pygame.Vector2(self.player.rect.centerx, self.player.rect.centery)
        for e in self.enemies:
            if not e.alive:
                continue
            ctrl = self.enemy_ctrl[id(e)]
            ec = pygame.Vector2(e.rect.centerx, e.rect.centery)
            move = ctrl.ai.update(dt, ec, pc)
            e.set_facing_from_move(move)
            delta = move * e.speed * dt
            e.rect = move_rect_with_collisions(e.rect, delta, self._solid_rects)

            if enemy_should_fire(ec, pc, e.facing):
                self._try_fire(e)

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

            # 子弹 vs 坦克
            if b.owner != "player" and self.player.alive and bullet_hits_rect(br, self.player.rect):
                self.player.take_hit(1)
                b.alive = False
                continue

            if b.owner != "enemy":
                for e in self.enemies:
                    if e.alive and bullet_hits_rect(br, e.rect):
                        e.take_hit(1)
                        if not e.alive:
                            self.kills += 1
                        b.alive = False
                        break

        # 清理可破坏墙
        before = len(self.walls)
        self.walls = [w for w in self.walls if not (w.breakable and w.hp <= 0)]
        if len(self.walls) != before:
            self._solid_rects = self._build_solids()

        # 清理死亡子弹
        self.bullets = [b for b in self.bullets if b.alive]

    def _resolve_end_conditions(self) -> None:
        alive_enemies = [e for e in self.enemies if e.alive]
        if not self.player.alive:
            self.manager.switch("gameover", {"won": False, "stats": {"kills": self.kills, "time_s": self.time_s}})
            return
        if len(alive_enemies) == 0:
            self.manager.switch("gameover", {"won": True, "stats": {"kills": self.kills, "time_s": self.time_s}})
            return

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)
        for w in self.walls:
            w.draw(screen)
        for b in self.bullets:
            b.draw(screen)
        if self.player.alive:
            self.player.draw(screen)
        for e in self.enemies:
            if e.alive:
                e.draw(screen)

        alive_enemies = sum(1 for e in self.enemies if e.alive)
        draw_text(screen, f"HP: {self.player.hp}", (12, 10), font=self.ui_font)
        draw_text(screen, f"敌人: {alive_enemies}", (12, 34), font=self.ui_font)

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

