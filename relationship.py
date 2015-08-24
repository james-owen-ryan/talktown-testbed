from belief import *

# TODO dating and attendant nuances (after break-up, do they go back to previous relationship
# or do they become enemies?)

# TODO make proposing, general romantic progressions better


class Relationship(object):
    """A social and/or romantic relationship between two people."""

    def __init__(self, owner, subject, preceded_by):
        """Initialize a Relationship object.

        @param owner: The person whom this conception of the relationship belongs to.
        @param subject: The other person to whom the conception pertains.
        @param preceded_by: A relationship that preceded this, if any.
        """
        self.type = self.__class__.__name__.lower()
        self.owner = owner
        self.subject = subject
        self.preceded_by = preceded_by
        self.succeeded_by = None
        self.where_they_met = owner.location
        self.when_they_met = owner.game.date
        self.where_they_last_met = owner.location  # Changes as appropriate
        self.when_they_last_met = owner.game.date
        self.total_interactions = 0
        # Set this as the primary relationship owner has with subject
        owner.relationships[subject] = self
        if not preceded_by:
            self.compatibility = self._init_get_compatibility()
            self.charge_increment = self._init_determine_charge_increment()
            self.charge = float(self.charge_increment)
            self.trust = owner.game.config.function_to_determine_trust_charge_boost(charge=self.charge)
            self.spark_increment = self._init_determine_initial_spark_increment()
            self.spark = float(self.spark_increment)
        elif preceded_by:
            preceded_by.succeeded_by = self
            self.compatibility = preceded_by.compatibility
            # Inherit the charge increment and current charge of the preceding Acquaintance
            self.charge_increment = float(preceded_by.charge_increment)
            self.charge = preceded_by.charge
            self.trust = preceded_by.trust
            # Inherit the spark increment and current spark of the preceding Acquaintance
            self.spark_increment = float(preceded_by.spark_increment)
            self.spark = preceded_by.spark
        # Prepare variables that specify the effects that age and job-level differences
        # will have on this relationship's charge and spark values; these are set immediately
        # by update_spark_and_charge_increments_for_new_age_difference() and update_spark_and_
        # charge_increments_for_new_job_level_difference, which will also be called whenever a
        # member of this relationship has a birthday or gets a new occupation
        self.age_difference_effect_on_charge_increment = None
        self.age_difference_effect_on_spark_increment = None
        self.job_level_difference_effect_on_charge_increment = None
        self.job_level_difference_effect_on_spark_increment = None
        self.update_spark_and_charge_increments_for_new_age_difference()
        self.update_spark_and_charge_increments_for_job_level_difference()
        # This attribute records whether the other person has already called the
        # progress_relationship() method of this object on this timestep -- it gets
        # set to True by progress_relationship() and then turned back to False by
        # Game.enact_hi_fi_simulation()
        self.interacted_this_timestep = False

    def _init_get_compatibility(self):
        """Determine the objective compatibility of these two people.

        From source [4]: # People with similar openness, extroversion, and agreeableness are
        more likely to become friends.
        """
        owner, subject = self.owner, self.subject
        # Get absolute difference in o, e, a
        diff = (
            abs(owner.personality.openness_to_experience - subject.personality.openness_to_experience) +
            abs(owner.personality.extroversion - subject.personality.extroversion) +
            abs(owner.personality.agreeableness - subject.personality.agreeableness)
        )
        # Normalize absolute difference to -1.0 to 1.0 compatibility scale (from its natural
        # 0.0-6.0 increasing difference scale, given each personality trait is on the scale -1 to 1)
        normalized_diff = (3.0 - diff) / 3.0
        compatibility = normalized_diff
        return compatibility

    def _init_determine_charge_increment(self):
        """Determine the increment by which the charge of this acquaintance will increase or decrease.

        The charge of an acquaintance increases as one likes the other and sees them often,
        decreases as one dislikes the other and sees them often, and regresses toward 0
        as one does not see each other (regardless of whether they like them). How much
        someone likes someone else is represented by the increment determined here, which is
        a function of their compatibility and one's extroversion and the other's agreeableness --
        following source [4], people higher in extroversion select more friends, while people high
        in agreeableness get selected more often.

        Charge intensity will dynamically get diminished (it gets brought toward 0) as a function of
        the age difference between these two people, as well as a function of the difference in job
        level between the two people. (This happens dynamically because age differences get less
        significant as people grow older, and job levels may change.)
        """
        config = self.owner.game.config
        charge_increment = (
            self.compatibility +
            self.owner.personality.extroversion * config.owner_extroversion_boost_to_charge_multiplier +
            self.subject.personality.agreeableness * config.subject_agreeableness_boost_to_charge_multiplier
        )
        # Reduce charge intensity for sex difference
        if self.owner.male != self.subject.male:
            charge_increment *= config.charge_intensity_reduction_due_to_sex_difference
        return charge_increment

    def _init_determine_initial_spark_increment(self):
        """Determine the initial spark increment for this relationship.

        Spark captures a person's cumulative romantic attraction to another person. The
        increment has a decay rate that is specified in config.py, which means that every
        time these two people spend time together, the spark increment will decrease. For
        this reason, this method only determines the *initial* spark increment, and not the
        a spark increment that will remain static, as the charge increment does.

        A source here for how personality affects attraction is [5].

        TODO: Have this be affected by physical appearance.
        """
        # Make sure this person isn't a family member of owner, is the sex
        # that owner is attracted to, and both are adults
        if self.subject in self.owner.extended_family:
            initial_spark_increment = 0
        elif self.subject.male and not self.owner.attracted_to_men:
            initial_spark_increment = 0
        elif self.subject.female and not self.owner.attracted_to_women:
            initial_spark_increment = 0
        elif not self.owner.adult or not self.subject.adult:
            initial_spark_increment = 0
        else:
            # Affect it according to personalities using source [5]
            initial_spark_increment = 0
            initial_spark_increment += self._affect_initial_spark_increment_by_own_personality()
            initial_spark_increment += self._affect_initial_spark_increment_by_acquaintance_personality()
        return initial_spark_increment

    def _affect_initial_spark_increment_by_own_personality(self):
        """Affect the initial spark increment according to the personality of the acquaintance.

        This method relies on source [5].
        """
        config = self.owner.game.config
        sex_key = 'm' if self.owner.male else 'f'
        effect_from_own_personality = 0
        effect_from_own_personality += (
            self.subject.personality.openness_to_experience * config.openness_boost_to_spark_multiplier[sex_key]
        )
        effect_from_own_personality += (
            self.subject.personality.conscientiousness * config.conscientiousness_boost_to_spark_multiplier[sex_key]
        )
        effect_from_own_personality += (
            self.subject.personality.extroversion * config.extroversion_boost_to_spark_multiplier[sex_key]
        )
        effect_from_own_personality += (
            self.subject.personality.agreeableness * config.agreeableness_boost_to_spark_multiplier[sex_key]
        )
        effect_from_own_personality += (
            self.subject.personality.neuroticism * config.neuroticism_boost_to_spark_multiplier[sex_key]
        )
        return effect_from_own_personality

    def _affect_initial_spark_increment_by_acquaintance_personality(self):
        """Affect the initial spark increment according to the personality of the acquaintance.

        This method relies on source [5].
        """
        config = self.owner.game.config
        sex_key = 'm' if self.owner.male else 'f'
        effect_from_acquaintance_personality = 0
        effect_from_acquaintance_personality += (
            self.subject.personality.openness_to_experience * config.openness_boost_to_spark_multiplier[sex_key]
        )
        effect_from_acquaintance_personality += (
            self.subject.personality.conscientiousness * config.conscientiousness_boost_to_spark_multiplier[sex_key]
        )
        effect_from_acquaintance_personality += (
            self.subject.personality.extroversion * config.extroversion_boost_to_spark_multiplier[sex_key]
        )
        effect_from_acquaintance_personality += (
            self.subject.personality.agreeableness * config.agreeableness_boost_to_spark_multiplier[sex_key]
        )
        effect_from_acquaintance_personality += (
            self.subject.personality.neuroticism * config.neuroticism_boost_to_spark_multiplier[sex_key]
        )
        return effect_from_acquaintance_personality

    def __str__(self):
        """Return string representation."""
        return "{}'s {} with {}".format(self.owner.name, self.type, self.subject.name)

    def update_spark_and_charge_increments_for_new_age_difference(self):
        """Set a new charge increment for this relationship that reflects a new age difference.

        This gets called whenever a member of this relationship has a birthday.
        """
        config = self.owner.game.config
        # Set new age-difference charge effect
        self.age_difference_effect_on_charge_increment = (
            config.function_to_determine_how_age_difference_reduces_charge_intensity(
                age1=self.owner.age, age2=self.subject.age
            )
        )
        # Set new age-difference spark effect
        self.age_difference_effect_on_spark_increment = (
            config.function_to_determine_how_age_difference_reduces_charge_intensity(
                age1=self.owner.age, age2=self.subject.age
            )
        )

    def update_spark_and_charge_increments_for_job_level_difference(self):
        """Set a new charge increment for this relationship that reflects a new job-level difference.

        This gets called whenever a member of this relationship gets a promotion.

        TODO once you implement people getting fired, make sure this gets called whenever that happens.
        """
        config = self.owner.game.config
        owner = self.owner
        subject = self.subject
        if owner.occupation:
            owner_job_level = owner.occupation.level
        elif owner.retired:
            owner_job_level = owner.occupations[-1].level
        else:
            owner_job_level = 0.1
        if subject.occupation:
            subject_job_level = subject.occupation.level
        elif subject.retired:
            subject_job_level = subject.occupations[-1].level
        else:
            subject_job_level = 0.1
        self.job_level_difference_effect_on_charge_increment = (
            config.function_to_determine_how_job_level_difference_reduces_charge_intensity(
                job_level1=owner_job_level, job_level2=subject_job_level
            )
        )
        self.job_level_difference_effect_on_spark_increment = (
            config.function_to_determine_how_job_level_difference_reduces_spark_increment(
                job_level1=owner_job_level, job_level2=subject_job_level
            )
        )

    def progress_relationship(self, missing_days_to_account_for):
        """Increment charge by its increment, and then potentially start a Friendship or Enmity."""
        # Attribute accessing is expensive -- set local variables
        config = self.owner.game.config
        owner = self.owner
        subject = self.subject
        charge = self.charge
        # Update data
        self.total_interactions += 1
        self.where_they_last_met = owner.location  # Changes as appropriate
        self.when_they_last_met = owner.game.date
        # Progress charge, possibly leading to a Friendship or Enmity
        change_to_charge = (
            self.charge_increment * self.age_difference_effect_on_charge_increment *
            self.job_level_difference_effect_on_charge_increment
        )
        change_to_charge *= missing_days_to_account_for
        self.charge += change_to_charge
        if self.type != "friendship" and charge > config.charge_threshold_friendship:
            Friendship(owner=owner, subject=subject, preceded_by=self)
        elif self.type != "enmity" and charge < config.charge_threshold_enmity:
            Enmity(owner=owner, subject=subject, preceded_by=self)
        # Progress trust according to new charge  TODO MAKE TRUST COMPUTATION RICHER
        self.trust = owner.game.config.function_to_determine_trust_charge_boost(charge=self.charge)
        # Progress spark, possibly leading to a
        self.spark_increment *= config.spark_decay_rate
        change_to_spark = (
            self.spark_increment * self.age_difference_effect_on_spark_increment *
            self.job_level_difference_effect_on_spark_increment
        )
        change_to_spark *= missing_days_to_account_for
        self.spark += change_to_spark
        # Check if subject is now owner's new best friend, worst enemy, or love interest; if
        # so, update accordingly
        self._update_social_network()
        # TODO fix currently dumb way of 'proposing' and divorcing
        if not owner.spouse and not subject.spouse and self.spark > 5:
            if owner in subject.relationships:
                if subject.relationships[owner].spark > 5:
                    owner.marry(subject)
            elif owner.spouse in owner.relationships:
                if self.spark > owner.relationships[owner.spouse] * 2:
                    owner.divorce(partner=owner.spouse)
        self.interacted_this_timestep = True
        # Call this method for the subject's own conception of this relationship
        # to update its attributes according to this interaction
        if not subject.relationships[owner].interacted_this_timestep:
            subject.relationships[owner].progress_relationship(
                missing_days_to_account_for=missing_days_to_account_for
            )

    def _update_social_network(self):
        """Check if this person is your new best friend, worst enemy, or love interest; if so, update accordingly."""
        config = self.owner.game.config
        owner, subject = self.owner, self.subject
        charge, spark = self.charge, self.spark
        # Potentially attribute new best friend
        if charge > owner.charge_of_best_friend and subject is not owner.best_friend:
            salience_change = config.salience_increment_from_relationship_change['best friend']
            old_best_friend = owner.best_friend
            if old_best_friend:
                owner.update_salience_of(entity=old_best_friend, change=-salience_change)  # Notice the minus sign
            owner.update_salience_of(entity=subject, change=salience_change)
            owner.best_friend = subject
            owner.charge_of_best_friend = charge
        # Potentially remove now former best friend if charge dropped below 0
        elif subject is owner.best_friend and charge < 0.0:
            salience_change = config.salience_increment_from_relationship_change['best friend']
            owner.update_salience_of(entity=subject, change=-salience_change)
            owner.best_friend = None
            owner.charge_of_best_friend = 0.0
        # Potentially attribute new worst enemy
        if self.charge < owner.charge_of_worst_enemy and subject is not owner.worst_enemy:
            salience_change = config.salience_increment_from_relationship_change['worst enemy']
            old_worst_enemy = owner.worst_enemy
            if old_worst_enemy:
                owner.update_salience_of(entity=old_worst_enemy, change=-salience_change)
            owner.update_salience_of(entity=subject, change=salience_change)
            owner.worst_enemy = subject
            owner.charge_of_worst_enemy = self.charge
        # Potentially remove now former worst enemy if charge climbed above 0
        elif subject is owner.worst_enemy and charge > 0.0:
            salience_change = config.salience_increment_from_relationship_change['worst_enemy']
            owner.update_salience_of(entity=subject, change=-salience_change)
            owner.worst_enemy = None
            owner.charge_of_worst_enemy = 0.0
        # Potentially attribute new love interest
        if self.spark > owner.spark_of_love_interest and subject is not owner.love_interest:
            salience_change = config.salience_increment_from_relationship_change['love interest']
            old_love_interest = owner.love_interest
            if old_love_interest:
                owner.update_salience_of(entity=old_love_interest, change=-salience_change)
            owner.update_salience_of(entity=subject, change=salience_change)
            owner.love_interest = subject
            owner.spark_of_love_interest = self.spark
        # Potentially remove now former love interest if spark dropped below 0
        elif subject is owner.love_interest and spark < 0.0:
            salience_change = config.salience_increment_from_relationship_change['love interest']
            owner.update_salience_of(entity=subject, change=-salience_change)
            owner.love_interest = None
            owner.spark_of_love_interest = 0.0


class Acquaintance(Relationship):
    """One person's conception of their acquaintance with another person."""

    def __init__(self, owner, subject, preceded_by):
        """Initialize an Acquaintance object.

        @param owner: The person whom this conception of the acquaintance belongs to.
        @param subject: The other person to whom the conception pertains.
        @param preceded_by: A Kinship relationship that preceded this, if any.
        """
        super(Acquaintance, self).__init__(owner, subject, preceded_by)
        owner.acquaintances.add(subject)
        if self.owner not in self.subject.relationships:
            Acquaintance(owner=self.subject, subject=self.owner, preceded_by=None)
        # Update the salience value owner has for subject (not vice versa, because relationships
        # are unidirectional)
        owner.update_salience_of(
            subject, change=owner.game.config.salience_increment_from_relationship_change['acquaintance']
        )


class Enmity(Relationship):
    """One person's conception of their enmity with another person."""

    def __init__(self, owner, subject, preceded_by):
        """Initialize a Enmity object.

        @param owner: The person whom this conception of the enmity belongs to.
        @param subject: The other person to whom the conception pertains.
        @param preceded_by: An Acquaintance relationship that preceded this.
        """
        super(Enmity, self).__init__(owner, subject, preceded_by)
        owner.acquaintances.remove(subject)
        owner.enemies.add(subject)
        # Update the salience value owner has for subject (not vice versa, because relationships
        # are unidirectional)
        owner.update_salience_of(
            subject, change=owner.game.config.salience_increment_from_relationship_change['enemy']
        )


class Friendship(Relationship):
    """One person's conception of their friendship with another person."""

    def __init__(self, owner, subject, preceded_by):
        """Initialize a Friendship object.

        @param owner: The person whom this conception of the enmity belongs to.
        @param subject: The other person to whom the conception pertains.
        @param preceded_by: An Acquaintance relationship that preceded this, if any.
        """
        super(Friendship, self).__init__(owner, subject, preceded_by)
        owner.acquaintances.remove(subject)
        owner.friends.add(subject)
        # Update the salience value owner has for subject (not vice versa, because relationships
        # are unidirectional)
        owner.update_salience_of(
            subject, change=owner.game.config.salience_increment_from_relationship_change['friend']
        )


class Romance(Relationship):
    """One person's conception of their romantic relationship with another person."""

    def __init__(self, owner, subject, preceded_by):
        """Initialize a Friendship object.

        @param owner: The person whom this conception of the enmity belongs to.
        @param subject: The other person to whom the conception pertains.
        @param preceded_by: A different type of relationship that preceded this, if any.
        """
        super(Romance, self).__init__(owner, subject, preceded_by)
        # Update the salience value owner has for subject (not vice versa, because relationships
        # are unidirectional)
        owner.update_salience_of(
            subject, change=owner.game.config.salience_increment_from_relationship_change['romance']
        )
        owner.significant_other = subject
        # TODO AUTOMATICALLY CALL SUBJECT.ROMANCE RIGHT? ROMANCE CAN'T BE UNIDIRECTIONAL, right?