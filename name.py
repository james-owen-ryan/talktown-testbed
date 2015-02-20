class Name(object):
    """A name, in the sense of a persistent object that can be passed on.

    Even if two people have the same name, they will only have the same name object if
    the two names have the same origination. In this sense, objects of this class represent
    the name as a persistent entity, not as a text symbol.
    """

    def __init__(self, rep, bearer, conceived_by):
        """Construct a Name object.

        @param rep: The name itself (a string).
        @param bearer: The person with whom this name originates.
        @param conceived_by: The person(s) who conceived of this name (generally, the bearer's parents).
        """
        self.rep = rep
        self.bearer = bearer
        self.conceived_by = conceived_by

    def __str__(self):
        """Return string representation."""
        return self.rep