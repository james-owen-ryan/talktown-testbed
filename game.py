from config import Config
from person import *
from business import *
from city import *
import datetime


class Game(object):
    """A gameplay instance."""

    def __init__(self):
        """Initialize a Game object."""
        self.config = Config()
        self.year = self.config.date_city_gets_founded[-1]
        self.true_year = self.config.date_city_gets_founded[-1]  # True year never gets changed during retconning
        self.ordinal_date = datetime.date(*self.config.date_city_gets_founded).toordinal()  # Days since 01-01-0001
        self.founder = None  # The person who founds the city -- gets set by self._establish_setting()
        self.city = None
        # This gets incremented each time a new person is born/generated,
        # which affords a persistent ID for each person
        self.current_person_id = 0
        self._establish_setting()
        self.time_of_day = "day"

    def _establish_setting(self):
        """Establish the city in which this gameplay instance will take place."""
        # Generate a city plan
        self.city = City(self)  # TEMP for testing only
        # Generate a city founder -- this is a very rich person who will construct the
        # infrastructure on which the city gets built; this person will also serve as
        # the patriarch/matriarch of a very large, very rich family that the person who
        # # dies at the beginning of the game and Player 2 and cronies will part of
        self.founder = self._produce_city_founder()
        # Placeholder until you set up how the founder moves into the city
        self.founder.city = self.founder.spouse.city = self.city
        self.city.name = self._generate_name_for_city()
        # Make the city founder mayor de facto
        self.city.mayor = self.founder
        # Have that city founder establish a construction form in the limits of the new
        # city plan -- this firm will shortly construct all the major buildings in town
        ConstructionFirm(owner=self.founder)
        # Now that there is a construction firm in town, the founder and family can
        # move into town
        self.founder.move_into_the_city(hiring_that_instigated_move=None)
        # Have the city founder build several apartment complexes downtown -- first, however,
        # build a realty firm so that these apartment units can be sold
        RealtyFirm(owner=self.founder.spouse)
        self._build_apartment_complexes_downtown()
        # Construct city hall -- this will automatically make the city founder its
        # mayor -- and other public institutions making up the city's infrastructure;
        # each of these establishments will bring in workers who will find vacant lots
        # on which to build homes
        self._establish_city_infrastructure()

    def _produce_city_founder(self):
        """Produce the very rich person who will essentially start up this city.

        Some facts about this person will not vary across playthroughs: they is a
        very rich person who first establishes a construction firm within the limits
        of what will become the city;
        """
        city_founder = PersonExNihilo(
            game=self, job_opportunity_impetus=None, spouse_already_generated=None, this_person_is_the_founder=True
        )
        return city_founder

    def _generate_name_for_city(self):
        """Generate a name for the city."""
        if random.random() < self.config.chance_city_gets_named_for_founder:
            suffix = random.choice(["ville", " City", " Town", ""])
            name = "{0}{1}".format(self.founder.last_name, suffix)
        else:
            name = Names.a_place_name()
        return name

    def _build_apartment_complexes_downtown(self):
        """Build multiple apartment complexes downtown."""
        for _ in xrange(self.config.number_of_apartment_complexes_founder_builds_downtown):
            ApartmentComplex(owner=self.founder)

    def _establish_city_infrastructure(self):
        """Build the essential public institutions that will serve as the city's infrastructure."""
        for public_institution in self.config.public_institutions_started_upon_city_founding:
            public_institution(owner=self.founder)
        for business in self.config.businesses_started_upon_city_founding:
            owner = PersonExNihilo(game=self, job_opportunity_impetus=Owner, spouse_already_generated=None)
            owner.city = self.city
            business(owner=owner)

        # 7. eventually, have other people come in and start more of the following: OptometryClinic,
        # LawFirm, PlasticSurgeryClinic, TattooParlor, Restaurant, Bank, Supermarket, ApartmentComplex.
        #
        # 	- For these, have them potentially be started by reasoning over supply, need, etc.

    @property
    def date(self):
        """Return the current full date."""
        year = datetime.date.fromordinal(self.ordinal_date).year
        month = datetime.date.fromordinal(self.ordinal_date).month
        day = datetime.date.fromordinal(self.ordinal_date).day
        month_ordinals_to_names = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
            8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        date = "{0} of {1} {2}, {3}".format(
            self.time_of_day.title(), month_ordinals_to_names[month], day, year
        )
        return date

    def advance_timestep(self):
        """Advance to the next day/night cycle."""
        self._advance_time()
        # Have people go to the location they will be at this timestep
        for person in self.city.residents:
            person.routine.enact()
        # Have people observe their surroundings, which will cause knowledge to
        # build up, and have them socialize with other people also at that location --
        # this will cause relationships to form/progress and knowledge to propagate
        for person in self.city.residents:
            person.observe()
            person.socialize()
        # Deteriorate people's mental models from time passing
        for person in self.city.residents:
            for thing in person.mind.mental_models:
                person.mind.mental_models[thing].deteriorate()
            # But also have them reflect accurately on their own features
            person.reflect()

    def _advance_time(self):
        """Advance time of day and date, if it's a new day."""
        self.time_of_day = "night" if self.time_of_day == "day" else "day"
        if self.time_of_day == "day":
            self.ordinal_date += 1
            if datetime.date.fromordinal(self.ordinal_date) != self.year:
                # Happy New Year
                self.year += 1
