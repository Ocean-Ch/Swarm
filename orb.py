import pygame


class Orb:
    """
    === Public Attributes ===

    screen: game screen
    screen_rect: rectangle of the screen object
    settings: contains all the game settings

    image: the bmp file that displays the orb
    rect: Current Orb's rectangle
    x: Current Orb's horizontal position
    y: Current Orb's vertical position

    moving_[direction]: True iff user is inputting keys for directional movement
    last_pressed: list of at most 4 elements. Last element is last pressed.
    """

    def __init__(self, fof_game):
        """Initialize the orb, and set its starting position"""
        self.screen = fof_game.screen
        self.screen_rect = fof_game.screen.get_rect()
        self.settings = fof_game.settings
        sr = self.settings.screen_ratio
        # load the ship image and get its rect
        image = pygame.image.load('images/orb.bmp')
        self.image = \
            pygame.transform.smoothscale(image, (int(100 * sr), int(100 * sr)))
        self.rect = self.image.get_rect()
        self.rect.center = self.screen_rect.center
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        # Flag for moving right keydown
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.blinking = False
        self.last_rotated = 0
        # self.last_pressed = []
        self.last_blinked = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.orb_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.orb_speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.orb_speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.orb_speed
        if self.blinking:
            if now - self.last_blinked \
                    >= self.settings.blink_time:
                self._stop_blinking()
                self.blinking = False
        self.rect.x = self.x
        self.rect.y = self.y
        if now - self.last_rotated >= self.settings.rotation_speed:
            self.image = pygame.transform.rotate(self.image, 90)
            self.last_rotated = now

    def blink(self):
        # try:
        #     last_pressed = self.last_pressed[-1]
        # except IndexError:
        #     last_pressed = 0
        # if last_pressed == 1:
        #     self.x += self.settings.blink_distance
        # elif last_pressed == 2:
        #     self.x -= self.settings.blink_distance
        # elif last_pressed == 3:
        #     self.y -= self.settings.blink_distance
        # elif last_pressed == 4:
        #     self.y += self.settings.blink_distance
        self.settings.orb_speed += self.settings.blink_speed
        self.blinking = True
        self.last_blinked = pygame.time.get_ticks()

    def _stop_blinking(self):
        self.settings.orb_speed -= self.settings.blink_speed

    def reset_movement(self):
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.rect.center = self.screen_rect.center

    def blitme(self):
        """Draw the ship at its current location"""
        self.screen.blit(self.image, self.rect)
