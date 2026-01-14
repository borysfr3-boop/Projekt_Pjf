import pygame
import random
from math import sqrt

SCREEN_W, SCREEN_H = 1100, 650

WAYPOINTS = [
    (40, 320),
    (220, 320),
    (220, 140),
    (420, 140),
    (420, 500),
    (650, 500),
    (650, 260),
    (820, 260),
    (820, 420),
    (1030, 420),
]

PATH_WIDTH = 44
_STAR_CACHE = None

def draw_background(screen):
    global _STAR_CACHE
    screen.fill((8, 8, 14))

    if _STAR_CACHE is None:
        rng = random.Random(12345)
        _STAR_CACHE = []
        for _ in range(180):
            x = rng.randint(0, screen.get_width()-1)
            y = rng.randint(0, screen.get_height()-1)
            r = rng.choice([1, 1, 1, 2])
            bright = rng.randint(120, 220)
            _STAR_CACHE.append((x, y, r, bright))

    for x, y, r, bright in _STAR_CACHE:
        pygame.draw.circle(screen, (bright, bright, bright), (x, y), r)

def draw_path(screen):
    if len(WAYPOINTS) >= 2:
        pygame.draw.lines(screen, (35, 35, 55), False, WAYPOINTS, PATH_WIDTH)
        pygame.draw.lines(screen, (80, 80, 120), False, WAYPOINTS, 3)

    for p in WAYPOINTS:
        pygame.draw.circle(screen, (120, 120, 170), p, 4)

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def point_to_segment_distance(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    abx, aby = bx-ax, by-ay
    apx, apy = px-ax, py-ay
    ab_len2 = abx*abx + aby*aby
    if ab_len2 == 0:
        return dist(p, a)
    t = (apx*abx + apy*aby) / ab_len2
    t = clamp(t, 0.0, 1.0)
    cx = ax + t * abx
    cy = ay + t * aby
    return dist(p, (cx, cy))

def is_on_path(pos):
    for i in range(len(WAYPOINTS) - 1):
        d = point_to_segment_distance(pos, WAYPOINTS[i], WAYPOINTS[i+1])
        if d <= PATH_WIDTH * 0.55:
            return True
    return False
