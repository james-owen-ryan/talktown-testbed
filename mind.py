import random


class Mind(object):
    """A person's mind."""

    def __init__(self, person):
        """Initialize a Mind object."""
        self.person = person
        if self.person.mother:  # Person object
            self.memory = self._init_memory()
        else:  # PersonExNihilo object
            self.memory = self._init_ex_nihilo_memory()
        self.mental_models = {}
        # A mind's preoccupation is an entity that this person is currently preoccupied
        # by, e.g., someone for whom this person is trying to fill in missing belief facets
        self.preoccupation = None

    def __str__(self):
        """Return string representation."""
        return "Mind of {}".format(self.person.name)

    def _init_memory(self):
        """Determine a person's base memory capability, given their parents'."""
        config = self.person.game.config
        if random.random() < config.memory_heritability:
            takes_after = random.choice([self.person.mother, self.person.father])
            memory = random.normalvariate(takes_after.mind.memory, config.memory_heritability_sd)
        else:
            takes_after = None
            memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if self.person.male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor_at_birth:
            memory = config.memory_floor_at_birth
        feature_object = Feature(value=memory, inherited_from=takes_after)
        return feature_object

    def _init_ex_nihilo_memory(self):
        """Determine this person's base memory capability."""
        config = self.person.game.config
        memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if self.person.male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor:
            memory = config.memory_floor
        feature_object = Feature(value=memory, inherited_from=None)
        return feature_object

    def closest_match(self, features, entity_type='person'):
        """Match a set of features describing an entity against this person's mental models to return
        a closest match.
        """
        # TODO check for partial matches, express multiple matches (if there are multiple)
        assert features, "A person's mind.closest_match() method was called with no indexing features."
        # Build a lambda function that will match mental models against the given features
        matches_description = lambda mental_model: all(
            str(mental_model.get_facet_to_this_belief_of_type(feature[0])) == feature[1]
            for feature in features if feature
        )
        # Collect all matches
        all_matches = [
            p for p in self.mental_models if p.type == entity_type and matches_description(self.mental_models[p])
        ]
        if not all_matches:
            return None
        # Return the most salient match (meaning most salient to this person)
        most_salient_match = max(all_matches, key=lambda match: self.person.salience_of_other_people.get(match, 0.0))
        return most_salient_match


class Feature(float):
    """A feature representing a person's memory capability and metadata about that."""

    def __init__(self, value, inherited_from):
        """Initialize a Feature object.

        @param value: A float representing the value, on a scale from -1 to 1, of a
                      person's memory capability.
        @param inherited_from: The parent from whom this memory capability was
                               inherited, if any.
        """
        super(Feature, self).__init__()
        self.inherited_from = inherited_from

    def __new__(cls, value, inherited_from):
        """Do float stuff."""
        return float.__new__(cls, value)