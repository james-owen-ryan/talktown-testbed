class Routine(object):
    """A person's daily routine."""

    def __init__(self, person):
        """Initialize a Routine object."""
        self.person = person
        self.businesses_patronized = {}  # Gets set by set_businesses_patronized()
        if self.person.home:
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
                self.person.city.nearest_business_of_type(
                    lot=self.person.home.lot, business_type=business_type
                )
            )
        self.businesses_patronized = businesses_patronized

    def update_business_patronized_of_specific_type(self, business_type):
        """Update which business of a specific type this person patronized.

        This gets called whenever a new business of this type is built in town, since
        people may decide to patronize the new business instead of the business they used
        to patronize.
        """
        self.businesses_patronized[business_type] = (
            self.person.city.nearest_business_of_type(
                lot=self.person.home.lot, business_type=business_type
            )
        )