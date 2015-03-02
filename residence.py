import random


class DwellingPlace(object):
    """A dwelling place in a city."""

    def __init__(self, lot, owners):
        """Initialize a DwellingPlace object.

        @param lot: A Lot object representing the lot this building is on.
        """
        self.city = lot.city
        self.city.dwelling_places.add(self)
        self.lot = lot
        self.address = self.lot.address
        self.residents = set()
        self.former_residents = set()
        self.transactions = []
        self.move_ins = []
        self.move_outs = []
        self.owners = set()  # Gets set via self._init_ownership()
        self.former_owners = set()
        self._init_ownership(initial_owners=owners)
        self.name = None  # Gets set by _init_get_named()
        self._init_get_named()
        self.people_here_now = set()  # People at home on a specific time step (either a resident or visitor)

    def __str__(self):
        """Return string representation."""
        return "{0}, {1}".format(self.name, self.address)

    def _init_get_named(self):
        """Get named by the owner of this building (the client for which it was constructed)."""

        owner_surnames = set([o.last_name for o in self.owners])
        self.name = "{0} Residence".format('-'.join(owner_surnames))

    def _init_ownership(self, initial_owners):
        """Set the initial owners of this dwelling place."""
        # I'm doing this klugey thing for now because of circular-dependency issue
        list(initial_owners)[0].purchase_home(purchasers=initial_owners, home=self)
        # HomePurchase(subjects=initial_owners, home=self, realtor=None)


class Apartment(DwellingPlace):
    """An individual apartment unit in an apartment building in a city."""

    def __init__(self, apartment_complex, lot, unit_number):
        self.apartment, self.house = True, False
        self.complex = apartment_complex
        self.unit_number = unit_number
        super(Apartment, self).__init__(lot, owners=(apartment_complex.owner.person,))

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        index_of_street_address_will_be_on = random.randint(0, len(self.lot.streets)-1)
        house_number = int(self.lot.house_numbers[index_of_street_address_will_be_on])
        street = self.lot.streets[index_of_street_address_will_be_on]
        return "{0} {1} (Unit #{2})".format(house_number, street, self.unit_number)


class House(DwellingPlace):
    """A house in a city.

    @param lot: A Lot object representing the lot this building is on.
    @param construction: A BusinessConstruction object holding data about
                         the construction of this building.
    """

    def __init__(self, lot, construction):
        self.apartment, self.house = False, True
        super(House, self).__init__(lot, owners=construction.subjects)
        self.construction = construction
        self.lot.building = self