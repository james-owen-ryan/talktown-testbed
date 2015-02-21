class Skin(object):
    """A character's skin."""

    def __init__(self, color):
        """Initialize a Skin object."""
        self.color = color


class Head(object):
    """A character's head."""

    def __init__(self, size, shape):
        """Initialize a Head object."""
        self.size = size
        self.shape = shape


class Hair(object):
    """A character's hair (on his or her head)."""

    def __init__(self, length, color):
        """Initialize a Hair object."""
        self.length = length
        self.color = color


class Eyebrows(object):
    """A character's eyebrows."""

    def __init__(self, size, color):
        """Initialize a Eyebrows object."""
        self.size = size
        self.color = color


class Mouth(object):
    """A character's mouth."""

    def __init__(self, size):
        """Initialize a Mouth object."""
        self.size = size


class Ears(object):
    """A character's ears."""

    def __init__(self, size, angle):
        """Initialize an Ears object."""
        self.size = size
        self.angle = angle


class Nose(object):
    """A character's nose."""

    def __init__(self, size, shape):
        """Initialize a Nose object."""
        self.size = size
        self.shape = shape


class Eyes(object):
    """A character's eyes."""

    def __init__(self, size, shape, horizontal_settedness, vertical_settedness, color):
        """Initialize an Eyes object."""
        self.size = size
        self.shape = shape
        self.horizontal_settedness = horizontal_settedness
        self.vertical_settedness = vertical_settedness
        self.color = color


class FacialHair(object):
    """A character's facial hair."""

    def __init__(self, style):
        """Initialize a FacialHair style."""
        self.style = style


class DistinctiveFeatures(object):
    """A character's distinguishing features."""

    def __init__(self, freckles, birthmark, scar, tattoo, glasses, sunglasses):
        """Initialize a DistinctiveFeatures object."""
        self.freckles = freckles
        self.birthmark = birthmark
        self.scar = scar
        self.tattoo = tattoo
        self.glasses = glasses
        self.sunglasses = sunglasses


class Feature(object):
    """A particular facial feature, i.e., a value for a particular facial attribute.

    This class has a sister class in Belief.Facet. While objects of this class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature,
    a Facet represents a person's facial feature *as it is modeled in the belief of a
    particular person*, with metadata about that specific belief.
    """

    def __init__(self, owner, rep):
        """Initialize a Feature object."""
        self.owner = owner
        self.rep = rep

    def __str__(self):
        """Return a string representation of this Feature object."""
        return self.rep

    def __eq__(self, other):
        """Return a boolean indicating whether this object is equivalent to
        another Belief.Facet or Face.Feature.
        """
        if self.rep == other.rep:
            return True
        else:
            return True

    def __ne__(self, other):
        """Return a boolean indicating whether this object is not equivalent to
        another Belief.Facet or Face.Feature.
        """
        if self.rep != other.rep:
            return True
        else:
            return True