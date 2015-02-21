from event import *
from config import Config


class Occupation(object):
    """An occupation at a business in a city."""

    def __init__(self, person, company, hiring):
        """Construct an Occupation object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by self.terminate
        self.terminus = None  # Changed by self.terminate
        self.person.occupation = self
        self.person.occupations.add(self)
        self.level = person.game.config.job_level[self]

    @property
    def years_experience(self):
        """Return years this person has had this occupation."""
        return self.person.game.year - self.start_date

    def terminate(self, reason):
        """Terminate this occupation, likely due to another hiring or retirement."""
        self.end_date = self.person.game.year
        self.terminus = reason


############################################
##           BUSINESS-INDEPENDENT         ##
############################################


class Cashier(Occupation):
    """A cashier at a business."""

    def __init__(self, person, company, hiring):
        """Construct a Cashier object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Janitor(Occupation):
    """A janitor at a business."""

    def __init__(self, person, company, hiring):
        """Construct a Janitor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Manager(Occupation):
    """A manager of a business."""

    def __init__(self, person, company, hiring):
        """Construct an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Owner(Occupation):
    """An owner of a business."""

    def __init__(self, person, company, hiring):
        """Construct an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


############################################
##           BUSINESS-DEPENDENT           ##
############################################


class Architect(Occupation):
    """An architect."""

    def __init__(self, person, company, hiring):
        """Construct an Architect object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)
        # Work accomplishments
        self.building_constructions = []
        self.house_constructions = []

    def construct_building(self, client, lot, type_of_building):
        """Return a constructed building."""
        construction = BuildingConstruction(
            client=client, architect=self, lot=lot, type_of_building=type_of_building
        )
        return construction.building

    def construct_house(self, clients, lot):
        """Return a constructed building."""
        construction = HouseConstruction(clients=clients, architect=self, lot=lot)
        return construction.house


class BankTeller(Occupation):
    """A bank teller."""

    def __init__(self, person, company, hiring):
        """Construct a BankTeller object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Concierge(Occupation):
    """A concierge at a hotel."""

    def __init__(self, person, company, hiring):
        """Construct a Concierge object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class ConstructionWorker(Occupation):
    """A construction worker."""

    def __init__(self, person, company, hiring):
        """Construct a ConstructionWorker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Doctor(Occupation):
    """A doctor at a hospital."""

    def __init__(self, person, company, hiring):
        """Construct a Doctor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class FireChief(Occupation):
    """A fire chief."""

    def __init__(self, person, company, hiring):
        """Construct a FireChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Firefighter(Occupation):
    """A firefighter."""

    def __init__(self, person, company, hiring):
        """Construct a Firefighter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class HairStylist(Occupation):
    """A hair stylist."""

    def __init__(self, person, company, hiring):
        """Construct a HairStylist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class HotelMaid(Occupation):
    """A hotel maid."""

    def __init__(self, person, company, hiring):
        """Construct a HotelMaid object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Nurse(Occupation):
    """A nurse at a hospital."""

    def __init__(self, person, company, hiring):
        """Construct a Nurse object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Optometrist(Occupation):
    """An optometrist."""

    def __init__(self, person, company, hiring):
        """Construct an Optometrist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class PlasticSurgeon(Occupation):
    """A plastic surgeon."""

    def __init__(self, person, company, hiring):
        """Construct a PlasticSurgeon object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class PoliceChief(Occupation):
    """A police chief."""

    def __init__(self, person, company, hiring):
        """Construct a PoliceChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class PoliceOfficer(Occupation):
    """A police officer."""

    def __init__(self, person, company, hiring):
        """Construct a PoliceOfficer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Realtor(Occupation):
    """A realtor."""

    def __init__(self, person, company, hiring):
        """Construct an Realtor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)
        # Work accomplishments
        self.home_sales = []

    def sell_home(self, clients, home):
        """Return a sold home."""
        home_purchase = HomePurchase(clients=clients, home=home, realtor=self)
        return home_purchase.home


class TattooArtist(Occupation):
    """A tattoo artist."""

    def __init__(self, person, company, hiring):
        """Construct a TattooArtist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)


class Waiter(Occupation):
    """A waiter at a restaurant."""

    def __init__(self, person, company, hiring):
        """Construct a Waiter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        Occupation.__init__(self=self, person=person, company=company, hiring=hiring)