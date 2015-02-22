# There are two types of landmarks: Cemetery and Park. The distinction
# between a landmark and a business is that a landmark does not have a
# building and is not owned by anyone.


class Landmark(object):
    """A landmark on a tract in a city."""

    def __init__(self, tract):
        """Initialize a Landmark object."""
        self.city = tract.city
        self.founded = self.city.game.year
        self.tract = tract
        self.employees = set()
        self.address = self._init_generate_address()

    def _init_get_named(self):
        """Get named by [???]."""
        pass

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        house_number = self.tract.house_number
        street = str(self.tract.street)
        return "{} {}".format(house_number, street)


class Cemetery(Landmark):
    """A cemetery on a tract in a city."""

    def __init__(self, tract):
        """Initialize a Cemetery object."""
        super(Cemetery, self).__init__(tract)
        self.plots = {}

    def inter_person(self, person):
        """Inter a new person by assigning them a plot in the graveyard."""
        new_plot_number = max(self.plots) + 1
        self.plots[new_plot_number] = person


class Park(Landmark):
    """A park on a tract in a city."""

    def __init__(self, tract):
        """Initialize a Park object."""
        super(Park, self).__init__(tract)