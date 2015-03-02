import random


# TODO -- visiting methods don't take into account
# whether the person they will visit is even home;
# once we implement a telephone system, have them
# call first, or have people invite people over too


class Routine(object):
    """A person's daily routine."""

    def __init__(self, person):
        """Initialize a Routine object."""
        self.person = person
        self.working = False  # Whether or not the person is working at an exact timestep
        self.businesses_patronized = {}  # Gets set by set_businesses_patronized()
        if self.person.home:
            self.set_businesses_patronized()

    def enact(self):
        """Enact this person's daily routine for a particular timestep."""
        self.person.location, self.working = self.decide_where_to_go()
        self.person.location.people_here_now.add(self.person)

    def decide_where_to_go(self):
        """Return this person's daytime location, which is dynamic."""
        config = self.person.game.config
        working = False  # Keep track of this, because they could be going into work on an off-day (e.g., restaurant)
        if not self.person.adult and self.person.game.time_of_day == "day":
            location = self._go_to_school_or_daycare()
            working = False
        elif self.person.occupation and self.person.occupation.shift == self.person.game.time_of_day:
            if random.random() < config.chance_someone_doesnt_have_to_work_some_day:
                if random.random() < config.chance_someone_leaves_home_on_day_off[self.person.game.time_of_day]:
                    location = self._go_in_public()
                else:
                    location = self.person.home
            elif random.random() < config.chance_someone_calls_in_sick_to_work:
                if random.random() < config.chance_someone_leaves_home_on_sick_day:
                    location = self._go_in_public()
                else:
                    location = self.person.home
            else:
                working = True
                location = self.person.occupation.company
        else:
            chance_of_leaving_home = self.person.personality.extroversion
            floor = config.chance_someone_leaves_home_on_day_off_floor[self.person.game.time_of_day]
            cap = config.chance_someone_leaves_home_on_day_off_cap[self.person.game.time_of_day]
            if chance_of_leaving_home < floor:
                chance_of_leaving_home = floor
            elif chance_of_leaving_home > cap:
                chance_of_leaving_home = cap
            if random.random() < chance_of_leaving_home:
                location = self._go_in_public()
            else:
                location = self.person.home
        return location, working

    def _go_to_school_or_daycare(self):
        """Return the school or day care that this child attends."""
        if self.person.age > 5:
            school_or_day_care = self.person.city.school
        else:
            school_or_day_care = self.businesses_patronized["DayCare"]
        return school_or_day_care

    def _go_in_public(self):
        """Return the location in public that this person will go to."""
        config = self.person.game.config
        if random.random() < config.chance_someone_goes_on_errand_vs_visits_someone:
            location = self._go_on_errand()
        else:
            person_they_will_visit = self._visit_someone()
            if person_they_will_visit:
                location = person_they_will_visit.home
            else:
                location = self.person.home
        # In case something went wrong, e.g., there's no business of a type
        # that this person patronizes, just have them stay at home
        if not location:
            location = self.person.home
        return location

    def _go_on_errand(self):
        """Return the location associated with some errand this person will go on."""
        config = self.person.game.config
        # TODO -- if someone goes on one of these errands, have them actually get
        # served by that business, e.g., have them actually get a haircut
        if random.random() < config.chance_someone_gets_a_haircut_some_day:
            business_type_of_errand = 'Barbershop'
        elif random.random() < config.chance_someone_gets_contacts_or_glasses:
            business_type_of_errand = 'OptometryClinic'
        elif random.random() < config.chance_someone_gets_a_tattoo_some_day:
            business_type_of_errand = 'TattooParlor'
        elif random.random() < config.chance_someone_gets_plastic_surgery_some_day:
            business_type_of_errand = 'PlasticSurgeryClinic'
        else:
            x = random.random()
            business_type_of_errand = next(
                # See config.py to understand what's going on here
                e for e in config.probabilities_of_errand_to_business_type if
                e[0][0] <= x <= e[0][1]
            )[1]
        location = self.businesses_patronized[business_type_of_errand]
        return location

    def _visit_someone(self):
        """Return the residence of the person who this person will go visit."""
        config = self.person.game.config
        x = random.random()
        relationship_to_person_who_person_who_will_be_visited = next(
            r for r in config.who_someone_visiting_will_visit_probabilities if r[0][0] <= x <= r[0][1]
        )[1]
        if (relationship_to_person_who_person_who_will_be_visited == 'nb' and
                self.person.neighbors):
            person_they_will_visit = self._visit_a_neighbor()
        elif (relationship_to_person_who_person_who_will_be_visited == "fr" and
                any(f for f in self.person.friends if f.present and f.home is not self.person.home)):
            person_they_will_visit = self._visit_a_friend()
        elif (relationship_to_person_who_person_who_will_be_visited == "if" and
                any(f for f in self.person.immediate_family if f.present and f.home is not self.person.home)):
            person_they_will_visit = self._visit_an_immediate_family_member()
        elif (relationship_to_person_who_person_who_will_be_visited == "ef" and
                any(f for f in self.person.extended_family if f.present and f.home is not self.person.home)):
            person_they_will_visit = self._visit_an_extended_family_member()
        else:
            # Just stay home lol
            person_they_will_visit = None
        return person_they_will_visit

    def _visit_a_neighbor(self):
        """Return the neighbor that this person will visit.

        TODO: Flesh this out.
        """
        neighbor_they_will_visit = random.choice(list(self.person.neighbors))
        return neighbor_they_will_visit

    def _visit_a_friend(self):
        """Return the friend that this person will visit.

        TODO: Flesh this out.
        """
        friends_person_doesnt_live_with = [
            f for f in self.person.friends if f.present and f.home is not self.person.home
        ]
        if random.random() > 0.5:
            # Visit best friend (who doesn't live with them)
            friend_they_will_visit = max(
                friends_person_doesnt_live_with, key=lambda friend: self.person.relationships[friend].charge
            )
        else:
            friend_they_will_visit = random.choice(friends_person_doesnt_live_with)
        return friend_they_will_visit

    def _visit_an_immediate_family_member(self):
        """Return the immediate family member that this person will visit.

        TODO: Flesh this out.
        """
        immediate_family_person_doesnt_live_with = [
            f for f in self.person.immediate_family if f.present and f.home is not self.person.home
        ]
        immediate_family_they_will_visit = random.choice(immediate_family_person_doesnt_live_with)
        return immediate_family_they_will_visit

    def _visit_an_extended_family_member(self):
        """Return the extended family member that this person will visit.

        TODO: Flesh this out.
        """
        extended_family_person_doesnt_live_with = [
            f for f in self.person.extended_family if f.present and f.home is not self.person.home
        ]
        extended_family_they_will_visit = random.choice(extended_family_person_doesnt_live_with)
        return extended_family_they_will_visit

    def set_businesses_patronized(self):
        """Return the businesses that this person patronizes.

        This currently only returns the businesses nearest to where a person
        lives, but one could conceive a person going near one where they work or
        even going out of their way to go to a family member's business, etc. [TODO]
        """
        # Compile types of businesses that people visit at least some time in their
        # normal routine living
        routine_business_types = [
            "Bank", "Barbershop", "BusDepot", "DayCare", "Hotel", "OptometryClinic",
            "Park", "Restaurant", "Supermarket", "TaxiDepot", "Cemetery",
            "TattooParlor", "PlasticSurgeryClinic", "University"
        ]
        # Ascertain and record the closest businesses for each of those types
        businesses_patronized = {}
        for business_type in routine_business_types:
            businesses_patronized[business_type] = (
                self.person.city.nearest_business_of_type(
                    lot=self.person.home.lot, business_type=business_type
                )
            )
        self.businesses_patronized = businesses_patronized

    def update_business_patronized_of_specific_type(self, business_type):
        """Update which business of a specific type this person patronized.

        This gets called whenever a new business of this type is built in town, since
        people may decide to patronize the new business instead of the business they used
        to patronize.
        """
        self.businesses_patronized[business_type] = (
            self.person.city.nearest_business_of_type(
                lot=self.person.home.lot, business_type=business_type
            )
        )
