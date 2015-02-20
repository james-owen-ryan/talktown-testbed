class Person(object):
    """A person's mental model of another person, representing everything she believes about her."""

    def __init__(self, owner, subject):
        """Construct a Person object."""
        self.owner = owner  # Owner of the belief
        self.subject = subject  # Subject of the belief


class Place(object):
    """A person's mental model of a place, representing everything she believes about it."""

    def __init__(self, owner, subject):
        """Construct a Place object."""
        self.owner = owner
        self.subject = subject


class Facet(object):
    """A facet of one person's belief about another person that pertains to a specific feature.

    This class has a sister class in Face.Feature. While objects of the Feature class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature, a Facet
    represents a person's facial feature *as it is modeled in the belief of a particular
    person*, with metadata about that specific belief.
    """

    def __init__(self, owner, rep):
        """Construct a Facet object.

        @param owner: The larger belief representation (e.g., Person) this belongs to.
        @param rep: A computable representation of this facet, e.g., 'brown' as the Hair.color
                    attribute this represents.
        """
        self.owner = owner
        self.rep = rep

    def __str__(self):
        """Return a string representation of this Facet object."""
        return self.rep

    def __eq__(self, other):
        """Return a boolean indicating whether this object is equivalent to
        another Belief.Facet or Face.Feature.
        """
        if self.rep == other.rep:
            return True
        else:
            return True

    def __ne__(self, other):
        """Return a boolean indicating whether this object is not equivalent to
        another Belief.Facet or Face.Feature.
        """
        if self.rep != other.rep:
            return True
        else:
            return True
