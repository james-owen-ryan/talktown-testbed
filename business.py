import heapq
from occupation import *
from person import Person, PersonExNihilo
from residence import *

# Objects of a business class represents both the company itself and the building
# at which it is headquartered. All business subclasses inherit generic attributes
# and methods from the superclass Business, and each define their own methods as
# appropriate.


class Business(object):
    """A business in a city (representing both the notion of a company and its physical building)."""

    def __init__(self, owner):
        """Initialize a Business object.

        @param owner: The owner of this business.
        """
        self.city = owner.city
        self.city.companies.add(self)
        self.owner = owner
        self.founded = self.city.game.year
        self.lot = self._init_choose_vacant_lot()
        architect = self.owner.contract_person_of_certain_occupation(occupation=Architect)
        self.construction = architect.construct_building(client=self.owner, business=self)
        self.employees = set()
        self.former_employees = set()
        self.name = self._init_get_named()
        self.address = self._init_generate_address()

    def _init_choose_vacant_lot(self):
        """Choose a vacant lot on which to build the company building.

        Currently, a company scores all the vacant lots in town and then selects
        one of the top three. TODO: Probabilistically select from all lots using
        the scores to derive likelihoods of selecting each.
        """
        assert self.city.vacant_lots, (
            "{} is attempting to found a company, but there's no vacant lots in {}".format(
                self.owner.name, self.city.name
            )
        )
        lot_scores = self._rate_all_vacant_lots()
        if len(lot_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, lot_scores, key=lot_scores.get)
            if random.random() < 0.6:
                choice = top_three_choices[0]
            elif random.random() < 0.9:
                choice = top_three_choices[1]
            else:
                choice = top_three_choices[2]
        elif lot_scores:
            choice = lot_scores[0]
        else:
            raise Exception("A company attempted to secure a lot in town when in fact none are vacant.")
        return choice

    def _rate_all_vacant_lots(self):
        """Rate all vacant lots for the desirability of their locations.
        """
        scores = {}
        for lot in self.city.vacant_lots:
            scores[lot] = self._rate_potential_lot(lot=lot)
        return scores

    def _rate_potential_lot(self, lot):
        """Rate a vacant lot for the desirability of its location.

        By this method, a company appraises a vacant lot in the city for how much they
        would like to build there, given considerations to its proximity to downtown,
        proximity to other businesses of the same type, and to the number of people living
        near the lot.
        """
        config = self.city.game.config
        score = 0
        # Increase score for population surrounding this lot -- secondary population is the
        # total population of this lot's neighboring lots; tertiary population is the
        # total population of this lot's neighboring lots and those lots' neighboring lots
        score += config.function_to_determine_company_preference_for_local_population(
            secondary_pop=lot.secondary_population, tertiary_pop=lot.tertiary_population
        )
        # Decrease score for being near to another company of this same type
        dist_to_nearest_company_of_same_type = (
            lot.dist_to_nearest_company_of_type(company_type=self.__class__)
        )
        if dist_to_nearest_company_of_same_type is not None:  # It will be None if there is no such business yet
            score -= config.function_to_determine_company_penalty_for_nearby_company_of_same_type(
                dist_to_nearest_company_of_same_type=dist_to_nearest_company_of_same_type
            )
        # As an emergency criterion for the case where there are no people or companies in the town
        # yet, rate lots according to their distance from downtown
        score -= lot.dist_from_downtown
        return score

    def _init_get_named(self):
        """Get named by the owner of this building (the client for which it was constructed)."""
        return 'lol {}'.format(self.__class__.__name__)  # Placeholder obviously

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
        # Instantiate the new occupation -- this means that the subject may
        # momentarily have two occupations simultaneously
        Occupation(person=selected_candidate, company=self)
        # Now terminate the person's former occupation, if any (which may cause
        # a hiring chain and this person's former position goes vacant and is filled,
        # and so forth); this has to happen after the new occupation is instantiated, or
        # else they may be hired to fill their own vacated position, which will cause problems
        # [Actually, this currently wouldn't happen, because lateral job movement is not
        # possible given how companies assemble job candidates, but it still makes more sense
        # to have this person put in their new position *before* the chain sets off, because it
        # better represents what really is a domino-effect situation)
        if selected_candidate.occupation:
            selected_candidate.occupation.terminate()
        # Now instantiate a Hiring object to hold data about the hiring
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
            game=self.owner.game, job_opportunity_impetus=occupation, spouse_already_generated=None
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
                if self._check_if_person_is_qualified_for_the_position(candidate=employee, occupation=occupation):
                    candidates.add(employee)
        # Consider unemployed (mostly young) people
        candidates |= self.city.unemployed
        return candidates

    def _check_if_person_is_qualified_for_the_position(self, candidate, occupation):
        """Check if the job candidate is qualified for the position you are hiring for."""
        qualified = False
        # Make sure they are overqualified
        if candidate.occupation.level < occupation.level:
            # Make sure they have experience in the right industry, if that's
            # a requirement of this occupation
            prerequisite_industry = self.city.game.config.prerequisite_industries[occupation]
            if prerequisite_industry:
                if self.city.game.config.prerequisite_industries[occupation] == 'Student':
                    if candidate.college_graduate:
                        qualified = True
                elif any(o for o in candidate.occupations if o.industry == prerequisite_industry):
                    qualified = True
            else:
                qualified = True
        return qualified


class ApartmentComplex(Business):
    """An apartment complex."""

    def __init__(self, owner):
        """Initialize an ApartmentComplex object.

        @param owner: The owner of this business.
        """
        super(ApartmentComplex, self).__init__(owner)
        self.units = self._init_apartment_units()

    def _init_apartment_units(self):
        """Instantiate objects for the individual units in this apartment complex."""
        apartment_units = []
        for i in xrange(len(self.owner.game.config.number_of_apartment_units_per_complex)):
            unit_number = i + 1
            apartment_units.append(
                Apartment(apartment_complex=self, lot=self.lot, unit_number=unit_number)
            )
        return apartment_units

    @property
    def residents(self):
        """Return the employees that work here and residents that live here."""
        residents = set(self.employees)
        for unit in self.units:
            residents |= unit.residents
        return residents


class Bank(Business):
    """A bank."""

    def __init__(self, owner):
        """Initialize a Bank object.

        @param owner: The owner of this business.
        """
        super(Bank, self).__init__(owner)


class Barbershop(Business):
    """A barbershop."""

    def __init__(self, owner):
        """Initialize a Barbershop object.

        @param owner: The owner of this business.
        """
        super(Barbershop, self).__init__(owner)


class BusDepot(Business):
    """A bus depot."""

    def __init__(self, owner):
        """Initialize a BusDepot object.

        @param owner: The owner of this business.
        """
        super(BusDepot, self).__init__(owner)


class CityHall(Business):
    """The city hall."""

    def __init__(self, owner):
        """Initialize a CityHall object.

        @param owner: The owner of this business.
        """
        super(CityHall, self).__init__(owner)

    def _init_make_city_founder_mayor_de_facto(self):
        """Make the city founder mayor."""
        mayor = self.city.the_founder


class ConstructionFirm(Business):
    """A construction firm."""

    def __init__(self, owner):
        """Initialize an ConstructionFirm object.

        @param owner: The owner of this business.
        """
        super(ConstructionFirm, self).__init__(owner)

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

    def __init__(self, owner):
        """Initialize an OptometryClinic object.

        @param owner: The owner of this business.
        """
        super(OptometryClinic, self).__init__(owner)


class FireStation(Business):
    """A fire station."""

    def __init__(self, owner):
        """Initialize an FireStation object.

        @param owner: The owner of this business.
        """
        super(FireStation, self).__init__(owner)


class Hospital(Business):
    """A hospital."""

    def __init__(self, owner):
        """Initialize an Hospital object.

        @param owner: The owner of this business.
        """
        super(Hospital, self).__init__(owner)

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

    def __init__(self, owner):
        """Initialize a Hotel object.

        @param owner: The owner of this business.
        """
        super(Hotel, self).__init__(owner)


class LawFirm(Business):
    """A law firm."""

    def __init__(self, owner):
        """Initialize a LawFirm object.

        @param owner: The owner of this business.
        """
        super(LawFirm, self).__init__(owner)

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
        for employee in self.employees | self.former_employees:
            filed_name_changes |= employee.filed_name_changes
        return filed_name_changes


class PlasticSurgeryClinic(Business):
    """A plastic-surgery clinic."""

    def __init__(self, owner):
        """Initialize a PlasticSurgeryClinic object.

        @param owner: The owner of this business.
        """
        super(PlasticSurgeryClinic, self).__init__(owner)


class PoliceStation(Business):
    """A police station."""

    def __init__(self, owner):
        """Initialize a PoliceStation object.

        @param owner: The owner of this business.
        """
        super(PoliceStation, self).__init__(owner)


class RealtyFirm(Business):
    """A realty firm."""

    def __init__(self, owner):
        """Initialize an RealtyFirm object.

        @param owner: The owner of this business.
        """
        super(RealtyFirm, self).__init__(owner)

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

    def __init__(self, owner):
        """Initialize a Restaurant object.

        @param owner: The owner of this business.
        """
        super(Restaurant, self).__init__(owner)


class Supermarket(Business):
    """A supermarket on a lot in a city."""

    def __init__(self, owner):
        """Initialize an Supermarket object.

        @param owner: The owner of this business.
        """
        super(Supermarket, self).__init__(owner)


class TattooParlor(Business):
    """A tattoo parlor."""

    def __init__(self, owner):
        """Initialize a TattooParlor object.

        @param owner: The owner of this business.
        """
        super(TattooParlor, self).__init__(owner)


class TaxiDepot(Business):
    """A taxi depot."""

    def __init__(self, owner):
        """Initialize a TaxiDepot object.

        @param owner: The owner of this business.
        """
        super(TaxiDepot, self).__init__(owner)


class University(Business):
    """The local university."""

    def __init__(self, owner):
        """Initialize a University object.

        @param owner: The owner of this business.
        """
        super(University, self).__init__(owner)