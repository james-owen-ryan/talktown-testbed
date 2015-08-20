import random
from evidence import *
from corpora import Names


# TODO StreetMentalModel, BlockMentalModel, CityMentalModel?


class MentalModel(object):
    """A person's mental model of a person or place."""

    def __init__(self, owner, subject):
        """Initialize a MentalModel object."""
        self.owner = owner
        self.subject = subject
        self.owner.mind.mental_models[self.subject] = self
        # This dictionary maps feature types (i.e., 'first name', 'hair color') to their
        # trajectories, meaning a list of the belief facets they've held for that attribute of the
        # subject in the order that they were held; facets may appear multiple times in the case
        # that they were overtaken and then subsequently were reinstated; this attribute gets
        # modified every time a new Facet object initializes or takes over
        self.belief_trajectories = {}

    def __str__(self):
        """Return string representation."""
        return "{0}'s mental model of {1}".format(self.owner.name, self.subject.name)

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for and boosting the
        strength of already correct facets.
        """
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature not in ("subject", "owner", "belief_trajectories"):
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is None or not current_belief_facet.accurate:
                    feature_type = self.attribute_to_belief_type(attribute=feature)
                    # Adopt a new, accurate belief facet (unless init_belief_facet returns None) --
                    # if a Facet object is instantiated, it will automatically be adopted because
                    # it's initial evidence will be a reflection or observation; specifically,
                    # Facet.init() will call attribute_new_evidence() which will call adopt_belief()
                    self.init_belief_facet(
                        feature_type=feature_type,
                        observation_or_reflection=new_observation_or_reflection
                    )
                else:
                    # Belief facet is already accurate, but update its evidence to point to the new
                    # observation or reflection (which will slow any potential deterioration) -- this
                    # will also increment the strength of the belief facet, which will make it less
                    # likely to deteriorate in the future
                    current_belief_facet.attribute_new_evidence(new_evidence=new_observation_or_reflection)

    def consider_new_evidence(self, feature_type, feature_value, feature_object_itself, new_evidence):
        """Consider new evidence that someone has given you.

        If this new evidence is in regards to a feature type for which this person has
        no existing belief, they will form a new belief and use this as its initial
        evidence. If it is contrary to a belief this person already has, the
        reasoning here will cause this person to either change their belief according
        to this new evidence or to attribute the new evidence to a challenger belief
        (a belief that contradicts their currently held belief, but for which they still
        keep track of and attribute evidence to). If the new evidence supports an existing
        belief (challenger), they will add this new evidence to their evidence for that
        belief (which will strengthen it).

        @param feature_type: A string for the type of feature to which this new evidence
                             pertains.
        @param feature_value: A string representing the value of this feature that the
                              new evidence supports.
        @param feature_object_itself: The feature object itself for knowledge that has that,
                                      e.g., a belief of what dwelling place a person lives in.
        @param new_evidence: A Statement or Lie object that reifies this new evidence.
        """
        command_to_access_my_current_belief = self.get_command_to_access_a_belief_facet(
            feature_type=feature_type
        )
        current_belief_facet = eval(command_to_access_my_current_belief)
        if current_belief_facet == feature_value:
            # This new evidence supports an existing belief, so attribute it accordingly
            current_belief_facet.attribute_new_evidence(new_evidence=new_evidence)
        elif current_belief_facet is None or current_belief_facet == '':
            # You don't have an existing belief, so instantiate a new belief facet
            # with this new evidence as its initial evidence -- this Facet will automatically
            # be adopted because it is this character's first belief about this attribute;
            # specifically, this will happen by a series of method calls starting with
            # Facet.init()
            Facet(
                value=feature_value, owner=self.owner, subject=self.subject, feature_type=feature_type,
                initial_evidence=new_evidence, object_itself=feature_object_itself
            )
        else:
            # This new evidence contradicts an existing belief, consider it accordingly
            self._consider_contradictory_evidence(
                feature_type=feature_type, feature_value=feature_value,
                feature_object_itself=feature_object_itself, new_evidence=new_evidence
            )

    def _consider_contradictory_evidence(self, feature_type, feature_value, feature_object_itself, new_evidence):
        """Consider new evidence that contradicts the currently held belief facet."""
        # Access the currently held belief facet
        command_to_access_my_current_belief = self.get_command_to_access_a_belief_facet(
            feature_type=feature_type
        )
        current_belief_facet = eval(command_to_access_my_current_belief)
        # Check if this evidence supports any challenger to the currently held belief facet
        if any(challenger for challenger in current_belief_facet.challengers if challenger == feature_value):
            # It does, so attribute this new evidence, which may cause this challenger to overtake
            # the current belief (this will be determined by challenger.attribute_new_evidence())
            challenger_this_evidence_supports = next(
                challenger for challenger in current_belief_facet.challengers if challenger == feature_value
            )
            challenger_this_evidence_supports.attribute_new_evidence(new_evidence=new_evidence)
        else:
            # There is no challenger belief for this feature_value, so instantiate one (again, this
            # may cause this new belief facet to overtake the current one)
            Facet(
                value=feature_value, owner=self.owner, subject=self.subject,
                feature_type=feature_type, initial_evidence=new_evidence,
                object_itself=feature_object_itself
            )

    def adopt_belief(self, new_belief_facet, old_belief_facet=None):
        """Adopt a new belief facet; if an old facet is being overtaken, update it accordingly."""
        command_to_access_my_current_belief = self.get_command_to_access_a_belief_facet(
            feature_type=new_belief_facet.feature_type
        )
        command_to_instantiate_new_belief_facet = command_to_access_my_current_belief + ' = new_belief_facet'
        exec command_to_instantiate_new_belief_facet
        # Update your belief trajectory
        self._update_belief_trajectory(new_belief_facet=new_belief_facet)
        # Attribute a predecessor (or lack thereof) to the new belief facet
        new_belief_facet.predecessor = old_belief_facet
        # Update the challenger status of the facet(s)
        new_belief_facet.challenger = False
        if old_belief_facet is not None:  # Could be '', in the case of a forgetting
            old_belief_facet.challenger = True
        # Have the new facet inherit any challengers of the old facet (excluding itself)
        if old_belief_facet is not None:
            new_belief_facet.challengers = set(old_belief_facet.challengers) - {new_belief_facet} | {old_belief_facet}
            # Remove any challengers that are evidenced by a forgetting (I think this could
            # only possibly be old_belief_facet), since we don't want future forgettings just
            # being new evidence for these, since that doesn't make sense
            if old_belief_facet == '':
                new_belief_facet.challengers.remove(old_belief_facet)
        else:
            new_belief_facet.challengers = set()
        # Remove all challengers to the old facet (if it's reinstated, it will inherit in this same way)
        if old_belief_facet is not None:
            old_belief_facet.challengers = set()

    def _update_belief_trajectory(self, new_belief_facet):
        """Update the belief trajectory for feature_type by appending new_belief_facet to it."""
        feature_type = new_belief_facet.feature_type
        if feature_type not in self.belief_trajectories:
            self.belief_trajectories[feature_type] = [new_belief_facet]
        else:
            self.belief_trajectories[feature_type].append(new_belief_facet)

    def init_belief_facet(self, feature_type, observation_or_reflection):
        """Determine a belief facet pertaining to a feature of the given type."""
        if not observation_or_reflection:
            # This is in service to preparation of a mental model composed (initially) of
            # blank belief attributes -- then these can be filled in manually according
            # to what a person tells another person, etc.
            return None
        else:
            # Generate a true facet
            true_feature_str = self._get_true_feature(feature_type=feature_type)
            true_object_itself = self._get_true_feature_object(feature_type=feature_type)
            belief_facet_obj = Facet(
                value=true_feature_str, owner=self.owner, subject=self.subject,
                feature_type=feature_type, initial_evidence=observation_or_reflection,
                object_itself=true_object_itself
            )
            return belief_facet_obj

    def deteriorate_belief_facet(self, feature_type, current_belief_facet):
        """Deteriorate a belief facet, either by mutation, transference, or forgetting."""
        config = self.owner.game.config
        if current_belief_facet != '' and current_belief_facet is not None:
            result = self._decide_how_knowledge_will_pollute_or_be_forgotten(config=config)
            entity_to_transfer_belief_facet_from = (
                self._decide_entity_to_transfer_belief_facet_from(feature_type=feature_type)
            )
            if result == 't' and entity_to_transfer_belief_facet_from:  # Transference
                belief_facet_obj = self._transfer_belief_facet(
                    feature_type=feature_type,
                    entity_being_transferred_from=entity_to_transfer_belief_facet_from
                )
            elif result == 'm':  # Mutation
                belief_facet_obj = self._mutate_belief_facet(
                    feature_type=feature_type, facet_being_mutated=current_belief_facet
                )
            else:  # Forgetting
                belief_facet_obj = self._forget_belief_facet(
                    feature_type=feature_type
                )
        else:  # Confabulation
            belief_facet_obj = self._confabulate_belief_facet(
                feature_type=feature_type, current_belief_facet=current_belief_facet
            )
        return belief_facet_obj

    def _confabulate_belief_facet(self, feature_type, current_belief_facet):
        """This method gets overridden by the subclasses to this base class."""
        pass

    def _mutate_belief_facet(self, feature_type, facet_being_mutated):
        """This method gets overridden by the subclasses to this base class."""
        pass

    def _transfer_belief_facet(self, feature_type, entity_being_transferred_from):
        """Cause a belief facet to change by transference."""
        transferred_belief_facet = (
            self.owner.mind.mental_models[entity_being_transferred_from].get_facet_to_this_belief_of_type(
                feature_type=feature_type
            )
        )
        feature_str = str(transferred_belief_facet)
        transferred_object_itself = transferred_belief_facet.object_itself
        transference = Transference(
            subject=self.subject, source=self.owner, belief_facet_transferred_from=transferred_belief_facet
        )
        belief_facet_obj = Facet(
            value=feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=transference,
            object_itself=transferred_object_itself
        )
        return belief_facet_obj

    def _decide_entity_to_transfer_belief_facet_from(self, feature_type):
        """This method gets overridden by the subclasses to this base class."""
        pass

    def _forget_belief_facet(self, feature_type):
        """Cause a belief facet to be forgotten."""
        forgetting = Forgetting(subject=self.subject, source=self.owner)
        # Facets evidenced by a Forgetting should always have an empty string
        # for their value
        belief_facet_obj = Facet(
            value='', owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=forgetting,
            object_itself=None
        )
        return belief_facet_obj

    def _get_true_feature(self, feature_type):
        true_feature_str = str(self.subject.get_feature(feature_type=feature_type))
        return true_feature_str

    def _get_true_feature_object(self, feature_type):
        """This method gets overridden by the subclasses to this base class."""
        pass

    @staticmethod
    def _decide_how_knowledge_will_pollute_or_be_forgotten(config):
        """Decide whether knowledge will succumb to degradation or transference or forgetting."""
        x = random.random()
        pollution_type_probabilities = config.memory_pollution_probabilities
        result = next(  # See config.py to understand what this is doing
            pollution_type[1] for pollution_type in pollution_type_probabilities if
            pollution_type[0][0] <= x <= pollution_type[0][1]
        )
        return result

    def _calculate_chance_feature_gets_remembered_perfectly(self, feature_type):
        """Calculate the chance that owner perfectly remembers a feature about subject."""
        config = self.owner.game.config
        salience_of_the_feature = config.person_feature_salience[feature_type][0]
        chance_it_gets_remembered_perfectly = self.owner.mind.memory * salience_of_the_feature
        chance_floor = config.person_feature_salience[feature_type][1]
        if chance_it_gets_remembered_perfectly < chance_floor:
            chance_it_gets_remembered_perfectly = chance_floor
        chance_cap = config.person_feature_salience[feature_type][2]
        if chance_it_gets_remembered_perfectly > chance_cap:
            chance_it_gets_remembered_perfectly = chance_cap
        return chance_it_gets_remembered_perfectly

    @staticmethod
    def get_command_to_access_a_belief_facet(feature_type):
        """This method gets overridden by the subclasses to this base class."""
        return ''


class BusinessMentalModel(MentalModel):
    """A person's mental model of a business."""

    def __init__(self, owner, subject, observation):
        """Initialize a BusinessMentalModel object.
        @param owner: The person who holds this belief.
        @param subject: The building to whom this belief pertains.
        """
        super(BusinessMentalModel, self).__init__(owner, subject)
        self.block = self._init_business_facet(
            feature_type="business block", observation_or_reflection=observation
        )
        self.address = self._init_business_facet(
            feature_type="business address", observation_or_reflection=observation
        )

    @property
    def employees(self):
        """Return all the people that owner believes works here."""
        believed_employees = [
            p for p in self.owner.mind.mental_models if p.type == "person" and
            self.owner.mind.mental_models[p].occupation.company.object_itself is self.subject
        ]
        return believed_employees

    def people_here_when(self, date):
        """Return all the people that owner believes were here at a given date."""
        believed_here_on_this_date = [
            p for p in self.owner.mind.mental_models if p.type == "person" and
            date in self.owner.mind.mental_models[p].whereabouts.date and
            self.owner.mind.mental_models[p].whereabouts.date[date].object_itself is self.subject
        ]
        return believed_here_on_this_date

    def _init_business_facet(self, feature_type, observation_or_reflection):
        """Establish a belief, or lack of belief, pertaining to a business."""
        # If you are physically at this business observing it, build up a belief
        # about it that will be evidenced by an Observation object
        if self.owner.location is self.subject:
            business_facet = self.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty facet -- having None for observation_or_reflection will automate this
            business_facet = self.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return business_facet

    def deteriorate(self):
        """Deteriorate the components of this belief (potentially) by mutation, transference, and/or forgetting."""
        config = self.owner.game.config
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature not in ("owner", "subject", "employees", "belief_trajectories"):
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is not None:
                    feature_type_str = current_belief_facet.feature_type
                    belief_facet_strength = current_belief_facet.strength
                    # Determine the chance of memory deterioration, which starts from a base value
                    # that gets affected by the person's memory and the strength of the belief facet
                    chance_of_memory_deterioration = (
                        config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                        self.owner.mind.memory /
                        belief_facet_strength
                    )
                else:  # Could still confabulate
                    feature_type_str = self.attribute_to_belief_type(attribute=feature)
                    chance_of_memory_deterioration = config.chance_of_confabulation_on_a_given_timestep
                if random.random() < chance_of_memory_deterioration:
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already) --
                    # when the facet object's init() method is called, it will call
                    # attribute_new_evidence(), which will automatically call adopt_belief()
                    # because its initial evidence will be of a deterioration type
                    self.deteriorate_belief_facet(
                        feature_type=feature_type_str, current_belief_facet=current_belief_facet
                    )

    def _confabulate_belief_facet(self, feature_type, current_belief_facet):
        """Confabulate a facet to a belief about a dwelling place."""
        config = self.owner.game.config
        confabulation = Confabulation(subject=self.subject, source=self.owner)
        if feature_type == "business block":
            random_block = random.choice(list(self.owner.city.blocks))
            confabulated_feature_str = str(random_block)
            confabulated_object_itself = None
        else:  # business address
            house_number = int(random.random() * config.largest_possible_house_number) + 1
            while house_number < config.smallest_possible_house_number:
                house_number += int(random.random() * 500)
            house_number = min(house_number, config.largest_possible_house_number)
            random_street = random.choice(list(self.owner.city.streets))
            confabulated_feature_str = "{0} {1}".format(house_number, random_street)
            confabulated_object_itself = None
        belief_facet_object = Facet(
            value=confabulated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=confabulation,
            object_itself=confabulated_object_itself
        )
        return belief_facet_object

    def _mutate_belief_facet(self, feature_type, facet_being_mutated):
        """Mutate a facet to a belief about a dwelling place."""
        if feature_type == "business block":
            mutated_feature_str, mutated_object_itself = (
                self._mutate_business_block_facet(facet_being_mutated=facet_being_mutated)
            )
        else:  # business address
            mutated_feature_str, mutated_object_itself = (
                self._mutate_business_address_facet(facet_being_mutated=facet_being_mutated)
            )
            # Make sure the address actually got mutated
            while mutated_feature_str == str(facet_being_mutated):
                mutated_feature_str, mutated_object_itself = (
                    self._mutate_business_address_facet(facet_being_mutated=facet_being_mutated)
                )
        mutation = Mutation(subject=self.subject, source=self.owner, mutated_belief_str=str(facet_being_mutated))
        belief_facet_obj = Facet(
            value=mutated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=mutation,
            object_itself=mutated_object_itself
        )
        return belief_facet_obj

    def _mutate_business_block_facet(self, facet_being_mutated):
        """Mutate a belief facet pertaining to a person's home block."""
        # Add 100-300 to block number
        block_number_first_digit = int(str(facet_being_mutated)[0])
        if random.random() < 0.5:
            change_to_block_number = random.randint(1, 3)
        else:
            change_to_block_number = random.randint(-3, -1)
        block_number_first_digit += change_to_block_number
        if block_number_first_digit < 1:
            block_number_first_digit = 1
        elif block_number_first_digit > 8:
            block_number_first_digit = 8
        if random.random() < 0.5:
            # Also mutate street to a nearby street
            street_of_current_facet = next(
                s for s in self.owner.city.streets if s.name == str(facet_being_mutated).split(' of ')[1]
            )
            street_being_mutated_to = next(
                s for s in self.owner.city.streets if s.direction == street_of_current_facet.direction and
                abs(s.number - street_of_current_facet.number) < 3
            )
            mutated_feature_str = str(block_number_first_digit) + '00' + ' of ' + street_being_mutated_to.name
        else:
            mutated_feature_str = str(block_number_first_digit) + str(facet_being_mutated)[1:]
        mutated_object_itself = None
        return mutated_feature_str, mutated_object_itself

    def _mutate_business_address_facet(self, facet_being_mutated):
        """Mutate a belief facet pertaining to a person's home address."""
        config = self.owner.game.config
        # Change the house number
        digits_of_house_number = list(str(facet_being_mutated)[:3])
        for i in xrange(3):
            if random.random() < 0.3:
                if random.random() < 0.5:
                    change_to_digit = 1
                else:
                    change_to_digit = -1
                mutated_digit = int(digits_of_house_number[i]) + change_to_digit
                if mutated_digit < 0:
                    mutated_digit = 0
                elif mutated_digit > 9:
                    mutated_digit = 9
                digits_of_house_number[i] = str(mutated_digit)
        mutated_house_number = ''.join(digits_of_house_number)
        # Make sure mutated house number is valid
        mutated_house_number = int(mutated_house_number)
        while mutated_house_number < config.smallest_possible_house_number:
            mutated_house_number += 100
        while mutated_house_number > config.largest_possible_house_number:
            mutated_house_number -= 100
        mutated_house_number = str(mutated_house_number)
        if random.random() < 0.1:
            # Also mutate street to a nearby street
            street_of_current_facet = next(
                # Get out just the street name (strip away house number and apartment unit number, if any)
                s for s in self.owner.city.streets if s.name == str(facet_being_mutated)[4:].split(' (')[0]
            )
            street_being_mutated_to = next(
                s for s in self.owner.city.streets if s.direction == street_of_current_facet.direction and
                abs(s.number - street_of_current_facet.number) < 3
            )
            mutated_feature_str = "{0} {1}".format(mutated_house_number, street_being_mutated_to.name)
        else:
            mutated_feature_str = str(mutated_house_number) + str(facet_being_mutated)[3:]
        mutated_object_itself = None
        return mutated_feature_str, mutated_object_itself

    def _decide_entity_to_transfer_belief_facet_from(self, feature_type):
        """Decide a person to transfer a belief facet from."""
        # TODO make transference of a name feature be more likely for familiar names
        # TODO notion of person similarity should be at play here
        # Find an entity to transfer from that is a dwelling place, is not the subject,
        # is something for which this person actually has a belief facet of the given type,
        # and ideally that is the same type of dwelling place (house or apartment unit)
        # as the subject
        other_business_mental_models = [
            biz for biz in self.owner.mind.mental_models if
            biz.type == "business" and biz is not self.subject and
            self.owner.mind.mental_models[biz].get_facet_to_this_belief_of_type(feature_type=feature_type)
        ]
        if other_business_mental_models:
            # Try to find a business of the same type to transfer from
            if any(biz for biz in other_business_mental_models if biz.__class__ is self.subject.__class__):
                business_belief_will_transfer_from = next(
                    biz for biz in other_business_mental_models if biz.__class__ is self.subject.__class__
                )
            else:
                business_belief_will_transfer_from = random.choice(other_business_mental_models)
        else:
            business_belief_will_transfer_from = None
        return business_belief_will_transfer_from

    def _get_true_feature_object(self, feature_type):
        true_feature_objects = {}  # None are needed currently for DwellingPlaceMentalModel attributes
        if feature_type in true_feature_objects:
            return true_feature_objects[feature_type]
        else:
            return None

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "block": "business block",
            "address": "business address"
        }
        return attribute_to_belief_type[attribute]

    def get_facet_to_this_belief_of_type(self, feature_type):
        """Return the facet to this mental model of the given type."""
        if feature_type == "business block":
            return self.block
        elif feature_type == "business address":
            return self.address

    @staticmethod
    def get_command_to_access_a_belief_facet(feature_type):
        """Return a command that will allow the belief facet for this feature type to be directly modified."""
        feature_type_to_command = {
            "business block": "self.block",
            "business address": "self.address",
        }
        return feature_type_to_command[feature_type]


class DwellingPlaceModel(MentalModel):
    """A person's mental model of a business."""

    def __init__(self, owner, subject, observation):
        """Initialize a DwellingPlaceMentalModel object.
        @param owner: The person who holds this belief.
        @param subject: The building to whom this belief pertains.
        """
        super(DwellingPlaceModel, self).__init__(owner, subject)
        self.apartment = self._init_dwelling_place_facet(
            feature_type="home is apartment", observation_or_reflection=observation
        )
        self.block = self._init_dwelling_place_facet(
            feature_type="home block", observation_or_reflection=observation
        )
        self.address = self._init_dwelling_place_facet(
            feature_type="home address", observation_or_reflection=observation
        )

    @property
    def residents(self):
        """Return all the people that owner believes lives here."""
        believed_residents = [
            p for p in self.owner.mind.mental_models if p.type == "person" and
            self.owner.mind.mental_models[p].home.object_itself is self.subject
        ]
        return believed_residents

    def people_here_when(self, date):
        """Return all the people that owner believes were here at a given date."""
        believed_here_on_this_date = [
            p for p in self.owner.mind.mental_models if p.type == "person" and
            date in self.owner.mind.mental_models[p].whereabouts.date and
            self.owner.mind.mental_models[p].whereabouts.date[date].object_itself is self.subject
        ]
        return believed_here_on_this_date

    def _init_dwelling_place_facet(self, feature_type, observation_or_reflection):
        """Establish a belief, or lack of belief, pertaining to a dwelling place."""
        # If you are physically at this dwelling place observing it, build up a belief
        # about it that will be evidenced by an Observation object
        if self.owner.location is self.subject:
            home_facet = self.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty facet -- having None for observation_or_reflection will automate this
            home_facet = self.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return home_facet

    def deteriorate(self):
        """Deteriorate the components of this belief (potentially) by mutation, transference, and/or forgetting."""
        config = self.owner.game.config
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature not in ("owner", "subject", "residents", "belief_trajectories"):
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is not None:
                    feature_type_str = current_belief_facet.feature_type
                    belief_facet_strength = current_belief_facet.strength
                else:
                    feature_type_str = self.attribute_to_belief_type(attribute=feature)
                    belief_facet_strength = 1
                # Determine the chance of memory deterioration, which starts from a base value
                # that gets affected by the person's memory and the strength of the belief facet
                chance_of_memory_deterioration = (
                    config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                    self.owner.mind.memory /
                    belief_facet_strength
                )
                if random.random() < chance_of_memory_deterioration:
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already) --
                    # when the facet object's init() method is called, it will call
                    # attribute_new_evidence(), which will automatically call adopt_belief()
                    # because its initial evidence will be of a deterioration type
                    self.deteriorate_belief_facet(
                        feature_type=feature_type_str, current_belief_facet=current_belief_facet
                    )

    def _confabulate_belief_facet(self, feature_type, current_belief_facet):
        """Confabulate a facet to a belief about a dwelling place."""
        config = self.owner.game.config
        confabulation = Confabulation(subject=self.subject, source=self.owner)
        if feature_type == "home is apartment":
            confabulated_feature_str = random.choice(["yes", "no"])
            confabulated_object_itself = None
        elif feature_type == "home block":
            random_block = random.choice(list(self.owner.city.blocks))
            confabulated_feature_str = str(random_block)
            confabulated_object_itself = None
        else:  # home address
            house_number = int(random.random() * config.largest_possible_house_number) + 1
            while house_number < config.smallest_possible_house_number:
                house_number += int(random.random() * 500)
            house_number = min(house_number, config.largest_possible_house_number)
            random_street = random.choice(list(self.owner.city.streets))
            if random.random() > 0.5:
                unit_number = int(random.random() * config.number_of_apartment_units_per_complex)
                confabulated_feature_str = "{0} {1} (Unit #{2})".format(house_number, random_street, unit_number)
            else:
                confabulated_feature_str = "{0} {1}".format(house_number, random_street)
            confabulated_object_itself = None
        belief_facet_object = Facet(
            value=confabulated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=confabulation,
            object_itself=confabulated_object_itself
        )
        return belief_facet_object

    def _mutate_belief_facet(self, feature_type, facet_being_mutated):
        """Mutate a facet to a belief about a dwelling place."""
        if feature_type == "home is apartment":
            mutated_feature_str = "yes" if facet_being_mutated == "no" else "no"
            mutated_object_itself = None
        elif feature_type == "home block":
            mutated_feature_str, mutated_object_itself = (
                self._mutate_home_block_facet(facet_being_mutated=facet_being_mutated)
            )
        else:   # home address
            mutated_feature_str, mutated_object_itself = (
                self._mutate_home_address_facet(facet_being_mutated=facet_being_mutated)
            )
            # Make sure the address actually got mutated
            while mutated_feature_str == str(facet_being_mutated):
                mutated_feature_str, mutated_object_itself = (
                    self._mutate_home_address_facet(facet_being_mutated=facet_being_mutated)
                )
        mutation = Mutation(subject=self.subject, source=self.owner, mutated_belief_str=str(facet_being_mutated))
        belief_facet_obj = Facet(
            value=mutated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=mutation,
            object_itself=mutated_object_itself
        )
        return belief_facet_obj

    def _mutate_home_block_facet(self, facet_being_mutated):
        """Mutate a belief facet pertaining to a person's home block."""
        # Add 100-300 to block number
        block_number_first_digit = int(str(facet_being_mutated)[0])
        if random.random() < 0.5:
            change_to_block_number = random.randint(1, 3)
        else:
            change_to_block_number = random.randint(-3, -1)
        block_number_first_digit += change_to_block_number
        if block_number_first_digit < 1:
            block_number_first_digit = 1
        elif block_number_first_digit > 8:
            block_number_first_digit = 8
        if random.random() < 0.5:
            # Also mutate street to a nearby street
            street_of_current_facet = next(
                s for s in self.owner.city.streets if s.name == str(facet_being_mutated).split(' of ')[1]
            )
            street_being_mutated_to = next(
                s for s in self.owner.city.streets if s.direction == street_of_current_facet.direction and
                abs(s.number - street_of_current_facet.number) < 3
            )
            mutated_feature_str = str(block_number_first_digit) + '00' + ' of ' + street_being_mutated_to.name
        else:
            mutated_feature_str = str(block_number_first_digit) + str(facet_being_mutated)[1:]
        mutated_object_itself = None
        return mutated_feature_str, mutated_object_itself

    def _mutate_home_address_facet(self, facet_being_mutated):
        """Mutate a belief facet pertaining to a person's home address."""
        config = self.owner.game.config
        # Change the house number
        digits_of_house_number = list(str(facet_being_mutated)[:3])
        for i in xrange(3):
            if random.random() < 0.3:
                if random.random() < 0.5:
                    change_to_digit = 1
                else:
                    change_to_digit = -1
                mutated_digit = int(digits_of_house_number[i]) + change_to_digit
                if mutated_digit < 0:
                    mutated_digit = 0
                elif mutated_digit > 9:
                    mutated_digit = 9
                digits_of_house_number[i] = str(mutated_digit)
        mutated_house_number = ''.join(digits_of_house_number)
        # Make sure mutated house number is valid
        mutated_house_number = int(mutated_house_number)
        while mutated_house_number < config.smallest_possible_house_number:
            mutated_house_number += 100
        while mutated_house_number > config.largest_possible_house_number:
            mutated_house_number -= 100
        mutated_house_number = str(mutated_house_number)
        if random.random() < 0.1:
            # Also mutate street to a nearby street
            street_of_current_facet = next(
                # Get out just the street name (strip away house number and apartment unit number, if any)
                s for s in self.owner.city.streets if s.name == str(facet_being_mutated)[4:].split(' (')[0]
            )
            street_being_mutated_to = next(
                s for s in self.owner.city.streets if s.direction == street_of_current_facet.direction and
                abs(s.number - street_of_current_facet.number) < 3
            )
            mutated_feature_str = "{0} {1}".format(mutated_house_number, street_being_mutated_to.name)
        else:
            mutated_feature_str = str(mutated_house_number) + str(facet_being_mutated)[3:]
        mutated_object_itself = None
        return mutated_feature_str, mutated_object_itself

    def _decide_entity_to_transfer_belief_facet_from(self, feature_type):
        """Decide a person to transfer a belief facet from."""
        # TODO make transference of a name feature be more likely for familiar names
        # TODO notion of person similarity should be at play here
        # Find an entity to transfer from that is a dwelling place, is not the subject,
        # is something for which this person actually has a belief facet of the given type,
        # and ideally that is the same type of dwelling place (house or apartment unit)
        # as the subject
        other_dwelling_place_mental_models = [
            res for res in self.owner.mind.mental_models if
            res.type == "residence" and res is not self.subject and
            self.owner.mind.mental_models[res].get_facet_to_this_belief_of_type(feature_type=feature_type)
        ]
        if other_dwelling_place_mental_models:
            if any(res for res in other_dwelling_place_mental_models if res.house == self.subject.house):
                dwelling_place_belief_will_transfer_from = next(
                    res for res in other_dwelling_place_mental_models if res.house == self.subject.house
                )
            else:
                dwelling_place_belief_will_transfer_from = random.choice(other_dwelling_place_mental_models)
        else:
            dwelling_place_belief_will_transfer_from = None
        return dwelling_place_belief_will_transfer_from

    def _get_true_feature_object(self, feature_type):
        true_feature_objects = {}  # None are needed currently for DwellingPlaceMentalModel attributes
        if feature_type in true_feature_objects:
            return true_feature_objects[feature_type]
        else:
            return None

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "apartment": "home is apartment",
            "block": "home block",
            "address": "home address"
        }
        return attribute_to_belief_type[attribute]

    def get_facet_to_this_belief_of_type(self, feature_type):
        """Return the facet to this mental model of the given type."""
        if feature_type == "home is apartment":
            return self.apartment
        elif feature_type == "home block":
            return self.block
        elif feature_type == "home address":
            return self.address

    @staticmethod
    def get_command_to_access_a_belief_facet(feature_type):
        """Return a command that will allow the belief facet for this feature type to be directly modified."""
        feature_type_to_command = {
            "home is apartment": "self.apartment",
            "home block": "self.block",
            "home address": "self.address",
        }
        return feature_type_to_command[feature_type]


class PersonMentalModel(MentalModel):
    """A person's mental model of a person, representing everything she believes about her."""

    def __init__(self, owner, subject, observation_or_reflection):
        """Initialize a PersonMentalModel object.
        @param owner: The person who holds this belief.
        @param subject: The person to whom this belief pertains.
        @param observation_or_reflection: The Observation or Reflection from which this
                                          the beliefs composing this mental model originate.
        """
        super(PersonMentalModel, self).__init__(owner, subject)
        # Prepare the belief hierarchy encapsulated by this object
        self.name = NameBelief(person_model=self)
        self.occupation = WorkBelief(person_model=self)
        self.face = FaceBelief(person_model=self)
        self.whereabouts = WhereaboutsBelief(person_model=self)
        self.home = None  # Currently a straggler because there's only one facet component to it
        # Establish initial belief facets according to an initial observation/reflection
        if observation_or_reflection:
            self.name.establish(observation_or_reflection=observation_or_reflection)
            self.occupation.establish(observation_or_reflection=observation_or_reflection)
            self.face.establish(observation_or_reflection=observation_or_reflection)
            self.whereabouts.establish(observation_or_reflection=observation_or_reflection)
            self.home = self._init_home_facet(observation_or_reflection=observation_or_reflection)

    def _init_home_facet(self, observation_or_reflection):
        """Establish a belief, or lack of belief, pertaining to a person's home."""
        if observation_or_reflection and observation_or_reflection.type == "reflection":
            home_facet = self.init_belief_facet(
                feature_type="home", observation_or_reflection=observation_or_reflection
            )
        # If you are observing the person at their home, build up a belief about that
        elif self.owner.location is self.subject.home:
            home_facet = self.init_belief_facet(
                feature_type="home", observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty facet -- having None for observation_or_reflection will automate this
            home_facet = self.init_belief_facet(
                feature_type="home", observation_or_reflection=None
            )
        return home_facet

    def build_up(self, new_observation_or_reflection):
        """Build up a mental model from a new observation or reflection."""
        self.name.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self.occupation.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self.face.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self.whereabouts.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self._build_up_other_belief_facets(new_observation_or_reflection=new_observation_or_reflection)

    def deteriorate(self):
        """Deteriorate a mental model from time passing."""
        self.name.deteriorate()
        self.occupation.deteriorate()
        self.face.deteriorate()
        # Manually deteriorate the home one (and other stragglers that may be defined later)
        self._deteriorate_other_belief_facets()

    def _build_up_other_belief_facets(self, new_observation_or_reflection):
        """Build up other beliefs facets that are components of this mental model.
        By other facets, I mean ones that don't get built up elsewhere, as, e.g.,
        facets to WorkBeliefs do."""
        for feature in ("home",):
            current_belief_facet = self.__dict__[feature]
            if current_belief_facet is None or not current_belief_facet.accurate:
                feature_type = self.attribute_to_belief_type(attribute=feature)
                # Adopt a new, accurate belief facet (unless init_belief_facet returns None) --
                # if a Facet object is instantiated, it will automatically be adopted because
                # it's initial evidence will be a reflection or observation; specifically,
                # Facet.init() will call attribute_new_evidence() which will call adopt_belief()
                self.init_belief_facet(
                    feature_type=feature_type,
                    observation_or_reflection=new_observation_or_reflection
                )
            else:
                # Belief facet is already accurate, but update its evidence to point to the new
                # observation or reflection (which will slow any potential deterioration) -- this
                # will also increment the strength of the belief facet, which will make it less
                # likely to deteriorate in this future
                current_belief_facet.attribute_new_evidence(new_evidence=new_observation_or_reflection)

    def _deteriorate_other_belief_facets(self):
        """Deteriorate other beliefs facets that are components of this mental model.
        By other facets, I mean ones that don't get deteriorated elsewhere, as, e.g.,
        facets to WorkBeliefs do.
        """
        config = self.owner.game.config
        for feature in ("home",):
            current_belief_facet = self.__dict__[feature]
            if current_belief_facet is not None:
                feature_type_str = current_belief_facet.feature_type
                belief_facet_strength = current_belief_facet.strength
            else:
                feature_type_str = self.attribute_to_belief_type(attribute=feature)
                belief_facet_strength = 1
            # Determine the chance of memory deterioration, which starts from a base value
            # that gets affected by the person's memory and the strength of the belief facet
            chance_of_memory_deterioration = (
                config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                self.owner.mind.memory /
                belief_facet_strength
            )
            if random.random() < chance_of_memory_deterioration:
                # Instantiate a new belief facet that represents a deterioration of
                # the existing one (which itself may be a deterioration already) --
                # when the facet object's init() method is called, it will call
                # attribute_new_evidence(), which will automatically call adopt_belief()
                # because its initial evidence will be of a deterioration type
                self.deteriorate_belief_facet(
                    feature_type=feature_type_str, current_belief_facet=current_belief_facet
                )

    def _confabulate_belief_facet(self, feature_type, current_belief_facet):
        """Confabulate a new belief facet of the given type.
        This is done using the feature distributions that are used to generate the features
        themselves for people that don't have parents.
        """
        config = self.owner.game.config
        confabulation = Confabulation(subject=self.subject, source=self.owner)
        if feature_type in config.name_feature_types:
            confabulated_feature_str = self._confabulate_name_facet(feature_type=feature_type)
            confabulated_object_itself = None
        elif feature_type in config.work_feature_types:
            confabulated_feature_str, confabulated_object_itself = self._confabulate_work_facet(
                feature_type=feature_type
            )
        elif feature_type in config.home_feature_types:
            confabulated_feature_str, confabulated_object_itself = self._confabulate_home_facet(
                feature_type=feature_type
            )
        else:  # Appearance feature
            if self.subject.male:
                distribution = config.facial_feature_distributions_male[feature_type]
            else:
                distribution = config.facial_feature_distributions_female[feature_type]
            x = random.random()
            confabulated_feature_str = next(  # See config.py to understand what this is doing
                feature_type[1] for feature_type in distribution if
                feature_type[0][0] <= x <= feature_type[0][1]
            )
            confabulated_object_itself = None
        belief_facet_object = Facet(
            value=confabulated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=confabulation,
            object_itself=confabulated_object_itself
        )
        return belief_facet_object

    def _confabulate_name_facet(self, feature_type):
        """Confabulate a facet to a belief about a person's name."""
        if feature_type == "last name":
            confabulated_feature_str = Names.any_surname()
        elif self.subject.male:
            # Confabulate a name that is appropriate given the subject's birth year
            confabulated_feature_str = Names.a_masculine_name(year=self.subject.birth_year)
        else:
            confabulated_feature_str = Names.a_feminine_name(year=self.subject.birth_year)
        return confabulated_feature_str

    def _confabulate_work_facet(self, feature_type):
        """Confabulate a facet to a belief about a person's work life."""
        if feature_type == "workplace":
            confabulated_company = random.choice(list(self.subject.city.companies))
            confabulated_feature_str = confabulated_company.name
            confabulated_object_itself = confabulated_company
        elif feature_type == "job shift":
            confabulated_feature_str = random.choice(["day", "day", "night"])
            confabulated_object_itself = None
        else:   # job title
            random_company = random.choice(list(self.owner.city.companies))
            random_job_title = random.choice(list(random_company.employees)).__class__.__name__
            confabulated_feature_str = random_job_title
            confabulated_object_itself = None
        return confabulated_feature_str, confabulated_object_itself

    def _confabulate_home_facet(self, feature_type):
        """Confabulate a facet to a belief about a person's home."""
        config = self.owner.game.config
        confabulated_home = random.choice(list(self.subject.city.dwelling_places))
        confabulated_feature_str = confabulated_home.name
        confabulated_object_itself = confabulated_home
        return confabulated_feature_str, confabulated_object_itself

    def _mutate_belief_facet(self, feature_type, facet_being_mutated):
        """Mutate a belief facet."""
        config = self.subject.game.config
        if feature_type in config.name_feature_types:
            mutated_feature_str = self._mutate_name_belief_facet(
                feature_type=feature_type, feature_being_mutated_from_str=str(facet_being_mutated)
            )
            mutated_object_itself = None
        elif feature_type in config.work_feature_types:
            mutated_feature_str, mutated_object_itself = self._mutate_work_belief_facet(
                feature_type=feature_type, facet_being_mutated=facet_being_mutated
            )
        elif feature_type in config.home_feature_types:
            mutated_feature_str, mutated_object_itself = self._mutate_home_belief_facet(
                feature_type=feature_type, facet_being_mutated=facet_being_mutated
            )
        else:  # Appearance facet
            x = random.random()
            possible_mutations = config.memory_mutations[feature_type][str(facet_being_mutated)]
            mutated_feature_str = next(  # See config.py to understand what this is doing
                mutation[1] for mutation in possible_mutations if
                mutation[0][0] <= x <= mutation[0][1]
            )
            mutated_object_itself = None
        mutation = Mutation(subject=self.subject, source=self.owner, mutated_belief_str=str(facet_being_mutated))
        belief_facet_obj = Facet(
            value=mutated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, initial_evidence=mutation,
            object_itself=mutated_object_itself
        )
        return belief_facet_obj

    def _mutate_name_belief_facet(self, feature_type, feature_being_mutated_from_str):
        """Mutate a belief facet pertaining to a person's name."""
        if feature_type in ("first name", "middle name"):
            # Mutate to a name that sounds like the subject's name (shares the same first
            # letter) and is appropriate given the subject's birth year
            if self.subject.male:
                mutated_feature_str = Names.a_masculine_name_starting_with(
                    letter=feature_being_mutated_from_str[0], year=self.subject.birth_year
                )
            else:
                mutated_feature_str = Names.a_feminine_name_starting_with(
                    letter=feature_being_mutated_from_str[0], year=self.subject.birth_year
                )
        else:
            mutated_feature_str = Names.a_surname_sounding_like(source_name=feature_being_mutated_from_str)
        return mutated_feature_str

    def _mutate_work_belief_facet(self, feature_type, facet_being_mutated):
        """Mutate a belief facet pertaining to a person's work life."""
        if feature_type == "workplace":
            mutated_feature_str, mutated_object_itself = self._mutate_workplace_facet(
                facet_being_mutated=facet_being_mutated
            )
        elif feature_type == "job shift":
            mutated_feature_str = "night" if facet_being_mutated == "day" else "day"
            mutated_object_itself = None
        else:   # job title
            mutated_feature_str, mutated_object_itself = self._mutate_job_title_facet(
                facet_being_mutated=facet_being_mutated
            )
        return mutated_feature_str, mutated_object_itself

    def _mutate_workplace_facet(self, facet_being_mutated):
        """Mutate a belief of the company at which a person works."""
        # Mutate to a different business of that type, if there is one; otherwise,
        # mutate to a random business
        business_type = facet_being_mutated.__class__.__name__
        if any(b for b in self.owner.city.businesses_of_type(business_type=business_type) if
               b is not facet_being_mutated):
            mutated_object_itself = next(
                b for b in self.owner.city.businesses_of_type(business_type=business_type) if
                b is not facet_being_mutated
            )
        else:
            mutated_object_itself = random.choice(list(self.owner.city.companies))
        mutated_feature_str = mutated_object_itself.name
        return mutated_feature_str, mutated_object_itself

    def _mutate_job_title_facet(self, facet_being_mutated):
        """Mutate a belief about a person's job title."""
        # If you have a belief about where this person works, mutate their job title
        # to another job title attested at that business
        if self.subject.occupation and self.subject.occupation.company:
        # if self.owner.mind.mental_models[self.subject].occupation.company:
            # other_job_titles_attested_there = [
            #     e.__class__.__name__ for e in
            #     self.owner.mind.mental_models[self.subject].occupation.company.employees if
            #     e.__class__.__name__ != facet_being_mutated
            # ]
            other_job_titles_attested_there = [
                e.__class__.__name__ for e in
                self.subject.occupation.company.employees if
                e.__class__.__name__ != facet_being_mutated
            ]
            mutated_feature_str = random.choice(other_job_titles_attested_there)
            mutated_object_itself = None
        else:
            # I guess just choose a random job title?
            random_company = random.choice(list(self.owner.city.companies))
            random_job_title = random.choice(list(random_company.employees)).__class__.__name__
            mutated_feature_str = random_job_title
            mutated_object_itself = None
        return mutated_feature_str, mutated_object_itself

    def _mutate_home_belief_facet(self, feature_type, facet_being_mutated):
        """Mutate a belief facet pertaining to a person's home."""
        # TODO make this more realistic, e.g., mutate to a relative's house
        # For now, only thing that makes sense is to just do the same thing as Confabulating a new home
        random_home = random.choice(list(self.subject.city.dwelling_places))
        mutated_feature_str = random_home.name
        mutated_object_itself = random_home
        return mutated_feature_str, mutated_object_itself

    def _decide_entity_to_transfer_belief_facet_from(self, feature_type):
        """Decide a person to transfer a belief facet from."""
        # TODO make transference of a name feature be more likely for familiar names
        # TODO notion of person similarity should be at play here
        # Find an entity to transfer this belief facet from that is a person, is
        # not owner or subject, is someone for whom you even have a belief facet of
        # the given type, and ideally who has the same sex as subject
        other_people_mental_models = [
            person for person in self.owner.mind.mental_models if person.type == "person" and
            person is not self.owner and person is not self.subject and
            self.owner.mind.mental_models[person].get_facet_to_this_belief_of_type(feature_type=feature_type)
        ]
        if other_people_mental_models:
            if any(person for person in other_people_mental_models if person.male == self.subject.male):
                person_belief_will_transfer_from = next(
                    person for person in other_people_mental_models if person.male == self.subject.male
                )
            else:
                person_belief_will_transfer_from = random.choice(other_people_mental_models)
        else:
            person_belief_will_transfer_from = None
        return person_belief_will_transfer_from

    def _get_true_feature_object(self, feature_type):
        if feature_type == "workplace":
            return self.subject.occupation.company if self.subject.occupation else None
        elif feature_type == "home":
            return self.subject.home
        else:
            return None

    def get_facet_to_this_belief_of_type(self, feature_type):
        """Return the facet to this mental model of the given type."""
        # Names
        if feature_type == "first name":
            return self.name.first_name
        elif feature_type == "middle name":
            return self.name.middle_name
        elif feature_type == "last name":
            return self.name.last_name
        # Work life
        elif feature_type == "workplace":
            return self.occupation.company
        elif feature_type == "job title":
            return self.occupation.job_title
        elif feature_type == "job shift":
            return self.occupation.shift
        # Home
        elif feature_type == "home":
            return self.home
        # Appearance
        elif feature_type == "skin color":
            return self.face.skin.color
        elif feature_type == "head size":
            return self.face.head.size
        elif feature_type == "head shape":
            return self.face.head.shape
        elif feature_type == "hair length":
            return self.face.hair.length
        elif feature_type == "hair color":
            return self.face.hair.color
        elif feature_type == "eyebrow size":
            return self.face.eyebrows.size
        elif feature_type == "eyebrow color":
            return self.face.eyebrows.color
        elif feature_type == "mouth size":
            return self.face.mouth.size
        elif feature_type == "ear size":
            return self.face.ears.size
        elif feature_type == "ear angle":
            return self.face.ears.angle
        elif feature_type == "nose size":
            return self.face.nose.size
        elif feature_type == "nose shape":
            return self.face.nose.shape
        elif feature_type == "eye size":
            return self.face.eyes.size
        elif feature_type == "eye shape":
            return self.face.eyes.shape
        elif feature_type == "eye color":
            return self.face.eyes.color
        elif feature_type == "eye horizontal settedness":
            return self.face.eyes.horizontal_settedness
        elif feature_type == "eye vertical settedness":
            return self.face.eyes.vertical_settedness
        elif feature_type == "facial hair style":
            return self.face.facial_hair.style
        elif feature_type == "freckles":
            return self.face.distinctive_features.freckles
        elif feature_type == "birthmark":
            return self.face.distinctive_features.birthmark
        elif feature_type == "scar":
            return self.face.distinctive_features.scar
        elif feature_type == "tattoo":
            return self.face.distinctive_features.tattoo
        elif feature_type == "glasses":
            return self.face.distinctive_features.glasses
        elif feature_type == "sunglasses":
            return self.face.distinctive_features.sunglasses

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "home": "home",
        }
        return attribute_to_belief_type[attribute]

    @staticmethod
    def get_command_to_access_a_belief_facet(feature_type):
        """Return a command that will allow the belief facet for this feature type to be directly modified."""
        feature_type_to_command = {
            # Name
            "first name": "self.name.first_name",
            "middle name": "self.name.middle_name",
            "last name": "self.name.last_name",
            # Occupation
            "workplace": "self.occupation.company",
            "job title": "self.occupation.job_title",
            "job shift": "self.occupation.shift",
            # Home
            "home": "self.home",
            # Appearance
            "skin color": "self.face.skin.color",
            "head size": "self.face.head.size",
            "head shape": "self.face.head.shape",
            "hair length": "self.face.hair.length",
            "hair color": "self.face.hair.color",
            "eyebrow size": "self.face.eyebrows.size",
            "eyebrow color": "self.face.eyebrows.color",
            "mouth size": "self.face.mouth.size",
            "ear size": "self.face.ears.size",
            "ear angle": "self.face.ears.angle",
            "nose size": "self.face.nose.size",
            "nose shape": "self.face.nose.shape",
            "eye size": "self.face.eyes.size",
            "eye shape": "self.face.eyes.shape",
            "eye color": "self.face.eyes.color",
            "eye horizontal settedness": "self.face.eyes.horizontal_settedness",
            "eye vertical settedness": "self.face.eyes.vertical_settedness",
            "facial hair style": "self.face.facial_hair.style",
            "freckles": "self.face.distinctive_features.freckles",
            "birthmark": "self.face.distinctive_features.birthmark",
            "scar": "self.face.distinctive_features.scar",
            "tattoo": "self.face.distinctive_features.tattoo",
            "glasses": "self.face.distinctive_features.glasses",
            "sunglasses": "self.face.distinctive_features.sunglasses",
        }
        # Have to do special thing for whereabouts, because they are indexed by date;
        # specifically, we parse the feature type, which will look something like
        # 'whereabouts 723099-1'
        if 'whereabouts' in feature_type:
            timestep = feature_type[12:]
            ordinal_date, day_or_night_bit = timestep.split('-')
            tuple_string = '({}, {})'.format(ordinal_date, day_or_night_bit)
            return 'self.whereabouts.date[{}]'.format(tuple_string)
        else:
            return feature_type_to_command[feature_type]


class WhereaboutsBelief(object):
    """A person's mental model of another person's past whereabouts."""

    def __init__(self, person_model):
        """Initialize a WhereaboutsBelief object."""
        self.person_model = person_model
        self.date = {}  # Where this person was when

    def establish(self, observation_or_reflection):
        """Establish an initial belief facet in response to an initial observation/reflection."""
        # If there is an observation or reflection taking place, take note of where this
        # person was at this time
        location_str = self.person_model.owner.location.name
        location_obj = self.person_model.owner.location
        day_or_night_id = 0 if self.person_model.owner.game.time_of_day == "day" else 1
        # Generate a unique hash so that we can maintain a trajectory for this belief
        feature_type = "whereabouts {}-{}".format(self.person_model.owner.game.ordinal_date, day_or_night_id)
        self.date[(self.person_model.owner.game.ordinal_date, day_or_night_id)] = Facet(
            value=location_str, owner=self.person_model.owner, subject=self.person_model.subject,
            feature_type=feature_type, initial_evidence=observation_or_reflection,
            object_itself=location_obj
        )

    def build_up(self, new_observation_or_reflection):
        """Build up this belief by adding in a new entry for the current date."""
        location_str = self.person_model.owner.location.name
        location_obj = self.person_model.owner.location
        day_or_night_id = 0 if self.person_model.owner.game.time_of_day == "day" else 1
        # Generate a unique hash so that we can maintain a trajectory for this belief
        feature_type = "whereabouts {}-{}".format(self.person_model.owner.game.ordinal_date, day_or_night_id)
        self.date[(self.person_model.owner.game.ordinal_date, day_or_night_id)] = Facet(
            value=location_str, owner=self.person_model.owner, subject=self.person_model.subject,
            feature_type=feature_type, initial_evidence=new_observation_or_reflection,
            object_itself=location_obj
        )


class NameBelief(object):
    """A person's mental model of a person's name."""

    def __init__(self, person_model):
        """Initialize a NameBelief object."""
        self.person_model = person_model
        self.first_name = None
        self.middle_name = None
        self.last_name = None

    def establish(self, observation_or_reflection):
        """Establish initial belief facets in response to an initial observation/reflection."""
        self.first_name = self._init_name_facet(
            feature_type="first name", observation_or_reflection=observation_or_reflection
        )
        self.middle_name = self._init_name_facet(
            feature_type="middle name", observation_or_reflection=observation_or_reflection
        )
        self.last_name = self._init_name_facet(
            feature_type="last name", observation_or_reflection=observation_or_reflection
        )

    def _init_name_facet(self, feature_type, observation_or_reflection):
        """Establish a belief, or lack of belief, pertaining to a person's name."""
        config = self.person_model.owner.game.config
        if observation_or_reflection and observation_or_reflection.type == "reflection":
            name_facet = self.person_model.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty name facet -- having None for observation_or_reflection will automate this
            name_facet = self.person_model.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return name_facet

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for already correct facets.
        """
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is None or not current_belief_facet.accurate:
                    feature_type = self.attribute_to_belief_type(attribute=feature)
                    # Adopt a new, accurate belief facet (unless init_belief_facet returns None) --
                    # if a Facet object is instantiated, it will automatically be adopted because
                    # it's initial evidence will be a reflection or observation; specifically,
                    # Facet.init() will call attribute_new_evidence() which will call adopt_belief()
                    self.person_model.init_belief_facet(
                        feature_type=feature_type,
                        observation_or_reflection=new_observation_or_reflection
                    )
                else:
                    # Belief facet is already accurate, but update its evidence to point to the new
                    # observation or reflection (which will slow any potential deterioration) -- this
                    # will also increment the strength of the belief facet, which will make it less
                    # likely to deteriorate in this future
                    current_belief_facet.attribute_new_evidence(new_evidence=new_observation_or_reflection)

    def deteriorate(self):
        """Deteriorate the components of this belief (potentially) by mutation, transference, and/or forgetting."""
        config = self.person_model.owner.game.config
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is not None:
                    feature_type_str = current_belief_facet.feature_type
                    belief_facet_strength = current_belief_facet.strength
                else:
                    feature_type_str = self.attribute_to_belief_type(attribute=feature)
                    belief_facet_strength = 1
                # Determine the chance of memory deterioration, which starts from a base value
                # that gets affected by the person's memory and the strength of the belief facet
                chance_of_memory_deterioration = (
                    config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                    self.person_model.owner.mind.memory /
                    belief_facet_strength
                )
                if random.random() < chance_of_memory_deterioration:
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already) --
                    # when the facet object's init() method is called, it will call
                    # attribute_new_evidence(), which will automatically call adopt_belief()
                    # because its initial evidence will be of a deterioration type
                    self.person_model.deteriorate_belief_facet(
                        feature_type=feature_type_str, current_belief_facet=current_belief_facet
                    )

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "first_name": "first name",
            "middle_name": "middle name",
            "last_name": "last name"
        }
        return attribute_to_belief_type[attribute]


class WorkBelief(object):
    """A person's mental model of a person's work life."""

    def __init__(self, person_model):
        """Initialize a WorkBelief object."""
        self.person_model = person_model
        self.company = None
        self.job_title = None
        self.shift = None

    def establish(self, observation_or_reflection):
        """Establish initial belief facets in response to an initial observation/reflection."""
        self.company = self._init_work_facet(  # Will have company object as 'object_itself' attribute on Facet
            feature_type="workplace", observation_or_reflection=observation_or_reflection
        )
        self.job_title = self._init_work_facet(
            feature_type="job title", observation_or_reflection=observation_or_reflection
        )
        self.shift = self._init_work_facet(
            feature_type="job shift", observation_or_reflection=observation_or_reflection
        )

    def _init_work_facet(self, feature_type, observation_or_reflection):
        """Establish a belief, or lack of belief, pertaining to a person's work life."""
        if observation_or_reflection and observation_or_reflection.type == "reflection":
            work_facet = self.person_model.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        # If you are observing the person working right now, build up a belief about that
        elif (self.person_model.subject.occupation and
              self.person_model.owner.location is self.person_model.subject.occupation.company and
              self.person_model.subject.routine.working):
            work_facet = self.person_model.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty work facet -- having None for observation_or_reflection will automate this
            work_facet = self.person_model.init_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return work_facet

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for already correct facets.
        """
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is None or not current_belief_facet.accurate:
                    feature_type = self.attribute_to_belief_type(attribute=feature)
                    # Adopt a new, accurate belief facet (unless init_belief_facet returns None) --
                    # if a Facet object is instantiated, it will automatically be adopted because
                    # it's initial evidence will be a reflection or observation; specifically,
                    # Facet.init() will call attribute_new_evidence() which will call adopt_belief()
                    self.person_model.init_belief_facet(
                        feature_type=feature_type,
                        observation_or_reflection=new_observation_or_reflection
                    )
                else:
                    # Belief facet is already accurate, but update its evidence to point to the new
                    # observation or reflection (which will slow any potential deterioration) -- this
                    # will also increment the strength of the belief facet, which will make it less
                    # likely to deteriorate in this future
                    current_belief_facet.attribute_new_evidence(new_evidence=new_observation_or_reflection)

    def deteriorate(self):
        """Deteriorate the components of this belief (potentially) by mutation, transference, and/or forgetting."""
        config = self.person_model.owner.game.config
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                current_belief_facet = self.__dict__[feature]
                if current_belief_facet is not None:
                    feature_type_str = current_belief_facet.feature_type
                    belief_facet_strength = current_belief_facet.strength
                else:
                    feature_type_str = self.attribute_to_belief_type(attribute=feature)
                    belief_facet_strength = 1
                # Determine the chance of memory deterioration, which starts from a base value
                # that gets affected by the person's memory and the strength of the belief facet
                chance_of_memory_deterioration = (
                    config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                    self.person_model.owner.mind.memory /
                    belief_facet_strength
                )
                if random.random() < chance_of_memory_deterioration:
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already) --
                    # when the facet object's init() method is called, it will call
                    # attribute_new_evidence(), which will automatically call adopt_belief()
                    # because its initial evidence will be of a deterioration type
                    self.person_model.deteriorate_belief_facet(
                        feature_type=feature_type_str, current_belief_facet=current_belief_facet
                    )

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "company": "workplace",
            "job_title": "job title",
            "shift": "job shift"
        }
        return attribute_to_belief_type[attribute]


class FaceBelief(object):
    """A person's mental model of a person's face."""

    def __init__(self, person_model):
        """Initialize a FaceBelief object."""
        # Prepare the structure of this belief hierarchy
        self.person_model = person_model
        self.skin = SkinBelief(face_belief=self)
        self.head = HeadBelief(face_belief=self)
        self.hair = HairBelief(face_belief=self)
        self.eyebrows = EyebrowsBelief(face_belief=self)
        self.eyes = EyesBelief(face_belief=self)
        self.ears = EarsBelief(face_belief=self)
        self.nose = NoseBelief(face_belief=self)
        self.mouth = MouthBelief(face_belief=self)
        self.facial_hair = FacialHairBelief(face_belief=self)
        self.distinctive_features = DistinctiveFeaturesBelief(face_belief=self)

    def establish(self, observation_or_reflection):
        """Establish initial belief facets in response to an initial observation/reflection."""
        for belief in (
            self.skin, self.head, self.hair, self.eyebrows, self.eyes, self.ears,
            self.nose, self.mouth, self.facial_hair, self.distinctive_features
        ):
            belief.establish(observation_or_reflection=observation_or_reflection)

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for already correct facets.
        """
        for belief_type in self.__dict__:  # Iterates over all attributes defined in __init__()
            if belief_type != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief = self.__dict__[belief_type]
                for feature in belief.__dict__:
                    if feature != 'face_belief':  # This should be the only one that doesn't resolve to a belief facet
                        belief_facet = belief.__dict__[feature]
                        if belief_facet is None or not belief_facet.accurate:
                            feature_type = belief.attribute_to_feature_type(attribute=feature)
                            # Adopt a new, accurate belief facet (unless init_belief_facet returns None)
                            belief.__dict__[feature] = (
                                belief.face_belief.person_model.init_belief_facet(
                                    feature_type=feature_type,
                                    observation_or_reflection=new_observation_or_reflection
                                )
                            )
                        else:
                            # Belief facet is already accurate, but update its evidence to point to the new
                            # observation or reflection (which will slow any potential deterioration) -- this
                            # will also increment the strength of the belief facet, which will make it less
                            # likely to deteriorate in this future
                            belief_facet.attribute_new_evidence(new_evidence=new_observation_or_reflection)

    def deteriorate(self):
        """Deteriorate the components of this belief (potentially) by mutation, transference, and/or forgetting."""
        config = self.person_model.owner.game.config
        for belief_type in self.__dict__:  # Iterates over all attributes defined in __init__()
            if belief_type != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief = self.__dict__[belief_type]
                for feature in belief.__dict__:
                    if feature != 'face_belief':  # This should be the only one that doesn't resolve to a belief facet
                        belief_facet = belief.__dict__[feature]
                        if belief_facet is not None:
                            feature_type_str = belief_facet.feature_type
                            belief_facet_strength = belief_facet.strength
                        else:
                            feature_type_str = belief.attribute_to_feature_type(attribute=feature)
                            belief_facet_strength = 1
                        if belief_facet_strength < 1:
                            belief_facet_strength = 1
                        # Determine the chance of memory deterioration, which starts from a base value
                        # that gets affected by the person's memory and the strength of the belief facet
                        chance_of_memory_deterioration = (
                            config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                            self.person_model.owner.mind.memory /
                            belief_facet_strength
                        )
                        if random.random() < chance_of_memory_deterioration:
                            # Instantiate a new belief facet that represents a deterioration of
                            # the existing one (which itself may be a deterioration already)
                            deteriorated_belief_facet = self.person_model.deteriorate_belief_facet(
                                feature_type=feature_type_str, current_belief_facet=belief_facet
                            )
                            belief.__dict__[feature] = deteriorated_belief_facet


class SkinBelief(object):
    """A person's mental model of a person's skin."""

    def __init__(self, face_belief):
        """Initialize a Skin object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.color = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.color = self.face_belief.person_model.init_belief_facet(
            feature_type="skin color", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "color": "skin color"
        }
        return attribute_to_feature_type[attribute]


class HeadBelief(object):
    """A person's mental model of a person's head."""

    def __init__(self, face_belief):
        """Initialize a Head object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = None
        self.shape = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.size = self.face_belief.person_model.init_belief_facet(
            feature_type="head size", observation_or_reflection=observation_or_reflection
        )
        self.shape = self.face_belief.person_model.init_belief_facet(
            feature_type="head shape", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "size": "head size",
            "shape": "head shape"
        }
        return attribute_to_feature_type[attribute]


class HairBelief(object):
    """A person's mental model of a person's hair (on his or her head)."""

    def __init__(self, face_belief):
        """Initialize a Hair object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.length = None
        self.color = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.length = self.face_belief.person_model.init_belief_facet(
            feature_type="hair length", observation_or_reflection=observation_or_reflection
        )
        self.color = self.face_belief.person_model.init_belief_facet(
            feature_type="hair color", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "length": "hair length",
            "color": "hair color"
        }
        return attribute_to_feature_type[attribute]


class EyebrowsBelief(object):
    """A person's mental model of a person's eyebrows."""

    def __init__(self, face_belief):
        """Initialize a Eyebrows object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = None
        self.color = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.size = self.face_belief.person_model.init_belief_facet(
            feature_type="eyebrow size", observation_or_reflection=observation_or_reflection
        )
        self.color = self.face_belief.person_model.init_belief_facet(
            feature_type="eyebrow color", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "size": "eyebrow size",
            "color": "eyebrow color"
        }
        return attribute_to_feature_type[attribute]


class MouthBelief(object):
    """A person's mental model of a person's mouth."""

    def __init__(self, face_belief):
        """Initialize a Mouth object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.size = self.face_belief.person_model.init_belief_facet(
            feature_type="mouth size", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "size": "mouth size",
        }
        return attribute_to_feature_type[attribute]


class EarsBelief(object):
    """A person's mental model of a person's ears."""

    def __init__(self, face_belief):
        """Initialize an Ears object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = None
        self.angle = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.size = self.face_belief.person_model.init_belief_facet(
            feature_type="ear size", observation_or_reflection=observation_or_reflection
        )
        self.angle = self.face_belief.person_model.init_belief_facet(
            feature_type="ear angle", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "size": "ear size",
            "angle": "ear angle",
        }
        return attribute_to_feature_type[attribute]


class NoseBelief(object):
    """A person's mental model of a person's nose."""

    def __init__(self, face_belief):
        """Initialize a Nose object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = None
        self.shape = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.size = self.face_belief.person_model.init_belief_facet(
            feature_type="nose size", observation_or_reflection=observation_or_reflection
        )
        self.shape = self.face_belief.person_model.init_belief_facet(
            feature_type="nose shape", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "size": "nose size",
            "shape": "nose shape",
        }
        return attribute_to_feature_type[attribute]


class EyesBelief(object):
    """A person's mental model of a person's eyes."""

    def __init__(self, face_belief):
        """Initialize an Eyes object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = None
        self.shape = None
        self.horizontal_settedness = None
        self.vertical_settedness = None
        self.color = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.size = self.face_belief.person_model.init_belief_facet(
            feature_type="eye size", observation_or_reflection=observation_or_reflection
        )
        self.shape = self.face_belief.person_model.init_belief_facet(
            feature_type="eye shape", observation_or_reflection=observation_or_reflection
        )
        self.horizontal_settedness = self.face_belief.person_model.init_belief_facet(
            feature_type="eye horizontal settedness", observation_or_reflection=observation_or_reflection
        )
        self.vertical_settedness = self.face_belief.person_model.init_belief_facet(
            feature_type="eye vertical settedness", observation_or_reflection=observation_or_reflection
        )
        self.color = self.face_belief.person_model.init_belief_facet(
            feature_type="eye color", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "size": "eye size",
            "shape": "eye shape",
            "horizontal_settedness": "eye horizontal settedness",
            "vertical_settedness": "eye vertical settedness",
            "color": "eye color",
        }
        return attribute_to_feature_type[attribute]


class FacialHairBelief(object):
    """A person's mental model of a person's facial hair."""

    def __init__(self, face_belief):
        """Initialize a FacialHair style.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.style = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.style = self.face_belief.person_model.init_belief_facet(
            feature_type="facial hair style", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "style": "facial hair style"
        }
        return attribute_to_feature_type[attribute]


class DistinctiveFeaturesBelief(object):
    """A person's mental model of a person's distinguishing features."""

    def __init__(self, face_belief):
        """Initialize a DistinctiveFeatures object.
        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.freckles = None
        self.birthmark = None
        self.scar = None
        self.tattoo = None
        self.glasses = None
        self.sunglasses = None

    def establish(self, observation_or_reflection):
        """Build up according to an observation or reflection."""
        self.freckles = self.face_belief.person_model.init_belief_facet(
            feature_type="freckles", observation_or_reflection=observation_or_reflection
        )
        self.birthmark = self.face_belief.person_model.init_belief_facet(
            feature_type="birthmark", observation_or_reflection=observation_or_reflection
        )
        self.scar = self.face_belief.person_model.init_belief_facet(
            feature_type="scar", observation_or_reflection=observation_or_reflection
        )
        self.tattoo = self.face_belief.person_model.init_belief_facet(
            feature_type="tattoo", observation_or_reflection=observation_or_reflection
        )
        self.glasses = self.face_belief.person_model.init_belief_facet(
            feature_type="glasses", observation_or_reflection=observation_or_reflection
        )
        self.sunglasses = self.face_belief.person_model.init_belief_facet(
            feature_type="sunglasses", observation_or_reflection=observation_or_reflection
        )

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "freckles": "freckles",
            "birthmark": "birthmark",
            "scar": "scar",
            "tattoo": "tattoo",
            "glasses": "glasses",
            "sunglasses": "sunglasses",
        }
        return attribute_to_feature_type[attribute]


class Facet(str):
    """A facet of one person's mental model of a person (pertaining to a specific attribute)."""

    def __init__(self, value, owner, subject, feature_type, initial_evidence, object_itself=None):
        """Initialize a Facet object.
        @param value: A string representation of this facet, e.g., 'brown' as the Hair.color
                      attribute this represents.
        @param owner: The person to whom this belief facet belongs.
        @param subject: The person to whom this belief facet pertains.
        @param feature_type: A string representing the type of feature this facet is about.
        @param initial_evidence: An information object that serves as the initial evidence for
                                 this being a facet of a person's belief.
        @param object_itself: The very object that this facet represents -- this is only
                              relevant in certain cases, e.g., in a belief facet about where
                              a person works, object_itself would be the Business object of
                              where they work (which will also be a key in the person's
                              mental models that points to a BusinessBelief, and so keeping
                              track of the object itself here affords an ontological network.
        """
        super(Facet, self).__init__()
        self.owner = owner
        self.subject = subject
        self.feature_type = feature_type
        # Only currently held belief facets are attributed a predecessor -- if you are merely
        # challenging some held facet, the latter is not your predecessor; the default value
        # for .predecessor is None; this value gets changed by MentalModel.adopt_belief()
        self.predecessor = None
        # If there is a currently held belief facet for this feature type, this facet will be
        # considered a challenger until some point at which the strength of its evidence exceeds
        # the strength of the evidence of the currently held belief (which could be as early as
        # during this initialization procedure, when .attribute_new_evidence() is called);
        # challenger status may be revised from True to False by MentalModel.adopt_belief()
        currently_held_belief = self._get_currently_held_belief()
        self.challenger = False if currently_held_belief is None else True
        if not self.challenger:
            # This is the character's first belief facet regarding this attribute -- have
            # it be adopted immediately
            mental_model = self.owner.mind.mental_models[self.subject]
            mental_model.adopt_belief(
                new_belief_facet=self, old_belief_facet=None
            )
        # A belief facet's challengers are other potential beliefs (instantiated as other
        # Facet objects) about this attribute for which the owner of this Facet has encountered
        # evidence. If at any time the strength of the evidence for some challenger exceeds the
        # strength of the evidence for the currently held belief, the owner will update their
        # belief accordingly (by .attribute_new_evidence) and relegate this belief to challenger
        # status. Upon adoption, a Facet that was a challenger inherits the challengers of
        # its predecessor, excluding itself
        self.challengers = set()  # Default value; may get changed by MentalModel.adopt_belief()
        self.evidence = set()
        self.object_itself = object_itself
        if object_itself:
            # If owner hasn't yet formed a mental model of the subject, form one
            if object_itself not in self.owner.mind.mental_models:
                if object_itself.type == "residence":
                    DwellingPlaceModel(owner=self.owner, subject=object_itself, observation=None)
                elif object_itself.type == "business":
                    BusinessMentalModel(owner=self.owner, subject=object_itself, observation=None)
            # Link directly to owner's mental model of the object that this belief facet
            # resolves to -- this affords an ontological structure in the sense that
            # entities across a person's network of mental models may be linked according
            # to semantic relations like believing a person for whom you've developed a
            # mental model lives in a home for which you've developed a mental model
            self.mental_model = self.owner.mind.mental_models[object_itself]
        else:
            self.mental_model = None
        # Finally, attribute the initial evidence to this new belief facet, which may cause a
        # currently held belief to shift to challenger status, and this new belief to the
        # character's actual current belief
        self.attribute_new_evidence(new_evidence=initial_evidence)

    def __new__(cls, value, owner, subject, feature_type, initial_evidence, object_itself):
        """Do str stuff."""
        return str.__new__(cls, value)

    @property
    def accurate(self):
        """Return whether this belief is accurate."""
        true_feature = self.subject.get_feature(feature_type=self.feature_type)
        if self == true_feature:
            return True
        else:
            return False

    @property
    def strength(self):
        """The strength of this particular belief at this particular timestep, given its evidence.

        Strength represents how confident owner is in this belief and decays over time; it
        is used to reduce the chance of a belief facet deteriorating (by dividing the base
        chance of deterioration by the strength of the facet) -- it gets updated by
        Facet.attribute_new_evidence().
        """
        strength = sum(self._determine_strength_of_a_piece_of_evidence(piece) for piece in self.evidence)
        return strength

    def _determine_strength_of_a_piece_of_evidence(self, evidence):
        """Determine the strength of a particular piece of evidence.

        This method takes into account how much the owner trusts the source of the
        evidence and how strong the source's belief was at the time that conveyed it
        to owner, in the case of propagation evidence types, as well as how long ago
        the evidence was instantiated.
        """
        config = self.owner.game.config
        if evidence.adjusted_strength:
            strength = evidence.adjusted_strength
        else:
            strength = config.base_strength_of_evidence_types[evidence.type]
            # If evidence is a type of propagation, alter the strength according to...
            if evidence.type in ('statement', 'lie', 'eavesdropping'):
                # ...the owner's trust value for the source
                if evidence.source in self.owner.relationships:
                    strength *= self.owner.relationships[evidence.source].trust
                else:
                    # They eavesdropped the source and don't actually have a relationship with them
                    strength *= config.trust_someone_has_for_random_person_they_eavesdrop
                # ...the strength of the source's belief at the time of telling
                if evidence.type == 'lie':
                    teller_belief_strength = random.randint(1, 300)  # TODO maybe model lying ability here?
                else:
                    teller_belief_strength = evidence.teller_belief_strength[self.feature_type]
                source_belief_strength_multiplier = config.function_to_determine_teller_strength_boost(
                    teller_belief_strength=teller_belief_strength
                )
                strength *= source_belief_strength_multiplier
        # Decay the strength of this evidence given how long ago it occurred. Note that this
        # will cause adjusted strengths to be considerably decayed, since their very adjustment
        # already was decayed according to how long ago the evidence was encountered relative to
        # the time of adjustment; this seems realistic, however, because if someone forgets some
        # piece of evidence, that should considerably penalize the strength of that evidence
        for day in xrange(self.owner.game.ordinal_date-evidence.ordinal_date):
            strength *= config.decay_rate_of_evidence_per_timestep
        return strength

    def adjust_strength_of_forgotten_evidence(self, total_strength_of_supplanter):
        """Adjust the strength of forgotten evidence.

        This method is called when the belief represented by this Facet is forgotten,
        or more precisely, is supplanted by a piece of evidence with a deterioration type.
        It adjusts the strength of the total evidence of a forgotten belief facet so that
        its strength is equal to the strength of the new Facet supported by some kind of
        deterioration. This allows a character to temporarily forget something but later,
        upon encountering new evidence supporting the forgotten belief, remember that they
        had previously believed it and then reinstate it again.
        """
        # Survey the evidence supporting this belief to determine the current actual strength
        # of each piece -- we keep track of these values in a dictionary so that we don't
        # carry out this computation twice in this method (once to determine the multiplier,
        # again to actually adjust the strength of each piece of evidence)
        actual_current_strength_of_each_piece_of_evidence = {}
        for piece in self.evidence:
            actual_current_strength = self._determine_strength_of_a_piece_of_evidence(evidence=piece)
            actual_current_strength_of_each_piece_of_evidence[piece] = actual_current_strength
        # Determine the multiplier that will allow us to adjust the strength of each piece
        # of evidence supporting this belief facet such that its adjusted total strength
        # will become (nearly) equal to the total strength of the new deteriorated belief
        cumulative_strength_of_this_belief = sum(actual_current_strength_of_each_piece_of_evidence.values())
        try:
            multiplier = float(total_strength_of_supplanter) / (cumulative_strength_of_this_belief-1)
        except ZeroDivisionError:
            multiplier = 0.01
        for piece in self.evidence:
            piece.adjusted_strength = actual_current_strength_of_each_piece_of_evidence[piece] * multiplier

    def attribute_new_evidence(self, new_evidence):
        """Attribute new evidence that supports this belief facet."""
        self.evidence.add(new_evidence)
        new_evidence.beliefs_evidenced.add(self)
        # If this is a challenger belief facet, check for whether this belief is now stronger
        # than the character's currently held belief, in which case it will lose its challenger
        # status and the old belief will be attributed as merely a challenger to this belief
        # facet (this is all done by MentalModel.adopt_belief); additionally, if new_evidence
        # is a deterioration/observation, this will automatically take over, since a
        # deterioration/observation always wins (and indeed the chance of deterioration
        # occurring is determined probabilistically according to the strength of the previously
        # held belief, so in a sense it has already been determined to be 'stronger')
        if self.challenger:
            currently_held_belief = self._get_currently_held_belief()
            assert currently_held_belief is not None, (
                "{}'s belief facet '{}' for {}'s {} has been wrongly attributed challenger status, i.e, "
                "there is no currently held belief for that facet.".format(
                    self.owner.name, self, self.subject.name, self.feature_type
                )
            )
            assert currently_held_belief is not self, (
                "A belief facet currently held by {} for feature type '{}' (about subject {}) "
                "was attributed challenger status.".format(
                    self.owner.name, self.feature_type, self.subject.name
                )
            )
            automatically_take_over_because_deterioration_or_observation = (
                'reflection', 'observation', 'confabulation', 'mutation', 'transference', 'forgetting'
            )
            strength_of_this_belief_facet = self.strength
            # If this belief facet is now stronger than the currently held one, revise your belief
            if (strength_of_this_belief_facet > currently_held_belief.strength or
                    new_evidence.type in automatically_take_over_because_deterioration_or_observation):
                mental_model = self.owner.mind.mental_models[self.subject]
                mental_model.adopt_belief(
                    new_belief_facet=self, old_belief_facet=currently_held_belief
                )
                # If the new evidence is a type of deterioration, adjust the strength of the evidence
                # supporting the belief that is being supplanted (check docstring for
                # adjust_strength_of_forgotten_evidence() to read more about what this is all about)
                if new_evidence.type in automatically_take_over_because_deterioration_or_observation:
                    currently_held_belief.adjust_strength_of_forgotten_evidence(
                        total_strength_of_supplanter=strength_of_this_belief_facet
                    )

    def _get_currently_held_belief(self):
        """Return the belief facet that is currently held for this feature type; if none, return None."""
        mental_model = self.owner.mind.mental_models[self.subject]
        command_to_access_currently_held_belief = mental_model.get_command_to_access_a_belief_facet(
            feature_type=self.feature_type
        )
        # Have to swap out 'self' in this command, because the return value for
        # mental_model.get_command_to_access_a_belief_facet() is relative to mental model
        # being referenceable by 'self'
        command_to_access_currently_held_belief = (
            command_to_access_currently_held_belief.replace('self', 'mental_model')
        )
        try:
            currently_held_belief = eval(command_to_access_currently_held_belief)
        except AttributeError:
            # This error gets raised when the mental model has not even been fully constructed
            # yet -- i.e., this is one of the initial belief facets that will make up the initial
            # mental model, so attribute hierarchies like MentalModel.Face.Hair.Color are not even
            # constructed yet (and thus cannot be accessed); in this case, we can safely assert that
            # there is no currently held belief for this attribute
            currently_held_belief = None
        except KeyError:
            # This error gets raised when an attempt is made (by evaluating command_to_access_
            # currently_held_belief) to access a non-existent whereabouts belief; i.e., the
            # command will specify accessing a WhereaboutsBelief.date dictionary with a key for
            # the timestep in question, but if this person did not already hold some belief about
            # subject's whereabouts on that timestep, then a KeyError will be raised, since there
            # will be no entry in the dictionary associated with that key;  in this case, we can
            # safely assert that there is no currently held belief for this attribute
            assert 'whereabouts' in self.feature_type, (
                "A KeyError was raised outside of the context of an attempt to access a "
                "non-existent whereabouts belief."
            )
            currently_held_belief = None
        return currently_held_belief

    def why(self):
        """Pretty-print why this character holds this particular belief."""
        print "\n{} believes {}'s {} is {} because of the following evidence:\n".format(
            self.owner.name, self.subject.name, self.feature_type, self
        )
        all_evidence_supporting_belief = list(self.evidence)
        all_evidence_supporting_belief.sort(key=lambda piece: piece.event_number)
        for piece in all_evidence_supporting_belief:
            print '--{}'.format(piece)