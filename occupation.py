from event import *


#######################################
##           NON-SPECIALIZED         ##
#######################################


class Cashier(object):
    """A cashier at a business."""

    def __init__(self, person, company):
        """Construct a Cashier object."""
        self.person = person
        self.company = company


class Manager(object):
    """A manager of a business."""

    def __init__(self, person, company):
        """Construct an Owner object."""
        self.person = person
        self.company = company


class Owner(object):
    """An owner of a business."""

    def __init__(self, person, company):
        """Construct an Owner object."""
        self.person = person
        self.company = company


#######################################
##           SPECIALIZED            ##
#######################################


class Architect(object):
    """An architect."""

    def __init__(self, person, company):
        """Construct an Architect object."""
        self.person = person
        self.company = company

    def construct_building(self, client, lot, type_of_building):
        """Return a constructed building."""
        construction = BuildingConstruction(
            architect=self, client=client, lot=lot, type_of_building=type_of_building
        )
        return construction.building


class BankTeller(object):
    """A bank teller."""

    def __init__(self, person, company):
        """Construct a BankTeller object."""
        self.person = person
        self.company = company


class Concierge(object):
    """A concierge at a hotel."""

    def __init__(self, person, company):
        """Construct a Concierge object."""
        self.person = person
        self.company = company


class ConstructionWorker(object):
    """A construction worker."""

    def __init__(self, person, company):
        """Construct a ConstructionWorker object."""
        self.person = person
        self.company = company


class Doctor(object):
    """A doctor at a hospital."""

    def __init__(self, person, company):
        """Construct a Doctor object."""
        self.person = person
        self.company = company


class FireChief(object):
    """A fire chief."""

    def __init__(self, person, company):
        """Construct a FireChief object."""
        self.person = person
        self.company = company


class Firefighter(object):
    """A firefighter."""

    def __init__(self, person, company):
        """Construct a Firefighter object."""
        self.person = person
        self.company = company


class HairStylist(object):
    """A hair stylist."""

    def __init__(self, person, company):
        """Construct a HairStylist object."""
        self.person = person
        self.company = company


class HotelMaid(object):
    """A hotel maid."""

    def __init__(self, person, company):
        """Construct a HotelMaid object."""
        self.person = person
        self.company = company


class Nurse(object):
    """A nurse at a hospital."""

    def __init__(self, person, company):
        """Construct a Nurse object."""
        self.person = person
        self.company = company


class Optometrist(object):
    """An optometrist."""

    def __init__(self, person, company):
        """Construct an Optometrist object."""
        self.person = person
        self.company = company


class PlasticSurgeon(object):
    """A plastic surgeon."""

    def __init__(self, person, company):
        """Construct a PlasticSurgeon object."""
        self.person = person
        self.company = company


class PoliceChief(object):
    """A police chief."""

    def __init__(self, person, company):
        """Construct a PoliceChief object."""
        self.person = person
        self.company = company


class PoliceOfficer(object):
    """A police officer."""

    def __init__(self, person, company):
        """Construct a PoliceOfficer object."""
        self.person = person
        self.company = company


class Realtor(object):
    """A realtor."""

    def __init__(self, person, company):
        """Construct an Realtor object."""
        self.person = person
        self.company = company


class TattooArtist(object):
    """A tattoo artist."""

    def __init__(self, person, company):
        """Construct a TattooArtist object."""
        self.person = person
        self.company = company


class Waiter(object):
    """A waiter at a restaurant."""

    def __init__(self, person, company):
        """Construct a Waiter object."""
        self.person = person
        self.company = company