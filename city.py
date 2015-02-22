from random import random
from business import *
from residence import *
from occupation import *
from corpora import Names
from config import Config


class City(object):
    """A city in which a gameplay instance takes place."""

    def __init__(self, game, founded):
        """Initialize a City object."""
        self.game = game
        self.founded = founded
        self.business_needs = self.determine_business_needs(config=self.game.config)
        self.residents = set()
        self.departed = set()  # People who left the city (i.e., left the simulation)
        self.deceased = set()  # People who died in in the city
        self.companies = set()
        self.vacant_homes = set()
        self.vacant_lots = set()

    @property
    def all_time_residents(self):
        """Return everyone who has at one time lived in the city."""
        return self.residents | self.deceased | self.departed

    @property
    def a_business_need(self):
        """Pop and return a random business need."""
        # If you've run out of business needs, just repopulate the list from scratch
        if not self.business_needs:
            self.business_needs = self.determine_business_needs(config=self.game.config)
        random.shuffle(self.business_needs)
        return self.business_needs.pop()

    @property
    def unemployed(self):
        """Return unemployed (young) people, excluding retirees."""
        unemployed_people = set()
        for resident in self.residents:
            if not resident.occupation and not resident.retired:
                if resident.age >= self.game.config.age_people_start_working:
                    unemployed_people.add(resident)
        return unemployed_people

    @staticmethod
    def determine_business_needs(config):
        """Determine what types of businesses are needed in this city."""
        business_needs = []
        for business_type in config.business_frequencies:
            business_needs += [business_type] * config.business_frequencies[business_type]
        return business_needs

    def workers_of_trade(self, occupation):
        """Return all residents in the city who practice to given occupation.

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

    def __init__(self, x_coord, y_coord, street, number):
        """Initialize a Block object."""
        self.game = street.city.game
        self.city = street.city
        self.street = street
        self.number = number
        self.lots = []

    def __str__(self):
        """Return string representation."""
        return "{} block of {}".format(self.number, str(self.street))

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


class Tract(object):
    """A tract of land on a block in a city, upon which parks and cemeteries are established."""

    def __init__(self, block):
        """Initialize a Lot object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block


class Lot(object):
    """A lot on a block in a city, upon which buildings and houses get erected."""

    def __init__(self, block, house_number):
        """Initialize a Lot object."""
        self.game = block.city.game
        self.city = block.city
        self.street = block.street
        self.block = block
        self.house_number = house_number  # In the event a building is erected here, it inherits this