class Name(str):
    """A name, in the sense of a persistent object that can be passed on.

    Even if two people have the same name, they will only have the same name object if
    the two names have the same origination. In this sense, objects of this class represent
    the name as a persistent entity, not as a text symbol.
    """

    def __init__(self, value, progenitor, conceived_by=(), derived_from=()):
        """Initialize a Name object.

        @param progenitor: The Person with whom this name originates; if this is a hyphenated surname,
                           the progenitor will be the first child to whom it is given.
        @param conceived_by: The Person(s) who conceived of this name; if it's a forename, this will
                             be the progenitor's parents, but if it's a surname this will be None unless
                             the name is hyphenated.
        @param derived_from: The two Names from which a hyphenated surname is derived.
        """
        super(Name, self).__init__()
        self.progenitor = progenitor
        self.conceived_by = conceived_by
        self.derived_from = derived_from
        self.hyphenated = True if derived_from else False

    def __new__(cls, value, progenitor, conceived_by, derived_from):
        """Do str stuff."""
        return str.__new__(cls, value)

    @property
    def bearers(self):
        """Return all people who have had this name."""
        bearers = set()
        for person in self.progenitor.game.city.all_time_residents:
            if person.first_name is self or person.middle_name is self or person.last_name is self:
                bearers.add(person)
        return bearers