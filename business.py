import heapq
from config import Config
from occupation import *


# A business Class represents both the company itself and the building
# at which it is headquartered.


class ApartmentComplex(object):
    """An apartment complex."""

    def __init__(self, lot, construction):
        """Construct an ApartmentComplex object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)
        self.manager = self.hire(occupation=Manager)
        self.employees = set()
        self.construction.construction_firm.buildings_constructed.append(self)
        self.owner.building_commissions.append(self)

    def hire(self, candidate):
        """Formally hire a person."""


    def select_candidate(self, occupation):
        """Select a person to serve in a certain occupational capacity."""
        candidates = self.assemble_job_candidates(occupation=occupation)
        if not candidates:
            chosen_candidate = self.find_candidate_from_outside_the_city()
        else:
            candidate_scores = self.rate_all_job_candidates(candidates=candidates)
            # Pick from top three
            top_three_choices = heapq.nlargest(3, candidate_scores, key=candidate_scores.get)
            if random.random() < 0.6:
                chosen_candidate = top_three_choices[0]
            elif random.random() < 0.9:
                chosen_candidate = top_three_choices[1]
            else:
                chosen_candidate = top_three_choices[2]
        return chosen_candidate

    def find_candidate_from_outside_the_city(self):
        """Generate a person with no parents to move into the city for this job."""
        config = self.city.game.config
        age_of_this_person = random.normalvariate(
            config.generated_job_candidate_from_outside_city_age_mean,
            config.generated_job_candidate_from_outside_city_age_sd
        )
        if age_of_this_person < config.generated_job_candidate_from_outside_city_age_floor:
            age_of_this_person = config.generated_job_candidate_from_outside_city_age_floor
        elif age_of_this_person > config.generated_job_candidate_from_outside_city_age_cap:
            age_of_this_person = config.generated_job_candidate_from_outside_city_age_cap
        birth_year_of_this_person = self.city.game.year-age_of_this_person
        candidate = Person(mother=None, father=None, birth_year=birth_year_of_this_person)
        return candidate

    def rate_all_job_candidates(self, candidates):
        """Rate all job candidates."""
        scores = {}
        for candidate in candidates:
            scores[candidate] = self.rate_job_candidate(person=candidate)
        return scores

    def rate_job_candidate(self, person):
        """Rate a job candidate, given an open position and owner biases."""
        config = self.city.game.config
        score = 0
        if person in self.employees:
            score += config.preference_to_hire_from_within_company
        if person in self.owner.immediate_family:
            score += config.preference_to_hire_immediate_family
        elif person in self.owner.extended_family:  # elif because immediate family is subset of extended family
            score += config.preference_to_hire_extended_family
        if person in self.owner.friends:
            score += config.preference_to_hire_friend
        elif person in self.owner.known_people:
            score += config.preference_to_hire_known_person
        if person.occupation:
            score *= person.occupation.level
        else:
            score *= config.unemployment_occupation_level
        return score

    def assemble_job_candidates(self, occupation):
        """Assemble a group of job candidates for an open position."""
        candidates = set()
        # Consider employees in this company for promotion
        for employee in self.employees:
            if employee.occupation.level < occupation.level:
                candidates.add(employee)
        # Consider people that work elsewhere in the city
        for company in self.city.companies-self:
            for employee in company.employees:
                if employee.occupation.level < occupation.level:
                    candidates.add(employee)
        # Consider unemployed (young) people
        candidates |= self.city.unemployed_people
        return candidates

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


class Bank(object):
    """A bank."""

    def __init__(self, lot, construction):
        """Construct a Bank object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # tellers, manager

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


class Barbershop(object):
    """A barbershop."""

    def __init__(self, lot, construction):
        """Construct a Barbershop object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # hair stylists, cashiers, manager

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


class ConstructionFirm(object):
    """A construction firm."""

    def __init__(self, lot, construction):
        """Construct an ConstructionFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)
        self.architects = set()
        self.former_architects = set()
        self.construction_workers = []
        self.former_construction_workers = []

        # architects, construction workers, janitors?

    @property
    def house_constructions(self):
        """Return all house constructions."""
        house_constructions = set()
        for architect in self.architects | self.former_architects:
            house_constructions |= architect.house_constructions
        return house_constructions

    @property
    def building_constructions(self):
        """Return all building constructions."""
        building_constructions = set()
        for architect in self.architects | self.former_architects:
            building_constructions |= architect.building_constructions
        return building_constructions

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


class OptometryClinic(object):
    """An optometry clinic."""

    def __init__(self, lot, construction):
        """Construct an OptometryClinic object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # optometrist(s), cashiers, manager

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


class FireStation(object):
    """A fire station."""

    def __init__(self, lot, construction):
        """Construct an FireStation object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # Firefighters, chief

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


class Hospital(object):
    """A hospital."""

    def __init__(self, lot, construction):
        """Construct an Hospital object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # Doctors, nurses, manager

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


class Hotel(object):
    """A hotel."""

    def __init__(self, lot, construction):
        """Construct a Hotel object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # concierge(s), maids, cashier, manager

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


class PlasticSurgeryClinic(object):
    """A plastic-surgery clinic."""

    def __init__(self, lot, construction):
        """Construct a PlasticSurgeryClinic object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # plastic surgeons, manager

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


class PoliceStation(object):
    """A police station."""

    def __init__(self, lot, construction):
        """Construct a PoliceStation object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # police officers, chief

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


class RealtyFirm(object):
    """A realty firm."""

    def __init__(self, lot, construction):
        """Construct an RealtyFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)
        self.realtors = set()
        self.former_realtors = set()

        # realtors, manager

    @property
    def home_sales(self):
        """Return all home sales."""
        home_sales = set()
        for realtor in self.realtors | self.former_realtors:
            home_sales |= realtor.home_sales
        return home_sales

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


class Restaurant(object):
    """A restaurant."""

    def __init__(self, lot, construction):
        """Construct a Restaurant object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # cashiers, waiters, manager

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


class Supermarket(object):
    """A supermarket on a lot in a city."""

    def __init__(self, lot, construction):
        """Construct an Supermarket object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # cashiers, manager

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


class TattooParlor(object):
    """A tattoo parlor."""

    def __init__(self, lot, construction):
        """Construct a TattooParlor object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.address = self.generate_address(lot=self.lot)

        # tattoo artists, cashiers, manager

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