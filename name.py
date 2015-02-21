class Name(object):
    """A name, in the sense of a persistent object that can be passed on.

    Even if two people have the same name, they will only have the same name object if
    the two names have the same origination. In this sense, objects of this class represent
    the name as a persistent entity, not as a text symbol.
    """

    def __init__(self, rep, progenitor, conceived_by):
        """Initialize a Name object.

        @param rep: The name itself (a string).
        @param bearer: The person with whom this name originates.
        @param conceived_by: The person(s) who conceived of this name (generally, the bearer's parents).
        """
        self.rep = rep
        self.game = progenitor.game
        self.progenitor = progenitor
        self.conceived_by = conceived_by

    def __str__(self):
        """Return string representation."""
        return self.rep

    @property
    def bearers(self):
        """Return all people who have had this name."""
        bearers = set()
        for person in self.game.city.all_time_residents:
            if person.first_name is self or person.middle_name is self or person.last_name is self:
                bearers.add(person)
        return bearers