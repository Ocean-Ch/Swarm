import random
import sys
import pygame.font

import pygame
from settings import Settings, Crosshair
from orb import Orb
from laser import Laser
from enemy import Cloud
from time import sleep
from stats import Stats
from button import Button


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
        self.stats = Stats(self)
        self.running = False
        self.paused = False
        self.options = False
        self.sr = self.settings.screen_ratio
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        pygame.display.set_caption('Swarm')
        bg = pygame.image.load('images/bg.bmp')
        self.bg = pygame.transform.smoothscale(bg,
                                               (self.settings.screen_width,
                                                self.settings.screen_height))
        self.orb = Orb(self)
        self.lasers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.last_enemy_spawn = 0
        self._spawn_enemies()
        self.crosshair = Crosshair(self)
        self.play_button = None
        self.options_button = None
        self.quit_button = None

    def run_game(self) -> None:
        """Starts the main loop for the game"""
        while 1:
            if self.paused:
                self._check_events()
            elif not self.running:
                pygame.mouse.set_visible(True)
                self.start_menu()
            else:
                pygame.mouse.set_visible(False)
                self.screen.fill("black")
                self._check_events()
                self.orb.update()
                self.lasers.update()
                self.enemies.update()
                self._spawn_enemies()
                self.laser_collisions()
                self.orb_collisions()
                self._update_screen()

    def start_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.bg, (0, 0))
        menu_text = self.get_font_1(int(150 * self.sr)).render("SWARM", True,
                                                               "#b68f40")
        menu_rect = menu_text.get_rect(
            center=(self.settings.screen_width // 2, int(250 * self.sr)))

        self.play_button = Button(None, (self.settings.screen_width // 2,
                                         int(500 * self.sr)), "PLAY",
                                  self.get_font_1(75), "#d7fcd4", "White")
        self.options_button = \
            Button(None, (self.settings.screen_width // 2, int(700 * self.sr)),
                   "OPTIONS", self.get_font_1(75), "#d7fcd4", "White")
        self.quit_button = Button(None, (self.settings.screen_width // 2,
                                         int(900 * self.sr)), "QUIT",
                                  self.get_font_1(75), "#d7fcd4", "White")
        self.screen.blit(menu_text, menu_rect)

        for button in [self.play_button, self.options_button, self.quit_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)
        self.check_events_menu(mouse_pos)

    def check_events_menu(self, mouse_pos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.checkForInput(mouse_pos):
                    self.running = True
                if self.options_button.checkForInput(mouse_pos):
                    self.options = True
                if self.quit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
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
        collisions = pygame.sprite.groupcollide(self.enemies, self.lasers,
                                                False, True)
        for enemy in collisions:
            enemy.hp -= 1
            if enemy.hp <= 0:
                self.stats.kills += 1
                enemy.kill()

    def orb_collisions(self):
        for enemy in self.enemies:
            if pygame.sprite.collide_rect_ratio(0.60)(self.orb, enemy):
                death_text = \
                    self.get_font_1(int(150 * self.sr)).render("DEATH", True,
                                                               "red")
                death_rect = death_text.get_rect(
                    center=(self.settings.screen_width // 2,
                            self.settings.screen_height // 2))
                self.screen.blit(death_text, death_rect)
                pygame.display.update(death_rect)
                sleep(2)
                self.enemies.empty()
                self.stats.reset()
                self.orb.reset_movement()
                self.running = False

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
        if event.button == 1 and self.running:
            self._fire_bullet()
        elif not self.running:
            if self.play_button.rect.collidepoint(pygame.mouse.get_pos()):
                self.running = True

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
            self.paused = not self.paused

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

    def get_font_1(self, size):
        return pygame.font.Font("assets/Organ.ttf", size)


if __name__ == "__main__":
    fof = FightOrFlight()
    fof.run_game()
