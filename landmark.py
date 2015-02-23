import random
import heapq
from person import PersonExNihilo
from event import Hiring


# There are two types of landmarks: Cemetery and Park. The distinction
# between a landmark and a business is that a landmark does not have a
# building and is not owned by anyone.


class Landmark(object):
    """A landmark on a tract in a city."""

    def __init__(self, tract):
        """Initialize a Landmark object."""
        self.city = tract.city
        self.city.companies.add(self)
        self.founded = self.city.game.year
        self.tract = tract
        self.employees = set()
        self.name = self._init_get_named()
        self.address = self._init_generate_address()

    def _init_get_named(self):
        """Get named by the city's mayor."""
        pass

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        house_number = self.tract.house_number
        street = str(self.tract.street)
        return "{} {}".format(house_number, street)

    def _init_hire_initial_employees(self):
        """Fill all the positions that are vacant at the time of this company forming."""
        for vacant_position in self.city.game.config.initial_job_vacancies:
            self.hire(occupation=vacant_position)

    def hire(self, occupation):
        """Scour the job market to hire someone to fulfill the duties of occupation."""
        job_candidates_in_town = self._assemble_job_candidates(occupation=occupation)
        if job_candidates_in_town:
            candidate_scores = self._rate_all_job_candidates(candidates=job_candidates_in_town)
            selected_candidate = self._select_candidate(candidate_scores=candidate_scores)
        else:
            selected_candidate = self._find_candidate_from_outside_the_city()
        Hiring(subject=selected_candidate, company=self, occupation=occupation)

    @staticmethod
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
        """Generate a PersonExNihilo to move into the city for this job."""
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
        candidate = PersonExNihilo(game=self.city.game, birth_year=birth_year_of_this_person)
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

    def __init__(self, tract):
        """Initialize a Cemetery object."""
        super(Cemetery, self).__init__(tract)
        self.plots = {}

    def inter_person(self, person):
        """Inter a new person by assigning them a plot in the graveyard."""
        new_plot_number = max(self.plots) + 1
        self.plots[new_plot_number] = person
        return new_plot_number


class Park(Landmark):
    """A park on a tract in a city."""

    def __init__(self, tract):
        """Initialize a Park object."""
        super(Park, self).__init__(tract)