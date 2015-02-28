import random
from knowledge import *


class PersonMentalModel(object):
    """A person's mental model of a person, representing everything she believes about her."""

    def __init__(self, owner, subject, originating_in_first_hand_observation):
        """Initialize a PersonMentalModel object.

        @param owner: The person who holds this belief.
        @param subject: The person to whom this belief pertains.
        @param originating_in_first_hand_observation: Whether this mental model is originating
                                                      from first-hand observation of the subject,
                                                      as opposed to hearing of them second-hand.
        """
        self.owner = owner
        self.subject = subject
        if originating_in_first_hand_observation:
            self.face = FaceBelief(person_model=self)

    def determine_belief_facet(self, feature_type):
        """Determine a belief facet pertaining to a feature of the given type."""
        config = self.owner.game.config
        true_feature_str, observation = (
            self._get_true_feature_and_generate_an_observation_for_it(feature_type=feature_type)
        )
        chance_feature_gets_remembered_perfectly = (
            self._calculate_chance_feature_gets_remembered_perfectly(feature_type=feature_type)
        )
        if random.random() < chance_feature_gets_remembered_perfectly:
            belief_facet_obj = Facet(value=true_feature_str, evidence=observation)
        else:
            # Knowledge will either succumb to mutation or transference or forgetting
            result = self._decide_how_knowledge_will_pollute_or_be_forgotten(config=config)
            if result == 't' and len(self.owner.mind.mental_models) > 1:  # Transference
                # Note: the check on the owner's mental models is to make sure they
                # actually have a mental model for a person other than themself to
                # transfer the feature attribute from
                belief_facet_obj = self._transfer_belief_facet(
                    feature_type=feature_type, parent_knowledge_object=observation
                )
            elif result == 'm':  # Mutation
                belief_facet_obj = self._mutate_belief_facet(
                    feature_type=feature_type, parent_knowledge_object=observation,
                    true_feature_str=true_feature_str
                )
            else:  # Forgetting
                belief_facet_obj = self._forget_belief_facet(parent_knowledge_object=observation)
        return belief_facet_obj

    def _mutate_belief_facet(self, feature_type, parent_knowledge_object, true_feature_str):
        """Mutate a belief facet."""
        config = self.subject.game.config
        x = random.random()
        possible_mutations = config.memory_mutations[feature_type][true_feature_str]
        mutated_feature_str = next(  # See config.py to understand what this is doing
            mutation[1] for mutation in possible_mutations if
            mutation[0][0] <= x <= mutation[0][1]
        )
        mutation = Mutation(parent=parent_knowledge_object, subject=self.subject)
        belief_facet_obj = Facet(value=mutated_feature_str, evidence=mutation)
        return belief_facet_obj

    def _transfer_belief_facet(self, feature_type, parent_knowledge_object):
        """Cause a belief facet to change by transference.

        TODO: Have transference be more likely to happen between similar people --
        this requires an operationalized notion of how similar any two people are.
        """
        config = self.subject.game.config
        if any(person for person in self.owner.mind.mental_models if person.sex == self.subject.sex):
            person_belief_will_transfer_from = next(
                person for person in self.owner.mind.mental_models if person.sex == self.subject.sex
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
            parent=parent_knowledge_object, subject=self.subject,
            belief_facet_transferred_from=belief_facet_transferred_from
        )
        belief_facet_obj = Facet(value=feature_str, evidence=transference)
        return belief_facet_obj

    def _forget_belief_facet(self, parent_knowledge_object):
        """Cause a belief facet to be forgotten."""
        forgetting = Forgetting(subject=self.subject, parent=parent_knowledge_object)
        # Facets evidenced by a Forgetting should always have an empty string
        # for their value
        belief_facet_obj = Facet(value='', evidence=forgetting)
        return belief_facet_obj

    def _get_true_feature_and_generate_an_observation_for_it(self, feature_type):
        true_feature_str = str(self._get_a_persons_true_feature_of_type(
            person=self.subject, feature_type=feature_type)
        )
        observation = Observation(subject=self.subject, source=self.owner)
        return true_feature_str, observation

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
    def _get_a_persons_true_feature_of_type(person, feature_type):
        """Return this person's feature of the given type."""
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

    def __init__(self, person_model):
        """Initialize a FaceBelief object."""
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


class SkinBelief(object):
    """A person's mental model of a person's skin."""

    def __init__(self, face_belief):
        """Initialize a Skin object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.color = self.face_belief.person_model.determine_belief_facet(feature_type="skin color")


class HeadBelief(object):
    """A person's mental model of a person's head."""

    def __init__(self, face_belief):
        """Initialize a Head object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(feature_type="head size")
        self.shape = self.face_belief.person_model.determine_belief_facet(feature_type="head shape")


class HairBelief(object):
    """A person's mental model of a person's hair (on his or her head)."""

    def __init__(self, face_belief):
        """Initialize a Hair object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.length = self.face_belief.person_model.determine_belief_facet(feature_type="hair length")
        self.color = self.face_belief.person_model.determine_belief_facet(feature_type="hair color")


class EyebrowsBelief(object):
    """A person's mental model of a person's eyebrows."""

    def __init__(self, face_belief):
        """Initialize a Eyebrows object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(feature_type="eyebrow size")
        self.color = self.face_belief.person_model.determine_belief_facet(feature_type="eyebrow color")


class MouthBelief(object):
    """A person's mental model of a person's mouth."""

    def __init__(self, face_belief):
        """Initialize a Mouth object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(feature_type="mouth size")


class EarsBelief(object):
    """A person's mental model of a person's ears."""

    def __init__(self, face_belief):
        """Initialize an Ears object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(feature_type="ear size")
        self.angle = self.face_belief.person_model.determine_belief_facet(feature_type="ear angle")


class NoseBelief(object):
    """A person's mental model of a person's nose."""

    def __init__(self, face_belief):
        """Initialize a Nose object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(feature_type="nose size")
        self.shape = self.face_belief.person_model.determine_belief_facet(feature_type="nose shape")


class EyesBelief(object):
    """A person's mental model of a person's eyes."""

    def __init__(self, face_belief):
        """Initialize an Eyes object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(feature_type="eye size")
        self.shape = self.face_belief.person_model.determine_belief_facet(feature_type="eye shape")
        self.horizontal_settedness = self.face_belief.person_model.determine_belief_facet(feature_type="eye horizontal settedness")
        self.vertical_settedness = self.face_belief.person_model.determine_belief_facet(feature_type="eye vertical settedness")
        self.color = self.face_belief.person_model.determine_belief_facet(feature_type="eye color")


class FacialHairBelief(object):
    """A person's mental model of a person's facial hair."""

    def __init__(self, face_belief):
        """Initialize a FacialHair style.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.style = self.face_belief.person_model.determine_belief_facet(feature_type="facial hair style")


class DistinctiveFeaturesBelief(object):
    """A person's mental model of a person's distinguishing features."""

    def __init__(self, face_belief):
        """Initialize a DistinctiveFeatures object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.freckles = self.face_belief.person_model.determine_belief_facet(feature_type="freckles")
        self.birthmark = self.face_belief.person_model.determine_belief_facet(feature_type="birthmark")
        self.scar = self.face_belief.person_model.determine_belief_facet(feature_type="scar")
        self.tattoo = self.face_belief.person_model.determine_belief_facet(feature_type="tattoo")
        self.glasses = self.face_belief.person_model.determine_belief_facet(feature_type="glasses")
        self.sunglasses = self.face_belief.person_model.determine_belief_facet(feature_type="sunglasses")


class Facet(str):
    """A facet of one person's belief about a person that pertains to a specific feature.

    This class has a sister class in Face.Feature. While objects of the Feature class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature, a Facet
    represents a person's facial feature *as it is modeled in the belief of a particular
    person*, with metadata about that specific belief.
    """

    def __init__(self, value, evidence):
        """Initialize a Facet object.

        @param value: A string representation of this facet, e.g., 'brown' as the Hair.color
                      attribute this represents.
        @param evidence: An information object that serves as the evidence for this being a
                         facet of a person's belief.
        """
        super(Facet, self).__init__()
        self.evidence = evidence
        self.evidence.beliefs_evidenced.add(self)

    def __new__(cls, value, evidence):
        """Do str stuff."""
        return str.__new__(cls, value)