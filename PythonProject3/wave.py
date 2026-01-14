from entities import Enemy, BossEnemy

class WaveManager:
    def __init__(self, waypoints, enemy_sprites=None, boss_sprite=None):
        self.waypoints = waypoints
        self.enemy_sprites = enemy_sprites or []
        self.boss_sprite = boss_sprite

        self.wave = 0
        self.to_spawn = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 0.65
        self.active = False

        self._boss_pending = False
        self._boss_spawned = False

    def start_next_wave(self):
        self.wave += 1

        # boss co 3 fale
        if self.wave % 3 == 0:
            self._boss_pending = True
            self._boss_spawned = False
            self.to_spawn = 0
        else:
            self._boss_pending = False
            self._boss_spawned = False
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

        self.spawn_timer -= dt
        if self.spawn_timer > 0:
            return


        if self._boss_pending and not self._boss_spawned:
            hp = 180 + (self.wave * 40)
            speed = 70 + self.wave
            reward = 60 + self.wave * 5

            boss = BossEnemy(
                self.waypoints,
                hp=hp,
                speed=speed,
                reward=reward,
                damage_to_base=5,
                tower_kill_cd=5.0
            )

            if self.boss_sprite is not None:
                boss.set_sprite(self.boss_sprite)
            elif self.enemy_sprites:
                boss.set_sprite(self.enemy_sprites[-1])

            enemies.append(boss)
            self._boss_spawned = True

            # po spawnie bossa nie spawnuje potworkow
            self.spawn_timer = 999999
            return


        if self.to_spawn <= 0:
            return

        hp = 20 + self.wave * 6
        speed = 85 + self.wave * 2
        reward = 8 + self.wave // 2

        e = Enemy(self.waypoints, hp=hp, speed=speed, reward=reward, damage_to_base=1)

        if self.enemy_sprites:
            sprite = self.enemy_sprites[(self.wave - 1) % len(self.enemy_sprites)]
            e.set_sprite(sprite)

        enemies.append(e)

        self.to_spawn -= 1
        self.spawn_interval = max(0.35, 0.65 - self.wave * 0.01)
        self.spawn_timer = self.spawn_interval
