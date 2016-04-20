import random
from event import Event


class Thought(Event):
    """A thought that occurs in the mind of a person and affects their internal state."""

    def __init__(self, mind, tag, effects, evoked_by=None, provoked_by=None):
        """Initialize a Thought object."""
        super(Thought, self).__init__(mind.person.cosmos)
        self.mind = mind
        self.tag = tag
        self.effects = effects  # A tuple of lambda expressions that expect the argument 'person'
        self.evoked_by = evoked_by
        self.provoked_by = provoked_by

    def __str__(self):
        """Return string representation."""
        return "A thought about {tag}, produced in the mind of {owner} on the {date}".format(
            tag=self.tag,
            owner=self.mind.person.name,
            date=self.date[0].lower()+self.date[1:]
        )

    def execute(self):
        """Register the effects of this thought on its thinker."""
        for effect in self.effects:
            effect(person=self.mind.person)()


class Thoughts(object):
    """A helper class that supports Person.Mind.wander() by supplying thoughts.

    More specifically, this class evaluates thought preconditions to supply viable Thought
    objects, whose effects may then be executed by calling method Thought.execute().
    """
    # Prepare thought prototypes; these will be sorted these by likelihood, so that the most
    # frequent thought prototypes are considered first; this just makes sense, but it will
    # also serve computational efficiency, because we'll be rolling far less random numbers
    # when we iterate in this order
    thought_prototypes = None  # This will be set by Game.__init__()

    @classmethod
    def a_thought(cls, mind):
        """Return a thought whose preconditions are met."""
        # Search for a viable thought pattern; if you find one, render and return a thought
        person = mind.person
        for thought_prototype in cls.thought_prototypes:
            if random.random() < thought_prototype.likelihood:
                if all(precondition(person=person) for precondition in thought_prototype.preconditions):
                    thought = Thought(mind=mind, tag=thought_prototype.tag, effects=thought_prototype.effects)
                    return thought
        # If there's no viable thought patterns, return None
        return None

    @classmethod
    def an_elicited_thought(cls, mind, thought_prototype, evoked_by, provoked_by):
        """Return a thought that was evoked or provoked using the pattern specified by thought_prototype."""
        # Check if this thought pattern is viable; if it is, render and return a thought
        person = mind.person
        if all(thought_prototype.preconditions(person=person)):
            thought = Thought(
                mind=mind, tag=thought_prototype.tag, effects=thought_prototype.effects,
                evoked_by=evoked_by, provoked_by=provoked_by
            )
            return thought
        # If this thought pattern is not viable, return None
        return None


class ThoughtPrototype(object):
    """A prototype for a kind of thought.

    Objects of this class represent the single prototype of a type of thought. They
    prescribe the thought's tag, likelihood, preconditions, and effects.
    """

    def __init__(self, tag, likelihood, preconditions, effects):
        """Initialize a ThoughtPrototype object."""
        self.tag = tag
        # Likelihood represents the chance of it even being considered when a thought
        # is requested by a wandering mind
        self.likelihood = likelihood
        # Preconditions are represented as a tuple of lambda expressions that will
        # be evaluated by the Thoughts class
        self.preconditions = preconditions  # A tuple of lambda expressions
        # Effects are represented as a tuple of lambda expressions that will be
        # executed by Thought.execute() (an object that will be passed the effects
        # of a ThoughtPrototype object)
        self.effects = effects  # A tuple of lambda expressions