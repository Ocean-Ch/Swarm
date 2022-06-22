class Stats:
    """Class to track player stats
    """
    def __init__(self, fof):
        self.settings = fof.settings
        self.score = 0
        self.reset()

    def reset(self):
        self.score = 0
