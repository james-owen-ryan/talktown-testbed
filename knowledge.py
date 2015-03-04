class Reflection(object):
    """A reflection by which one person perceives something about themself."""

    def __init__(self, subject, source):
        """Initialize a Reflection object."""
        self.type = "reflection"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        assert subject is source, "{} attempted to reflect about {}, who is not themself.".format(
            source.name, subject.name
        )
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Observation(object):
    """An observation by which one person perceives something about another person."""

    def __init__(self, subject, source):
        """Initialize an Observation object."""
        self.type = "observation"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Concoction(object):
    """A concoction by which a person unintentionally concocts new false knowledge (i.e., changes an
    attribute's value from None to something).

    Note: There is only two ways a concoction can happen: when a person modifies a mental model of
    a person they have never met (i.e., they hear things about this person from someone,
    but then concoct other things about this person that no one told them), or when they concoct
    a new value for an attribute whose true value they had forgotten.
    """

    def __init__(self, subject, source, parent=None):
        """Initialize a Concoction object."""
        self.type = "concoction"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Lie(object):
    """A lie by which one person invents and conveys knowledge about someone that they know is false."""

    def __init__(self, subject, source, recipient):
        """Initialize a Lie object."""
        self.type = "lie"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.recipient = recipient
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Statement(object):
    """A statement by which one person conveys knowledge about someone that they believe is true."""

    def __init__(self, subject, source, recipient, parent):
        """Initialize a Statement object."""
        self.type = "statement"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.recipient = recipient
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Mutation(object):
    """A mutation by which a person misremembers knowledge from time passing (i.e., changes an attribute's value)."""

    def __init__(self, parent, subject, source, mutated_belief_str):
        """Initialize a Mutation object."""
        self.type = "mutation"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.mutated_belief_str = mutated_belief_str
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Transference(object):
    """A transference by which a person unintentionally transposes another person's attribute onto their model
    of someone else."""

    def __init__(self, subject, source, belief_facet_transferred_from):
        """Initialize a Transference object.

        @param subject: The person to whom this knowledge pertains.
        @param source: The person doing the transference.
        @param belief_facet_transferred_from: The believed attribute of *another* person that mistakenly
                                      gets transferred as a believed attribute about subject.
        """
        self.type = "transference"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.attribute_transferred = belief_facet_transferred_from
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Forgetting(object):
    """A forgetting by which a person forgets knowledge.

    A forgetting represents an ultimate terminus of a particular information item -- they
    should only be attributed as evidence to Belief.Facets that are represented as an empty
    string.
    """

    def __init__(self, subject, source):
        """Initialize a Forgetting object.

        @param subject: The person to whom this knowledge pertains.
        @param source: The person doing the forgetting.
        """
        self.type = "forgetting"
        self.location = source.location
        self.time = source.game.date
        self.subject = subject
        self.source = source
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()