class Config(object):
    """Configuration parameters for a gameplay instance."""

    def __init__(self):
        """Construct a Config object."""
        self.n_buildings_per_block = 5
        self.business_frequencies = self.set_frequency_of_each_business_type()

    @staticmethod
    def set_frequency_of_each_business_type(self):
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