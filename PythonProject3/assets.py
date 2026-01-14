import os
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

def load_image(path: str, scale=None) -> pygame.Surface:
    full = os.path.join(ASSET_DIR, path)
    img = pygame.image.load(full).convert_alpha()
    if scale is not None:
        img = pygame.transform.smoothscale(img, scale)
    return img
