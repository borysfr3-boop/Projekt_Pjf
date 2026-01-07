from entities import Enemy

class WaveManager:
    def __init__(self, waypoints):
        self.waypoints = waypoints
        self.wave = 0
        self.to_spawn = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 0.65

        self.active = False

    def start_next_wave(self):
        self.wave += 1
        self.to_spawn = 6 + self.wave * 2
        self.spawn_timer = 0.2
        self.active = True

    def is_wave_finished(self, enemies):

        if self.to_spawn > 0:
            return False
        return all(not e.alive for e in enemies)

    def update(self, dt, enemies):
        if not self.active:
            return

        if self.to_spawn <= 0:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            # skaluje parametry fali
            hp = 20 + self.wave * 12
            speed = 85 + self.wave * 2
            reward = 8 + self.wave // 2

            enemies.append(Enemy(self.waypoints, hp=hp, speed=speed, reward=reward))
            self.to_spawn -= 1
            # przy większych falach minimalnie szybciej
            self.spawn_interval = max(0.35, 0.65 - self.wave * 0.01)
            self.spawn_timer = self.spawn_interval
