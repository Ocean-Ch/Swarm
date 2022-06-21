import math
import random

import pygame
from pygame.sprite import Sprite


class Laser(Sprite):
    """
    === Public Attributes ===
    speed: speed of projectile
    image: image of projectile
    """

    def __init__(self, fof_game):
        super().__init__()
        self.settings = fof_game.settings
        self.screen = fof_game.screen
        self.speed = self.settings.laser_speed
        self.orb = fof_game.orb
        sr = self.settings.screen_ratio
        images = ['blue-laser.bmp', 'red-laser.bmp', 'green-laser.bmp']
        random_image = random.choice(images)
        image = pygame.image.load(f'images/{random_image}')
        image = pygame.transform.smoothscale(image, (40 * sr, 30 * sr))
        self.direction = self._calculate_proj_vector()
        angle = (180/math.pi) * math.atan(self.direction[1]/self.direction[0])
        self.image = pygame.transform.rotate(image, -angle)

        self.rect = self.image.get_rect()
        self.rect.center = self.orb.rect.center
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        self.x += self.direction[0]
        self.y += self.direction[1]
        self.rect.y = self.y
        self.rect.x = self.x

    def _calculate_proj_vector(self) -> tuple[float, float]:
        """Get resulting vector relative to mouse cursor"""
        location = pygame.mouse.get_pos()
        resultant = (location[0] - self.orb.rect.center[0],
                     location[1] - self.orb.rect.center[1])
        # HANDLE ZERO DIVISION ERROR
        if resultant[0] == 0:
            resultant = (0.01, resultant[1])
        slope = resultant[1] / resultant[0]
        x_dir = math.sqrt(self.speed ** 2 / (1 + slope ** 2))
        if resultant[0] < 0:
            x_dir *= -1
        y_dir = x_dir * slope
        return x_dir, y_dir
