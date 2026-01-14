import pygame
from math import sqrt

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def normalize(vx, vy):
    d = sqrt(vx*vx + vy*vy)
    if d == 0:
        return 0.0, 0.0
    return vx/d, vy/d

class Enemy:
    def __init__(self, waypoints, hp, speed, reward):
        self.waypoints = waypoints
        self.hp_max = int(hp)
        self.hp = float(hp)
        self.base_speed = float(speed)
        self.speed = float(speed)
        self.reward = int(reward)

        self.wp_idx = 0
        self.pos = pygame.Vector2(waypoints[0][0], waypoints[0][1])
        self.radius = 12

        # slow status
        self.slow_timer = 0.0
        self.slow_factor = 1.0  # 1.0 = normal

        self.alive = True
        self.reached_base = False

        # progress (do targetowania "najdalej")
        self.progress = 0.0

        # sprite
        self.sprite = None

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

        # dotarł do końca?
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

        # progress (proste)
        self.progress = self.wp_idx + (1.0 - min(1.0, dist((self.pos.x, self.pos.y), (tx, ty)) / 220.0))

        # jeśli blisko waypointu -> przeskocz
        if dist((self.pos.x, self.pos.y), (tx, ty)) < 8:
            self.wp_idx += 1

    def draw(self, screen):
        if not self.alive:
            return

        x, y = int(self.pos.x), int(self.pos.y)

        if self.sprite is not None:
            rect = self.sprite.get_rect(center=(x, y))
            screen.blit(self.sprite, rect)
        else:
            body = (220, 70, 70) if self.slow_factor >= 1.0 else (120, 170, 255)
            pygame.draw.circle(screen, body, (x, y), self.radius)

        # pasek HP
        w, h = 34, 6
        bx = x - w // 2
        by = y - self.radius - 18
        pygame.draw.rect(screen, (30, 30, 40), (bx, by, w, h), border_radius=3)
        fill = int(w * max(0.0, self.hp / self.hp_max))
        pygame.draw.rect(screen, (80, 220, 120), (bx, by, fill, h), border_radius=3)
        pygame.draw.rect(screen, (150, 150, 200), (bx, by, w, h), 1, border_radius=3)

class Bullet:
    def __init__(self, pos, target, speed, dmg, radius=4, slow=None):
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.target = target  # Enemy
        self.speed = float(speed)
        self.dmg = float(dmg)
        self.radius = radius
        self.alive = True
        self.slow = slow  # tuple(factor, duration) albo None

    def update(self, dt: float):
        if not self.alive:
            return
        if self.target is None or not self.target.alive:
            self.alive = False
            return

        tx, ty = self.target.pos.x, self.target.pos.y
        vx = tx - self.pos.x
        vy = ty - self.pos.y
        nx, ny = normalize(vx, vy)
        self.pos.x += nx * self.speed * dt
        self.pos.y += ny * self.speed * dt

        # kolizja
        if dist((self.pos.x, self.pos.y), (tx, ty)) <= (self.radius + self.target.radius):
            self.target.take_damage(self.dmg)
            if self.slow is not None and self.target.alive:
                factor, duration = self.slow
                self.target.apply_slow(factor, duration)
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.circle(screen, (255, 230, 120), (int(self.pos.x), int(self.pos.y)), self.radius)

class Tower:
    NAME = "Tower"
    COST = 50
    UPGRADE_COSTS = (40, 60)  # lvl1->2, lvl2->3

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

    def try_shoot(self, enemies, bullets):
        if self.cd_timer > 0:
            return
        target = self.pick_target(enemies)
        if target is None:
            return
        bullets.append(Bullet(self.pos, target, self.bullet_speed, self.damage))
        self.cd_timer = self.cooldown

    def update(self, dt, enemies, bullets):
        if self.cd_timer > 0:
            self.cd_timer -= dt
            if self.cd_timer < 0:
                self.cd_timer = 0
        self.try_shoot(enemies, bullets)

    def draw(self, screen, selected=False):
        x, y = int(self.pos.x), int(self.pos.y)

        if self.sprite is not None:
            rect = self.sprite.get_rect(center=(x, y))
            screen.blit(self.sprite, rect)
        else:
            pygame.draw.circle(screen, (60, 60, 90), (x, y), self.radius)

        # obwódka zaznaczenia
        if selected:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.radius + 2, 2)

class LaserTower(Tower):
    NAME = "Laser"
    COST = 60
    UPGRADE_COSTS = (45, 70)

    def __init__(self, pos, sprite=None):
        super().__init__(pos, sprite=sprite)
        self.range = 145
        self.cooldown = 0.22
        self.damage = 8
        self.bullet_speed = 520

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

    def try_shoot(self, enemies, bullets):
        if self.cd_timer > 0:
            return
        target = self.pick_target(enemies)
        if target is None:
            return
        bullets.append(Bullet(self.pos, target, self.bullet_speed, self.damage, slow=(self.slow_factor, self.slow_duration)))
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
