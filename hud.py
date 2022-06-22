from stats import Stats


class HUD:
    def __init__(self, fof):
        """Initializes the HUD for the game"""
        self.screen = fof.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = fof.settings
        self.stats = fof.stats

        self.score_text = \
            fof.get_font_1(int(100 * fof.sr)).render(str(self.stats.score),
                                                     True, (225, 0, 0))
        self.score_rect = self.score_text.get_rect(center=self.screen_rect.center)
        # self.score_rect.right = self.settings.screen_width - 110 * fof.sr
        # self.score_rect.top = self.settings.screen_height + 110 * fof.sr

    def show_score(self):
        """Blit player score onto the screen"""
        self.screen.blit(self.score_text, self.score_rect)
