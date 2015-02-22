# There are two types of landmarks: Cemetery and Park. The distinction
# between a landmark and a business is that a landmark does not have a
# building and is not owned by anyone.


class Cemetery(object):
    """A cemetery on a tract in a city."""

    def __init__(self, block):
        """Initialize a Cemetery object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block

        # groundskeepers, mortician


class Park(object):
    """A park on a tract in a city."""

    def __init__(self, block):
        """Initialize a Park object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block

        # groundskeepers