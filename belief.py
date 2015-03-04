import random
from knowledge import *
from corpora import Names


# TODO StreetMentalModel, BlockMentalModel, CityMentalModel?


class BusinessMentalModel(object):
    """A person's mental model of a business."""

    def __init__(self, owner, subject, observation):
        """Initialize a BusinessMentalModel object.

        @param owner: The person who holds this belief.
        @param subject: The building to whom this belief pertains.
        """
        self.owner = owner
        self.subject = subject


#### OBSERVING WHERE SOMEONE WORKS SHOULD ONLY COME FROM ACTUALLY OBSERVING, REP THE REST AS STATEMENT


class DwellingPlaceModel(object):
    """A person's mental model of a business."""

    def __init__(self, owner, subject, observation):
        """Initialize a BusinessMentalModel object.

        @param owner: The person who holds this belief.
        @param subject: The building to whom this belief pertains.
        """
        self.owner = owner
        self.subject = subject

        # put address, block, is_apartment on this instead of as attributes on a person


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
        self.owner.mind.mental_models[self.subject] = self
        # Form beliefs about the person's name
        self.name_belief = NameBelief(person_model=self, observation_or_reflection=observation_or_reflection)
        self.first_name, self.middle_name, self.last_name = (
            self.name_belief.first_name, self.name_belief.middle_name, self.name_belief.last_name
        )
        # Form beliefs about the person's work life
        self.occupation = WorkBelief(person_model=self, observation_or_reflection=observation_or_reflection)
        # Form beliefs about the person's home
        self.home = HomeBelief(person_model=self, observation_or_reflection=observation_or_reflection)
        # Form beliefs about the person's face
        self.face = FaceBelief(person_model=self, observation_or_reflection=observation_or_reflection)

    def __str__(self):
        """Return string representation."""
        return "{0}'s mental model of {1}".format(self.owner.name, self.subject.name)

    def build_up(self, new_observation_or_reflection):
        """Build up a mental model from a new observation or reflection."""
        self.name_belief.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self.first_name, self.middle_name, self.last_name = (
            self.name_belief.first_name, self.name_belief.middle_name, self.name_belief.last_name
        )
        self.occupation.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self.home.build_up(new_observation_or_reflection=new_observation_or_reflection)
        self.face.build_up(new_observation_or_reflection=new_observation_or_reflection)

    def deteriorate(self):
        """Deteriorate a mental model from time passing."""
        self.name_belief.deteriorate()
        self.first_name, self.middle_name, self.last_name = (
            self.name_belief.first_name, self.name_belief.middle_name, self.name_belief.last_name
        )
        self.home.deteriorate()
        self.occupation.deteriorate()
        self.face.deteriorate()

    def insert_belief_facet(self, feature_type, evidence):
        """Insert a particular belief facet into this mental model (for when a person hears about another person)."""

    def determine_belief_facet(self, feature_type, observation_or_reflection):
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
                feature_type=feature_type, evidence=observation_or_reflection, object_itself=true_object_itself
            )
            return belief_facet_obj

    def deteriorate_belief_facet(self, feature_type, parent_knowledge_object, current_belief_facet):
        """Deteriorate a belief facet, either by mutation, transference, or forgetting."""
        config = self.owner.game.config
        if current_belief_facet != '' and current_belief_facet is not None:
            result = self._decide_how_knowledge_will_pollute_or_be_forgotten(config=config)
            if result == 't' and any(p for p in self.owner.mind.mental_models if
                                     p is not self.owner and p is not self.subject):  # Transference
                # Note: the check on the owner's mental models is to make sure they
                # actually have a mental model for a person other than themself to
                # transfer the feature attribute from
                belief_facet_obj = self._transfer_belief_facet(
                    feature_type=feature_type, parent_knowledge_object=parent_knowledge_object
                )
            elif result == 'm':  # Mutation
                belief_facet_obj = self._mutate_belief_facet(
                    feature_type=feature_type, parent_knowledge_object=parent_knowledge_object,
                    facet_being_mutated=current_belief_facet
                )
            else:  # Forgetting
                belief_facet_obj = self._forget_belief_facet(
                    feature_type=feature_type, parent_knowledge_object=parent_knowledge_object
                )
        else:
            belief_facet_obj = self._concoct_belief_facet(
                feature_type=feature_type, parent_knowledge_object=parent_knowledge_object
            )
        return belief_facet_obj

    def _concoct_belief_facet(self, feature_type, parent_knowledge_object):
        """Concoct a new belief facet of the given type.

        This is done using the feature distributions that are used to generate the features
        themselves for people that don't have parents.
        """
        config = self.owner.game.config
        concoction = Concoction(subject=self.subject, source=self.owner, parent=parent_knowledge_object)
        if feature_type in config.name_feature_types:
            concocted_feature_str = self._concoct_name_facet(feature_type=feature_type)
            concocted_object_itself = None
        elif feature_type in config.work_feature_types:
            concocted_feature_str, concocted_object_itself = self._concoct_work_facet(feature_type=feature_type)
        elif feature_type in config.home_feature_types:
            concocted_feature_str, concocted_object_itself = self._concoct_home_facet(feature_type=feature_type)
        else:  # Appearance feature
            if self.subject.male:
                distribution = config.facial_feature_distributions_male[feature_type]
            else:
                distribution = config.facial_feature_distributions_female[feature_type]
            x = random.random()
            concocted_feature_str = next(  # See config.py to understand what this is doing
                feature_type[1] for feature_type in distribution if feature_type[0][0] <= x <= feature_type[0][1]
            )
            concocted_object_itself = None
        belief_facet_object = Facet(
            value=concocted_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=concoction, object_itself=concocted_object_itself
        )
        return belief_facet_object

    def _concoct_name_facet(self, feature_type):
        """Concoct a facet to a belief about a person's name."""
        if feature_type == "last name":
            concocted_feature_str = Names.any_surname()
        elif self.subject.male:
            concocted_feature_str = Names.a_masculine_name()
        else:
            concocted_feature_str = Names.a_feminine_name()
        return concocted_feature_str

    def _concoct_work_facet(self, feature_type):
        """Concoct a facet to a belief about a person's work life."""
        if feature_type == "workplace":
            concocted_company = random.choice(list(self.subject.city.companies))
            concocted_feature_str = concocted_company.name
            concocted_object_itself = concocted_company
        elif feature_type == "job shift":
            concocted_feature_str = random.choice(["day", "day", "night"])
            concocted_object_itself = None
        else:   # job title
            random_company = random.choice(list(self.owner.city.companies))
            random_job_title = random.choice(list(random_company.employees)).__class__.__name__
            concocted_feature_str = random_job_title
            concocted_object_itself = None
        return concocted_feature_str, concocted_object_itself

    def _concoct_home_facet(self, feature_type):
        """Concoct a facet to a belief about a person's home."""
        if feature_type == "home":  # TODO make this more realistic?
            concocted_home = random.choice(list(self.subject.city.dwelling_places))
            concocted_feature_str = concocted_home.name
            concocted_object_itself = concocted_home
        elif feature_type == "home is apartment":
            concocted_feature_str = random.choice(["yes", "no"])
            concocted_object_itself = None
        elif feature_type == "home block":
            random_block = random.choice(list(self.owner.city.blocks))
            concocted_feature_str = str(random_block)
            concocted_object_itself = None
        else:   # home address
            house_number = int(random.random() * 799) + 1
            while house_number < 99:
                house_number += int(random.random() * 500)
            house_number = min(house_number, 799)
            random_street = random.choice(list(self.owner.city.streets))
            if random.random() > 0.5:
                unit_number = int(random.random() * 8.4)
                concocted_feature_str = "{0} {1} (Unit #{2})".format(house_number, random_street, unit_number)
            else:
                concocted_feature_str = "{0} {1}".format(house_number, random_street)
            concocted_object_itself = None
        return concocted_feature_str, concocted_object_itself

    def _mutate_belief_facet(self, feature_type, parent_knowledge_object, facet_being_mutated):
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
        mutation = Mutation(
            parent=parent_knowledge_object, subject=self.subject, source=self.owner,
            mutated_belief_str=str(facet_being_mutated))
        belief_facet_obj = Facet(
            value=mutated_feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=mutation, object_itself=mutated_object_itself
        )
        return belief_facet_obj

    def _mutate_name_belief_facet(self, feature_type, feature_being_mutated_from_str):
        """Mutate a belief facet pertaining to a person's name."""
        if feature_type in ("first name", "middle name"):
            if self.subject.male:
                mutated_feature_str = Names.a_masculine_name_starting_with(letter=feature_being_mutated_from_str[0])
            else:
                mutated_feature_str = Names.a_masculine_name_starting_with(letter=feature_being_mutated_from_str[0])
        else:
            mutated_feature_str = Names.a_surname_starting_with(letter=feature_being_mutated_from_str[0])
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
        if feature_type == "home":  # TODO make this more realistic, e.g., mutate to a relative's house
            # For now, only thing that makes sense is to just do the same thing as concocting a new home
            random_home = random.choice(list(self.subject.city.dwelling_places))
            mutated_feature_str = random_home.name
            mutated_object_itself = random_home
        elif feature_type == "home is apartment":
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
        return mutated_feature_str, mutated_object_itself

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
        # Change the house number
        digits_of_house_number = list(str(facet_being_mutated)[:3])
        for i in xrange(3):
            if random.random() < 0.5:
                change_to_digit = random.randint(1, 2)
            else:
                change_to_digit = random.randint(-2, -1)
            mutated_digit = int(digits_of_house_number[i]) + change_to_digit
            if mutated_digit < 1:
                mutated_digit = 1
            elif mutated_digit > 9:
                mutated_digit = 9
            digits_of_house_number[i] = str(mutated_digit)
        mutated_house_number = ''.join(digits_of_house_number)
        if random.random() < 0.5:
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

    def _transfer_belief_facet(self, feature_type, parent_knowledge_object):
        """Cause a belief facet to change by transference.

        TODO: Have transference be more likely to happen between similar people --
        this requires an operationalized notion of how similar any two people are.
        """
        # TODO make transference of a name feature be more likely for familiar names
        # TODO notion of person similarity should be at play here
        # Find a person to transfer from who is not owner or subject, and ideally who has
        # the same sex as subject
        if any(person for person in self.owner.mind.mental_models if person.male == self.subject.male and
               person is not self.subject and person is not self.owner):
            person_belief_will_transfer_from = next(
                person for person in self.owner.mind.mental_models if person.male == self.subject.male and
                person is not self.subject and person is not self.owner
            )
        else:
            person_belief_will_transfer_from = random.sample(self.owner.mind.mental_models, 1)[0]
        belief_facet_transferred_from = (
            self.owner.mind.mental_models[person_belief_will_transfer_from].get_facet_to_this_belief_of_type(
                feature_type=feature_type
            )
        )
        feature_str = str(belief_facet_transferred_from)
        transferred_object_itself = None  # MAKE SURE THIS ONLY PERTAINS TO APPEARANCE FEATURES
        transference = Transference(
            subject=self.subject, source=self.owner, parent=parent_knowledge_object,
            belief_facet_transferred_from=belief_facet_transferred_from
        )
        belief_facet_obj = Facet(
            value=feature_str, owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=transference, object_itself=transferred_object_itself
        )
        return belief_facet_obj

    def _forget_belief_facet(self, feature_type, parent_knowledge_object):
        """Cause a belief facet to be forgotten."""
        forgetting = Forgetting(subject=self.subject, source=self.owner, parent=parent_knowledge_object)
        # Facets evidenced by a Forgetting should always have an empty string
        # for their value
        belief_facet_obj = Facet(
            value='', owner=self.owner, subject=self.subject,
            feature_type=feature_type, evidence=forgetting, object_itself=None
        )
        return belief_facet_obj

    def _get_true_feature(self, feature_type):
        true_feature_str = str(self.subject.get_feature(feature_type=feature_type))
        return true_feature_str

    def _get_true_feature_object(self, feature_type):
        true_feature_objects = {
            "workplace": self.subject.occupation.company if self.subject.occupation else None
        }
        if feature_type in true_feature_objects:
            return true_feature_objects[feature_type]
        else:
            return None

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

    def get_facet_to_this_belief_of_type(self, feature_type):
        """Return the facet to this mental model of the given type."""
        features = {
            # Names
            "first name": self.first_name,
            "middle name": self.middle_name,
            "last name": self.last_name,
            # Work life
            "workplace": self.occupation.company,
            "job title": self.occupation.job_title,
            "job shift": self.occupation.shift,
            # Home
            "home": self.home.home,
            "home is apartment": self.home.apartment,
            "home block": self.home.block,
            "home address": self.home.address,
            # Appearance
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


class NameBelief(object):
    """A person's mental model of a person's name."""

    def __init__(self, person_model, observation_or_reflection):
        """Initialize a NameBelief object."""
        self.person_model = person_model
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
        if observation_or_reflection.type == "reflection":
            name_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        elif random.random() < config.chance_someones_feature_comes_up_in_conversation_with_them[feature_type]:
            name_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty name facet -- having None for observation_or_reflection will automate this
            name_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return name_facet

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for already correct facets.
        """
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief_facet = self.__dict__[feature]
                if belief_facet is None or not belief_facet.accurate:
                    feature_type = self.attribute_to_belief_type(attribute=feature)
                    # Potentially make it accurate
                    self.__dict__[feature] = (
                        self.person_model.determine_belief_facet(
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
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief_facet = self.__dict__[feature]
                if belief_facet is not None:
                    feature_type_str = belief_facet.feature_type
                else:
                    feature_type_str = ''
                # Determine the chance of memory deterioration, which starts from a base value
                # that gets affected by the person's memory and the strength of the belief facet
                chance_of_memory_deterioration = (
                    config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                    self.person_model.owner.mind.memory /
                    belief_facet.strength
                )
                if random.random() < chance_of_memory_deterioration:
                    if belief_facet is None:
                        parent_knowledge_object = None
                    else:
                        parent_knowledge_object = belief_facet.evidence
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already)
                    deteriorated_belief_facet = self.person_model.deteriorate_belief_facet(
                        feature_type=belief_facet.feature_type,
                        parent_knowledge_object=parent_knowledge_object,
                        current_belief_facet=belief_facet
                    )
                    self.__dict__[feature] = deteriorated_belief_facet

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

    def __init__(self, person_model, observation_or_reflection):
        """Initialize a WorkBelief object."""
        self.person_model = person_model
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
        if observation_or_reflection.type == "reflection":
            work_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        # If you are observing the person working right now, build up a belief about that
        elif (self.person_model.subject.occupation and
              self.person_model.owner.location is self.person_model.subject.occupation.company and
              self.person_model.subject.routine.working):
            work_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty work facet -- having None for observation_or_reflection will automate this
            work_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return work_facet

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for already correct facets.
        """
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief_facet = self.__dict__[feature]
                if belief_facet is None or not belief_facet.accurate:
                    feature_type = self.attribute_to_belief_type(attribute=feature)
                    # Potentially make it accurate
                    self.__dict__[feature] = (
                        self.person_model.determine_belief_facet(
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
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief_facet = self.__dict__[feature]
                if belief_facet is not None:
                    feature_type_str = belief_facet.feature_type
                else:
                    feature_type_str = ''
                # Determine the chance of memory deterioration, which starts from a base value
                # that gets affected by the person's memory and the strength of the belief facet
                chance_of_memory_deterioration = (
                    config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                    self.person_model.owner.mind.memory /
                    belief_facet.strength
                )
                if random.random() < chance_of_memory_deterioration:
                    if belief_facet is None:
                        parent_knowledge_object = None
                    else:
                        parent_knowledge_object = belief_facet.evidence
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already)
                    deteriorated_belief_facet = self.person_model.deteriorate_belief_facet(
                        feature_type=belief_facet.feature_type,
                        parent_knowledge_object=parent_knowledge_object,
                        current_belief_facet=belief_facet
                    )
                    self.__dict__[feature] = deteriorated_belief_facet

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "company": "workplace",
            "job_title": "job title",
            "shift": "job shift"
        }
        return attribute_to_belief_type[attribute]


class HomeBelief(object):
    """A person's mental model of a person's home."""

    def __init__(self, person_model, observation_or_reflection):
        """Initialize a HomeBelief object."""
        self.person_model = person_model
        self.home = self._init_home_facet(  # Will have home object as 'object_itself' attribute on Facet
            feature_type="home", observation_or_reflection=observation_or_reflection
        )
        self.apartment = self._init_home_facet(
            feature_type="home is apartment", observation_or_reflection=observation_or_reflection
        )
        self.block = self._init_home_facet(
            feature_type="home block", observation_or_reflection=observation_or_reflection
        )
        self.address = self._init_home_facet(
            feature_type="home address", observation_or_reflection=observation_or_reflection
        )

    def _init_home_facet(self, feature_type, observation_or_reflection):
        """Establish a belief, or lack of belief, pertaining to a person's home."""
        if observation_or_reflection.type == "reflection":
            home_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        # If you are observing the person at their home, build up a belief about that
        elif self.person_model.owner.location is self.person_model.subject.home:
            home_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=observation_or_reflection
            )
        else:
            # Build empty work facet -- having None for observation_or_reflection will automate this
            home_facet = self.person_model.determine_belief_facet(
                feature_type=feature_type, observation_or_reflection=None
            )
        return home_facet

    def build_up(self, new_observation_or_reflection):
        """Build up the components of this belief by potentially filling in missing information
        and/or repairing wrong information, or else by updating the evidence for already correct facets.
        """
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief_facet = self.__dict__[feature]
                if belief_facet is None or not belief_facet.accurate:
                    feature_type = self.attribute_to_belief_type(attribute=feature)
                    # Potentially make it accurate
                    self.__dict__[feature] = (
                        self.person_model.determine_belief_facet(
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
        for feature in self.__dict__:  # Iterates over all attributes defined in __init__()
            if feature != 'person_model':  # This should be the only one that doesn't resolve to a belief type
                belief_facet = self.__dict__[feature]
                if belief_facet is not None:
                    feature_type_str = belief_facet.feature_type
                else:
                    feature_type_str = ''
                # Determine the chance of memory deterioration, which starts from a base value
                # that gets affected by the person's memory and the strength of the belief facet
                chance_of_memory_deterioration = (
                    config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                    self.person_model.owner.mind.memory /
                    belief_facet.strength
                )
                if random.random() < chance_of_memory_deterioration:
                    if belief_facet is None:
                        parent_knowledge_object = None
                    else:
                        parent_knowledge_object = belief_facet.evidence
                    # Instantiate a new belief facet that represents a deterioration of
                    # the existing one (which itself may be a deterioration already)
                    deteriorated_belief_facet = self.person_model.deteriorate_belief_facet(
                        feature_type=belief_facet.feature_type,
                        parent_knowledge_object=parent_knowledge_object,
                        current_belief_facet=belief_facet
                    )
                    self.__dict__[feature] = deteriorated_belief_facet

    @staticmethod
    def attribute_to_belief_type(attribute):
        """Return the belief type of an attribute."""
        attribute_to_belief_type = {
            "home": "home",
            "apartment": "home is apartment",
            "block": "home block",
            "address": "home address"
        }
        return attribute_to_belief_type[attribute]


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
                        if belief_facet is None or not belief_facet.accurate:
                            feature_type = belief.attribute_to_feature_type(attribute=feature)
                            # Potentially make it accurate
                            belief.__dict__[feature] = (
                                belief.face_belief.person_model.determine_belief_facet(
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
                        else:
                            feature_type_str = ''
                        # Determine the chance of memory deterioration, which starts from a base value
                        # that gets affected by the person's memory and the strength of the belief facet
                        chance_of_memory_deterioration = (
                            config.chance_of_memory_deterioration_on_a_given_timestep[feature_type_str] /
                            self.person_model.owner.mind.memory /
                            belief_facet.strength
                        )
                        if random.random() < chance_of_memory_deterioration:
                            if belief_facet is None:
                                parent_knowledge_object = None
                            else:
                                parent_knowledge_object = belief_facet.evidence
                            # Instantiate a new belief facet that represents a deterioration of
                            # the existing one (which itself may be a deterioration already)
                            deteriorated_belief_facet = self.person_model.deteriorate_belief_facet(
                                feature_type=belief_facet.feature_type,
                                parent_knowledge_object=parent_knowledge_object,
                                current_belief_facet=belief_facet
                            )
                            belief.__dict__[feature] = deteriorated_belief_facet


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

    @staticmethod
    def attribute_to_feature_type(attribute):
        """Return the feature type associated with the attribute."""
        attribute_to_feature_type = {
            "color": "skin color"
        }
        return attribute_to_feature_type[attribute]


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

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a Mouth object.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.size = self.face_belief.person_model.determine_belief_facet(
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

    def __init__(self, face_belief, observation_or_reflection):
        """Initialize a FacialHair style.

        @param face_belief: The FaceBelief of which this belief is a component.
        """
        self.face_belief = face_belief
        self.style = self.face_belief.person_model.determine_belief_facet(
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
    """A facet of one person's belief about a person that pertains to a specific feature.

    This class has a sister class in Face.Feature. While objects of the Feature class represent
    a person's facial feature *as it exists in reality*, with metadata about that feature, a Facet
    represents a person's facial feature *as it is modeled in the belief of a particular
    person*, with metadata about that specific belief.
    """

    def __init__(self, value, owner, subject, feature_type, evidence, object_itself=None):
        """Initialize a Facet object.

        @param value: A string representation of this facet, e.g., 'brown' as the Hair.color
                      attribute this represents.
        @param owner: The person to whom this belief facet belongs.
        @param owner: The person to whom this belief facet pertains.
        @param owner: A string representing the type of feature this facet is about.
        @param evidence: An information object that serves as the evidence for this being a
                         facet of a person's belief.
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
        self.evidence = evidence
        self.evidence.beliefs_evidenced.add(self)
        self.object_itself = object_itself
        # Strength represents the number of times new evidence has
        # supported this belief -- it's used to reduce the chance of a
        # belief facet deteriorating (by dividing the base chance of
        # deterioration by the strength of the facet)
        self.strength = 1

    def __new__(cls, value, owner, subject, feature_type, evidence, object_itself):
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

    def attribute_new_evidence(self, new_evidence):
        """Attribute new evidence that supports this belief facet."""
        self.evidence = new_evidence
        new_evidence.beliefs_evidenced.add(self)
        self.strength += 1
