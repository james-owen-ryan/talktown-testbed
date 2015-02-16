from random import random
from business import *
from residence import *
from names import Names


class City(object):
    """A city wherein a gameplay instance takes place."""

    def __init__(self, game):
        """Construct a City object."""
        self.game = game
        self.business_needs = self.determine_business_needs(config=self.game.config)

    @staticmethod
    def determine_business_needs(config):
        """Determine what types of businesses are needed in this city."""
        business_needs = []
        for business_type in config.business_frequencies:
            business_needs += [business_type] * config.business_frequencies[business_type]
        return business_needs

    @property
    def a_business_need(self):
        """Pop and return a random business need."""
        # If you've run out of business needs, just repopulate the list from scratch
        if not self.business_needs:
            self.business_needs = self.determine_business_needs(config=self.game.config)
        random.shuffle(self.business_needs)
        return self.business_needs.pop()


class Street(object):
    """A street in a city."""

    def __init__(self, city, number, direction):
        """Construct a Street object."""
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
            name = Names.any_surname
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

    def __init__(self, street, number):
        """Construct a Block object."""
        self.game = street.city.game
        self.city = street.city
        self.street = street
        self.number = number
        self.buildings = self.generate_buildings()

    def __str__(self):
        """Return string representation."""
        return "{} block of {}".format(self.number, str(self.street))

    def generate_buildings(self):
        """Generate the buildings located on this lot."""
        house_numbers = self.determine_house_numbering(
            block_number=self.number, n_buildings=self.game.config.n_buildings_per_block
        )
        buildings = []
        for house_number in house_numbers:
            pass
        return buildings

    @staticmethod
    def determine_house_numbering(block_number, n_buildings):
        """Devise an appropriate house numbering scheme given the number of buildings on the block."""
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