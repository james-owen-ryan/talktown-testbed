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
        self.thoughts = []
        self.salient_action_selector = None
        self.receptors = {}  # Dictionary mapping signal names to corresponding signal receptors
        self.synapses = {}

    def __str__(self):
        """Return string representation."""
        return "Mind of {person}".format(person=self.person.name)

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

    def associate(self, artifact):
        """Associate the signals emitting from an artifact with salient notions in this mind to
        produce a set of stimuli, which may elicit a thought.

        @param artifact: The artifact that this person has encountered.
        """
        stimuli = {}
        # Start with the artifact signals
        for signal, strength in artifact.signals:
            if signal not in stimuli:
                stimuli[signal] = 0
            stimuli[signal] += strength
        # Boost the signals according to any corresponding signal receptors that
        # this person may have
        for signal, _ in artifact.signals:
            if signal in self.receptors:
                stimuli[signal] += self.receptors[signal].voltage
                # Generate an action potential, which will propagate activity across this
                # receptors synapses to potentially bring in more stimuli
                for activated_signal, activated_signal_voltage in self.receptors[signal].activate():
                    if activated_signal not in stimuli:
                        stimuli[activated_signal] = 0
                    stimuli[activated_signal] += activated_signal_voltage
        return stimuli

    def elicit_thought(self, stimuli):
        """Elicit a thought from a set of stimuli"""
        # Request a thought from Productionist by association with the stimuli
        elicited_thought = (
            self.person.game.thought_productionist.target_association(thinker=self.person, stimuli=stimuli)
        )
        return elicited_thought

    # def wander(self):
    #     """Let this mind wander."""
    #     a_thought = Thoughts.a_thought(mind=self)
    #     if a_thought:
    #         self.think(a_thought)

    def think(self, thought):
        """Think a thought."""
        self.thoughts.append(thought)
        thought.realize()
        thought.execute()

    def update_receptor_voltages_and_synapse_weights(self, voltage_updates):
        """Update the voltages of this person's signal receptors."""
        # Add receptors for all the new signals that have elicited a thought in
        # this mind for the first time
        for signal in voltage_updates:
            if signal not in self.receptors:
                self.receptors[signal] = Receptor(mind=self, signal=signal)
        # Now, update receptor voltages and instantiate new synapses (or strengthen
        # existing ones)
        for signal, voltage_update in voltage_updates.iteritems():
            # Update voltages
            self.receptors[signal].voltage += voltage_update
            # Instantiate/strengthen synapses (i.e., increase their weights) for all pairs of signals
            for other_signal in voltage_updates:
                if other_signal != signal:
                    # If no such synapse yet exists, instantiate one
                    if tuple(sorted([signal, other_signal])) not in self.synapses:
                        receptors = (self.receptors[signal], self.receptors[other_signal])
                        Synapse(receptors=receptors)
                    self.receptors[signal].synapses[self.receptors[other_signal]].strengthen()


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


class Receptor(object):
    """A signal receptor in the mind of a person.

    Signal receptors correspond to individual environmental signals (e.g.,
    'work' or 'birth' or a particular person or bar in the world) and have
    a voltage. Higher receptor voltages make their associated signals more
    salient to an individual, which makes the person more likely to have
    thoughts that are elicited by the signal.

    Receptors connect to one another via synapses, which are pathways that
    connect receptors and facilitate activity propagation across them. When
    a person has a thought that is associated with multiple signals, synapses
    connecting the corresponding receptors are constructed pairwise. The more
    often signal receptors are activated simultaneously (by a thought associated
    with both signals being thunk), the stronger the weight of the synapse
    becomes.

    When a signal in the world activates its receptor in the mind of a person,
    an action potential will be generated in that receptor, which will propagate
    across its synapses to in turn activate connected receptors. This makes
    signals become associated in the mind of characters to the degree that
    they have co-occurred in their cumulative subjective experience of the
    world. (This is a loose operationalization of long-term potentiation.)
    """

    def __init__(self, mind, signal):
        """Initialize a Receptor object."""
        self.mind = mind
        self.signal = signal  # ID of the signal (e.g., 'job' or a character object's ID in memory)
        self.voltage = 0
        self.synapses = {}

    def __str__(self):
        """Return string representation."""
        return "A receptor for '{signal_name}' signals in the mind of {owner}".format(
            signal_name=self.signal,
            owner=self.mind.person.name
        )

    def activate(self):
        """Activate this signal receptor to generate an action potential that will propagate across its synapses.

        Specifically, this method returns a set of receptors activated by the action potential, along
        with the associated synapse weights.
        """
        activations = set()
        for synapse in self.synapses.values():
            other_receptor = synapse.other_receptor(receptor=self)
            activated_signal = other_receptor.signal
            activated_signal_weight = synapse.config.action_potential_signal_weight_multiplier * synapse.weight
            activations.add((activated_signal, activated_signal_weight))
        return activations


class Synapse(object):
    """A synapse in the mind of a person that connects two signal receptors and has a weight."""

    def __init__(self, receptors):
        """Initialize a Synapse object."""
        # We'll need to make a lot of calls to config -- amortize this by setting it
        # as an attribute on this class
        self.config = list(receptors)[0].mind.person.game.config
        self.receptors = receptors
        self.weight = self.config.signal_receptor_synapse_starting_weight
        # Update the .synapses attribute of the receptors
        receptor, other_receptor = receptors
        receptor.synapses[other_receptor] = self
        other_receptor.synapses[receptor] = self
        # Update the .synapses attribute of the mind
        mind_synapses_key = tuple(sorted([receptors[0].signal, receptors[1].signal]))
        self.receptors[0].mind.synapses[mind_synapses_key] = self

    def __str__(self):
        """Return string representation."""
        return "A synapse between receptors for '{receptor1}' and '{receptor2}' signals in the mind of {owner}".format(
            receptor1=self.receptors[0].signal,
            receptor2=self.receptors[1].signal,
            owner=self.receptors[0].mind.person.name
        )

    def other_receptor(self, receptor):
        """Return the receptor incident on this synpase that is not the given receptor."""
        return self.receptors[0] if self.receptors[0] is not receptor else self.receptors[1]

    def strengthen(self):
        """Strengthen this synapse."""
        self.weight += self.config.signal_receptor_synapse_weight_increase_increment

