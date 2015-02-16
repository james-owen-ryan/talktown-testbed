import random
from names import Names


class Person(object):
    """A person living in a city of a gameplay instance."""

    def __init__(self, mother, father):
        """Construct a Person object."""
        # Set location and gameplay instance
        self.game = self.mother.city.game
        self.city = self.mother.city
        # Set parents
        self.mother = mother
        self.father = father
        # Set sex
        self.male, self.female = self.init_sex()
        # Set name
        if not self.mother:
            self.first_name, self.middle_name, self.last_name, self.suffix = (
                self.prim_init_name(male=self.male)
            )
        elif self.mother:
            self.first_name, self.middle_name, self.last_name, self.suffix = (
                self.mother.name_child(child=self, father=father)
            )
        self.maiden_name = self.last_name
        self.tag = ''  # Allows players to tag characters with arbitrary strings
        # Set biological characteristics
        self.infertile = self.init_fertility(male=self.male, config=self.game.config)
        self.attracted_to_men, self.attracted_to_women = (
            self.init_sexuality(male=self.male, config=self.game.config)
        )
        # Set personality
        if not self.mother:
            self.big_5_o, self.big_5_c, self.big_5_e, self.big_5_a, self.big_5_n = (
                self.prim_init_personality()
            )
        elif self.mother:
            self.big_5_o, self.big_5_c, self.big_5_e, self.big_5_a, self.big_5_n = (
                self.init_personality(mother=self.mother, father=self.father)
            )
        # Set mental attributes
        if not self.mother:
            self.memory = self.prim_init_memory(male=self.male, config=self.game.config)
        elif self.mother:
            self.memory = self.init_memory(
                male=self.male, mother=self.mother, father=self.father, config=self.game.config
            )


    @staticmethod
    def prim_init_name(male):
        """Generate a name for a primordial person who has no parents."""
        if male:
            first_name = Names.a_masculine_name()
            middle_name = Names.a_masculine_name()
        elif not male:
            first_name = Names.a_feminine_name()
            middle_name = Names.a_feminine_name()
        last_name = Names.any_surname()
        suffix = ''
        return first_name, middle_name, last_name, suffix

    @staticmethod
    def prim_init_personality(config):
        """Generate values for each of the Big Five personality traits."""
        # Openness to experience
        openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience > 1:
            openness_to_experience = 1.0
        elif openness_to_experience < -1:
            openness_to_experience = -1.0
        # Conscientiousness
        conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness > 1:
            conscientiousness = 1.0
        elif conscientiousness < -1:
            conscientiousness = -1.0
        # Extroversion
        extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion > 1:
            extroversion = 1.0
        elif extroversion < -1:
            extroversion = -1.0
        # Agreeableness
        agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness > 1:
            agreeableness = 1.0
        elif agreeableness < -1:
            extroversion = -1.0
        # Neuroticism
        neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism > 1:
            neuroticism = 1.0
        elif neuroticism < -1:
            neuroticism = -1.0
        return openness_to_experience, conscientiousness, extroversion, agreeableness, neuroticism

    @staticmethod
    def prim_init_memory(male, config):
        """Determine this person's base memory capability, which will deteriorate with age."""
        memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor:
            memory = config.memory_floor
        return memory

    @staticmethod
    def init_sex():
        """Determine the sex of this person."""
        if random.random() < 0.5:
            male = True
            female = False
        else:
            male = False
            female = True
        return male, female

    @staticmethod
    def init_fertility(male, config):
        """Determine whether this person will be able to reproduce."""
        x = random.random()
        if male and x < config.male_infertility_rate:
            infertile = True
        elif not male and x < config.female_infertility_rate:
            infertile = True
        else:
            infertile = False
        return infertile

    @staticmethod
    def init_sexuality(male, config):
        """Determine this person's sexuality."""
        x = random.random()
        if x < config.homosexuality_incidence:
            # Homosexual
            if male:
                attracted_to_men = True
                attracted_to_women = False
            elif not male:
                attracted_to_men = False
                attracted_to_women = True
        elif x < config.homosexuality_incidence+config.bisexuality_incidence:
            # Bisexual
            attracted_to_men = True
            attracted_to_women = True
        elif x < config.homosexuality_incidence+config.bisexuality_incidence+config.asexuality_incidence:
            # Asexual
            attracted_to_men = True
            attracted_to_women = True
        else:
            # Heterosexual
            if male:
                attracted_to_men = False
                attracted_to_women = True
            elif not male:
                attracted_to_men = True
                attracted_to_women = False
        return attracted_to_men, attracted_to_women

    @staticmethod
    def init_personality(mother, father, config):
        """Determine this person's Big Five disposition, given their parents'."""
        # Openness to experience
        if random.random() < config.big_5_o_heritability:
            # Inherit this trait (with slight variance)
            takes_after = random.choice([father, mother])
            openness_to_experience = random.normalvariate(
                takes_after.openness_to_experience, config.big_5_heritability_sd
            )
        else:
            # Generate from the population mean
            openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience > 1:
            openness_to_experience = 1.0
        elif openness_to_experience < -1:
            openness_to_experience = -1.0
        # Conscientiousness
        if random.random() < config.big_5_c_heritability:
            takes_after = random.choice([father, mother])
            conscientiousness = random.normalvariate(
                takes_after.conscientiousness, config.big_5_heritability_sd
            )
        else:
            conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness > 1:
            conscientiousness = 1.0
        elif conscientiousness < -1:
            conscientiousness = -1.0
        # Extroversion
        if random.random() < config.big_5_e_heritability:
            takes_after = random.choice([father, mother])
            extroversion = random.normalvariate(
                takes_after.extroversion, config.big_5_heritability_sd
            )
        else:
            extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion > 1:
            extroversion = 1.0
        elif extroversion < -1:
            extroversion = -1.0
        # Agreeableness
        if random.random() < config.big_5_a_heritability:
            takes_after = random.choice([father, mother])
            agreeableness = random.normalvariate(
                takes_after.agreeableness, config.big_5_heritability_sd
            )
        else:
            agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness > 1:
            agreeableness = 1.0
        elif agreeableness < -1:
            extroversion = -1.0
        # Neuroticism
        if random.random() < config.big_5_n_heritability:
            takes_after = random.choice([father, mother])
            neuroticism = random.normalvariate(
                takes_after.neuroticism, config.big_5_heritability_sd
            )
        else:
            neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism > 1:
            neuroticism = 1.0
        elif neuroticism < -1:
            neuroticism = -1.0
        return openness_to_experience, conscientiousness, extroversion, agreeableness, neuroticism

    @staticmethod
    def init_memory(male, mother, father, config):
        """Determine a person's base memory capability, given their parents'."""
        if random.random() < config.memory_heritability:
            takes_after = random.choice([mother, father])
            memory = random.normalvariate(takes_after.memory, config.memory_heritability_sd)
        else:
            memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor_at_birth:
            memory = config.memory_floor_at_birth
        return memory

    @property
    def full_name(self):
        """Return a person's full name."""
        full_name = "{} {} {} {}".format(
            self.first_name, self.middle_name, self.last_name, self.suffix
        )
        return full_name

    @property
    def name(self):
        """Return a person's name."""
        name = "{} {} {}".format(self.first_name, self.last_name, self.suffix)
        return name

    @property
    def nametag(self):
        """Return a person's name, appended with their tag."""
        nametag = "{} {}".format(self.name, self.tag)
        return nametag

    def attracted_to(self, person):
        """Return whether this person is attracted to another person."""
        if person.male and self.attracted_to_men:
            attracted = True
        elif person.female and self.attracted_to_women:
            attracted = True
        else:
            attracted = False
        return attracted