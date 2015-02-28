from belief import *


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
        self._init_build_mental_models_of_each_other()

    def _init_build_mental_models_of_each_other(self):
        """Instantiate (or further fill in) mental models of each other.

        Note: People may already have mental models of people they haven't met from
        other people having told them about them.
        """
        for person in self.subjects:
            other_person = self.subjects[0] if self.subjects[0] is not person else self.subjects[1]
            person.mind.mental_models[other_person] = PersonMentalModel(
                owner=person, subject=other_person, originating_in_first_hand_observation=True
            )


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