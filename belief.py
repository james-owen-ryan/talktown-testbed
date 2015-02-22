class Person(object):
    """A person's mental model of another person, representing everything she believes about her."""

    def __init__(self, owner, subject):
        """Initialize a Person object."""
        self.owner = owner  # Owner of the belief
        self.subject = subject  # Subject of the belief


class Place(object):
    """A person's mental model of a place, representing everything she believes about it."""

    def __init__(self, owner, subject):
        """Initialize a Place object."""
        self.owner = owner
        self.subject = subject


class Facet(str):
    """A facet of one person's belief about another person that pertains to a specific feature.

    This class has a sister class in Face.Feature. While objects of the Feature class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature, a Facet
    represents a person's facial feature *as it is modeled in the belief of a particular
    person*, with metadata about that specific belief.
    """

    def __init__(self, value, evidence):
        """Initialize a Facet object.

        @param value: A string representation of this facet, e.g., 'brown' as the Hair.color
                      attribute this represents.
        @param evidence: An information object that serves as the evidence for this being a
                         facet of a person's belief.
        """
        super(Facet, self).__init__()
        self.evidence = evidence

    def __new__(cls, value, evidence):
        return str.__new__(cls, value)