import pygame

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen, font):
        bg = (40, 40, 60) if not self.hover else (70, 70, 100)
        pygame.draw.rect(screen, bg, self.rect, border_radius=10)
        pygame.draw.rect(screen, (160, 160, 220), self.rect, 2, border_radius=10)

        surf = font.render(self.text, True, (235, 235, 255))
        screen.blit(surf, (self.rect.centerx - surf.get_width()//2, self.rect.centery - surf.get_height()//2))

def draw_hud(screen, font, small_font, wave, hp, credits, score, highscore, selected_tower, build_mode):
    x, y = 14, 12
    lines = [
        f"Fala: {wave}",
        f"HP bazy: {hp}",
        f"Kredyty: {credits}",
        f"Wynik: {score}   (Highscore: {highscore})",
    ]
    for i, t in enumerate(lines):
        surf = font.render(t, True, (235, 235, 255))
        screen.blit(surf, (x, y + i*26))

    tip = "1 Laser (60) | 2 Cannon (85) | 3 Slow (70) | U - ulepsz zazn. | PPM - odznacz | Spacja - next wave"
    tip2 = "Tryb budowy: " + (build_mode if build_mode else "brak")
    surf_tip = small_font.render(tip, True, (170, 170, 210))
    screen.blit(surf_tip, (14, screen.get_height() - 44))
    surf_tip2 = small_font.render(tip2, True, (170, 170, 210))
    screen.blit(surf_tip2, (14, screen.get_height() - 22))

    if selected_tower is not None:
        t = selected_tower
        info = f"Zaznaczona: {t.NAME} | lvl {t.level} | dmg {t.damage:.1f} | rng {t.range:.0f} | cd {t.cooldown:.2f}"
        surf = small_font.render(info, True, (210, 210, 255))
        screen.blit(surf, (14, 122))

def draw_game_over(screen, font, big_font, score, highscore):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    t1 = big_font.render("GAME OVER", True, (255, 255, 255))
    t2 = font.render(f"Wynik: {score}", True, (235, 235, 255))
    t3 = font.render(f"Highscore: {highscore}", True, (235, 235, 255))
    t4 = font.render("Naciśnij R aby zrestartować, ESC aby wyjść", True, (200, 200, 230))

    screen.blit(t1, (w//2 - t1.get_width()//2, 220))
    screen.blit(t2, (w//2 - t2.get_width()//2, 310))
    screen.blit(t3, (w//2 - t3.get_width()//2, 345))
    screen.blit(t4, (w//2 - t4.get_width()//2, 395))
