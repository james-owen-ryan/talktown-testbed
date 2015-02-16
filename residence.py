class ApartmentBuilding(object):
    """An apartment building on a block in a city."""

    def __init__(self, block, house_number):
        """Construct an ApartmentBuilding object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block
        self.house_number = house_number


class House(object):
    """A house on a block in a city."""

    def __init__(self, block, house_number):
        """Construct an ApartmentBuilding object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block
        self.house_number = house_number


class Apartment(object):
    """An individual apartment unit in an apartment building."""

    def __init__(self, building, unit_number):
        self.game = building.block.city.game
        self.city = building.block.city
        self.block = building.block
        self.building = building
        self.unit_number = unit_number