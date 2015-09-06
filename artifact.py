# ARTIFACTS ARE LIKE ITEMS IN THE SIMS, EXCEPT THEY ARE NOT COLLECTIONS OF AFFORDANCES,
# BUT OF KNOWLEDGE-TRANSFER FUNCTIONS -- E.G., WHEN YOU LOOK AT A PHOTOGRAPH, KNOWLEDGE
# JUMPS INTO YOUR MIND ABOUT ITS SUBJECTS, OR WHEN YOU LOOK AT PERSON WEARING A WEDDING
# RING, YOU LEARN THAT THEY ARE MARRIED.

# ONE THING I NEED: A METHOD OF DETERMINING WHETHER SOMEONE CAN RECOGNIZE WHO IS IN
# A PHOTOGRAPH GIVEN THEIR OWN MENTAL MODELS. NAIVE WAY WOULD BE TO SAY IF THEY HAVE
# A MENTAL MODEL OF SUBJECT, THEY RECOGNIZE THEM. BETTER WOULD BE TO LOOK AT FEATURE
# OVERLAP BETWEEN WHAT A PHOTOGRAPH PROJECTS ABOUT THE SUBJECTS AND EVERYONE THEY
# KNOW ABOUT AND WHAT THEY KNOW ABOUT THOSE PEOPLE RE: THE FEATURES IN QUESTION.

# WHILE YOU THINK ABOUT THIS STUFF, KEEP IN MIND PLANNED TYPES OF KNOWLEDGE TRANSMISSION
# LIKE RADIO BROADCASTS, NEWSPAPER ARTICLES, OBITUARIES, ETC.


class Artifact(object):
    """A base class that all artifact subclasses inherit from."""

    def __init__(self):
        """Initialize an Artifact object."""
        self.provenance = []
        self.origin = None
        self.destruction = None


class Document(Artifact):
    """A base class that all document subclasses inherit from."""

    def __init__(self):
        """Initialize a Document object."""
        super(Document, self).__init__()


class Map(Artifact):
    """A base class that all map subclasses inherit from."""

    def __init__(self):
        """Initialize a Document object."""
        super(Map, self).__init__()


class Photograph(Artifact):
    """A base call that all photograph subclasses inherit from."""

    def __init__(self):
        """Initialize a Photograph object."""
        super(Photograph, self).__init__()


class Painting(Artifact):
    """A base call that all painting subclasses inherit from."""

    def __init__(self):
        """Initialize a Photograph object."""
        super(Painting, self).__init__()


class Gravestone(Artifact):
    """A gravestone that transmits its subject's name, birth year, and death year."""

    def __init__(self):
        """Initialize a Gravestone object."""
        super(Gravestone, self).__init__()

        # TODO gravestone could also transmit that the person had a spouse
        # or kids (e.g., 'Loved by his wife and children'), and if another
        # stone is next to it and obviously in the same family then that
        # very information is expressed


# Prescription, notice of doctors appointment, glasses (have to enforce people going to optometrist
# if they have glasses), upcoming dentist appointment (simulate dentist office bookkeeping).