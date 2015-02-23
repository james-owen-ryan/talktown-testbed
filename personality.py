import random


class Personality(object):
    """A person's personality."""

    def __init__(self, subject):
        """Initialize a Personality object."""
        self.subject = subject
        if self.subject.mother:  # Person object
            self.openness_to_experience = self._init_openness_to_experience()
            self.conscientiousness = self._init_conscientiousness()
            self.extroversion = self._init_extroversion()
            self.agreeableness = self._init_agreeableness()
            self.neuroticism = self._init_neuroticism()
        else:  # PersonExNihilo object
            self.openness_to_experience = self._init_ex_nihilo_openness_to_experience()
            self.conscientiousness = self._init_ex_nihilo_conscientiousness()
            self.extroversion = self._init_ex_nihilo_extroversion()
            self.agreeableness = self._init_ex_nihilo_agreeableness()
            self.neuroticism = self._init_ex_nihilo_neuroticism()

    @property
    def o(self):
        """Return this person's openness to experience."""
        return self.openness_to_experience

    @property
    def c(self):
        """Return this person's conscientiousness."""
        return self.conscientiousness

    @property
    def e(self):
        """Return this person's extroversion."""
        return self.extroversion

    @property
    def a(self):
        """Return this person's agreeableness."""
        return self.agreeableness

    @property
    def n(self):
        """Return this person's neuroticism."""
        return self.neuroticism

    def _init_openness_to_experience(self):
        """Initialize a value for the Big Five personality trait 'openness to experience'."""
        config = self.subject.game.config
        if random.random() < config.big_5_o_heritability:
            # Inherit this trait (with slight variance)
            takes_after = random.choice([self.subject.father, self.subject.mother])
            openness_to_experience = random.normalvariate(
                takes_after.openness_to_experience, config.big_5_heritability_sd
            )
        else:
            takes_after = None
            # Generate from the population mean
            openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience < config.big_5_floor:
            openness_to_experience = -1.0
        elif openness_to_experience > config.big_5_cap:
            openness_to_experience = 1.0
        feature_object = Feature(value=openness_to_experience, inherited_from=takes_after)
        return feature_object

    def _init_conscientiousness(self):
        """Initialize a value for the Big Five personality trait 'conscientiousness'."""
        config = self.subject.game.config
        if random.random() < config.big_5_c_heritability:
            takes_after = random.choice([self.subject.father, self.subject.mother])
            conscientiousness = random.normalvariate(
                takes_after.conscientiousness, config.big_5_heritability_sd
            )
        else:
            takes_after = None
            conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness < config.big_5_floor:
            conscientiousness = -1.0
        elif conscientiousness > config.big_5_cap:
            conscientiousness = 1.0
        feature_object = Feature(value=conscientiousness, inherited_from=takes_after)
        return feature_object

    def _init_extroversion(self):
        """Initialize a value for the Big Five personality trait 'extroversion'."""
        config = self.subject.game.config
        if random.random() < config.big_5_e_heritability:
            takes_after = random.choice([self.subject.father, self.subject.mother])
            extroversion = random.normalvariate(
                takes_after.extroversion, config.big_5_heritability_sd
            )
        else:
            takes_after = None
            extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion < config.big_5_floor:
            extroversion = -1.0
        elif extroversion > config.big_5_cap:
            extroversion = 1.0
        feature_object = Feature(value=extroversion, inherited_from=takes_after)
        return feature_object

    def _init_agreeableness(self):
        """Initialize a value for the Big Five personality trait 'agreeableness'."""
        config = self.subject.game.config
        if random.random() < config.big_5_a_heritability:
            takes_after = random.choice([self.subject.father, self.subject.mother])
            agreeableness = random.normalvariate(
                takes_after.agreeableness, config.big_5_heritability_sd
            )
        else:
            takes_after = None
            agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness < config.big_5_floor:
            agreeableness = -1.0
        elif agreeableness > config.big_5_cap:
            agreeableness = 1.0
        feature_object = Feature(value=agreeableness, inherited_from=takes_after)
        return feature_object

    def _init_neuroticism(self):
        """Initialize a value for the Big Five personality trait 'neuroticism'."""
        config = self.subject.game.config
        if random.random() < config.big_5_n_heritability:
            takes_after = random.choice([self.subject.father, self.subject.mother])
            neuroticism = random.normalvariate(
                takes_after.neuroticism, config.big_5_heritability_sd
            )
        else:
            takes_after = None
            neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism < config.big_5_floor:
            neuroticism = -1.0
        elif neuroticism > config.big_5_cap:
            neuroticism = 1.0
        feature_object = Feature(value=neuroticism, inherited_from=takes_after)
        return feature_object

    def _init_ex_nihilo_openness_to_experience(self):
        """Initialize a value for the Big Five personality trait 'openness to experience'."""
        config = self.subject.game.config
        openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience < config.big_5_floor:
            openness_to_experience = -1.0
        elif openness_to_experience > config.big_5_cap:
            openness_to_experience = 1.0
        feature_object = Feature(value=openness_to_experience, inherited_from=None)
        return feature_object

    def _init_ex_nihilo_conscientiousness(self):
        """Initialize a value for the Big Five personality trait 'conscientiousness'."""
        config = self.subject.game.config
        conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness < config.big_5_floor:
            conscientiousness = -1.0
        elif conscientiousness > config.big_5_cap:
            conscientiousness = 1.0
        feature_object = Feature(value=conscientiousness, inherited_from=None)
        return feature_object

    def _init_ex_nihilo_extroversion(self):
        """Initialize a value for the Big Five personality trait 'extroversion'."""
        config = self.subject.game.config
        extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion < config.big_5_floor:
            extroversion = -1.0
        elif extroversion > config.big_5_cap:
            extroversion = 1.0
        feature_object = Feature(value=extroversion, inherited_from=None)
        return feature_object

    def _init_ex_nihilo_agreeableness(self):
        """Initialize a value for the Big Five personality trait 'agreeableness'."""
        config = self.subject.game.config
        agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness < config.big_5_floor:
            agreeableness = -1.0
        elif agreeableness > config.big_5_cap:
            agreeableness = 1.0
        feature_object = Feature(value=agreeableness, inherited_from=None)
        return feature_object

    def _init_ex_nihilo_neuroticism(self):
        """Initialize a value for the Big Five personality trait 'neuroticism'."""
        config = self.subject.game.config
        neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism < config.big_5_floor:
            neuroticism = -1.0
        elif neuroticism > config.big_5_cap:
            neuroticism = 1.0
        feature_object = Feature(value=neuroticism, inherited_from=None)
        return feature_object


class Feature(float):
    """A particular personality feature, i.e., a value for a particular personality attribute."""

    def __init__(self, value, inherited_from):
        """Initialize a Feature object.

        @param value: A float representing the value, on a scale from -1 to 1, for this
                      particular personality feature.
        @param inherited_from: The parent from whom this personality feature was
                               inherited, if any.
        """
        super(Feature, self).__init__()
        self.inherited_from = inherited_from

    def __new__(cls, value, inherited_from):
        return float.__new__(cls, value)