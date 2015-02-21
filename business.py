import heapq
from config import Config
from occupation import *


# Objects of a business class represents both the company itself and the building
# at which it is headquartered. All business subclasses inherit generic attributes
# and methods from the superclass Business, and each define their own methods as
# appropriate.


class Business(object):
    """A business in a city (representing both the notion of a company and its physical building)."""

    def __init__(self, lot, construction):
        """Construct a Business object.

        @param lot: A Lot object representing the lot this company's building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this company's building.
        """
        self.city = lot.city
        self.founded = self.city.game.year
        self.lot = lot
        self.construction = construction
        self.owner = construction.client
        self.owner.building_commissions.append(self)
        self.employees = set()
        self.address = self.init_generate_address(lot=self.lot)

    @staticmethod
    def init_get_named(owner):
        """Get named by the owner of this building (the client for which it was constructed)."""
        pass

    @staticmethod
    def init_generate_address(lot):
        """Generate an address, given the lot building is on."""
        house_number = lot.house_number
        street = str(lot.street)
        return "{} {}".format(house_number, street)

    def hire(self, occupation):
        """Scour the job market to hire someone to fulfill the duties of occupation."""
        job_candidates_in_town = self._assemble_job_candidates(occupation=occupation)
        if job_candidates_in_town:
            candidate_scores = self._rate_all_job_candidates(candidates=job_candidates_in_town)
            selected_candidate = self._select_candidate(candidate_scores=candidate_scores)
        else:
            selected_candidate = self._find_candidate_from_outside_the_city()
        Hiring(subject=selected_candidate, company=self, occupation=occupation)

    def _select_candidate(self, candidate_scores):
        """Select a person to serve in a certain occupational capacity."""
        # Pick from top three
        top_three_choices = heapq.nlargest(3, candidate_scores, key=candidate_scores.get)
        if random.random() < 0.6:
            chosen_candidate = top_three_choices[0]
        elif random.random() < 0.9:
            chosen_candidate = top_three_choices[1]
        else:
            chosen_candidate = top_three_choices[2]
        return chosen_candidate

    def _find_candidate_from_outside_the_city(self):
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

    def _rate_all_job_candidates(self, candidates):
        """Rate all job candidates."""
        scores = {}
        for candidate in candidates:
            scores[candidate] = self._rate_job_candidate(person=candidate)
        return scores

    def _rate_job_candidate(self, person):
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

    def _assemble_job_candidates(self, occupation):
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


class ApartmentComplex(Business):
    """An apartment complex."""

    def __init__(self, lot, construction):
        """Construct an ApartmentComplex object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)


class Bank(Business):
    """A bank."""

    def __init__(self, lot, construction):
        """Construct a Bank object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # tellers, manager, janitors


class Barbershop(Business):
    """A barbershop."""

    def __init__(self, lot, construction):
        """Construct a Barbershop object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # hair stylists, cashiers, manager


class ConstructionFirm(Business):
    """A construction firm."""

    def __init__(self, lot, construction):
        """Construct an ConstructionFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # architects, construction workers, janitors

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


class OptometryClinic(Business):
    """An optometry clinic."""

    def __init__(self, lot, construction):
        """Construct an OptometryClinic object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # optometrist(s), cashiers, manager, janitors


class FireStation(Business):
    """A fire station."""

    def __init__(self, lot, construction):
        """Construct an FireStation object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # Firefighters, chief, janitors


class Hospital(Business):
    """A hospital."""

    def __init__(self, lot, construction):
        """Construct an Hospital object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # Doctors, nurses, manager, janitors


class Hotel(Business):
    """A hotel."""

    def __init__(self, lot, construction):
        """Construct a Hotel object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # concierge(s), maids, cashier, manager


class PlasticSurgeryClinic(Business):
    """A plastic-surgery clinic."""

    def __init__(self, lot, construction):
        """Construct a PlasticSurgeryClinic object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # plastic surgeons, manager


class PoliceStation(Business):
    """A police station."""

    def __init__(self, lot, construction):
        """Construct a PoliceStation object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # police officers, chief


class RealtyFirm(Business):
    """A realty firm."""

    def __init__(self, lot, construction):
        """Construct an RealtyFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # realtors, manager

    @property
    def home_sales(self):
        """Return all home sales."""
        home_sales = set()
        for realtor in self.realtors | self.former_realtors:
            home_sales |= realtor.home_sales
        return home_sales


class Restaurant(Business):
    """A restaurant."""

    def __init__(self, lot, construction):
        """Construct a Restaurant object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # cashiers, waiters, manager


class Supermarket(Business):
    """A supermarket on a lot in a city."""

    def __init__(self, lot, construction):
        """Construct an Supermarket object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # cashiers, manager


class TattooParlor(Business):
    """A tattoo parlor."""

    def __init__(self, lot, construction):
        """Construct a TattooParlor object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        Business.__init__(self=self, lot=lot, construction=construction)

        # tattoo artists, cashiers, manager