from config import Config
from event import HomePurchase


class DwellingPlace(object):
    """A dwelling place in a city."""

    def __init__(self, lot, owners):
        """Initialize a DwellingPlace object.

        @param lot: A Lot object representing the lot this building is on.
        """
        self.city = lot.city
        self.lot = lot
        self._init_get_named()
        self.address = self._init_generate_address()
        self.owners = set()  # Gets set via self._init_ownership()
        self.former_owners = set()
        self.residents = set()
        self.former_residents = set()
        self.transactions = []
        self.move_ins = []
        self.move_outs = []
        self._init_ownership(initial_owners=owners)

    def _init_get_named(self):
        """Get named by the owner of this building (the client for which it was constructed)."""
        pass

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        house_number = self.lot.house_number
        street = str(self.lot.street)
        return "{} {}".format(house_number, street)

    def _init_ownership(self, initial_owners):
        """Set the initial owners of this dwelling place."""
        HomePurchase(subjects=initial_owners, home=self, realtor=None)


class Apartment(DwellingPlace):
    """An individual apartment unit in an apartment building in a city."""

    def __init__(self, apartment_complex, lot, unit_number):
        super(Apartment, self).__init__(lot, owners=(apartment_complex.subject,))
        self.complex = apartment_complex
        self.unit_number = unit_number

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        house_number = self.lot.house_number
        street = str(self.lot.street)
        return "{} {} (Unit #{})".format(house_number, street, self.unit_number)


class House(DwellingPlace):
    """A house in a city.

    @param lot: A Lot object representing the lot this building is on.
    @param construction: A BusinessConstruction object holding data about
                         the construction of this building.
    """

    def __init__(self, lot, construction):
        super(House, self).__init__(lot, owners=construction.subjects)
        self.construction = construction