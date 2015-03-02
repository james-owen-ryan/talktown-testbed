import random
from knowledge import *


class PersonMentalModel(object):
    """A person's mental model of a person, representing everything she believes about her."""

    def __init__(self, owner, subject, observation_or_reflection):
        """Initialize a PersonMentalModel object.

        @param owner: The person who holds this belief.
        @param subject: The person to whom this belief pertains.
        @param observation_or_reflection: The Observation or Reflection from which this
                                          the beliefs composing this mental model originate.
        """
        self.owner = owner
        self.subject = subject
        self.face = FaceBelief(
            person_model=self, observation_or_reflection=observation_or_reflection
        )
        self.owner.mind.mental_models[self.subject] = self

    def build_up(self, new_observation_or_reflection):
        """Build up a mental model from a new observation or reflection."""
        self.face.build_up(new_observation_or_reflection=new_observation_or_reflection)

    def determine_belief_facet(self, feature_type, observation_or_reflection):
        """Determine a belief facet pertaining to a feature of the given type."""
        config = self.owner.game.config
        if not observation_or_reflection:
            # This is in service to preparation of a mental model composed (initially) of
            # blank belief attributes -- then these can be filled in manually according
            # to what a person tells another person, etc.
            return None
        else:
            true_feature_str = self._get_true_feature(feature_type=feature_type)
            observation_or_reflection = observation_or_reflection
            chance_feature_gets_remembered_perfectly = (
                self._calculate_chance_feature_gets_remembered_perfectly(feature_type=feature_type)
            )
            # Affect this chance by the person's memory
            chance_feature_gets_remembered_perfectly *= self.owner.mind.memory
            # If this is a reflection, there's no chance person will forget
            if observation_or_reflection.type == "reflection":
                chance_feature_gets_remembered_perfectly = 1.0
            if random.random() < chance_feature_gets_remembered_perfectly:
                belief_facet_obj = Facet(
                    value=true_feature_str, owner=self.owner, subject=self.subject,
                    feature_type=feature_type, evidence=observation_or_reflection
                )
            else:
                # Knowledge will deteriorate, either mutation, transference, forgetting
                belief_facet_obj = self.deteriorate_belief_facet(
                    feature_type=feature_type, parent_knowledge_object=observation_or_reflection,
                    current_feature_str=true_feature_str
                )
            return belief_facet_obj

    def deteriorate_belief_facet(self, feature_type, parent_knowledge_object, current_feature_str):
        """Deteriorate a belief facet, either by mutation, transference, or forgetting."""
        config = self.owner.game.config
        result = self._decide_how_knowledge_will_pollute_or_be_forgotten(config=config)
        if result == 't' and len(self.owner.mind.mental_models) > 1:  # Transference
            # Note: the check on the owner's mental models is to make sure they
            # actually have a mental model for a person other than themself to
            # transfer the feature attribute from
            belief_facet_obj = self._transfer_belief_facet(
                feature_type=feature_type, parent_knowledge_object=parent_knowledge_object
            )
        elif result == 'm':  # Mutation
            belief_facet_obj = self._mutate_belief_facet(
                feature_type=feature_type, parent_knowledge_object=parent_knowledge_object,
                feature_being_mutated_from_str=current_feature_str
            )
        else:  # Forgetting
            belief_facet_obj = self._forget_belief_facet(
                feature_type=feature_type, parent_knowledge_object=parent_knowledge_object
            )
        return belief_facet_obj

    def _mutate_belief_facet(self, feature_type, parent_knowledge_object, feature_being_mutated_from_str):
        """Mutate a belief facet."""
        config = self.subject.game.config
        x = random.random()
        possible_mutations = config.memory_mutations[feature_type][feature_being_mutated_from_str]
        mutated_feature_str = next(  # See config.py to understand what this is doing
            mutation[1] for mutation in possible_mutations if
            mutation[0][0] <= x <= mutation[0][1]
        )
        mutation = Mutation(
            parent=parent_knowledge_object, subject=self.subject, source=self.owner,
            mutated_belief_str=feature_being_mutated_from_str)
        belief_facet_obj = Facet(
            value=mutated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=mutation
        )
        return belief_facet_obj

    def _transfer_belief_facet(self, feature_type, parent_knowledge_object):
        """Cause a belief facet to change by transference.

        TODO: Have transference be more likely to happen between similar people --
        this requires an operationalized notion of how similar any two people are.
        """
        config = self.subject.game.config
        if any(person for person in self.owner.mind.mental_models if person.male == self.subject.male):
            person_belief_will_transfer_from = next(
                person for person in self.owner.mind.mental_models if person.male == self.subject.male
            )
        else:
            person_belief_will_transfer_from = random.sample(self.owner.mind.mental_models, 1)[0]
        belief_facet_transferred_from = (
            self.owner.mind.mental_models[person_belief_will_transfer_from]._get_a_facet_to_this_belief_of_type(
                feature_type=feature_type
            )
        )
        feature_str = str(belief_facet_transferred_from)
        transference = Transference(
            subject=self.subject, source=self.owner, parent=parent_knowledge_object,
            belief_facet_transferred_from=belief_facet_transferred_from
        )
        belief_facet_obj = Facet(
            value=feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=transference
        )
        return belief_facet_obj

    def _forget_belief_facet(self, feature_type, parent_knowledge_object):
        """Cause a belief facet to be forgotten."""
        forgetting = Forgetting(subject=self.subject, source=self.owner, parent=parent_knowledge_object)
        # Facets evidenced by a Forgetting should always have an empty string
        # for their value
        belief_facet_obj = Facet(
            value='', owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=forgetting
        )
        return belief_facet_obj

    def _get_true_feature(self, feature_type):
        true_feature_str = str(self.subject.feature_of_type(feature_type=feature_type))
        return true_feature_str

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

    def _get_a_facet_to_this_belief_of_type(self, feature_type):
        """Return the facet to this mental model of the given type."""
        features = {
            "skin color": self.face.skin.color,
            "head size": self.face.head.size,
            "head shape": self.face.head.shape,
            "hair length": self.face.hair.length,
            "hair color": self.face.hair.color,
            "eyebrow size": self.face.eyebrows.size,
            "eyebrow color": self.face.eyebrows.color,
            "mouth size": self.face.mouth.size,
            "ear size": self.face.ears.size,
            "ear angle": self.face.ears.angle,
            "nose size": self.face.nose.size,
            "nose shape": self.face.nose.shape,
            "eye size": self.face.eyes.size,
            "eye shape": self.face.eyes.shape,
            "eye color": self.face.eyes.color,
            "eye horizontal settedness": self.face.eyes.horizontal_settedness,
            "eye vertical settedness": self.face.eyes.vertical_settedness,
            "facial hair style": self.face.facial_hair.style,
            "freckles": self.face.distinctive_features.freckles,
            "birthmark": self.face.distinctive_features.birthmark,
            "scar": self.face.distinctive_features.scar,
            "tattoo": self.face.distinctive_features.tattoo,  # From nurture
            "glasses": self.face.distinctive_features.glasses,
            "sunglasses": self.face.distinctive_features.sunglasses  # From nurture
        }
        return features[feature_type]


class BuildingMentalModel(object):
    """A person's mental model of a building, representing everything she believes about it."""

    def __init__(self, owner, subject):
        """Initialize a BuildingMentalModel object.

        @param owner: The person who holds this belief.
        @param subject: The building to whom this belief pertains.
        """
        self.owner = owner
        self.subject = subject


class FaceBelief(object):
    """A person's mental model of a person's face."""

    def __init__(self, person_model, observation_or_reflection):
        """Initialize a FaceBelief object."""
        self.person_model = person_model
        self.skin = SkinBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.head = HeadBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.hair = HairBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.eyebrows = EyebrowsBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.eyes = EyesBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.ears = EarsBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.nose = NoseBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.mouth = MouthBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.facial_hair = FacialHairBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )
        self.distinctive_features = DistinctiveFeaturesBelief(
            face_belief=self, observation_or_reflection=observation_or_reflection
        )

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
                        if not belief_facet.accurate:
                            # Potentially make it accurate
                            belief.__dict__[feature] = (
                                belief.face_belief.person_model.determine_belief_facet(
                                    feature_type=belief_facet.feature_type,
                                    observation_or_reflection=new_observation_or_reflection
                                )
                            )
                        else:
                            # Belief facet is already accurate, but update its evidence to point to
                            # the new observation or reflection (which will slow any potential deterioration)
                            belief.__dict__[feature] = Facet(
                                value=str(belief_facet), owner=belief_facet.owner, subject=belief_facet.subject,
                                feature_type=belief_facet.feature_type, evidence=new_observation_or_reflection
                            )


class SkinBelief(object):
    """A person's mental model of a person's skin."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Skin object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.color = self.face_belief.person_model.determine_belief_facet(
            feature_type="skin color", observation_or_reflection=observation_or_reflection
        )


class HeadBelief(object):
    """A person's mental model of a person's head."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Head object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
            feature_type="head size", observation_or_reflection=observation_or_reflection
        )
        self.shape = self.face_belief.person_model.determine_belief_facet(
            feature_type="head shape", observation_or_reflection=observation_or_reflection
        )


class HairBelief(object):
    """A person's mental model of a person's hair (on his or her head)."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Hair object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.length = self.face_belief.person_model.determine_belief_facet(
            feature_type="hair length", observation_or_reflection=observation_or_reflection
        )
        self.color = self.face_belief.person_model.determine_belief_facet(
            feature_type="hair color", observation_or_reflection=observation_or_reflection
        )


class EyebrowsBelief(object):
    """A person's mental model of a person's eyebrows."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Eyebrows object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
            feature_type="eyebrow size", observation_or_reflection=observation_or_reflection
        )
        self.color = self.face_belief.person_model.determine_belief_facet(
            feature_type="eyebrow color", observation_or_reflection=observation_or_reflection
        )


class MouthBelief(object):
    """A person's mental model of a person's mouth."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Mouth object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
            feature_type="mouth size", observation_or_reflection=observation_or_reflection
        )


class EarsBelief(object):
    """A person's mental model of a person's ears."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize an Ears object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
            feature_type="ear size", observation_or_reflection=observation_or_reflection
        )
        self.angle = self.face_belief.person_model.determine_belief_facet(
            feature_type="ear angle", observation_or_reflection=observation_or_reflection
        )


class NoseBelief(object):
    """A person's mental model of a person's nose."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Nose object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
            feature_type="nose size", observation_or_reflection=observation_or_reflection
        )
        self.shape = self.face_belief.person_model.determine_belief_facet(
            feature_type="nose shape", observation_or_reflection=observation_or_reflection
        )


class EyesBelief(object):
    """A person's mental model of a person's eyes."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize an Eyes object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
            feature_type="eye size", observation_or_reflection=observation_or_reflection
        )
        self.shape = self.face_belief.person_model.determine_belief_facet(
            feature_type="eye shape", observation_or_reflection=observation_or_reflection
        )
        self.horizontal_settedness = self.face_belief.person_model.determine_belief_facet(
            feature_type="eye horizontal settedness", observation_or_reflection=observation_or_reflection
        )
        self.vertical_settedness = self.face_belief.person_model.determine_belief_facet(
            feature_type="eye vertical settedness", observation_or_reflection=observation_or_reflection
        )
        self.color = self.face_belief.person_model.determine_belief_facet(
            feature_type="eye color", observation_or_reflection=observation_or_reflection
        )


class FacialHairBelief(object):
    """A person's mental model of a person's facial hair."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a FacialHair style.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.style = self.face_belief.person_model.determine_belief_facet(
            feature_type="facial hair style", observation_or_reflection=observation_or_reflection
        )


class DistinctiveFeaturesBelief(object):
    """A person's mental model of a person's distinguishing features."""

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a DistinctiveFeatures object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.freckles = self.face_belief.person_model.determine_belief_facet(
            feature_type="freckles", observation_or_reflection=observation_or_reflection
        )
        self.birthmark = self.face_belief.person_model.determine_belief_facet(
            feature_type="birthmark", observation_or_reflection=observation_or_reflection
        )
        self.scar = self.face_belief.person_model.determine_belief_facet(
            feature_type="scar", observation_or_reflection=observation_or_reflection
        )
        self.tattoo = self.face_belief.person_model.determine_belief_facet(
            feature_type="tattoo", observation_or_reflection=observation_or_reflection
        )
        self.glasses = self.face_belief.person_model.determine_belief_facet(
            feature_type="glasses", observation_or_reflection=observation_or_reflection
        )
        self.sunglasses = self.face_belief.person_model.determine_belief_facet(
            feature_type="sunglasses", observation_or_reflection=observation_or_reflection
        )


class Facet(str):
    """A facet of one person's belief about a person that pertains to a specific feature.

    This class has a sister class in Face.Feature. While objects of the Feature class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature, a Facet
    represents a person's facial feature *as it is modeled in the belief of a particular
    person*, with metadata about that specific belief.
    """

    def __init__(self, value, owner, subject, feature_type, evidence):
        """Initialize a Facet object.

        @param value: A string representation of this facet, e.g., 'brown' as the Hair.color
                      attribute this represents.
        @param evidence: An information object that serves as the evidence for this being a
                         facet of a person's belief.
        """
        super(Facet, self).__init__()
        self.owner = owner
        self.subject = subject
        self.feature_type = feature_type
        self.evidence = evidence
        self.evidence.beliefs_evidenced.add(self)

    def __new__(cls, value, owner, subject, feature_type, evidence):
        """Do str stuff."""
        return str.__new__(cls, value)

    @property
    def accurate(self):
        """Return whether this belief is accurate."""
        true_feature = self.subject.feature_of_type(feature_type=self.feature_type)
        if self == true_feature:
            return True
        else:
            return False
