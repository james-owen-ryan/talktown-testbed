import heapq
from occupation import *
from person import PersonExNihilo
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
        config = owner.game.config
        self.city = owner.city
        self.city.companies.add(self)
        self.founded = self.city.game.year
        self.lot = self._init_choose_vacant_lot()
        if self.__class__ in config.companies_that_get_established_on_tracts:
            self.lot.landmark = self
        else:
            self.lot.building = self
        # First, hire employees -- this is done first because the first-ever business, a
        # construction firm started by the city founder, will need to hire the city's
        # first architect before it can construct its own building
        self.employees = set()
        self.former_employees = set()
        if self.__class__ in config.public_companies:  # Hospital, police station, fire station, etc.
            self.owner = None
        else:
            self.owner = self._init_set_and_get_owner_occupation(owner=owner)
        self._init_hire_initial_employees()
        if self.__class__ not in config.companies_that_get_established_on_tracts:
            architect = owner.contract_person_of_certain_occupation(occupation_in_question=Architect)
            self.construction = architect.occupation.construct_building(client=owner, business=self)
        # These get set by _init_generate_address()
        self.address = None
        self.street_address_is_on = None
        self._init_generate_address()
        # This gets set by self._init_get_named()
        self.name = None
        while not self.name or any(c for c in self.city.companies if c is not self and c.name == self.name):
            self._init_get_named()

    def _init_set_and_get_owner_occupation(self, owner):
        """Set the owner of this new company's occupation to Owner."""
        # The order really matters here -- see hire() below
        new_position = Owner(person=owner, company=self, shift="day")
        hiring = Hiring(subject=owner, company=self, occupation=Owner)
        if owner.occupation and owner is not self.city.game.founder:
            # The city founder will have multiple occupations, in the sense that they will
            # also own multiple apartment complexes, but they will only be attributed as
            # their occupation being owner of the construction firm
            owner.occupation.terminate(reason=hiring)
        owner.occupation = new_position
        # Lastly, if the person was hired from outside the city, have them move to it --
        # don't do this for the city founder though, who must hold off on moving here until
        # an architect already has
        if owner.city is not self.city and owner is not self.city.game.founder:
            owner.move_into_the_city(hiring_that_instigated_move=hiring)
        return owner.occupation

    def _init_get_named(self):
        """Get named by the owner of this building (the client for which it was constructed)."""
        config = self.city.game.config
        class_to_company_name_component = {
            ApartmentComplex: 'Apartments',
            Bank: 'Bank',
            Barbershop: 'Barbershop',
            BusDepot: 'Bus Depot',
            CityHall: 'City Hall',
            ConstructionFirm: 'Construction',
            OptometryClinic: 'Optometry',
            FireStation: 'Fire Dept.',
            Hospital: 'Hospital',
            Hotel: 'Hotel',
            LawFirm: 'Law Offices of',
            PlasticSurgeryClinic: 'Cosmetic Surgery Clinic',
            PoliceStation: 'Police Dept.',
            RealtyFirm: 'Realty',
            Restaurant: 'Restaurant',
            Supermarket: 'Grocers',
            TattooParlor: 'Tattoo',
            TaxiDepot: 'Taxi',
            University: 'University',
            Cemetery: 'Cemetery',
            Park: 'Park',
        }
        classes_that_get_special_names = (
            CityHall, FireStation, Hospital, PoliceStation, Cemetery, LawFirm, Restaurant, University, Park
        )
        if self.__class__ not in classes_that_get_special_names:
            if random.random() < config.chance_company_gets_named_after_owner:
                prefix = self.owner.person.last_name
            elif random.random() < 0.9:
                prefix = self.street_address_is_on.name
            else:
                prefix = Names.a_place_name()
            name = "{0} {1}".format(prefix, class_to_company_name_component[self.__class__])
        elif self.__class__ in (CityHall, FireStation, Hospital, PoliceStation, Cemetery):
            name = "{0} {1}".format(self.city.name, class_to_company_name_component[self.__class__])
        elif self.__class__ is LawFirm:
            associates = [self.owner] + [e for e in self.employees if e.__class__ is Lawyer]
            suffix = "{0} & {1}".format(
                ', '.join(a.person.last_name for a in associates[:-1]), associates[-1].person.last_name
            )
            name = "{0} {1}".format(class_to_company_name_component[LawFirm], suffix)
        elif self.__class__ is Restaurant:
            name = Names.a_restaurant_name()
        elif self.__class__ in (University, Park):
            name = "{0} {1}".format(self.city.game.founder.name, class_to_company_name_component[self.__class__])
        else:
            raise Exception("A company of class {0} was unable to be named.".format(self.__class__.__name__))
        self.name = name

    def __str__(self):
        """Return string representation."""
        return "{0}, {1}".format(self.name, self.address)

    def _init_hire_initial_employees(self):
        """Fill all the positions that are vacant at the time of this company forming."""
        # Hire employees for the day shift
        for vacant_position in self.city.game.config.initial_job_vacancies[self.__class__]['day']:
            self.hire(occupation_of_need=vacant_position, shift="day")
        # Hire employees for the night shift
        for vacant_position in self.city.game.config.initial_job_vacancies[self.__class__]['night']:
            self.hire(occupation_of_need=vacant_position, shift="night")

    def _init_choose_vacant_lot(self):
        """Choose a vacant lot on which to build the company building.

        Currently, a company scores all the vacant lots in town and then selects
        one of the top three. TODO: Probabilistically select from all lots using
        the scores to derive likelihoods of selecting each.
        """
        if self.__class__ in self.city.game.config.companies_that_get_established_on_tracts:
            vacant_lots_or_tracts = self.city.vacant_tracts
        else:
            vacant_lots_or_tracts = self.city.vacant_lots
        assert vacant_lots_or_tracts, (
            "{0} is attempting to found a {1}, but there's no vacant lots/tracts in {2}".format(
                self.owner.person.name, self.__class__.__name__, self.city.name
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
        if self.__class__ in self.city.game.config.companies_that_get_established_on_tracts:
            vacant_lots_or_tracts = self.city.vacant_tracts
        else:
            vacant_lots_or_tracts = self.city.vacant_lots
        scores = {}
        for lot in vacant_lots_or_tracts:
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
            secondary_pop=self.city.secondary_population(lot), tertiary_pop=self.city.tertiary_population(lot)
        )
        # Decrease score for being near to another company of this same type
        dist_to_nearest_company_of_same_type = (
            self.city.dist_to_nearest_business_of_type(lot, business_type=type(self), exclusion=self)
        )
        if dist_to_nearest_company_of_same_type is not None:  # It will be None if there is no such business yet
            score -= config.function_to_determine_company_penalty_for_nearby_company_of_same_type(
                dist_to_nearest_company_of_same_type=dist_to_nearest_company_of_same_type
            )
        # As an emergency criterion for the case where there are no people or companies in the town
        # yet, rate lots according to their distance from downtown
        score -= self.city.dist_from_downtown(lot)
        return score

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        index_of_street_address_will_be_on = random.randint(0, len(self.lot.streets)-1)
        house_number = int(self.lot.house_numbers[index_of_street_address_will_be_on])
        street = self.lot.streets[index_of_street_address_will_be_on]
        self.address = "{0} {1}".format(house_number, street.name)
        self.street_address_is_on = street

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

    @property
    def day_shift(self):
        """Return all employees who work the day shift here."""
        day_shift = set([employee for employee in self.employees if employee.shift == "day"])
        return day_shift

    @property
    def night_shift(self):
        """Return all employees who work the night shift here."""
        day_shift = set([employee for employee in self.employees if employee.shift == "night"])
        return day_shift

    def hire(self, occupation_of_need, shift):
        """Scour the job market to hire someone to fulfill the duties of occupation."""
        job_candidates_in_town = self._assemble_job_candidates(occupation_of_need=occupation_of_need)
        if job_candidates_in_town:
            candidate_scores = self._rate_all_job_candidates(candidates=job_candidates_in_town)
            selected_candidate = self._select_candidate(candidate_scores=candidate_scores)
        else:
            selected_candidate = self._find_candidate_from_outside_the_city(occupation_of_need=occupation_of_need)
        # Instantiate the new occupation -- this means that the subject may
        # momentarily have two occupations simultaneously
        new_position = occupation_of_need(person=selected_candidate, company=self, shift=shift)
        # Now instantiate a Hiring object to hold data about the hiring
        hiring = Hiring(subject=selected_candidate, company=self, occupation=occupation_of_need)
        # Now terminate the person's former occupation, if any (which may cause
        # a hiring chain and this person's former position goes vacant and is filled,
        # and so forth); this has to happen after the new occupation is instantiated, or
        # else they may be hired to fill their own vacated position, which will cause problems
        # [Actually, this currently wouldn't happen, because lateral job movement is not
        # possible given how companies assemble job candidates, but it still makes more sense
        # to have this person put in their new position *before* the chain sets off, because it
        # better represents what really is a domino-effect situation)
        if selected_candidate.occupation:
            selected_candidate.occupation.terminate(reason=hiring)
        # Now you can set the employee's occupation to the new occupation (had you done it
        # prior, either here or elsewhere, it would have terminated the occupation that this
        # person was just hired for, triggering endless recursion as the company tries to
        # fill this vacancy in a Sisyphean nightmare)
        selected_candidate.occupation = new_position
        # Lastly, if the person was hired from outside the city, have them move to it
        if selected_candidate.city is not self.city:
            selected_candidate.move_into_the_city(hiring_that_instigated_move=hiring)

    @staticmethod
    def _select_candidate(candidate_scores):
        """Select a person to serve in a certain occupational capacity."""
        if len(candidate_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, candidate_scores, key=candidate_scores.get)
            if random.random() < 0.6:
                chosen_candidate = top_three_choices[0]
            elif random.random() < 0.9:
                chosen_candidate = top_three_choices[1]
            else:
                chosen_candidate = top_three_choices[2]
        else:
            chosen_candidate = max(candidate_scores)
        return chosen_candidate

    def _find_candidate_from_outside_the_city(self, occupation_of_need):
        """Generate a PersonExNihilo to move into the city for this job."""
        candidate = PersonExNihilo(
            game=self.city.game, job_opportunity_impetus=occupation_of_need, spouse_already_generated=None
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
        decision_maker = self.owner.person if self.owner else self.city.mayor
        score = 0
        if person in self.employees:
            score += config.preference_to_hire_from_within_company
        if person in decision_maker.immediate_family:
            score += config.preference_to_hire_immediate_family
        elif person in decision_maker.extended_family:
            score += config.preference_to_hire_extended_family
        if person in decision_maker.friends:
            score += config.preference_to_hire_friend
        elif person in decision_maker.acquaintances:
            score += config.preference_to_hire_acquaintance
        if person in decision_maker.enemies:
            score += config.dispreference_to_hire_enemy
        if person.occupation:
            score *= person.occupation.level
        else:
            score *= config.unemployment_occupation_level
        return score

    def _assemble_job_candidates(self, occupation_of_need):
        """Assemble a group of job candidates for an open position."""
        candidates = set()
        # Consider people that already work in this city -- this will subsume
        # reasoning over people that could be promoted from within this company
        for company in self.city.companies:
            for position in company.employees:
                person_is_qualified = self._check_if_person_is_qualified_for_the_position(
                    candidate=position.person, occupation_of_need=occupation_of_need
                )
                if person_is_qualified:
                    candidates.add(position.person)
        # Consider unemployed (mostly young) people
        candidates |= self.city.unemployed
        return candidates

    def _check_if_person_is_qualified_for_the_position(self, candidate, occupation_of_need):
        """Check if the job candidate is qualified for the position you are hiring for."""
        config = self.city.game.config
        qualified = False
        level_of_this_position = config.job_levels[occupation_of_need]
        # Make sure they are not overqualified
        if candidate.occupation.level < level_of_this_position:
            # Make sure they have experience in the right industry, if that's
            # a requirement of this occupation
            prerequisite_industry = self.city.game.config.prerequisite_industries[occupation_of_need]
            if prerequisite_industry:
                if self.city.game.config.prerequisite_industries[occupation_of_need] == 'Student':
                    if candidate.college_graduate:
                        qualified = True
                elif any(o for o in candidate.occupations if o.industry == prerequisite_industry):
                    qualified = True
            else:
                qualified = True
        # Lastly, make sure they have been at their old job for at least a year
        # if this isn't an entry-level position (otherwise people climb the ranks
        # instantaneously)
        if level_of_this_position > 1:
            if candidate.occupation.years_experience < 1:
                qualified = False
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
        for i in xrange(self.city.game.config.number_of_apartment_units_per_complex):
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


class Cemetery(Business):
    """A cemetery on a tract in a city."""

    def __init__(self, owner):
        """Initialize a Cemetery object."""
        super(Cemetery, self).__init__(owner)
        self.plots = {}

    def inter_person(self, person):
        """Inter a new person by assigning them a plot in the graveyard."""
        new_plot_number = max(self.plots) + 1
        self.plots[new_plot_number] = person
        return new_plot_number


class CityHall(Business):
    """The city hall."""

    def __init__(self, owner):
        """Initialize a CityHall object.

        @param owner: The owner of this business.
        """
        super(CityHall, self).__init__(owner)


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


class Park(Business):
    """A park on a tract in a city."""

    def __init__(self, owner):
        """Initialize a Park object."""
        super(Park, self).__init__(owner)


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