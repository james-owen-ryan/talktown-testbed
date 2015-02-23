import heapq
from config import Config
from occupation import *
from person import Person, PersonExNihilo

# Objects of a business class represents both the company itself and the building
# at which it is headquartered. All business subclasses inherit generic attributes
# and methods from the superclass Business, and each define their own methods as
# appropriate.


class Business(object):
    """A business in a city (representing both the notion of a company and its physical building)."""

    def __init__(self, lot, construction):
        """Initialize a Business object.

        @param lot: A Lot object representing the lot this company's building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this company's building.
        """
        self.city = lot.city
        self.city.companies.add(self)
        self.founded = self.city.game.year
        self.lot = self._init_secure_lot()
        self.construction = construction
        self.owner = construction.client
        self.owner.building_commissions.append(self)
        self.employees = set()
        self.former_employees = set()
        self.name = self._init_get_named()
        self.address = self._init_generate_address()

    def _init_secure_lot(self):
        """Secure a lot on which to build the company building."""

    def _rate_all_vacant_lots(self):
        """Find a home to move into in a chosen neighborhood.

        By this method, a person appraises every vacant home and lot in the city for
        how much they would like to move or build there, given considerations to the people
        that live nearby it (this reasoning via self.score_potential_home_or_lot()). There is
        a penalty that makes people less willing to build a home on a vacant lot than to move
        into a vacant home.
        """
        scores = {}
        for home in self.city.vacant_homes:
            my_score = self._rate_potential_lot(lot=home.lot)
            if self.spouse:
                spouse_score = self.spouse.score_potential_home_or_lot(home_or_lot=home)
            else:
                spouse_score = 0
            scores[home] = my_score + spouse_score
        for lot in self.city.vacant_lots:
            my_score = self._rate_potential_lot(lot=lot)
            if self.spouse:
                spouse_score = self.spouse.score_potential_home_or_lot(home_or_lot=lot)
            else:
                spouse_score = 0
            scores[lot] = (
                (my_score + spouse_score) * self.game.config.penalty_for_having_to_build_a_home_vs_buying_one
            )
        return scores

    def _rate_potential_lot(self, lot):
        """Score the desirability of living at the location of a lot.

        TODO: Other considerations here.
        """
        config = self.game.config
        desire_to_live_near_family = self._determine_desire_to_move_near_family()
        # Score home for its proximity to family (either positively or negatively, depending); only
        # consider family members that are alive, in town, and not living with you already (i.e., kids)
        relatives_in_town = {
            f for f in self.extended_family if f.present and f.home is not self.home
        }
        score = 0
        for relative in relatives_in_town:
            relation_to_me = self.relation_to_me(person=relative)
            pull_toward_someone_of_that_relation = config.pull_to_live_near_family[relation_to_me]
            dist = relative.home.lot.get_dist_to(lot=lot) + 1.0  # To avoid ZeroDivisionError
            score += (desire_to_live_near_family * pull_toward_someone_of_that_relation) / dist
        # Score for proximity to friends (only positively)
        for friend in self.friends:
            dist = friend.home.lot.get_dist_to(lot=lot) + 1.0
            score += config.pull_to_live_near_a_friend / dist
        # Score for proximity to workplace (only positively) -- will be only criterion for person
        # who is new to the city (and thus knows no one there yet)
        if self.occupation:
            dist = self.occupation.company.lot.get_dist_to(lot=lot) + 1.0
            score += config.pull_to_live_near_workplace / dist
        return score

    def _init_get_named(self):
        """Get named by the owner of this building (the client for which it was constructed)."""
        pass

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        house_number = self.lot.house_number
        street = str(self.lot.street)
        return "{} {}".format(house_number, street)

    def _init_hire_initial_employees(self):
        """Fill all the positions that are vacant at the time of this company forming."""
        for vacant_position in self.city.game.config.initial_job_vacancies:
            self.hire(occupation=vacant_position)

    @property
    def residents(self):
        """Return the employees that work here.

         This is meant to facilitate a Lot reasoning over its population and the population
         of its local area. This reasoning is needed so that developers can decide where to
         build businesses. For all businesses but ApartmentComplex, this just returns the
         employees that work at this building (which makes sense in the case of, e.g., building
         a restaurant nearby where people work); for ApartmentComplex, this is overridden
         to return the employees that work there and also the people that live there.
         """
        return self.employees

    def hire(self, occupation):
        """Scour the job market to hire someone to fulfill the duties of occupation."""
        job_candidates_in_town = self._assemble_job_candidates(occupation=occupation)
        if job_candidates_in_town:
            candidate_scores = self._rate_all_job_candidates(candidates=job_candidates_in_town)
            selected_candidate = self._select_candidate(candidate_scores=candidate_scores)
        else:
            selected_candidate = self._find_candidate_from_outside_the_city(occupation=occupation)
        Hiring(subject=selected_candidate, company=self, occupation=occupation)

    @staticmethod
    def _select_candidate(candidate_scores):
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

    def _find_candidate_from_outside_the_city(self, occupation):
        """Generate a PersonExNihilo to move into the city for this job."""
        candidate = PersonExNihilo(
            game=self.owner.game, job_opportunity_impetus=occupation, spouse_already_generated=False
        )
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
        # Consider unemployed (mostly young) people
        candidates |= self.city.unemployed
        return candidates


class ApartmentComplex(Business):
    """An apartment complex."""

    def __init__(self, lot, construction):
        """Initialize an ApartmentComplex object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(ApartmentComplex, self).__init__(lot, construction)
        self.units = set()

    @property
    def residents(self):
        """Return the employees that work here and residents that live here."""
        residents = set(self.employees)
        for unit in self.units:
            residents |= unit.residents
        return residents


class Bank(Business):
    """A bank."""

    def __init__(self, lot, construction):
        """Initialize a Bank object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(Bank, self).__init__(lot, construction)


class Barbershop(Business):
    """A barbershop."""

    def __init__(self, lot, construction):
        """Initialize a Barbershop object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(Barbershop, self).__init__(lot, construction)


class BusDepot(Business):
    """A bus depot."""

    def __init__(self, lot, construction):
        """Initialize a BusDepot object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(BusDepot, self).__init__(lot, construction)


class CityHall(Business):
    """The city hall."""

    def __init__(self, lot, construction):
        """Initialize a CityHall object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(CityHall, self).__init__(lot, construction)


class ConstructionFirm(Business):
    """A construction firm."""

    def __init__(self, lot, construction):
        """Initialize an ConstructionFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(ConstructionFirm, self).__init__(lot, construction)

    @property
    def house_constructions(self):
        """Return all house constructions."""
        house_constructions = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'house_constructions'):
                house_constructions |= employee.house_constructions
        return house_constructions

    @property
    def building_constructions(self):
        """Return all building constructions."""
        building_constructions = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'building_constructions'):
                building_constructions |= employee.building_constructions
        return building_constructions


class OptometryClinic(Business):
    """An optometry clinic."""

    def __init__(self, lot, construction):
        """Initialize an OptometryClinic object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(OptometryClinic, self).__init__(lot, construction)


class FireStation(Business):
    """A fire station."""

    def __init__(self, lot, construction):
        """Initialize an FireStation object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(FireStation, self).__init__(lot, construction)


class Hospital(Business):
    """A hospital."""

    def __init__(self, lot, construction):
        """Initialize an Hospital object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(Hospital, self).__init__(lot, construction)

    @property
    def baby_deliveries(self):
        """Return all baby deliveries."""
        baby_deliveries = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'baby_deliveries'):
                baby_deliveries |= employee.baby_deliveries
        return baby_deliveries


class Hotel(Business):
    """A hotel."""

    def __init__(self, lot, construction):
        """Initialize a Hotel object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(Hotel, self).__init__(lot, construction)


class LawFirm(Business):
    """A law firm."""

    def __init__(self, lot, construction):
        """Initialize a LawFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(LawFirm, self).__init__(lot, construction)

    @property
    def filed_divorces(self):
        """Return all divorces filed through this law firm."""
        filed_divorces = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'filed_divorces'):
                filed_divorces |= employee.filed_divorces
        return filed_divorces

    @property
    def filed_name_changes(self):
        """Return all name changes filed through this law firm."""
        filed_name_changes = set()
        for lawyer in self.lawyers | self.former_lawyers:
            filed_name_changes |= lawyer.filed_name_changes
        return filed_name_changes


class PlasticSurgeryClinic(Business):
    """A plastic-surgery clinic."""

    def __init__(self, lot, construction):
        """Initialize a PlasticSurgeryClinic object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(PlasticSurgeryClinic, self).__init__(lot, construction)


class PoliceStation(Business):
    """A police station."""

    def __init__(self, lot, construction):
        """Initialize a PoliceStation object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(PoliceStation, self).__init__(lot, construction)


class RealtyFirm(Business):
    """A realty firm."""

    def __init__(self, lot, construction):
        """Initialize an RealtyFirm object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(RealtyFirm, self).__init__(lot, construction)

    @property
    def home_sales(self):
        """Return all home sales."""
        home_sales = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'home_sales'):
                home_sales |= employee.home_sales
        return home_sales


class Restaurant(Business):
    """A restaurant."""

    def __init__(self, lot, construction):
        """Initialize a Restaurant object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(Restaurant, self).__init__(lot, construction)


class Supermarket(Business):
    """A supermarket on a lot in a city."""

    def __init__(self, lot, construction):
        """Initialize an Supermarket object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(Supermarket, self).__init__(lot, construction)


class TattooParlor(Business):
    """A tattoo parlor."""

    def __init__(self, lot, construction):
        """Initialize a TattooParlor object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(TattooParlor, self).__init__(lot, construction)


class TaxiDepot(Business):
    """A taxi depot."""

    def __init__(self, lot, construction):
        """Initialize a TaxiDepot object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(TaxiDepot, self).__init__(lot, construction)


class University(Business):
    """The local university."""

    def __init__(self, lot, construction):
        """Initialize a University object.

        @param lot: A Lot object representing the lot this building is on.
        @param construction: A BuildingConstruction object holding data about
                             the construction of this building.
        """
        super(University, self).__init__(lot, construction)