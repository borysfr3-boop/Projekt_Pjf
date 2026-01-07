import pygame
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

def draw_background(screen):
    screen.fill((12, 12, 18))  # kosmos


    for i in range(0, 1100, 70):
        pygame.draw.circle(screen, (40, 40, 60), (i + 15, (i * 7) % 650), 1)

def draw_path(screen):

    if len(WAYPOINTS) >= 2:
        pygame.draw.lines(screen, (35, 35, 55), False, WAYPOINTS, PATH_WIDTH)
        pygame.draw.lines(screen, (80, 80, 120), False, WAYPOINTS, 3)

    # punkty kontrolne
    for p in WAYPOINTS:
        pygame.draw.circle(screen, (120, 120, 170), p, 4)

def draw_base(screen, base_rect):
    pygame.draw.rect(screen, (30, 70, 120), base_rect, border_radius=14)
    pygame.draw.rect(screen, (120, 200, 255), base_rect, 2, border_radius=14)

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def point_to_segment_distance(p, a, b):
    # Odległość punktu p od odcinka a-b
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
    # zeby te wieze nie byly na sobie
    for i in range(len(WAYPOINTS) - 1):
        d = point_to_segment_distance(pos, WAYPOINTS[i], WAYPOINTS[i+1])
        if d <= PATH_WIDTH * 0.55:
            return True
    return False
