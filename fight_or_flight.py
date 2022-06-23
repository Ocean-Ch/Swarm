import random
import sys
import pygame.font

import pygame
from settings import Settings, Crosshair
from orb import Orb
from laser import Laser
from enemy import Cloud, Red
from time import sleep
from stats import Stats
from button import Button
from hud import HUD

# TODO reset game clock everytime game starts
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
        """Creates a FOF game object"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock.tick(144)
        self.settings = Settings()
        self.stats = Stats(self)
        self.running = False
        self.paused = False
        self.options = False
        self.first_red = False
        # self.sr is display size relative to 2560 * 1440p monitor
        self.sr = self.settings.screen_ratio
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        self.hud = HUD(self)
        pygame.display.set_caption('Swarm')
        bg = pygame.image.load('images/bg.bmp')
        self.bg = pygame.transform.smoothscale(bg,
                                               (self.settings.screen_width,
                                                self.settings.screen_height))
        pause_img = pygame.image.load('images/paused.bmp')
        self.pause_img = pygame.transform.smoothscale(pause_img,
                                                      (int(400 * self.sr),
                                                       int(208 * self.sr)))
        self.pause_rect = self.pause_img.get_rect(
            center=(self.settings.screen_width // 2,
                    self.settings.screen_height // 2))
        self.orb = Orb(self)
        self.lasers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.last_cloud_spawn = 0
        self.last_red_spawn = 0
        self._spawn_enemies()
        self.crosshair = Crosshair(self)
        self.play_button = None
        self.options_button = None
        self.quit_button = None

    def run_game(self) -> None:
        """MAIN LOOP"""
        while 1:
            if self.paused:
                self._check_events()
                self.display_pause()
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
        """MAIN METHOD for the start menu. Does not run during game phase."""
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.bg, (0, 0))
        menu_text = self.get_font_1(int(150 * self.sr)).render("SWARM", True,
                                                               "#b68f40")
        menu_rect = menu_text.get_rect(
            center=(self.settings.screen_width // 2, int(300 * self.sr)))

        self.play_button = Button(None, (self.settings.screen_width // 2,
                                         int(700 * self.sr)), "PLAY",
                                  self.get_font_1(75), "#d7fcd4", "White")
        self.options_button = \
            Button(None, (self.settings.screen_width // 2, int(900 * self.sr)),
                   "OPTIONS", self.get_font_1(75), "#d7fcd4", "White")
        self.quit_button = Button(None, (self.settings.screen_width // 2,
                                         int(1100 * self.sr)), "QUIT",
                                  self.get_font_1(75), "#d7fcd4", "White")
        self.screen.blit(menu_text, menu_rect)

        for button in [self.play_button, self.options_button, self.quit_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)
        self.check_events_menu(mouse_pos)

    def check_events_menu(self, mouse_pos):
        """Method to check any events happening in the main menu.
        Does not run during game phase."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.checkForInput(mouse_pos):
                    self.running = True
                    self.reset_game()
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
        """Spawns enemies over a given time period"""
        cd_cloud = random.randint(self.settings.cloud_cooldown_min,
                                  self.settings.cloud_cooldown)
        cd_red = random.randint(self.settings.red_cooldown_min,
                                self.settings.red_cooldown)
        now = pygame.time.get_ticks()
        if now - self.last_cloud_spawn > cd_cloud \
                and len(self.enemies) < self.settings.max_enemies:
            enemy = Cloud(self)
            self.enemies.add(enemy)
            self.last_cloud_spawn = now
        if not self.first_red and self.stats.score >= 690:
            self.enemies.add(Red(self))
            self.last_red_spawn = now
            self.first_red = True
        if now - self.last_red_spawn > cd_red:
            self.enemies.add(Red(self))
            self.last_red_spawn = now

    def laser_collisions(self):
        """Tracks when any object from the laser group intereacts with an object
        of the enemy group"""
        collisions = pygame.sprite.groupcollide(self.enemies, self.lasers,
                                                False, True)
        for enemy in collisions:
            # Deduct one health point
            enemy.hp -= 1
            if enemy.hp <= 0:
                if isinstance(enemy, Cloud):
                    self.stats.score += 10
                elif isinstance(enemy, Red):
                    self.stats.score += 500
                enemy.kill()
                self.hud.update_score()
        for laser in self.lasers.sprites():
            if -20 > laser.x > self.settings.screen_width + 50 or \
                    -10 > laser.y > self.settings.screen_height:
                laser.kill()

    def orb_collisions(self):
        """Tracks if any enemies touch the orb"""
        for enemy in self.enemies:
            # Ratio 0.6 because orb rect is much larger
            if pygame.sprite.collide_rect_ratio(0.60)(self.orb, enemy):
                death_text = \
                    self.get_font_1(int(150 * self.sr)).render("DEATH", True,
                                                               "red")
                death_rect = death_text.get_rect(
                    center=(self.settings.screen_width // 2,
                            self.settings.screen_height // 2))
                self.screen.blit(death_text, death_rect)
                # Updates only the death rectangle of the display
                pygame.display.update(death_rect)
                # Pauses game for 1.5 seconds
                sleep(1.5)
                self.enemies.empty()
                self.stats.reset()
                self.orb.reset_movement()
                self.running = False

    def _update_screen(self):
        """Updates images to the screen"""
        # Fill in display colour after each pass of the loop
        self.crosshair.update_crosshair()
        # Blit background photo onto display screen
        self.screen.blit(self.bg, (0, 0))
        self.orb.blitme()

        # pygame.draw.rect(self.screen, (0, 255, 255), self.hud.score_rect)
        # Draws lasers and enemies (if any)
        self.lasers.draw(self.screen)
        self.enemies.draw(self.screen)
        self.hud.show_score()
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
        """Private method to check which keys have been pressed"""
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
        """Instantiates a laser object and adds it to the laser group"""
        new_laser = Laser(self)
        self.lasers.add(new_laser)

    def _check_keyup_events(self, event):
        """Checks when player releases any keys"""
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

    def display_pause(self):
        self.screen.blit(self.pause_img, self.pause_rect)
        pygame.display.update(self.pause_rect)

    def reset_game(self):
        self.stats.reset()
        self.clock = pygame.time.Clock()
        self.clock.tick(144)
        self.first_red = False

    def get_font_1(self, size):
        """Alien space theme font"""
        return pygame.font.Font("assets/Organ.ttf", size)

    def get_font_2(self, size):
        """Alien space theme font"""
        return pygame.font.Font("assets/slkscr.ttf", size)


if __name__ == "__main__":
    fof = FightOrFlight()
    fof.run_game()
