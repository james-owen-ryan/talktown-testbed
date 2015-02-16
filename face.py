class Skin(object):
    """A character's skin."""

    def __init__(self, color):
        """Construct a Skin object."""
        self.color = color


class Head(object):
    """A character's head."""

    def __init__(self, size, shape):
        """Construct a Head object."""
        self.size = size
        self.shape = shape


class Hair(object):
    """A character's hair (on his or her head)."""

    def __init__(self, length, color):
        """Construct a Hair object."""
        self.length = length
        self.color = color


class Eyebrows(object):
    """A character's eyebrows."""

    def __init__(self, size, color):
        """Construct a Eyebrows object."""
        self.size = size
        self.color = color


class Mouth(object):
    """A character's mouth."""

    def __init__(self, size):
        """Construct a Mouth object."""
        self.size = size


class Ears(object):
    """A character's ears."""

    def __init__(self, size, angle):
        """Construct an Ears object."""
        self.size = size
        self.angle = angle


class Nose(object):
    """A character's nose."""

    def __init__(self, size, shape):
        """Construct a Nose object."""
        self.size = size
        self.shape = shape


class Eyes(object):
    """A character's eyes."""

    def __init__(self, size, shape, horizontal_settedness, vertical_settedness, color):
        """Construct an Eyes object."""
        self.size = size
        self.shape = shape
        self.horizontal_settedness = horizontal_settedness
        self.vertical_settedness = vertical_settedness
        self.color = color


class FacialHair(object):
    """A character's facial hair."""

    def __init__(self, style):
        """Construct a FacialHair style."""
        self.style = style


class DistinctiveFeatures(object):
    """A character's distinguishing features."""

    def __init__(self, freckles, birthmark, scar, tattoo, glasses, sunglasses):
        """Construct a DistinctiveFeatures object."""
        self.freckles = freckles
        self.birthmark = birthmark
        self.scar = scar
        self.tattoo = tattoo
        self.glasses = glasses
        self.sunglasses = sunglasses