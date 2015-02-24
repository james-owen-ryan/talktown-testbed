from random import random
from business import *
from landmark import *
from residence import *
from occupation import *
from corpora import Names
from config import Config


class City(object):
    """A city in which a gameplay instance takes place."""

    def __init__(self, game):
        """Initialize a City object."""
        self.game = game
        self.founded = game.config.year_city_gets_founded
        self.residents = set()
        self.departed = set()  # People who left the city (i.e., left the simulation)
        self.deceased = set()  # People who died in in the city
        self.companies = set()
        self.lots = set()
        self.tracts = set()
        self.dwelling_places = set()  # Both houses and apartment units (not complexes)

    @property
    def vacant_lots(self):
        """Return all vacant lots in the city."""
        vacant_lots = (lot for lot in self.lots if not lot.building)
        return vacant_lots

    @property
    def vacant_homes(self):
        """Return all vacant homes in the city."""
        vacant_homes = (home for home in self.dwelling_places if not home.residents)
        return vacant_homes

    @property
    def all_time_residents(self):
        """Return everyone who has at one time lived in the city."""
        return self.residents | self.deceased | self.departed

    @property
    def unemployed(self):
        """Return unemployed (mostly young) people, excluding retirees."""
        unemployed_people = set()
        for resident in self.residents:
            if not resident.occupation and not resident.retired:
                if resident.age >= self.game.config.age_people_start_working:
                    unemployed_people.add(resident)
        return unemployed_people

    def workers_of_trade(self, occupation):
        """Return all population in the city who practice to given occupation.

        @param occupation: The class pertaining to the occupation in question.
        """
        return (resident for resident in self.residents if isinstance(resident.occupation, occupation))


class Street(object):
    """A street in a city."""

    def __init__(self, city, number, direction):
        """Initialize a Street object."""
        self.game = city.game
        self.city = city
        self.type = type
        self.number = number
        self.direction = direction  # Direction relative to the center of the city
        self.name = self.generate_name(number, direction)

    @staticmethod
    def generate_name(number, direction):
        """Generate a street name."""
        number_to_ordinal = {
            1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th'
        }
        if random.random() < 0.13:
            name = Names.any_surname()
        else:
            name = number_to_ordinal[number]
        if direction == 'E' or direction == 'W':
            street_type = 'Street'
        else:
            street_type = 'Avenue'
        name = "{} {} {}".format(name, street_type, direction)
        return name

    def __str__(self):
        """Return string representation."""
        return self.name


class Block(object):
    """A block on a street in a city."""

    def __init__(self, x_coord, y_coord,ewstreet,nsstreet, number):
        """Initialize a Block object."""
        # self.game = street.city.game
        # self.city = street.city
        self.ewstreet = ewstreet
        self.nsstreet = nsstreet
        self.number = number
        self.lots = []

    def __str__(self):
        """Return string representation."""
        return "intersection of {} and {}".format(str(self.ewstreet),str(self.nsstreet))
        #return "{} block of {}".format(self.number, str(self.street))

    @property
    def buildings(self):
        """Return all the buildings on this block."""
        return (lot.building for lot in self.lots if lot.building)

    @staticmethod
    def determine_house_numbering(block_number, config):
        """Devise an appropriate house numbering scheme given the number of buildings on the block."""
        n_buildings = config.n_buildings_per_block
        house_numbers = []
        house_number_increment = 100.0 / n_buildings
        # Determine numbers for even side of the street
        for i in xrange(n_buildings):
            base_house_number = (i * house_number_increment) - 1
            house_number = base_house_number + int(random.random() * house_number_increment)
            if house_number % 2 == 1:  # Odd
                house_number += 1
            if house_number < 2:
                house_number = 2
            elif house_number > 98:
                house_number = 98
            house_number += block_number
            house_numbers.append(house_number)
        # Determine numbers for odd side of the street
        for i in xrange(n_buildings):
            base_house_number = (i * house_number_increment) - 1
            house_number = base_house_number + int(random.random() * house_number_increment)
            if house_number % 2 == 0:  # Even
                house_number += 1
            if house_number < 1:
                house_number = 1
            elif house_number > 99:
                house_number = 99
            house_number += block_number
            house_numbers.append(house_number)
        return house_numbers


class Lot(object):
    """A lot on a block in a city, upon which buildings and houses get erected."""

    def __init__(self, block, house_number):
        """Initialize a Lot object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block
        self.house_number = house_number  # In the event a business/landmark is erected here, it inherits this
        self.building = None  # Will always be None for Tract
        self.landmark = None  # Will always be None for Lot
        self._init_add_to_city_plan()
        self.neighboring_lots = self._init_get_neighboring_lots()

    def _init_add_to_city_plan(self):
        """Add self to the city plan."""
        self.city.lots.add(self)

    def _init_get_neighboring_lots(self):
        """Collect all lots that neighbor this lot."""
        neighboring_lots = set()
        return neighboring_lots

    @property
    def population(self):
        """Return the number of people living/working on the lot."""
        return len(self.building.residents)

    @property
    def secondary_population(self):
        """Return the total population of this lot and its neighbors."""
        secondary_population = 0
        for lot in {self} | self.neighboring_lots:
            secondary_population += lot.population
        return secondary_population

    @property
    def tertiary_population(self):
        """Return the total population of this lot and its neighbors and its neighbors' neighbors."""
        lots_already_considered = set()
        tertiary_population = 0
        for lot in {self} | self.neighboring_lots:
            if lot not in lots_already_considered:
                lots_already_considered |= lot
                tertiary_population += lot.population
                for neighbor_to_that_lot in lot.neighboring_lots:
                    if neighbor_to_that_lot not in lots_already_considered:
                        tertiary_population += lot.population
        return tertiary_population

    @property
    def dist_from_downtown(self):
        """Return the Manhattan distance between this lot and the center of downtown."""
        dist = -1
        return dist

    def get_dist_to(self, lot_or_tract):
        """Return the Manhattan distance between this lot and some lot or tract."""
        dist = -1
        return dist

    def dist_to_nearest_company_of_type(self, company_type):
        """Return the Manhattan distance between this lot and the nearest company of the given type."""
        distances = (
            self.get_dist_to(company.lot) for company in self.city.companies if isinstance(company, company_type)
        )
        if distances:
            return min(distances)
        else:
            return None


class Tract(Lot):
    """A tract of land on a block in a city, upon which parks and cemeteries are established."""

    def __init__(self, block, house_number):
        """Initialize a Lot object."""
        super(Tract, self).__init__(block, house_number)

    def _init_add_to_city_plan(self):
        """Add self to the city plan."""
        self.city.tracts.add(self)
