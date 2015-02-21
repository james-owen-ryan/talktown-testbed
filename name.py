class Name(object):
    """A name, in the sense of a persistent object that can be passed on.

    Even if two people have the same name, they will only have the same name object if
    the two names have the same origination. In this sense, objects of this class represent
    the name as a persistent entity, not as a text symbol.
    """

    def __init__(self, rep, progenitor, conceived_by):
        """Initialize a Name object.

        @param rep: The name itself (a string).
        @param progenitor: The person with whom this name originates.
        @param conceived_by: The person(s) who conceived of this name (generally, the bearer's parents).
        """
        self.rep = rep
        self.game = progenitor.game
        self.progenitor = progenitor
        self.conceived_by = conceived_by

    def __str__(self):
        """Return string representation."""
        return self.rep

    def __eq__(self, other):
        """Return whether two names have the same rep."""
        assert (isinstance(other, Name)), (
            "An attempt was made to compare a Name object to an object of another class."
        )
        if self.rep == other.rep:
            return True
        else:
            return False

    def __ne__(self, other):
        """Return whether two names do not have the same rep."""
        assert (isinstance(other, Name)), (
            "An attempt was made to compare a Name object to an object of another class."
        )
        if self.rep != other.rep:
            return True
        else:
            return False

    @property
    def bearers(self):
        """Return all people who have had this name."""
        bearers = set()
        for person in self.game.city.all_time_residents:
            if person.first_name is self or person.middle_name is self or person.last_name is self:
                bearers.add(person)
        return bearers