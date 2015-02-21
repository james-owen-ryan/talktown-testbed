from config import Config


class House(object):
    """A house on a block in a city."""

    def __init__(self, lot, construction):
        """Initialize a House object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.lot = lot
        self.construction = construction
        self.address = self.generate_address(lot=self.lot)
        self.owners = construction.clients
        self.residents = set()
        self.transactions = []
        self.move_ins = []
        self.move_outs = []
        self.construction.construction_firm.houses_constructed.append(self)
        for owner in self.owners:
            owner.building_commissions.append(self)

    @staticmethod
    def get_named(owner):
        """Get named by the owner of this building (the client for which it was constructed)."""
        pass

    @staticmethod
    def generate_address(lot):
        """Generate an address, given the lot building is on."""
        house_number = lot.house_number
        street = str(lot.street)
        return "{} {}".format(house_number, street)


class Apartment(object):
    """An individual apartment unit in an apartment building."""

    def __init__(self, complex):
        self.city = complex.city
        self.lot = complex.lot
        self.complex = complex
        self.address = self.generate_address(lot=self.lot)
        self.owners = None  # Owned when someone moves in
        self.residents = set()
        self.transactions = []
        self.move_ins = []
        self.move_outs = []

    @staticmethod
    def get_named(owner):
        """Get named by the owner of this building (the client for which it was constructed)."""
        pass

    @staticmethod
    def generate_address(lot):
        """Generate an address, given the lot building is on."""
        house_number = lot.house_number
        street = str(lot.street)
        return "{} {}".format(house_number, street)