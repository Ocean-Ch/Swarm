import random
import math

import pygame
from pygame.sprite import Sprite
from settings import Settings


class Cloud(Sprite):
    def __init__(self, fof_game):
        """Initializes cloud object"""
        super().__init__()
        self.screen = fof_game.screen
        self.settings = Settings()
        self.orb = fof_game.orb
        self.speed = self.settings.cloud_speed
        self.foo = 0
        self.last_moved = 0
        self.hp = 1
        sr = self.settings.screen_ratio

        image = pygame.image.load('images/enemy.bmp')
        self.image = \
            pygame.transform.smoothscale(image, (int(70 * sr), int(97 * sr)))
        self.rect = self.image.get_rect()

        # Min/max points where enemies can spawn
        spawn_min_x = -20
        spawn_max_x = self.settings.screen_width + 20
        spawn_min_y = -20
        spawn_max_y = self.settings.screen_height + 20
        # Below will determine where enemy will spawn (anywhere on the border)
        side = random.choice([1, 2, 3, 4])
        if side == 1:
            # Spawn on the top
            self.rect.center = (random.choice(range(spawn_min_x, spawn_max_x)),
                                spawn_min_y)
        elif side == 2:
            # Spawn at bottom
            self.rect.center = (random.choice(range(spawn_min_x, spawn_max_x)),
                                spawn_max_y)
        elif side == 3:
            # Spawn on left
            self.rect.center = (spawn_min_x,
                                random.choice(range(spawn_min_y, spawn_max_y)))
        else:
            # Spawn on right
            self.rect.center = (spawn_max_x,
                                random.choice(range(spawn_min_y, spawn_max_y)))
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        """Updates movement for this cloud (Decides which direction to go)."""
        now = pygame.time.get_ticks()
        # Makes a chance decision every 15 ms (20% chance of moving towards orb)
        if now - self.last_moved > 15:
            self.foo = random.randint(0, 100)
            self.last_moved = now
        if self.foo > 80 and self.rect.right < self.settings.screen_width:
            self.x += self.settings.cloud_speed
        elif self.foo > 60 and self.rect.left > 0:
            self.x -= self.settings.cloud_speed
        elif self.foo > 40 and self.rect.top > 0:
            self.y -= self.settings.cloud_speed
        elif self.foo > 20 and self.rect.bottom < self.settings.screen_height:
            self.y += self.settings.cloud_speed
        else:
            direction = self._calculate_proj_vector()
            self.x += direction[0]
            self.y += direction[1]
        self.rect.x = self.x
        self.rect.y = self.y

    def _calculate_proj_vector(self) -> tuple[float, float]:
        """Gets the vector towards orb (Normalized according to desired
        magnitude). Magnitude of the vector in this case is the speed or enemy."""
        location = self.orb.rect.center
        resultant = (location[0] - self.rect.center[0],
                     location[1] - self.rect.center[1])
        # HANDLE ZERO DIVISION ERROR
        if resultant[0] == 0:
            resultant = (0.01, resultant[1])
        slope = resultant[1] / resultant[0]
        x_dir = math.sqrt(self.speed ** 2 / (1 + slope ** 2))
        if resultant[0] < 0:
            x_dir *= -1
        y_dir = x_dir * slope
        return x_dir, y_dir
