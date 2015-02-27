import random


class Face(object):
    """A character's face."""

    def __init__(self, person):
        """Initialize a Face object."""
        self.person = person
        self.skin = Skin(face=self)
        self.head = Head(face=self)
        self.hair = Hair(face=self)
        self.eyebrows = Eyebrows(face=self)
        self.eyes = Eyes(face=self)
        self.ears = Ears(face=self)
        self.nose = Nose(face=self)
        self.mouth = Mouth(face=self)
        self.facial_hair = FacialHair(face=self)
        self.distinctive_features = DistinctiveFeatures(face=self)

    def determine_feature(self, feature_type):
        """Determine a person's facial feature, given their parents' and/or the population distribution.

        Two facial features do not always get determined by this method: skin color is deterministic
        according to a person's parents' skin colors, and so skin color is only determined here for
        PersonsExNihilo; eyebrow color is depends heavily on a person's hair color, and because of this
        it is rarely determined by this method.
        """
        config = self.person.game.config
        feature_will_get_inherited = (
            self.person.biological_mother and
            random.random() < config.facial_feature_type_heritability[feature_type]
        )
        if feature_will_get_inherited:
            takes_after = self._determine_whom_feature_gets_inherited_from(feature_type=feature_type)
            type_str = self._get_a_persons_feature_of_type(person=takes_after, feature_type=feature_type)
            variant_id, exact_variant_inherited = self._determine_graphical_variant_of_this_feature(
                takes_after=takes_after, feature_type=feature_type
            )
        else:
            # Generate this feature from its population distribution
            takes_after = None
            exact_variant_inherited = False
            type_str, variant_id = self._generate_feature_from_its_population_distribution(
                feature_type=feature_type
            )
        # Construct the actual feature object
        feature_object = Feature(
            value=type_str, variant_id=variant_id, inherited_from=takes_after,
            exact_variant_inherited=exact_variant_inherited
        )
        return feature_object

    def _generate_feature_from_its_population_distribution(self, feature_type):
        """Generate a facial feature for a person given that feature's population distribution."""
        config = self.person.game.config
        if self.person.male:
            distribution = config.facial_feature_distributions_male[feature_type]
        else:
            distribution = config.facial_feature_distributions_female[feature_type]
        x = random.random()
        type_str = next(  # See config.py to understand what this is doing
            feature_type[1] for feature_type in distribution if feature_type[0][0] <= x <= feature_type[0][1]
        )
        variant_id = int(random.random() * 1000)
        return type_str, variant_id

    def _determine_whom_feature_gets_inherited_from(self, feature_type):
        """Determine whom this person will inherit this facial feature from."""
        config = self.person.game.config
        # Some features are more likely to be inherited from a parent/grandparent of the same sex
        if random.random() < config.facial_feature_chance_inheritance_according_to_sex[feature_type]:
            if self.person.male:
                possible_sources = (  # Two chances to inherit from father, one from maternal grandfather
                    self.person.biological_father, self.person.biological_father,
                    self.person.biological_mother.biological_father
                )
            else:
                possible_sources = (  # Two chances to inherit from mother, one from paternal grandmother
                    self.person.biological_mother, self.person.biological_mother,
                    self.person.biological_father.biological_mother
                )
        else:
            possible_sources = (self.person.biological_father, self.person.biological_mother)
        possible_sources = [source for source in possible_sources if source]  # Remove non-existent grandparents
        takes_after = random.choice(possible_sources)
        return takes_after

    def _determine_graphical_variant_of_this_feature(self, takes_after, feature_type):
        config = self.person.game.config
        if random.random() < config.facial_feature_variant_heritability[feature_type]:
            # Inherit the exact graphical variant that that parent/grandparent has
            variant_id = self._get_persons_feature_variant_of_type(
                person=takes_after, feature_type=feature_type
            )
            exact_variant_inherited = True
        else:
            variant_id = int(random.random() * 1000)  # Generate a seed for which variant gets selected
            exact_variant_inherited = False
        return variant_id, exact_variant_inherited

    @staticmethod
    def _get_a_persons_feature_of_type(person, feature_type):
        """Return this person's facial feature of the given type (only heritable features listed)."""
        features = {
            "skin color": person.face.skin.color,
            "head size": person.face.head.size,
            "head shape": person.face.head.shape,
            "hair length": person.face.hair.length,
            "hair color": person.face.hair.color,
            "eyebrow size": person.face.eyebrows.size,
            "eyebrow color": person.face.eyebrows.color,
            "mouth size": person.face.mouth.size,
            "ear size": person.face.ears.size,
            "ear angle": person.face.ears.angle,
            "nose size": person.face.nose.size,
            "nose shape": person.face.nose.shape,
            "eye size": person.face.eyes.size,
            "eye shape": person.face.eyes.shape,
            "eye color": person.face.eyes.color,
            "eye horizontal settedness": person.face.eyes.horizontal_settedness,
            "eye vertical settedness": person.face.eyes.vertical_settedness,
            "facial hair style": person.face.facial_hair.style,
            "freckles": person.face.distinctive_features.freckles,
            "birthmark": person.face.distinctive_features.birthmark,
            "scar": person.face.distinctive_features.scar,
            "tattoo": person.face.distinctive_features.tattoo,  # From nurture
            "glasses": person.face.distinctive_features.glasses,
            "sunglasses": person.face.distinctive_features.sunglasses  # From nurture
        }
        return features[feature_type]

    @staticmethod
    def _get_persons_feature_variant_of_type(person, feature_type):
        """Return this person's facial-feature variant for the given type (only heritable features listed)."""
        features = {
            "skin color": person.face.skin.color.variant_id,
            "head size": person.face.head.size.variant_id,
            "head shape": person.face.head.shape.variant_id,
            "hair length": person.face.hair.length.variant_id,
            "hair color": person.face.hair.color.variant_id,
            "eyebrow size": person.face.eyebrows.size.variant_id,
            "eyebrow color": person.face.eyebrows.color.variant_id,
            "mouth size": person.face.mouth.size.variant_id,
            "ear size": person.face.ears.size.variant_id,
            "ear angle": person.face.ears.angle.variant_id,
            "nose size": person.face.nose.size.variant_id,
            "nose shape": person.face.nose.shape.variant_id,
            "eye size": person.face.eyes.size.variant_id,
            "eye shape": person.face.eyes.shape.variant_id,
            "eye color": person.face.eyes.color.variant_id,
            "eye horizontal settedness": person.face.eyes.horizontal_settedness.variant_id,
            "eye vertical settedness": person.face.eyes.vertical_settedness.variant_id,
            "facial hair style": person.face.facial_hair.style.variant_id,
            "freckles": person.face.distinctive_features.freckles.variant_id,
            "birthmark": person.face.distinctive_features.birthmark.variant_id,
            "scar": person.face.distinctive_features.scar.variant_id,
            "tattoo": person.face.distinctive_features.tattoo.variant_id,  # From nurture
            "glasses": person.face.distinctive_features.glasses.variant_id,
            "sunglasses": person.face.distinctive_features.sunglasses.variant_id  # From nurture
        }
        return features[feature_type]


class Skin(object):
    """A character's skin."""

    def __init__(self, face):
        """Initialize a Skin object."""
        self.face = face
        if self.face.person.biological_mother:
            parent_skin_color_tuple = (
                self.face.person.biological_mother.face.skin.color,
                self.face.person.biological_father.face.skin.color
            )
            if parent_skin_color_tuple[0] == parent_skin_color_tuple[1]:
                skin_color = parent_skin_color_tuple[0]
            else:
                skin_color = (
                    self.face.person.game.config.child_skin_color_given_parents[parent_skin_color_tuple]
                )
            self.color = skin_color
        else:  # Generate from population distribution
            self.color = self.face.determine_feature(feature_type="skin color")


class Head(object):
    """A character's head."""

    def __init__(self, face):
        """Initialize a Head object."""
        self.face = face
        self.size = self.face.determine_feature(feature_type="head size")
        self.shape = self.face.determine_feature(feature_type="head shape")


class Hair(object):
    """A character's hair (on his or her head)."""

    def __init__(self, face):
        """Initialize a Hair object."""
        self.face = face
        self.length = self.face.determine_feature(feature_type="hair length")
        self.color = self.face.determine_feature(feature_type="hair color")


class Eyebrows(object):
    """A character's eyebrows."""

    def __init__(self, face):
        """Initialize a Eyebrows object."""
        self.face = face
        self.size = self.face.determine_feature(feature_type="eyebrow size")
        if random.random() < self.face.person.game.config.chance_eyebrows_are_same_color_as_hair:
            self.color = self.face.hair.color
        else:
            self.color = self.face.determine_feature(feature_type="eyebrow color")


class Eyes(object):
    """A character's eyes."""

    def __init__(self, face):
        """Initialize an Eyes object."""
        self.face = face
        self.size = self.face.determine_feature(feature_type="eye size")
        self.shape = self.face.determine_feature(feature_type="eye shape")
        self.color = self.face.determine_feature(feature_type="eye color")
        self.horizontal_settedness = self.face.determine_feature(feature_type="eye horizontal settedness")
        self.vertical_settedness = self.face.determine_feature(feature_type="eye vertical settedness")


class Ears(object):
    """A character's ears."""

    def __init__(self, face):
        """Initialize an Ears object."""
        self.face = face
        self.size = self.face.determine_feature(feature_type="ear size")
        self.angle = self.face.determine_feature(feature_type="ear angle")


class Nose(object):
    """A character's nose."""

    def __init__(self, face):
        """Initialize a Nose object."""
        self.face = face
        self.size = self.face.determine_feature(feature_type="nose size")
        self.shape = self.face.determine_feature(feature_type="nose shape")


class Mouth(object):
    """A character's mouth."""

    def __init__(self, face):
        """Initialize a Mouth object."""
        self.face = face
        self.size = self.face.determine_feature(feature_type="mouth size")


class FacialHair(object):
    """A character's facial hair."""

    def __init__(self, face):
        """Initialize a FacialHair style."""
        self.face = face
        self.style = self.face.determine_feature(feature_type="facial hair style")


class DistinctiveFeatures(object):
    """A character's other distinguishing facial features."""

    def __init__(self, face):
        """Initialize a DistinctiveFeatures object."""
        self.face = face
        self.freckles = self.face.determine_feature(feature_type="freckles")
        self.birthmark = self.face.determine_feature(feature_type="birthmark")
        self.scar = self.face.determine_feature(feature_type="scar")
        self.tattoo = self.face.determine_feature(feature_type="tattoo")
        self.glasses = self.face.determine_feature(feature_type="glasses")
        self.sunglasses = self.face.determine_feature(feature_type="sunglasses")


class Feature(str):
    """A particular facial feature, i.e., a value for a particular facial attribute.

    This class has a sister class in Belief.Facet. While objects of this class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature,
    a Facet represents a person's facial feature *as it is modeled in the belief of a
    particular person*, with metadata about that specific belief.
    """

    def __init__(self, value, variant_id, inherited_from, exact_variant_inherited):
        """Initialize a Facet object.

        @param variant_id: A persistent ID that is used as a seed to generate the specific
                           graphical variant of this type of facial feature (e.g., a *specific*
                           graphical variant of 'brown hair').
        @param value: A string representation of this facet, e.g., 'brown' as the Hair.color
                      attribute this represents.
        @param inherited_from: The parent from whom this personality feature was inherited,
                               if any. (Note, this refers to the feature type, not necessarily
                               the variant.)
        @param exact_variant_inherited: Whether the exact feature variant was also inherited
                                        from inherited_from.
        """
        super(Feature, self).__init__()
        self.variant_id = variant_id
        self.inherited_from = inherited_from
        self.exact_variant_inherited = exact_variant_inherited

    def __new__(cls, value, variant_id, inherited_from, exact_variant_inherited):
        """Do str stuff."""
        return str.__new__(cls, value)