from event import *
from config import Config


#######################################
##           NON-SPECIALIZED         ##
#######################################


class Cashier(object):
    """A cashier at a business."""

    def __init__(self, person, company, hiring):
        """Construct a Cashier object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_cashier
        self.person.occupation = self
        self.person.occupations.add(self)


class Janitor(object):
    """A janitor at a business."""

    def __init__(self, person, company, hiring):
        """Construct a Janitor object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_janitor
        self.person.occupation = self
        self.person.occupations.add(self)


class Manager(object):
    """A manager of a business."""

    def __init__(self, person, company, hiring):
        """Construct an Owner object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_manager
        self.person.occupation = self
        self.person.occupations.add(self)


class Owner(object):
    """An owner of a business."""

    def __init__(self, person, company, hiring):
        """Construct an Owner object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_owner
        self.person.occupation = self
        self.person.occupations.add(self)


#######################################
##           SPECIALIZED            ##
#######################################


class Architect(object):
    """An architect."""

    def __init__(self, person, company, hiring):
        """Construct an Architect object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_architect
        self.person.occupation = self
        self.person.occupations.add(self)
        # Work accomplishments
        self.building_constructions = []
        self.house_constructions = []

    @property
    def years_experience(self):
        """Return years this person has had this occupation."""
        return self.person.game.year - self.start_date

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


class BankTeller(object):
    """A bank teller."""

    def __init__(self, person, company, hiring):
        """Construct a BankTeller object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_bank_teller
        self.person.occupation = self
        self.person.occupations.add(self)


class Concierge(object):
    """A concierge at a hotel."""

    def __init__(self, person, company, hiring):
        """Construct a Concierge object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_concierge
        self.person.occupation = self
        self.person.occupations.add(self)


class ConstructionWorker(object):
    """A construction worker."""

    def __init__(self, person, company, hiring):
        """Construct a ConstructionWorker object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_construction_worker
        self.person.occupation = self
        self.person.occupations.add(self)


class Doctor(object):
    """A doctor at a hospital."""

    def __init__(self, person, company, hiring):
        """Construct a Doctor object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_doctor
        self.person.occupation = self
        self.person.occupations.add(self)


class FireChief(object):
    """A fire chief."""

    def __init__(self, person, company, hiring):
        """Construct a FireChief object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_fire_chief
        self.person.occupation = self
        self.person.occupations.add(self)


class Firefighter(object):
    """A firefighter."""

    def __init__(self, person, company, hiring):
        """Construct a Firefighter object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_firefighter
        self.person.occupation = self
        self.person.occupations.add(self)


class HairStylist(object):
    """A hair stylist."""

    def __init__(self, person, company, hiring):
        """Construct a HairStylist object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_hair_stylist
        self.person.occupation = self
        self.person.occupations.add(self)


class HotelMaid(object):
    """A hotel maid."""

    def __init__(self, person, company, hiring):
        """Construct a HotelMaid object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_hotel_maid
        self.person.occupation = self
        self.person.occupations.add(self)


class Nurse(object):
    """A nurse at a hospital."""

    def __init__(self, person, company, hiring):
        """Construct a Nurse object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_nurse
        self.person.occupation = self
        self.person.occupations.add(self)


class Optometrist(object):
    """An optometrist."""

    def __init__(self, person, company, hiring):
        """Construct an Optometrist object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_optometrist
        self.person.occupation = self
        self.person.occupations.add(self)


class PlasticSurgeon(object):
    """A plastic surgeon."""

    def __init__(self, person, company, hiring):
        """Construct a PlasticSurgeon object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_plastic_surgeon
        self.person.occupation = self
        self.person.occupations.add(self)


class PoliceChief(object):
    """A police chief."""

    def __init__(self, person, company, hiring):
        """Construct a PoliceChief object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_police_chief
        self.person.occupation = self
        self.person.occupations.add(self)


class PoliceOfficer(object):
    """A police officer."""

    def __init__(self, person, company, hiring):
        """Construct a PoliceOfficer object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_police_officer
        self.person.occupation = self
        self.person.occupations.add(self)


class Realtor(object):
    """A realtor."""

    def __init__(self, person, company, hiring):
        """Construct an Realtor object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_realtor
        self.person.occupation = self
        self.person.occupations.add(self)
        # Work accomplishments
        self.home_sales = []

    def sell_home(self, clients, home):
        """Return a sold home."""
        home_purchase = HomePurchase(clients=clients, home=home, realtor=self)
        return home_purchase.home


class TattooArtist(object):
    """A tattoo artist."""

    def __init__(self, person, company, hiring):
        """Construct a TattooArtist object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_tattoo_artist
        self.person.occupation = self
        self.person.occupations.add(self)


class Waiter(object):
    """A waiter at a restaurant."""

    def __init__(self, person, company, hiring):
        """Construct a Waiter object."""
        self.person = person
        self.company = company
        self.hiring = hiring  # event.Hiring object holding data about the hiring
        self.start_date = person.game.year
        self.end_date = None  # Changed by Hiring.__init__() of next job
        self.level = person.game.config.job_level_waiter
        self.person.occupation = self
        self.person.occupations.add(self)