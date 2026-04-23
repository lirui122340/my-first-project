from __future__ import annotations

import pygame


def move_rect_with_collisions(
    rect: pygame.Rect,
    delta: pygame.Vector2,
    solids: list[pygame.Rect],
) -> pygame.Rect:
    """AABB 碰撞：先 X 后 Y。返回移动后的新 Rect。"""
    new_rect = rect.copy()

    # X axis
    new_rect.x += int(round(delta.x))
    for s in solids:
        if new_rect.colliderect(s):
            if delta.x > 0:
                new_rect.right = s.left
            elif delta.x < 0:
                new_rect.left = s.right

    # Y axis
    new_rect.y += int(round(delta.y))
    for s in solids:
        if new_rect.colliderect(s):
            if delta.y > 0:
                new_rect.bottom = s.top
            elif delta.y < 0:
                new_rect.top = s.bottom

    return new_rect


def bullet_hits_rect(bullet_rect: pygame.Rect, target: pygame.Rect) -> bool:
    return bullet_rect.colliderect(target)

