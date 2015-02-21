class Reflection(object):
    """A reflection by which one person perceives something about themself."""

    def __init__(self, subject, source):
        """Initialize a Reflection object."""
        pass


class Observation(object):
    """An observation by which one person perceives something about another person."""

    def __init__(self, subject, source):
        """Initialize an Observation object."""
        pass


class Concoction(object):
    """A concoction by which a person unintentionally concocts new information (i.e., changes an
    attribute's value from None to something)."""

    def __init__(self, subject, parent):
        """Initialize a Concoction object."""
        pass


class Lie(object):
    """A lie by which one person invents and conveys misinformation about someone."""

    def __init__(self, subject, source, recipient):
        """Initialize a Lie object."""
        pass


class Statement(object):
    """A statement by which one person conveys information about someone."""

    def __init__(self, subject, source, recipient):
        """Initialize a Statement object."""
        pass


class Degradation(object):
    """A degradation by which a person misremembers information (i.e., changes an attribute's value)."""

    def __init__(self, subject, parent):
        """Initialize a Degradation object."""
        pass


class Transference(object):
    """A transference by which a person unintentionally concocts new information (i.e., changes an
    attribute's value from None to something)."""

    def __init__(self, subject, parent):
        """Initialize a Transference object."""
        pass


class Forgetting(object):
    """A forgetting by which a person forgets information.

    A forgetting represents an ultimate terminus of a particular information item."""

    def __init__(self, subject, parent):
        """Initialize a Forgetting object."""
        pass