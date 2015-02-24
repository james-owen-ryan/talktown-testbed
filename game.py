from config import Config
import citygen
from person import *


class Game(object):
    """A gameplay instance."""

    def __init__(self):
        """Initialize a Game object."""
        self.config = Config()
        self.year = self.config.year_city_gets_founded
        self.true_year = self.config.year_city_gets_founded  # True year never gets changed during retconning
        self.founder = None  # The person who founds the city -- gets set by self._establish_setting()
        self.city = self._establish_setting()

    def _establish_setting(self):
        """Establish the city in which this gameplay instance will take place."""
        # Generate a city plan
        city = citygen.generate_city_plan(game=self)  # Placeholder
        # Generate a city founder -- this is a very rich person who will construct the
        # infrastructure on which the city gets built; this person will also serve as
        # the patriarch/matriarch of a very large, very rich family that the person who
        # dies at the beginning of the game and Player 2 and cronies will part of
        self.founder = self._produce_city_founder()
        # Have that city founder establish a construction form in the limits of
        # the new city plan
        construction_firm = ConstructionFirm(owner=city_founder)

        return city

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

    #
    # 2/1. have them declare themself mayor (or just be it by default)
    #
    # 3. have that construction firm build a city hall, a police station, a fire station, and a hospital, and a
    # university (which the rich person owns and is named after them)
    #
    # 4. have the city hall establish a park, cemetery (also named after the rich guy?)
    #
    # 5. have the rich man's children start Bank, RealtyFirm, multiple ApartmentComplexes, Hotel, Supermarket,
    # BusDepot, TaxiDepot
    #
    # 6. have other people come into town and start Barbershop, multiple Restaurants
    #
    # 7. eventually, have other people come in and start first or more of the following: OptometryClinic,
    # LawFirm, PlasticSurgeryClinic, TattooParlor, Restaurant, Bank, Supermarket, ApartmentComplex.
    #
    # 	- For these, have them potentially be started by reasoning over supply, need, etc.

    def advance_one_year(self):
        """Advance one year (the timestep during simulation."""
        self.true_year += 1
        self.year = self.true_year