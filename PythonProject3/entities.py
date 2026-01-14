import pygame
import random
from math import sqrt, sin

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def normalize(vx, vy):
    d = sqrt(vx*vx + vy*vy)
    if d == 0:
        return 0.0, 0.0
    return vx/d, vy/d

# -------------------- ENEMIES --------------------

class Enemy:
    def __init__(self, waypoints, hp, speed, reward, damage_to_base=1):
        self.waypoints = waypoints
        self.hp_max = int(hp)
        self.hp = float(hp)
        self.base_speed = float(speed)
        self.speed = float(speed)
        self.reward = int(reward)
        self.damage_to_base = int(damage_to_base)

        self.wp_idx = 0
        self.pos = pygame.Vector2(waypoints[0][0], waypoints[0][1])
        self.radius = 12


        self.slow_timer = 0.0
        self.slow_factor = 1.0

        self.alive = True
        self.reached_base = False


        self.progress = 0.0


        self.sprite = None
        self._bob_t = random.random() * 6.28

    def set_sprite(self, sprite: pygame.Surface):
        self.sprite = sprite
        self.radius = max(12, sprite.get_width() // 2)

    def apply_slow(self, factor: float, duration: float):
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def take_damage(self, dmg: float):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def update(self, dt: float):
        if not self.alive:
            return

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_timer = 0
                self.slow_factor = 1.0

        self.speed = self.base_speed * self.slow_factor

        # do dotarcia przecinwka
        if self.wp_idx >= len(self.waypoints) - 1:
            self.alive = False
            self.reached_base = True
            return

        tx, ty = self.waypoints[self.wp_idx + 1]
        vx = tx - self.pos.x
        vy = ty - self.pos.y
        nx, ny = normalize(vx, vy)

        step = self.speed * dt
        self.pos.x += nx * step
        self.pos.y += ny * step

        self.progress = self.wp_idx + (1.0 - min(1.0, dist((self.pos.x, self.pos.y), (tx, ty)) / 220.0))

        if dist((self.pos.x, self.pos.y), (tx, ty)) < 8:
            self.wp_idx += 1

        self._bob_t += dt * 4.5

    def draw(self, screen):
        if not self.alive:
            return

        x, y = int(self.pos.x), int(self.pos.y)
        bob = int(2 * sin(self._bob_t))

        if self.sprite is not None:
            rect = self.sprite.get_rect(center=(x, y + bob))
            screen.blit(self.sprite, rect)
        else:
            body = (220, 70, 70) if self.slow_factor >= 1.0 else (120, 170, 255)
            pygame.draw.circle(screen, body, (x, y + bob), self.radius)


        w, h = 34, 6
        bx = x - w // 2
        by = (y + bob) - self.radius - 18
        pygame.draw.rect(screen, (30, 30, 40), (bx, by, w, h), border_radius=3)
        fill = int(w * max(0.0, self.hp / self.hp_max))
        pygame.draw.rect(screen, (80, 220, 120), (bx, by, fill, h), border_radius=3)
        pygame.draw.rect(screen, (150, 150, 200), (bx, by, w, h), 1, border_radius=3)

class BossEnemy(Enemy):

    def __init__(self, waypoints, hp, speed, reward, damage_to_base=5, tower_kill_cd=5.0):
        super().__init__(waypoints, hp, speed, reward, damage_to_base=damage_to_base)
        self.radius = 22
        self.tower_kill_cd = float(tower_kill_cd)
        self.tower_kill_timer = self.tower_kill_cd
        self.is_boss = True

        self.used_tower_kill = False  # <-- tylko raz na falę

    def update(self, dt: float):
        super().update(dt)
        if not self.alive:
            return
        self.tower_kill_timer -= dt

    def try_destroy_random_tower(self, towers):
        # max 1 wieża na całą falę
        if not self.alive:
            return None
        if self.used_tower_kill:
            return None

        # nie od razu po spawnie
        if self.tower_kill_timer > 0:
            return None

        if not towers:
            self.tower_kill_timer = self.tower_kill_cd
            return None

        victim = random.choice(towers)
        self.used_tower_kill = True  # <-- po tym już nie niszczy więcej
        return victim

    def draw(self, screen):
        if not self.alive:
            return

        x, y = int(self.pos.x), int(self.pos.y)
        bob = int(3 * sin(self._bob_t))

        if self.sprite is not None:
            t = pygame.time.get_ticks() / 1000.0
            s = 1.0 + 0.05 * sin(t * 3.0)
            w = int(self.sprite.get_width() * s)
            h = int(self.sprite.get_height() * s)
            spr = pygame.transform.smoothscale(self.sprite, (w, h))
            rect = spr.get_rect(center=(x, y + bob))
            screen.blit(spr, rect)
        else:
            pygame.draw.circle(screen, (255, 120, 50), (x, y + bob), self.radius)
            pygame.draw.circle(screen, (255, 220, 150), (x, y + bob), self.radius, 2)


        w, h = 60, 7
        bx = x - w // 2
        by = (y + bob) - self.radius - 20
        pygame.draw.rect(screen, (30, 30, 40), (bx, by, w, h), border_radius=3)
        fill = int(w * max(0.0, self.hp / self.hp_max))
        pygame.draw.rect(screen, (255, 170, 70), (bx, by, fill, h), border_radius=3)
        pygame.draw.rect(screen, (200, 200, 230), (bx, by, w, h), 1, border_radius=3)

# -------------------- PROJECTILES --------------------

class Bullet:

    def __init__(self, pos, target, speed, dmg, kind="cannon", radius=4, slow=None):
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.prev = self.pos.copy()
        self.target = target
        self.speed = float(speed)
        self.dmg = float(dmg)
        self.radius = radius
        self.kind = kind
        self.alive = True
        self.slow = slow
        self._t = 0.0

    def update(self, dt: float):
        if not self.alive:
            return
        self._t += dt
        if self.target is None or not self.target.alive:
            self.alive = False
            return

        self.prev = self.pos.copy()

        tx, ty = self.target.pos.x, self.target.pos.y
        vx = tx - self.pos.x
        vy = ty - self.pos.y
        nx, ny = normalize(vx, vy)
        self.pos.x += nx * self.speed * dt
        self.pos.y += ny * self.speed * dt

        if dist((self.pos.x, self.pos.y), (tx, ty)) <= (self.radius + self.target.radius):
            self.target.take_damage(self.dmg)
            if self.slow is not None and self.target.alive:
                factor, duration = self.slow
                self.target.apply_slow(factor, duration)
            self.alive = False

    def _draw_star(self, screen, center, r_outer, r_inner):
        cx, cy = center
        pts = []
        for i in range(10):
            ang = i * 3.14159 / 5.0
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((cx + r * sin(ang*2.0 + 0.0), cy - r * sin(ang*2.0 - 1.0)))
        pygame.draw.polygon(screen, (170, 210, 255), pts)
        pygame.draw.polygon(screen, (230, 240, 255), pts, 1)

    def draw(self, screen):
        if not self.alive:
            return
        x, y = int(self.pos.x), int(self.pos.y)

        if self.kind == "cannon":
            pygame.draw.circle(screen, (255, 210, 120), (x, y), self.radius)
        elif self.kind == "slow":
            pulse = 1.0 + 0.2 * sin(self._t * 10.0)
            ro = int(6 * pulse)
            ri = int(3 * pulse)
            self._draw_star(screen, (x, y), ro, ri)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.radius)

class Beam:

    def __init__(self, start_pos, target, dmg, duration=0.06):
        self.start = pygame.Vector2(start_pos[0], start_pos[1])
        self.target = target
        self.dmg = float(dmg)
        self.timer = float(duration)
        self.alive = True

        if self.target is not None and self.target.alive:
            self.target.take_damage(self.dmg)

    def update(self, dt: float):
        if not self.alive:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return
        if self.target is None or not self.target.alive:
            return
        sx, sy = int(self.start.x), int(self.start.y)
        tx, ty = int(self.target.pos.x), int(self.target.pos.y)

        pygame.draw.line(screen, (80, 180, 255), (sx, sy), (tx, ty), 4)
        pygame.draw.line(screen, (220, 245, 255), (sx, sy), (tx, ty), 2)

# -------------------- TOWERS --------------------

class Tower:
    NAME = "Tower"
    COST = 50
    UPGRADE_COSTS = (40, 60)

    def __init__(self, pos, sprite: pygame.Surface = None):
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.level = 1
        self.range = 130
        self.cooldown = 0.5
        self.damage = 10
        self.bullet_speed = 380
        self.cd_timer = 0.0

        self.sprite = sprite
        self.radius = 18 if sprite is None else max(18, sprite.get_width() // 2)

        self._anim_t = random.random() * 6.28

    def can_upgrade(self):
        return self.level < 3

    def upgrade_cost(self):
        if self.level == 1:
            return self.UPGRADE_COSTS[0]
        if self.level == 2:
            return self.UPGRADE_COSTS[1]
        return 999999

    def upgrade(self):
        if self.level >= 3:
            return
        self.level += 1
        self.damage *= 1.25
        self.range += 15
        self.cooldown *= 0.92

    def pick_target(self, enemies):
        best = None
        best_prog = -1e9
        for e in enemies:
            if not e.alive:
                continue
            if dist((self.pos.x, self.pos.y), (e.pos.x, e.pos.y)) <= self.range:
                if e.progress > best_prog:
                    best_prog = e.progress
                    best = e
        return best

    def update(self, dt, enemies, bullets, beams):
        self._anim_t += dt * 4.0

        if self.cd_timer > 0:
            self.cd_timer -= dt
            if self.cd_timer < 0:
                self.cd_timer = 0

        self.try_shoot(enemies, bullets, beams)

    def try_shoot(self, enemies, bullets, beams):
        if self.cd_timer > 0:
            return
        target = self.pick_target(enemies)
        if target is None:
            return
        bullets.append(Bullet(self.pos, target, self.bullet_speed, self.damage, kind="cannon"))
        self.cd_timer = self.cooldown

    def draw(self, screen, selected=False):
        x, y = int(self.pos.x), int(self.pos.y)

        pulse = 1.0 + 0.04 * sin(self._anim_t)
        if self.sprite is not None:
            w = int(self.sprite.get_width() * pulse)
            h = int(self.sprite.get_height() * pulse)
            spr = pygame.transform.smoothscale(self.sprite, (w, h))
            rect = spr.get_rect(center=(x, y))
            screen.blit(spr, rect)
        else:
            pygame.draw.circle(screen, (60, 60, 90), (x, y), self.radius)

        if selected:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.radius + 2, 2)

class LaserTower(Tower):
    NAME = "Laser"
    COST = 60
    UPGRADE_COSTS = (45, 70)

    def __init__(self, pos, sprite=None):
        super().__init__(pos, sprite=sprite)
        self.range = 155
        self.cooldown = 0.20
        self.damage = 8

    def try_shoot(self, enemies, bullets, beams):
        if self.cd_timer > 0:
            return
        target = self.pick_target(enemies)
        if target is None:
            return
        beams.append(Beam(self.pos, target, self.damage, duration=0.06))
        self.cd_timer = self.cooldown

class CannonTower(Tower):
    NAME = "Cannon"
    COST = 85
    UPGRADE_COSTS = (60, 90)

    def __init__(self, pos, sprite=None):
        super().__init__(pos, sprite=sprite)
        self.range = 160
        self.cooldown = 0.75
        self.damage = 22
        self.bullet_speed = 330

class SlowTower(Tower):
    NAME = "Slow"
    COST = 70
    UPGRADE_COSTS = (55, 80)

    def __init__(self, pos, sprite=None):
        super().__init__(pos, sprite=sprite)
        self.range = 150
        self.cooldown = 0.55
        self.damage = 5
        self.bullet_speed = 420
        self.slow_factor = 0.65
        self.slow_duration = 1.4

    def try_shoot(self, enemies, bullets, beams):
        if self.cd_timer > 0:
            return
        target = self.pick_target(enemies)
        if target is None:
            return
        bullets.append(
            Bullet(self.pos, target, self.bullet_speed, self.damage, kind="slow", slow=(self.slow_factor, self.slow_duration))
        )
        self.cd_timer = self.cooldown

    def upgrade(self):
        if self.level >= 3:
            return
        self.level += 1
        self.damage *= 1.15
        self.range += 12
        self.cooldown *= 0.92
        self.slow_factor *= 0.93
        self.slow_duration += 0.15
