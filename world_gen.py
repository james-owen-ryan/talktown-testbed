import random
from person import Person


class Creator(object):
    """Creator of a city that simulates up to the start of gameplay."""

    def __init__(self, game):
        """Construct a Creator object."""
        self.game = game

    def generate_city(self):
        """Generate a city."""
        return self

    def simulate_to_present_day(self):
        """Simulate the development of a city from its founding to the time gameplay takes place."""
        pass

    def plat_city_plan(self):
        """Plat a city plan by recursively partitioning its land area into blocks, and those blocks into lots."""
        config = self.game.config
        downtown_x_coordinate, downtown_y_coordinate = self.determine_location_of_downtown(config=config)


    @staticmethod
    def determine_location_of_downtown(config):
        """Determine the location of downtown, around which city founders will establish themselves."""
        downtown_x_coordinate = (config.city_width_in_blocks / 2)
        downtown_x_coordinate += random.randint(  # Displace horizontally from the center of the map
            -config.city_downtown_blocks_displaced_from_center_max,
            config.city_downtown_blocks_displaced_from_center_max
        )
        downtown_y_coordinate = (config.city_width_in_blocks / 2)
        downtown_y_coordinate += random.randint(  # Displace vertically from the center of the map
            -config.city_downtown_blocks_displaced_from_center_max,
            config.city_downtown_blocks_displaced_from_center_max
        )
        return downtown_x_coordinate, downtown_y_coordinate

    def generate_founding_residents(self):
        """Generate a group of families and single people constituting the city's founding residents.

        To generate a family, game time reverts to the births of the parents, respectively, and then
        to their marriage date. Each of these dates is chosen randomly. Next, the couple's marriage,
        in terms of sex and, if applicable, birth, is simulated up to the founding of the city.

        Single people, who will live alone, are also generated similarly to the parents of the above
        families.
        """
        config = self.game.config
        n_families_to_generate, n_single_founders_to_generate = (
            self.determine_number_of_founding_families_and_other_people(config=config)
        )
        families = []
        for family in xrange(n_families_to_generate):
            mother, father = self.generate_mother_and_father_of_a_founding_family(config=config)
            families.append((mother, father))
            # Change year to marriage year, father builds house, moves in, marries mother
            marriage_year = father.birth_year + (
                random.normalvariate(
                    config.founding_father_age_at_marriage_mean, config.founding_father_age_at_marriage_sd
                )
            )
            marriage_year = int(round(marriage_year))
            while (
                # Make sure father or mother isn't too young for marriage, or that marriage is slated
                # to happen after the city has been founded (which is in the future relative to the sim
                # at this point)
                marriage_year - father.birth_year < config.founding_father_age_at_marriage_floor or
                marriage_year - mother.birth_year < config.founding_mother_age_at_marriage_floor or
                marriage_year >= config.year_city_gets_founded
            ):
                marriage_year = father.birth_year + (
                    random.normalvariate(
                        config.founding_father_age_at_marriage_mean, config.founding_father_age_at_marriage_sd
                    )
                )
                marriage_year = int(round(marriage_year))
            father.marry(mother)
            # Simulate sex and birth in marriage thus far
            for year in xrange(self.year, self.genesis+1): # This will also end with year at world gen year
                self.year = year
                if mother.pregnant:
                    mother.bear()
                if not mother.kids:
                    if random.randint(0,99) < 75:
                        father.copulate(mother)
                elif mother.kids:
                    chance = 70/len(mother.kids)
                    if random.randint(0,99) < chance:
                        father.copulate(mother)
        for single_founder in xrange(n_single_founders_to_generate):
            # Generate single people
            age = random.randint(13, 59)
            p = Primordial(origin=settlement, player=False, forced_gender=None, forced_age=age,
                force_family=False)

    @staticmethod
    def determine_number_of_founding_families_and_other_people(config):
        """Determine how many founding families and other people to generate."""
        # Determine number of founding families, given parameters specified in config.py
        n_families_to_generate = random.normalvariate(
            config.n_founding_families_mean, config.n_founding_families_sd
        )
        n_families_to_generate = int(round(n_families_to_generate))
        if n_families_to_generate < config.n_founding_families_floor:
            n_families_to_generate = config.n_founding_families_floor
        elif n_families_to_generate > config.n_founding_families_cap:
            n_families_to_generate = config.n_founding_families_cap
        # Determine number of single founders, given parameters specified in config.py
        n_single_founders_to_generate = random.normalvariate(
            config.n_single_founders_mean, config.n_single_founders_sd
        )
        n_single_founders_to_generate = int(round(n_single_founders_to_generate))
        if n_single_founders_to_generate < config.n_single_founders_floor:
            n_single_founders_to_generate = config.n_single_founders_floor
        elif n_single_founders_to_generate > config.n_single_founders_cap:
            n_single_founders_to_generate = config.n_single_founders_cap
        return n_families_to_generate, n_single_founders_to_generate

    @staticmethod
    def generate_mother_and_father_of_a_founding_family(config):
        """Generate a mother and father of a founding family."""
        # Generate age of mother and father of this family
        mother_age = random.randint(config.founding_mother_age_floor, config.founding_mother_age_cap)
        father_age = mother_age + (
            random.randint(config.founding_father_age_diff_floor, config.founding_father_age_diff_cap)
        )
        if father_age < config.founding_father_age_floor:
            father_age = config.founding_father_age_floor
        # Generate mother and father with appropriate sex and age assigned
        mother_birth_year = config.year_city_gets_founded - mother_age
        father_birth_year = config.year_city_gets_founded - father_age
        mother = Person(mother=None, father=None, birth_year=mother_birth_year, assigned_female=True)
        father = Person(mother=None, father=None, birth_year=father_birth_year, assigned_male=True)
        return mother, father
