from config import Config
from person import *
from business import *
from city import *
#from city_for_testing import *
from relationship import Acquaintance  # FOR TESTING


class Game(object):
    """A gameplay instance."""

    def __init__(self):
        """Initialize a Game object."""
        self.config = Config()
        self.year = self.config.year_city_gets_founded
        self.true_year = self.config.year_city_gets_founded  # True year never gets changed during retconning
        self.founder = None  # The person who founds the city -- gets set by self._establish_setting()
        self.city = None
        self._establish_setting()

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

        # FOR TESTING
        self.date = 11
        self.founder.location = 'hi'
        self.a = Acquaintance(self.founder, self.founder.spouse, None)

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

    def _build_apartment_complexes_downtown(self):
        """Build multiple apartment complexes downtown."""
        for _ in xrange(self.config.number_of_apartment_complexes_founder_builds_downtown):
            ApartmentComplex(owner=self.founder)

    def _establish_city_infrastructure(self):
        """Build the essential public institutions that will serve as the city's infrastructure."""
        CityHall(owner=self.founder)
        Hospital(owner=self.founder)
        FireStation(owner=self.founder)
        PoliceStation(owner=self.founder)
        University(owner=self.founder)
        # Park(owner=self.founder)
        # Cemetery(owner=self.founder)


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