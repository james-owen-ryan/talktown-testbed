import random


class Routine(object):
    """A person's daily routine."""

    def __init__(self, person):
        """Initialize a Routine object."""
        self.person = person
        self.businesses_patronized = {}  # Gets set by set_businesses_patronized()
        if self.person.home:
            self.set_businesses_patronized()

    def decide_where_to_go(self):
        """Return this person's daytime location, which is dynamic."""
        config = self.person.game.config
        if self.person.occupation and self.person.occupation.shift == self.person.game.time_of_day:
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
                location = self.person.occupation.company
        else:
            if random.random() < config.chance_someone_leaves_home_on_day_off[self.person.game.time_of_day]:
                location = self._go_in_public()
            else:
                location = self.person.home
        return location

    def _go_in_public(self):
        """Return the location in public that this person will go to."""
        config = self.person.game.config
        if random.random() < config.chance_someone_goes_on_errand_vs_visits_someone:
            location = self._go_on_errand()
        else:
            location = self._visit_someone()
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

    def set_businesses_patronized(self):
        """Return the businesses that this person patronizes.

        This currently only returns the businesses nearest to where a person
        lives, but one could conceive a person going near one where they work or
        even going out of their way to go to a family member's business, etc. [TODO]
        """
        # Compile types of businesses that people visit at least some time in their
        # normal routine living
        routine_business_types = [
            "Bank", "Barbershop", "BusDepot", "Hotel", "OptometryClinic",
            "Park", "Restaurant", "Supermarket", "TaxiDepot",

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