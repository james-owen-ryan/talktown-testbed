# TODO enemies?


class Acquaintance(object):
    """An acquaintance between two people."""

    def __init__(self, subjects, preceded_by):
        """Initialize an Acquaintance object.

        @param subjects: The two people involved in this relationship.
        @param preceded_by: A Kinship relationship that preceded this, if any.
        """
        self.subjects = subjects
        self.preceded_by = preceded_by
        if preceded_by:
            preceded_by.succeeded_by = self
        self.succeeded_by = None  # Gets set by a succeeding Friendship object


class Friendship(object):
    """A friendship between two people."""

    def __init__(self, subjects, preceded_by):
        """Initialize a Friendship object.

        @param subjects: The two people involved in this relationship.
        @param preceded_by: An Acquaintance relationship that preceded this, if any.
        """
        self.subjects = subjects
        self.preceded_by = preceded_by


class Kinship(object):
    """A family relationship between two people."""

    def __init__(self, subjects, relationship):
        """Initialize a Kinship object.

        @param subjects: The two people involved in this relationship.
        @param relationship: A string representing the specific family relationship.
        """
        self.subjects = subjects
        self.relationship = relationship
        self.succeeded_by = None  # Gets set by a succeeding Acquaintance or (ultimately) Friendship object