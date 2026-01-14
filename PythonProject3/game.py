import pygame

from map_data import SCREEN_W, SCREEN_H, WAYPOINTS, draw_background, draw_path, is_on_path
from entities import LaserTower, CannonTower, SlowTower
from wave import WaveManager
from ui import Button, draw_hud, draw_game_over
from highscore import load_highscore, save_highscore
from assets import load_image

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tower Defense: Obrona Stacji (Pixel Art)")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 56, bold=True)

        self.running = True

        self.state = "MENU"  # MENU, PLAY, GAME_OVER
        self.btn_start = Button((SCREEN_W//2-120, 280, 240, 54), "START")
        self.btn_quit = Button((SCREEN_W//2-120, 350, 240, 54), "WYJŚCIE")

        self.highscore = load_highscore()

        self.reset_game()

    def reset_game(self):
        self.enemies = []
        self.towers = []
        self.bullets = []

        self.base_hp = 25
        self.credits = 120
        self.score = 0

        self.base_rect = pygame.Rect(SCREEN_W-110, SCREEN_H//2-70, 90, 140)

        # ---- SPRITES ----
        self.enemy_sprites = [
            load_image("enemies/alien.png", scale=(40, 40)),
            load_image("enemies/alien2.png", scale=(40, 40)),
        ]
        self.base_sprite = load_image("base.png", scale=(120, 160))

        self.tower_sprites = {
            "Laser": load_image("towers/laser.png", scale=(44, 44)),
            "Cannon": load_image("towers/cannon.png", scale=(44, 44)),
            "Slow": load_image("towers/slow.png", scale=(44, 44)),
        }

        self.wave_manager = WaveManager(WAYPOINTS, enemy_sprites=self.enemy_sprites)
        self.selected_tower = None
        self.build_mode = None  # "Laser"/"Cannon"/"Slow"

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == "MENU":
                if self.btn_start.handle_event(event):
                    self.reset_game()
                    self.state = "PLAY"
                if self.btn_quit.handle_event(event):
                    self.running = False

            elif self.state == "PLAY":
                self.handle_events_play(event)

            elif self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = "PLAY"
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

    def handle_events_play(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.build_mode = "Laser"
            elif event.key == pygame.K_2:
                self.build_mode = "Cannon"
            elif event.key == pygame.K_3:
                self.build_mode = "Slow"
            elif event.key == pygame.K_SPACE:
                if self.wave_manager.is_wave_finished(self.enemies):
                    self.wave_manager.start_next_wave()
            elif event.key == pygame.K_u:
                if self.selected_tower is not None and self.selected_tower.can_upgrade():
                    cost = self.selected_tower.upgrade_cost()
                    if self.credits >= cost:
                        self.credits -= cost
                        self.selected_tower.upgrade()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.selected_tower = None

            if event.button == 1:
                mx, my = event.pos

                # klik w wieżę => zaznacz
                clicked = None
                for t in self.towers:
                    if (t.pos.x - mx) ** 2 + (t.pos.y - my) ** 2 <= (t.radius + 6) ** 2:
                        clicked = t
                        break
                if clicked is not None:
                    self.selected_tower = clicked
                    return

                # budowa
                if self.build_mode is not None:
                    if self.base_rect.collidepoint((mx, my)):
                        return
                    if is_on_path((mx, my)):
                        return
                    if self.is_too_close_to_other_tower((mx, my)):
                        return
                    self.try_build_tower((mx, my), self.build_mode)

    def is_too_close_to_other_tower(self, pos):
        px, py = pos
        for t in self.towers:
            if (t.pos.x - px)**2 + (t.pos.y - py)**2 < (36)**2:
                return True
        return False

    def try_build_tower(self, pos, mode):
        if mode == "Laser":
            if self.credits >= LaserTower.COST:
                self.credits -= LaserTower.COST
                self.towers.append(LaserTower(pos, sprite=self.tower_sprites["Laser"]))
        elif mode == "Cannon":
            if self.credits >= CannonTower.COST:
                self.credits -= CannonTower.COST
                self.towers.append(CannonTower(pos, sprite=self.tower_sprites["Cannon"]))
        elif mode == "Slow":
            if self.credits >= SlowTower.COST:
                self.credits -= SlowTower.COST
                self.towers.append(SlowTower(pos, sprite=self.tower_sprites["Slow"]))

    def update(self, dt):
        if self.state in ("MENU", "GAME_OVER"):
            return

        self.wave_manager.update(dt, self.enemies)

        for e in self.enemies:
            e.update(dt)

        # enemy doszedł => -HP
        for e in self.enemies:
            if (not e.alive) and e.reached_base:
                self.base_hp -= 1
                e.reached_base = False

        for t in self.towers:
            t.update(dt, self.enemies, self.bullets)

        for b in self.bullets:
            b.update(dt)

        # nagrody za zabicia
        for e in self.enemies:
            if (not e.alive) and (not e.reached_base) and (e.hp <= 0):
                if getattr(e, "_counted", False) is False:
                    e._counted = True
                    self.credits += e.reward
                    self.score += 1

        # sprzątanie
        self.enemies = [e for e in self.enemies if e.alive]
        self.bullets = [b for b in self.bullets if b.alive]

        if self.base_hp <= 0:
            self.base_hp = 0
            self.highscore = max(self.highscore, self.score)
            save_highscore(self.highscore)
            self.state = "GAME_OVER"

    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
            return

        draw_background(self.screen)
        draw_path(self.screen)

        # baza sprite
        base_rect = self.base_sprite.get_rect(center=self.base_rect.center)
        self.screen.blit(self.base_sprite, base_rect)

        # zasięg zaznaczonej wieży
        if self.selected_tower is not None:
            pygame.draw.circle(
                self.screen, (80, 80, 120),
                (int(self.selected_tower.pos.x), int(self.selected_tower.pos.y)),
                int(self.selected_tower.range), 1
            )

        for t in self.towers:
            t.draw(self.screen, selected=(t is self.selected_tower))
        for e in self.enemies:
            e.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)

        draw_hud(
            self.screen,
            self.font,
            self.small_font,
            self.wave_manager.wave,
            self.base_hp,
            self.credits,
            self.score,
            self.highscore,
            self.selected_tower,
            self.build_mode
        )

        if self.state == "GAME_OVER":
            draw_game_over(self.screen, self.font, self.big_font, self.score, self.highscore)

        pygame.display.flip()

    def draw_menu(self):
        self.screen.fill((10, 10, 16))

        title = self.big_font.render("TOWER DEFENSE", True, (255, 255, 255))
        sub = self.font.render("Obrona stacji kosmicznej (Pixel Art)", True, (200, 200, 230))
        hs = self.font.render(f"Highscore: {self.highscore}", True, (200, 200, 230))

        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 140))
        self.screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 210))
        self.screen.blit(hs, (SCREEN_W//2 - hs.get_width()//2, 240))

        self.btn_start.draw(self.screen, self.font)
        self.btn_quit.draw(self.screen, self.font)

        tip = self.small_font.render(
            "Sterowanie: 1/2/3 wybór wieży, klik - buduj, U - ulepsz, Spacja - fala",
            True, (170, 170, 210)
        )
        self.screen.blit(tip, (SCREEN_W//2 - tip.get_width()//2, 430))

        pygame.display.flip()
