class Park(object):
    """A park on a block in a city."""

    def __init__(self, block):
        """Construct a Park object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block