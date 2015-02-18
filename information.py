class Reflection(object):
    """A reflection by which one person perceives something about themself."""

    def __init__(self, subject, source):
        """Construct a Reflection object."""
        pass


class Observation(object):
    """An observation by which one person perceives something about another person."""

    def __init__(self, subject, source):
        """Construct a Observation object."""
        pass


class Lie(object):
    """A lie by which one person invents and conveys misinformation about someone."""

    def __init__(self, subject, source, recipient):
        """Construct a Lie object."""
        pass


class Statement(object):
    """A statement by which one person conveys information about someone."""

    def __init__(self, subject, source, recipient):
        """Construct a Statement object."""
        pass