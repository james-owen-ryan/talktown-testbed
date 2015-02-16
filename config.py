class Config(object):
    """Configuration for a gameplay instance in terms of simulation and gameplay parameters."""

    def __init__(self):
        """Construct a Config object."""
        self.n_buildings_per_block = 5
        # Infertility
        self.male_infertility_rate = 0.07
        self.female_infertility_rate = 0.11
        # Sexuality
        self.homosexuality_incidence = 0.045
        self.bisexuality_incidence = 0.01
        self.asexuality_incidence = 0.002
        # Memory
        self.memory_mean = 0.7
        self.memory_sd = 0.1
        self.memory_cap = 0.9
        self.memory_floor = 0.1
        self.memory_floor_at_birth = 0.55  # Worst possible memory of newborn
        self.memory_sex_diff = 0.03  # Men have worse memory, studies show
        self.memory_heritability = 0.6  # Couldn't quickly find a study on this
        self.memory_heritability_sd = 0.05
        # Big Five personality traits (source Schmitt et al. "Big Five Traits
        # Across 56 Nations"; other papers for heritability)
        self.big_5_sd = 0.35
        self.big_5_o_mean = 0.375
        self.big_5_c_mean = 0.25
        self.big_5_e_mean = 0.15
        self.big_5_a_mean = 0.35
        self.big_5_n_mean = 0.0
        self.big_5_o_heritability = 0.57
        self.big_5_c_heritability = 0.54
        self.big_5_e_heritability = 0.49
        self.big_5_a_heritability = 0.48
        self.big_5_n_heritability = 0.42
        self.big_5_heritability_sd = 0.05
        # Businesses
        self.business_frequencies = self.set_frequency_of_each_business_type()

    @staticmethod
    def set_frequency_of_each_business_type():
        """Sets the frequency of each business type (relative to one another)."""
        business_frequency = {
            "Supermarket": 8,
            "Bank": 6,
            "Hotel": 5,
            "Barbershop": 5,
            "Eyeglass Shop": 3,
            "Tattoo Parlor": 3,
            "LASIK": 2,
            "Plastic Surgeon": 2,
            "Tattoo Removal": 1,
        }
        return business_frequency