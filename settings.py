import pygame


class Settings:
    """
    === Attributes ===
    screen_width: default user's screen width
    screen_height: default user's screen height
    bg_colour: tuple containing RGB values of the screen
    """
    screen_width: int
    screen_height: int
    bg_colour: tuple[int, int, int]

    def __init__(self):
        # Screen Settings
        screen_size = pygame.display.Info()
        self.screen_width = screen_size.current_w
        self.screen_height = screen_size.current_h
        self.screen_ratio = self.screen_width / 2560
        self.bg_colour = (0, 0, 0)
        self.orb_speed = 3.5
        self.blink_speed = 30
        self.blink_time = 15
        self.rotation_speed = 75
        self.laser_speed = 30
        self.cloud_speed = 5
        self.cloud_cooldown = 1600
        self.cloud_cooldown_min = 400
        self.max_enemies = 50


class Crosshair:
    def __init__(self, fof):
        image = pygame.image.load('images/crosshair.bmp')
        self.image = pygame.transform.smoothscale(image, (17, 17))
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()
        self.screen = fof.screen

    def update_crosshair(self):
        self.rect.center = pygame.mouse.get_pos()

    def blitme(self):
        self.screen.blit(self.image, self.rect)
