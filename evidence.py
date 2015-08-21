import random


class PieceOfEvidence(object):
    """A superclass that all evidence subclasses inherit from."""

    def __init__(self, subject, source):
        """Initialize a PieceOfEvidence object."""
        self.type = self.__class__.__name__.lower()
        self.location = source.location
        self.time = source.game.date
        self.ordinal_date = source.game.ordinal_date
        # Also request and attribute an event number, so that we can later
        # determine the precise ordering of events that happen on the same timestep
        self.event_number = source.game.assign_event_number(new_event=self)
        self.subject = subject
        self.source = source
        self.recipient = None  # Will get overwritten in case of Lie, Statement, Declaration, Eavesdropping
        self.eavesdropper = None  # Will get overwritten in case of Eavesdropping
        self.attribute_transferred = None  # Will get overwritten in case of Transference
        self.beliefs_evidenced = set()  # Gets added to by Belief.Facet.__init__()
        self.base_strength = None  # Used to hold partial results of determine_strength()

    def __str__(self):
        """Return string representation."""
        location_and_time = "at {} on the {}".format(
            self.location.name, self.time[0].lower()+self.time[1:]
        )
        if self.type == 'eavesdropping':
            return "{}'s eavesdropping of {}'s statement to {} about {} {}".format(
                self.eavesdropper.name, self.source.name, self.recipient.name,
                self.subject.name, location_and_time
            )
        elif self.type == 'statement':
            return "{}'s statement to {} about {} {}".format(
                self.source.name, self.recipient.name, self.subject.name,
                location_and_time
            )
        elif self.type == 'declaration':
            return "{}'s own statement (declaration) to {} about {} {}".format(
                self.source.name, self.recipient.name, self.subject.name,
                location_and_time
            )
        elif self.type == 'lie':
            return "{}'s lie to {} about {} {}".format(
                self.source.name, self.recipient.name, self.subject.name,
                location_and_time
            )
        elif self.type == 'reflection':
            return "{}'s reflection about {} {}".format(
                self.subject.name, self.subject.reflexive, location_and_time
            )
        elif self.type == 'observation':
            return "{}'s observation of {} {}".format(
                self.source.name, self.subject.name, location_and_time
            )
        elif self.type == 'confabulation':
            return "{}'s confabulation about {} {}".format(
                self.source.name, self.subject.name, location_and_time
            )
        elif self.type == 'mutation':
            return "{}'s mutation of {} mental model of {} {}".format(
                self.source.name, self.source.possessive, self.subject.name, location_and_time
            )
        elif self.type == 'transference':
            return "{}'s transference from {} mental model of {} to {} mental model of {} {}".format(
                self.source.name, self.source.possessive, self.attribute_transferred.subject.name,
                self.source.possessive, self.subject.name, location_and_time
            )
        elif self.type == 'forgetting':
            return "{}'s forgetting of knowledge about {} {}".format(
                self.source.name, self.subject.name, location_and_time
            )

    def determine_strength(self, feature_type):
        """Determine the strength of a particular piece of evidence.

        This method takes into account how much the recipient trusts the source of the
        evidence and how strong the source's belief is (at this timestep, i.e., the time
        of it being conveyed to the recipient).
        """
        config = self.source.game.config
        source, recipient, subject = self.source, self.recipient, self.subject
        this_is_propagation = self.type in ('statement', 'lie', 'eavesdropping')
        if not self.base_strength:
            base_strength = config.base_strength_of_evidence_types[self.type]
            # If evidence is a type of propagation, alter the strength according to
            # recipient's trust value for the source
            if this_is_propagation:
                if source in recipient.relationships:
                    base_strength *= recipient.relationships[source].trust
                else:
                    # Recipient eavesdropped the source and don't actually have a relationship with them
                    base_strength *= config.trust_someone_has_for_random_person_they_eavesdrop
            self.base_strength = base_strength
        # If evidence is a type of propagation, alter the strength according to
        # the strength of the source's belief at the time of telling
        if this_is_propagation:
            if self.type == 'lie':
                teller_belief_strength = random.randint(1, 300)  # TODO maybe model lying ability here?
            else:
                teller_belief_facet = source.mind.mental_models[subject].get_facet_to_this_belief_of_type(
                    feature_type=feature_type
                )
                teller_belief_strength = teller_belief_facet.strength
            source_belief_strength_multiplier = config.function_to_determine_teller_strength_boost(
                teller_belief_strength=teller_belief_strength
            )
            return self.base_strength*source_belief_strength_multiplier
        else:
            return self.base_strength


class Reflection(PieceOfEvidence):
    """A reflection by which one person perceives something about themself."""

    def __init__(self, subject, source):
        """Initialize a Reflection object."""
        super(Reflection, self).__init__(subject=subject, source=source)
        assert subject is source, "{} attempted to reflect about {}, who is not themself.".format(
            source.name, subject.name
        )


class Observation(PieceOfEvidence):
    """An observation by which one person perceives something about another person."""

    def __init__(self, subject, source):
        """Initialize an Observation object."""
        super(Observation, self).__init__(subject=subject, source=source)
        if subject.type == 'person':
            assert source.location is subject.location, (
                "{} attempted to observe {}, who is in a different location.".format(
                    source.name, subject.name
                )
            )
        else:  # Subject is home or business
            assert source.location is subject, (
                "{} attempted to observe {}, but they are not located there.".format(
                    source.name, subject.name
                )
            )


class Confabulation(PieceOfEvidence):
    """A confabulation by which a person unintentionally concocts new false knowledge (i.e., changes an
    attribute's value from None to something).

    Note: There is only two ways a confabulation can happen: when a person modifies a mental model of
    a person they have never met (i.e., they hear things about this person from someone,
    but then concoct other things about this person that no one told them), or when they confabulate
    a new value for an attribute whose true value they had forgotten.
    """

    def __init__(self, subject, source):
        """Initialize a Confabulation object."""
        super(Confabulation, self).__init__(subject=subject, source=source)


class Lie(PieceOfEvidence):
    """A lie by which one person invents and conveys knowledge about someone that they know is false."""

    def __init__(self, subject, source, recipient):
        """Initialize a Lie object."""
        super(Lie, self).__init__(subject=subject, source=source)
        self.recipient = recipient


class Statement(PieceOfEvidence):
    """A statement by which one person conveys knowledge about someone that they believe is true."""

    def __init__(self, subject, source, recipient):
        """Initialize a Statement object."""
        super(Statement, self).__init__(subject=subject, source=source)
        self.recipient = recipient


class Declaration(PieceOfEvidence):
    """A declaration by which one person delivers a statement and comes to believe its information even more.

    See source [6] for evidence that this is realistic.
    """

    def __init__(self, subject, source, recipient):
        """Initialize a Declaration object."""
        super(Declaration, self).__init__(subject=subject, source=source)
        self.recipient = recipient


class Eavesdropping(PieceOfEvidence):
    """An eavesdropping by which one person overhears the information being conveyed by a statement or lie."""

    def __init__(self, subject, source, recipient, eavesdropper):
        """Initialize an Eavesdropping object."""
        super(Eavesdropping, self).__init__(subject=subject, source=source)
        self.recipient = recipient
        self.eavesdropper = eavesdropper


class Mutation(PieceOfEvidence):
    """A mutation by which a person misremembers knowledge from time passing (i.e., changes an attribute's value)."""

    def __init__(self, subject, source, mutated_belief_str):
        """Initialize a Mutation object."""
        super(Mutation, self).__init__(subject=subject, source=source)
        self.mutated_belief_str = mutated_belief_str


class Transference(PieceOfEvidence):
    """A transference by which a person unintentionally transposes another person's attribute onto their model
    of someone else."""

    def __init__(self, subject, source, belief_facet_transferred_from):
        """Initialize a Transference object.

        @param subject: The person to whom this knowledge pertains.
        @param source: The person doing the transference.
        @param belief_facet_transferred_from: The believed attribute of *another* person that mistakenly
                                      gets transferred as a believed attribute about subject.
        """
        super(Transference, self).__init__(subject=subject, source=source)
        self.attribute_transferred = belief_facet_transferred_from


class Forgetting(PieceOfEvidence):
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
        super(Forgetting, self).__init__(subject=subject, source=source)