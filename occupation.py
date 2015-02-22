from event import *
from config import Config


class Occupation(object):
    """An occupation at a business in a city."""

    def __init__(self, person, company, hiring):
        """Initialize an Occupation object.

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
        self.level = person.game.config.job_levels[self.__class__]

    @property
    def years_experience(self):
        """Return years this person has had this occupation."""
        return self.person.game.year - self.start_date

    def terminate(self, reason):
        """Terminate this occupation, likely due to another hiring or retirement."""
        self.end_date = self.person.game.year
        self.terminus = reason


##################################
##      BUSINESS-INDEPENDENT    ##
##################################


class Cashier(Occupation):
    """A cashier at a business."""

    def __init__(self, person, company, hiring):
        """Initialize a Cashier object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Cashier, self).__init__(person=person, company=company, hiring=hiring)


class Janitor(Occupation):
    """A janitor at a business."""

    def __init__(self, person, company, hiring):
        """Initialize a Janitor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Janitor, self).__init__(person=person, company=company, hiring=hiring)


class Manager(Occupation):
    """A manager of a business."""

    def __init__(self, person, company, hiring):
        """Initialize an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Manager, self).__init__(person=person, company=company, hiring=hiring)


class Owner(Occupation):
    """An owner of a business."""

    def __init__(self, person, company, hiring):
        """Initialize an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Owner, self).__init__(person=person, company=company, hiring=hiring)


##################################
##      BUSINESS-SEMIDEPENDENT  ##
##################################


class Groundskeeper(Occupation):
    """A mortician at a cemetery or park."""

    def __init__(self, person, company, hiring):
        """Initialize a Mortician object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Groundskeeper, self).__init__(person=person, company=company, hiring=hiring)


class Nurse(Occupation):
    """A nurse at a hospital or optometry clinic or plastic-surgery clinic."""

    def __init__(self, person, company, hiring):
        """Initialize a Nurse object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Nurse, self).__init__(person=person, company=company, hiring=hiring)


##################################
##      BUSINESS-DEPENDENT      ##
##################################


class Architect(Occupation):
    """An architect."""

    def __init__(self, person, company, hiring):
        """Initialize an Architect object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Architect, self).__init__(person=person, company=company, hiring=hiring)
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
        """Initialize a BankTeller object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(BankTeller, self).__init__(person=person, company=company, hiring=hiring)


class Concierge(Occupation):
    """A concierge at a hotel."""

    def __init__(self, person, company, hiring):
        """Initialize a Concierge object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Concierge, self).__init__(person=person, company=company, hiring=hiring)


class ConstructionWorker(Occupation):
    """A construction worker."""

    def __init__(self, person, company, hiring):
        """Initialize a ConstructionWorker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(ConstructionWorker, self).__init__(person=person, company=company, hiring=hiring)


class Doctor(Occupation):
    """A doctor at a hospital."""

    def __init__(self, person, company, hiring):
        """Initialize a Doctor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Doctor, self).__init__(person=person, company=company, hiring=hiring)
        # Work accomplishments
        self.baby_deliveries = []

    def deliver_baby(self, mother):
        """Instantiate a new Birth object."""
        Birth(mother=mother, doctor=self)


class FireChief(Occupation):
    """A fire chief."""

    def __init__(self, person, company, hiring):
        """Initialize a FireChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(FireChief, self).__init__(person=person, company=company, hiring=hiring)


class Firefighter(Occupation):
    """A firefighter."""

    def __init__(self, person, company, hiring):
        """Initialize a Firefighter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Firefighter, self).__init__(person=person, company=company, hiring=hiring)


class HairStylist(Occupation):
    """A hair stylist."""

    def __init__(self, person, company, hiring):
        """Initialize a HairStylist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(HairStylist, self).__init__(person=person, company=company, hiring=hiring)


class HotelMaid(Occupation):
    """A hotel maid."""

    def __init__(self, person, company, hiring):
        """Initialize a HotelMaid object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(HotelMaid, self).__init__(person=person, company=company, hiring=hiring)


class Mortician(Occupation):
    """A mortician at a cemetery."""

    def __init__(self, person, company, hiring):
        """Initialize a Mortician object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Mortician, self).__init__(person=person, company=company, hiring=hiring)

    def inter_body(self, deceased, cause_of_death):
        """Inter a body in a cemetery."""
        Death(subject=deceased, mortician=self, cause_of_death=cause_of_death)


class Optometrist(Occupation):
    """An optometrist."""

    def __init__(self, person, company, hiring):
        """Initialize an Optometrist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Optometrist, self).__init__(person=person, company=company, hiring=hiring)


class PlasticSurgeon(Occupation):
    """A plastic surgeon."""

    def __init__(self, person, company, hiring):
        """Initialize a PlasticSurgeon object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(PlasticSurgeon, self).__init__(person=person, company=company, hiring=hiring)


class PoliceChief(Occupation):
    """A police chief."""

    def __init__(self, person, company, hiring):
        """Initialize a PoliceChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(PoliceChief, self).__init__(person=person, company=company, hiring=hiring)


class PoliceOfficer(Occupation):
    """A police officer."""

    def __init__(self, person, company, hiring):
        """Initialize a PoliceOfficer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(PoliceOfficer, self).__init__(person=person, company=company, hiring=hiring)


class Realtor(Occupation):
    """A realtor."""

    def __init__(self, person, company, hiring):
        """Initialize an Realtor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Realtor, self).__init__(person=person, company=company, hiring=hiring)
        # Work accomplishments
        self.home_sales = []

    def sell_home(self, clients, home):
        """Return a sold home."""
        home_sales = HomePurchase(clients=clients, home=home, realtor=self)
        return home_sales.home


class TattooArtist(Occupation):
    """A tattoo artist."""

    def __init__(self, person, company, hiring):
        """Initialize a TattooArtist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(TattooArtist, self).__init__(person=person, company=company, hiring=hiring)


class Waiter(Occupation):
    """A waiter at a restaurant."""

    def __init__(self, person, company, hiring):
        """Initialize a Waiter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param hiring: The Hiring object that constructed this object and holds metadata about
                       the person's hiring into this occupation at this company.
        """
        super(Waiter, self).__init__(person=person, company=company, hiring=hiring)