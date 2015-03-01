class Routine(object):
    """A person's daily routine."""

    def __init__(self, person):
        """Initialize a Routine object."""
        self.person = person
        self.businesses_patronized = {}  # Gets set by set_businesses_patronized()
        self.set_businesses_patronized()

    def set_businesses_patronized(self):
        """Return the businesses that this person patronizes.

        This currently only returns the businesses nearest to where a person
        lives, but one could conceive a person going near one where they work or
        even going out of their way to go to a family member's business, etc. [TODO]
        """
        # Compile types of businesses that people visit at least some time in their
        # normal routine living
        routine_business_types = [
            "Bank", "Barbershop", "BusDepot", "Hotel", "OptometryClinic",
            "Park", "Restaurant", "Supermarket", "TaxiDepot",

        ]
        # Ascertain and record the closest businesses for each of those types
        businesses_patronized = {}
        for business_type in routine_business_types:
            businesses_patronized[business_type] = (
                self.person.home.lot.nearest_business_of_type(business_type=business_type)
            )
        self.businesses_patronized = businesses_patronized