from config import Config


class Game(object):
    """A gameplay instance."""

    def __init__(self):
        """Initialize a Game object."""
        self.config = Config()
        self.year = self.config.year_city_gets_founded
        self.true_year = self.config.year_city_gets_founded  # True year never gets changed during retconning

    def establish_setting(self):
        """Establish the city in which this gameplay instance will take place."""
        return self

    def advance_one_year(self):
        """Advance one year (the timestep during simulation."""
        self.true_year += 1
        self.year = self.true_year