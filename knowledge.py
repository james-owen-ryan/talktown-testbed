class Reflection(object):
    """A reflection by which one person perceives something about themself."""

    def __init__(self, location, time, subject, source):
        """Initialize a Reflection object."""
        self.location = location
        self.time = time
        self.parent = None  # Will always be None
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.source = source
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Observation(object):
    """An observation by which one person perceives something about another person."""

    # def __init__(self, location, time, subject, source):
    def __init__(self, subject, source):
        """Initialize an Observation object."""
        # self.location = location
        # self.time = time
        self.parent = None  # Will always be None
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.source = source
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Concoction(object):
    """A concoction by which a person unintentionally concocts new false knowledge (i.e., changes an
    attribute's value from None to something).

    Note: I only think this can happen when a person modifies a mental model of
    a person they have never met (i.e., they hear things about this person from someone,
    but then concoct other things about this person that no one told them). Concoction
    can't occur from a person actually meeting someone firsthand, because all mis/knowledge
    stemming from such an encounter will begin as an observation and then pollute either from
    a mutation or transference, or else be forgotten.
    """

    def __init__(self, subject, source):
        """Initialize a Concoction object."""
        self.location = None  # Spawn at nebulous time and space
        self.time = None
        self.parent = None  # Will always be None
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.source = source
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Lie(object):
    """A lie by which one person invents and conveys knowledge about someone that they know is false."""

    def __init__(self, location, time, subject, source, recipient):
        """Initialize a Lie object."""
        self.location = location
        self.time = time
        self.parent = None  # Will always be None
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.source = source
        self.recipient = recipient
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Statement(object):
    """A statement by which one person conveys knowledge about someone that they believe is true."""

    def __init__(self, location, time, parent, subject, source, recipient):
        """Initialize a Statement object."""
        self.location = location
        self.time = time
        self.parent = parent  # The knowledge object from which this directly descended
        self.parent.children.add(self)
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.source = source
        self.recipient = recipient
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Mutation(object):
    """A mutation by which a person misremembers knowledge from time passing (i.e., changes an attribute's value)."""

    def __init__(self, parent, subject):
        """Initialize a Mutation object."""
        self.location = None  # Happen at nebulous time and space
        self.time = None
        self.parent = parent  # The knowledge object from which this directly descended
        self.parent.children.add(self)
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Transference(object):
    """A transference by which a person unintentionally transposes another person's attribute onto their model
    of someone else."""

    def __init__(self, parent, subject, belief_facet_transferred_from):
        """Initialize a Transference object.

        @param subject: The person to whom this knowledge pertains.
        @param parent: The Reflection, Observation, Concoction, Lie, or Statement that this
                       Transference has mutated.
        @param belief_facet_transferred_from: The believed attribute of *another* person that mistakenly
                                      gets transferred as a believed attribute about subject.
        """
        self.location = None  # Happen at nebulous time and space
        self.time = None
        self.parent = parent  # The knowledge object from which this directly descended
        self.parent.children.add(self)
        self.children = set()  # Other knowledge objects that descend from this
        self.subject = subject
        self.attribute_transferred = belief_facet_transferred_from
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()


class Forgetting(object):
    """A forgetting by which a person forgets knowledge.

    A forgetting represents an ultimate terminus of a particular information item -- they
    should only be attributed as evidence to Belief.Facets that are represented as an empty
    string.
    """

    def __init__(self, subject, parent):
        """Initialize a Forgetting object.

        @param subject: The person to whom this knowledge pertains.
        @param parent: The Reflection, Observation, Concoction, Lie, or Statement that
                       represents the final state of this piece of knowledge prior to it
                       being terminated by this Forgetting.
        """
        self.location = None  # Happen at nebulous time and space
        self.time = None
        self.parent = parent  # The knowledge object from which this directly descended
        self.parent.children.add(self)
        self.children = set()  # Will always be empty set
        self.subject = subject
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()