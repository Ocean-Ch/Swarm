import random
import sys

import pygame
from settings import Settings, Crosshair
from orb import Orb
from laser import Laser
from enemy import Cloud
from time import sleep


class FightOrFlight:
    """Managing assets/behaviour
    === Attributes ===
    settings: A Settings object containing all the screen/colour settings
    screen: initial panel containing main screen
    bg_colour: Background colour
    """
    settings: Settings
    screen: pygame
    bg_colour: tuple[int, int, int]

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock.tick(144)
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        pygame.display.set_caption('FightOrFlight')
        bg = pygame.image.load('images/bg.bmp')
        self.bg = pygame.transform.smoothscale(bg,
                                               (self.settings.screen_width,
                                                self.settings.screen_height))
        self.orb = Orb(self)
        self.lasers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.last_enemy_spawn = 0
        self._spawn_enemies()
        pygame.mouse.set_visible(False)
        self.crosshair = Crosshair(self)

    def run_game(self) -> None:
        """Starts the main loop for the game"""
        while 1:
            self._check_events()
            self.orb.update()
            self.lasers.update()
            self.enemies.update()
            self._spawn_enemies()
            self.laser_collisions()
            self.orb_collisions()
            self._update_screen()

    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._check_mouse_events(event)

    def _spawn_enemies(self):
        cd = random.randint(self.settings.cloud_cooldown_min,
                            self.settings.cloud_cooldown)
        now = pygame.time.get_ticks()
        if now - self.last_enemy_spawn > cd \
                and len(self.enemies) < self.settings.max_enemies:
            enemy = Cloud(self)
            self.enemies.add(enemy)
            self.last_enemy_spawn = now

    def laser_collisions(self):
        collisions = pygame.sprite.groupcollide(self.lasers,
                                                self.enemies, True, True)

    def orb_collisions(self):
        for enemy in self.enemies:
            if pygame.sprite.collide_rect_ratio(0.60)(self.orb, enemy):
                sleep(2)
                self.enemies.empty()

    def _update_screen(self):
        """Updates images to the screen"""
        # Fill in display colour after each pass of the loop
        self.crosshair.update_crosshair()

        self.screen.blit(self.bg, (0, 0))
        self.orb.blitme()
        for laser in self.lasers.sprites():
            if -10 > laser.x > self.settings.screen_width + 100 or \
                    -10 > laser.y > self.settings.screen_height:
                laser.kill()
        self.lasers.draw(self.screen)
        self.enemies.draw(self.screen)
        # Makes recently created screen visible
        # pygame.draw.rect(self.screen, (0, 0, 255), self.orb.rect)
        self.crosshair.blitme()
        # pygame.draw.rect(self.screen, (0, 0, 255), self.crosshair.rect)
        pygame.display.flip()

    def _check_mouse_events(self, event):
        if event.button == 1:
            self._fire_bullet()

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            # Move right
            self.orb.moving_right = True
            # self.orb.last_pressed.append(1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            # Move left
            self.orb.moving_left = True
            # self.orb.last_pressed.append(2)
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            # Move up
            self.orb.moving_up = True
            # self.orb.last_pressed.append(3)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            # Move down
            self.orb.moving_down = True
            # self.orb.last_pressed.append(4)
        elif event.key == pygame.K_SPACE:
            self.orb.blink()
        elif event.key == pygame.K_k:
            self._fire_bullet()
        elif event.key == pygame.K_ESCAPE:
            sys.exit()

    def _fire_bullet(self):
        new_laser = Laser(self)
        self.lasers.add(new_laser)

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.orb.moving_right = False
            # self.orb.last_pressed.remove(1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            # Move left
            self.orb.moving_left = False
            # self.orb.last_pressed.remove(2)
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            # Move up
            self.orb.moving_up = False
            # self.orb.last_pressed.remove(3)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            # Move down
            self.orb.moving_down = False
            # self.orb.last_pressed.remove(4)


if __name__ == "__main__":
    fof = FightOrFlight()
    fof.run_game()
