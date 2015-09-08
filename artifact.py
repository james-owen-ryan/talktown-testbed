from corpora import GravestoneDetails
from belief import PersonMentalModel
from evidence import Examination
import random


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

# Prescription, notice of doctors appointment, glasses (have to enforce people going to optometrist
# if they have glasses), upcoming dentist appointment (simulate dentist office bookkeeping).


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

    # TODO PLOTS NEXT TO EACH OTHER ALSO TRANSMIT KNOWLEDGE, E.G., if another
    # stone is next to it and obviously in the same family then that
    # very information is expressed

    def __init__(self, subject):
        """Initialize a Gravestone object."""
        super(Gravestone, self).__init__()
        self.subject = subject
        if self.subject.extended_family:
            self.header = GravestoneDetails.a_header() + '\n'
            self.family_inscription = self._generate_family_inscription()
            self.epitaph = GravestoneDetails.an_epitaph() + '\n'
        else:
            self.header = random.choice(['Here lies buried', 'Rest in peace']) + '\n'
            self.family_inscription = ''
            self.epitaph = ''
        if (self.subject.occupations and
                self.subject.occupations[-1].__class__.__name__ in
                self.subject.game.config.occupations_that_may_appear_on_gravestones):
            self.occupation_inscription = '{vocation_str}\n'.format(
                vocation_str=self.subject.occupations[-1].vocation.title()
            )
        else:
            self.occupation_inscription = ''

    def _generate_family_inscription(self):
        """Generate a short inscription indicating this person's family roles, e.g., 'A loving husband'."""
        pertinent_relations = []
        if self.subject.spouse or self.subject.widowed:
            pertinent_relations.append('Husband' if self.subject.male else 'Wife')
        if self.subject.kids:
            pertinent_relations.append('Father' if self.subject.male else 'Mother')
        if self.subject.grandchildren:
            pertinent_relations.append('Grandfather' if self.subject.male else 'Grandmother')
        if not pertinent_relations:
            if self.subject.parents:
                pertinent_relations.append('Son' if self.subject.male else 'Daughter')
            if self.subject.siblings:
                pertinent_relations.append('Brother' if self.subject.male else 'Sister')
        if pertinent_relations:
            if len(pertinent_relations) == 2:
                return 'Loving {relations_str}\n'.format(
                    relations_str=' and '.join(pertinent_relations)
                )
            else:
                return 'Loving {relations_str}\n'.format(
                    relations_str=', '.join(pertinent_relations)
                )
        else:
            return None

    def _get_age_adjective(self):
        """Return an adjective indicating the age of this gravestone."""
        age_of_this_gravestone = self.subject.game.year-self.subject.death_year
        if age_of_this_gravestone > 200:
            age_description = 'very weathered'
        elif age_of_this_gravestone > 100:
            age_description = 'weathered'
        elif age_of_this_gravestone > 50:
            age_description = 'worn'
        elif age_of_this_gravestone > 5:
            age_description = 'fairly new'
        else:
            age_description = 'pristine'
        return age_description

    def __str__(self):
        """Return a string representation."""
        return "Gravestone of {subject.name}".format(subject=self.subject)

    @property
    def description(self):
        """A description of this gravestone."""
        age_adj = self._get_age_adjective()
        description = (
            "\nA {age_adj} gravestone that reads:\n\n"
            "{self.header}"
            "\n{subject.full_name}\n"
            "{subject.birth_year}-{subject.death_year}\n\n"
            "{self.occupation_inscription}"
            "{self.family_inscription}"
            "{self.epitaph}\n"
        ).format(
            age_adj=age_adj,
            self=self,
            subject=self.subject
        )
        return description

    def transmit_knowledge(self, examiner):
        """Transmit knowledge to a person observing this gravestone.

        A gravestone transmits its subject's first name, middle name, last name, suffix,
        surname ethnicity, surname hyphenatedness, birth year, death year, approximate age,
        status (i.e., dead), and potentially also their occupation.
        """
        # TODO WHAT DOES GRAVESTONE TRANSMIT ABOUT A PERSON'S FAMILY?
        deceased = self.subject
        if deceased not in examiner.mind.mental_models:
            # Instantiate a blank mental model (it will have no belief facets because
            # there is no initial observation or reflection)
            mental_model = PersonMentalModel(owner=examiner, subject=deceased, observation_or_reflection=None)
        else:
            mental_model = examiner.mind.mental_models[deceased]
        # Prepare an Examination piece of evidence
        examination = Examination(subject=deceased, source=examiner, artifact=self)
        # Update examiner's mental model of subject
        for feature_type in (
            'first name', 'middle name', 'last name', 'suffix',
            'surname ethnicity', 'hyphenated surname', 'birth year',
            'death year', 'approximate age', 'status'
        ):
            mental_model.consider_new_evidence(
                feature_type=feature_type,
                feature_value=deceased.get_feature(feature_type=feature_type),
                feature_object_itself=None,
                new_evidence=examination
            )
        if self.occupation_inscription:
            mental_model.consider_new_evidence(
                feature_type="job title",
                feature_value=deceased.get_feature(feature_type="job title"),
                feature_object_itself=None,
                new_evidence=examination
            )


class WeddingRing(Artifact):
    """A wedding ring that transmits a person's being married (if they're wearing it)."""

    def __init__(self):
        """Initialize a WeddingRing object."""
        super(WeddingRing, self).__init__()

    def transmit_knowledge(self):
        """Do nothing.

        A wedding ring doesn't transmit anything except when it's being worn, and this is
        handled differently than artifacts that in and of themselves transmit knowledge (in
        which cases this method actually gets called.
        """
        pass


