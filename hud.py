from stats import Stats


class HUD:
    def __init__(self, fof):
        """Initializes the HUD for the game"""
        self.score_rect = None
        self.score_text = None
        self.game = fof
        self.screen = self.game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = fof.settings
        self.stats = fof.stats
        self.update_score()

    def update_score(self):
        self.score_text = \
            self.game.get_font_2(int(50 * self.game.sr)).render(
                str(self.stats.score), True, "White")
        self.score_rect = \
            self.score_text.get_rect(
                right=self.settings.screen_width - int(40 * self.game.sr),
                top=int(40 * self.game.sr))

    def show_score(self):
        """Blit player score onto the screen"""
        self.screen.blit(self.score_text, self.score_rect)
