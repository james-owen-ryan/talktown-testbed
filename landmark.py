import random
import heapq
from person import PersonExNihilo
from event import Hiring


# There are two types of landmarks: Cemetery and Park. The distinction
# between a landmark and a business is that a landmark does not have a
# building and is not owned by anyone.


class Landmark(object):
    """A landmark on a tract in a city."""

    def __init__(self, city):
        """Initialize a Landmark object."""
        self.city = city
        self.city.companies.add(self)
        self.founded = self.city.game.year
        self.lot = self._init_choose_vacant_tract()  # We call this lot to make all get_dist()-like methods work
        self.employees = set()
        self.name = self._init_get_named()
        self.address = self._init_generate_address()

    def _init_choose_vacant_tract(self):
        """Choose a vacant tract on which to build the company building.

        Currently, a landmark scores all the vacant tracts in town and then selects
        one of the top three. TODO: Probabilistically select from all tracts using
        the scores to derive likelihoods of selecting each.
        """
        tract_scores = self._rate_all_vacant_tracts()
        if len(tract_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, tract_scores, key=tract_scores.get)
            if random.random() < 0.6:
                choice = top_three_choices[0]
            elif random.random() < 0.9:
                choice = top_three_choices[1]
            else:
                choice = top_three_choices[2]
        elif tract_scores:
            choice = tract_scores[0]
        else:
            raise Exception("A company attempted to secure a lot in town when in fact none are vacant.")
        return choice

    def _rate_all_vacant_tracts(self):
        """Rate all vacant tracts for the desirability of their locations.
        """
        scores = {}
        for tract in self.city.vacant_tracts:
            scores[tract] = self._rate_potential_tract(tract=tract)
        return scores

    def _rate_potential_tract(self, tract):
        """Rate a vacant tract for the desirability of its location.

        By this method, a landmark appraises a vacant tract in the city for how much they
        would like to build there, given considerations to its proximity to downtown,
        proximity to other landmarks of the same type, and to the number of people living
        near the tract.
        """
        config = self.city.game.config
        score = 0
        # Increase score for population surrounding this tract -- secondary population is the
        # total population of this tract's neighboring tracts; tertiary population is the
        # total population of this tract's neighboring tracts and those tracts' neighboring tracts
        score += config.function_to_determine_company_preference_for_local_population(
            secondary_pop=tract.secondary_population, tertiary_pop=tract.tertiary_population
        )
        # Decrease score for being near to another landmark of this same type
        dist_to_nearest_company_of_same_type = (
            tract.dist_to_nearest_company_of_type(company_type=self.__class__)
        )
        if dist_to_nearest_company_of_same_type is not None:  # It will be None if there is no such business yet
            score -= config.function_to_determine_company_penalty_for_nearby_company_of_same_type(
                dist_to_nearest_company_of_same_type=dist_to_nearest_company_of_same_type
            )
        # As an emergency criterion for the case where there are no people or companies in the town
        # yet, rate lots according to their distance from downtown
        score -= tract.dist_from_downtown
        return score

    def _init_get_named(self):
        """Get named by the city's mayor."""
        return 'lol {}'.format(self.__class__.__name__)

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
         build businesses.
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
            game=self.city.game, job_opportunity_impetus=occupation, spouse_already_generated=None
        )
        return candidate

    def _rate_all_job_candidates(self, candidates):
        """Rate all job candidates."""
        scores = {}
        for candidate in candidates:
            scores[candidate] = self._rate_job_candidate(person=candidate)
        return scores

    def _rate_job_candidate(self, person):
        """Rate a job candidate, given an open position and mayor biases."""
        config = self.city.game.config
        score = 0
        if person in self.employees:
            score += config.preference_to_hire_from_within_company
        if person in self.city.mayor.immediate_family:
            score += config.preference_to_hire_immediate_family
        elif person in self.city.mayor.extended_family:  # elif because immediate family is subset of extended family
            score += config.preference_to_hire_extended_family
        if person in self.city.mayor.friends:
            score += config.preference_to_hire_friend
        elif person in self.city.mayor.known_people:
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


class Cemetery(Landmark):
    """A cemetery on a tract in a city."""

    def __init__(self, city):
        """Initialize a Cemetery object."""
        super(Cemetery, self).__init__(city)
        self.plots = {}

    def inter_person(self, person):
        """Inter a new person by assigning them a plot in the graveyard."""
        new_plot_number = max(self.plots) + 1
        self.plots[new_plot_number] = person
        return new_plot_number


class Park(Landmark):
    """A park on a tract in a city."""

    def __init__(self, city):
        """Initialize a Park object."""
        super(Park, self).__init__(city)