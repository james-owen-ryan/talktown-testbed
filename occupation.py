from event import *


class Occupation(object):
    """An occupation at a business in a city."""

    def __init__(self, person, company):
        """Initialize an Occupation object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        self.person = person
        self.company = company
        self.company.employees.add(self)
        self.start_date = person.game.year
        self.hiring = None  # event.Hiring object holding data about the hiring; gets set by that object's __init__()
        self.end_date = None  # Changed by self.terminate
        self.terminus = None  # Changed by self.terminate
        # Note: self.person.occupation gets set by Business.hire(), because there's
        # a really tricky pipeline that has to be maintained
        self.person.occupations.append(self)
        # Set job level of this occupation
        self.level = person.game.config.job_levels[self.__class__]
        # Set industry and what industry a potential applicant must come from to be hired for this occupation
        self.industry = person.game.config.industries[self.__class__]
        self.prerequisite_industry = person.game.config.prerequisite_industries[self.__class__]

    @property
    def years_experience(self):
        """Return years this person has had this occupation."""
        return self.person.game.year - self.start_date

    def terminate(self, reason):
        """Terminate this occupation, due to another hiring, retirement, or death or departure."""
        self.end_date = self.person.game.year
        self.terminus = reason
        if not isinstance(reason, Hiring) and reason.promotion:
            self.company.employees.remove(self)
            self.company.former_employees.add(self)
        # If the person hasn't already been hired to a new position, set their
        # occupation attribute to None
        if self.person.occupation is self:
            self.person.occupation = None
        # This position is now vacant, so now have the company that this person worked
        # for fill that now vacant position (which may cause a hiring chain)
        position_that_is_now_vacant = self.__class__
        self.company.hire(occupation_of_need=position_that_is_now_vacant)


##################################
##      BUSINESS-INDEPENDENT    ##
##################################


class Cashier(Occupation):
    """A cashier at a business."""

    def __init__(self, person, company):
        """Initialize a Cashier object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Cashier, self).__init__(person=person, company=company)


class Janitor(Occupation):
    """A janitor at a business."""

    def __init__(self, person, company):
        """Initialize a Janitor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Janitor, self).__init__(person=person, company=company)


class Manager(Occupation):
    """A manager at a business."""

    def __init__(self, person, company):
        """Initialize an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Manager, self).__init__(person=person, company=company)


class Secretary(Occupation):
    """A secretary at a business."""

    def __init__(self, person, company):
        """Initialize an Secretary object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Secretary, self).__init__(person=person, company=company)


class Owner(Occupation):
    """An owner of a business."""

    def __init__(self, person, company):
        """Initialize an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Owner, self).__init__(person=person, company=company)


##################################
##      BUSINESS-SEMIDEPENDENT  ##
##################################


class Groundskeeper(Occupation):
    """A mortician at a cemetery or park."""

    def __init__(self, person, company):
        """Initialize a Mortician object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Groundskeeper, self).__init__(person=person, company=company)


class Nurse(Occupation):
    """A nurse at a hospital or optometry clinic or plastic-surgery clinic."""

    def __init__(self, person, company):
        """Initialize a Nurse object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Nurse, self).__init__(person=person, company=company)


##################################
##      BUSINESS-DEPENDENT      ##
##################################


class Architect(Occupation):
    """An architect at a construction firm."""

    def __init__(self, person, company):
        """Initialize an Architect object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Architect, self).__init__(person=person, company=company)
        # Work accomplishments
        self.building_constructions = []
        self.house_constructions = []

    def construct_building(self, client, business):
        """Return a constructed building."""
        construction = BusinessConstruction(subject=client, business=business, architect=self)
        return construction

    def construct_house(self, clients, lot):
        """Return a constructed building."""
        construction = HouseConstruction(subjects=clients, architect=self, lot=lot)
        return construction.house


class BankTeller(Occupation):
    """A bank teller at a bank."""

    def __init__(self, person, company):
        """Initialize a BankTeller object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(BankTeller, self).__init__(person=person, company=company)


class BusDriver(Occupation):
    """A bus driver at a bus depot."""

    def __init__(self, person, company):
        """Initialize a BusDriver object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(BusDriver, self).__init__(person=person, company=company)


class Concierge(Occupation):
    """A concierge at a hotel."""

    def __init__(self, person, company):
        """Initialize a Concierge object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Concierge, self).__init__(person=person, company=company)


class ConstructionWorker(Occupation):
    """A construction worker at a construction firm."""

    def __init__(self, person, company):
        """Initialize a ConstructionWorker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(ConstructionWorker, self).__init__(person=person, company=company)


class Doctor(Occupation):
    """A doctor at a hospital."""

    def __init__(self, person, company):
        """Initialize a Doctor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Doctor, self).__init__(person=person, company=company)
        # Work accomplishments
        self.baby_deliveries = []

    def deliver_baby(self, mother):
        """Instantiate a new Birth object."""
        Birth(mother=mother, doctor=self)


class FireChief(Occupation):
    """A fire chief at a fire station."""

    def __init__(self, person, company):
        """Initialize a FireChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(FireChief, self).__init__(person=person, company=company)


class Firefighter(Occupation):
    """A firefighter at a fire station."""

    def __init__(self, person, company):
        """Initialize a Firefighter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Firefighter, self).__init__(person=person, company=company)


class HairStylist(Occupation):
    """A hair stylist at a barbershop."""

    def __init__(self, person, company):
        """Initialize a HairStylist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(HairStylist, self).__init__(person=person, company=company)


class HotelMaid(Occupation):
    """A hotel maid at a hotel."""

    def __init__(self, person, company):
        """Initialize a HotelMaid object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(HotelMaid, self).__init__(person=person, company=company)


class Lawyer(Occupation):
    """A lawyer at a law firm."""

    def __init__(self, person, company):
        """Initialize a Lawyer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Lawyer, self).__init__(person=person, company=company)
        # Work accomplishments
        self.filed_divorces = []
        self.filed_name_changes = []

    def file_divorce(self, clients):
        """File a name change on behalf of person."""
        Divorce(subjects=clients, lawyer=self)

    def file_name_change(self, person, new_last_name, reason):
        """File a name change on behalf of person."""
        NameChange(subject=person, new_last_name=new_last_name, reason=reason, lawyer=self)


class Mayor(Occupation):
    """A mayor at the city hall."""

    def __init__(self, person, company):
        """Initialize a Mayor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Mayor, self).__init__(person=person, company=company)


class Mortician(Occupation):
    """A mortician at a cemetery."""

    def __init__(self, person, company):
        """Initialize a Mortician object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Mortician, self).__init__(person=person, company=company)
        # Work accomplishments
        self.body_interments = []

    def inter_body(self, deceased, cause_of_death):
        """Inter a body in a cemetery."""
        Death(subject=deceased, mortician=self, cause_of_death=cause_of_death)


class Optometrist(Occupation):
    """An optometrist at an optometry clinic."""

    def __init__(self, person, company):
        """Initialize an Optometrist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Optometrist, self).__init__(person=person, company=company)


class PlasticSurgeon(Occupation):
    """A plastic surgeon at a plastic-surgery clinic."""

    def __init__(self, person, company):
        """Initialize a PlasticSurgeon object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(PlasticSurgeon, self).__init__(person=person, company=company)


class PoliceChief(Occupation):
    """A police chief at a police station."""

    def __init__(self, person, company):
        """Initialize a PoliceChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(PoliceChief, self).__init__(person=person, company=company)


class PoliceOfficer(Occupation):
    """A police officer at a police station."""

    def __init__(self, person, company):
        """Initialize a PoliceOfficer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(PoliceOfficer, self).__init__(person=person, company=company)


class Professor(Occupation):
    """A professor at the university."""

    def __init__(self, person, company):
        """Initialize a Professor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Professor, self).__init__(person=person, company=company)


class Realtor(Occupation):
    """A realtor at a realty firm."""

    def __init__(self, person, company):
        """Initialize an Realtor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Realtor, self).__init__(person=person, company=company)
        # Work accomplishments
        self.home_sales = []

    def sell_home(self, clients, home):
        """Return a sold home."""
        home_sales = HomePurchase(subjects=clients, home=home, realtor=self)
        return home_sales.home


class TattooArtist(Occupation):
    """A tattoo artist at a tattoo parlor."""

    def __init__(self, person, company):
        """Initialize a TattooArtist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(TattooArtist, self).__init__(person=person, company=company)


class TaxiDriver(Occupation):
    """A taxi driver at a taxi depot."""

    def __init__(self, person, company):
        """Initialize a TaxiDriver object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(TaxiDriver, self).__init__(person=person, company=company)


class Waiter(Occupation):
    """A waiter at a restaurant."""

    def __init__(self, person, company):
        """Initialize a Waiter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Waiter, self).__init__(person=person, company=company)