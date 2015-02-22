import random
import heapq
from corpora import Names
from config import Config
from event import *
from name import Name


class Person(object):
    """A person living in a city of a gameplay instance."""

    def __init__(self, game, birth):
        """Initialize a Person object."""
        # Set location and gameplay instance
        self.game = game
        self.city = game.city
        if birth:
            # Set parents
            self.biological_mother = birth.biological_mother
            self.mother = birth.mother
            self.biological_father = birth.biological_father
            self.father = birth.father
            # Set year of birth
            self.birth_year = birth.year
        else:
            # PersonExNihilo
            self.biological_mother = None
            self.mother = None
            self.biological_father = None
            self.father = None
            self.birth_year = None  # Gets set by PersonExNihilo.__init__()
        # Set sex
        self.male, self.female = self._init_sex()
        self.tag = ''  # Allows players to tag characters with arbitrary strings
        # Set misc attributes
        self.alive = True
        self.death_year = None
        # Set biological characteristics
        self.infertile = self._init_fertility(male=self.male, config=self.game.config)
        self.attracted_to_men, self.attracted_to_women = (
            self._init_sexuality(male=self.male, config=self.game.config)
        )
        # Set personality
        self.big_5_o, self.big_5_c, self.big_5_e, self.big_5_a, self.big_5_n = (
            self._init_personality()
        )
        # Set mental attributes
        self.memory = self._init_memory()
        # Prepare name attributes that get set by event.Birth._name_baby() (or PersonExNihilo.init_name())
        self.first_name = None
        self.middle_name = None
        self.last_name = None
        self.suffix = None
        self.maiden_name = None
        self.named_for = (None, None)  # From whom first and middle name originate, respectively
        # Prepare familial attributes that get populated by self.init_familial_attributes()
        self.ancestors = set()  # Biological only
        self.descendants = set()  # Biological only
        self.immediate_family = set()
        self.extended_family = set()
        self.greatgrandparents = set()
        self.grandparents = set()
        self.aunts = set()
        self.uncles = set()
        self.siblings = set()
        self.full_siblings = set()
        self.half_siblings = set()
        self.brothers = set()
        self.full_brothers = set()
        self.half_brothers = set()
        self.sisters = set()
        self.full_sisters = set()
        self.half_sisters = set()
        self.cousins = set()
        self.kids = set()
        self.sons = set()
        self.daughters = set()
        self.nephews = set()
        self.nieces = set()
        self.grandchildren = set()
        self.grandsons = set()
        self.granddaughters = set()
        self.greatgrandchildren = set()
        self.bio_parents = set()
        self.bio_grandparents = set()
        self.bio_siblings = set()
        self.bio_full_siblings = set()
        self.bio_half_siblings = set()
        self.bio_brothers = set()
        self.bio_full_brothers = set()
        self.bio_half_brothers = set()
        self.bio_sisters = set()
        self.bio_full_sisters = set()
        self.bio_half_sisters = set()
        self.bio_immediate_family = set()
        self.bio_greatgrandparents = set()
        self.bio_uncles = set()
        self.bio_aunts = set()
        self.bio_cousins = set()
        self.bio_nephews = set()
        self.bio_nieces = set()
        self.bio_ancestors = set()
        self.bio_extended_family = set()
        # Set familial attributes; update those of family members
        self._init_familial_attributes()
        self._init_update_familial_attributes_of_family_members()
        # Prepare attributes representing this person's interpersonal relationships.
        self.spouse = None
        self.widowed = False
        self.friends = set()
        self.known_people = set()
        self.known_by = set()
        self.first_met = {}
        self.last_saw = {}
        self.talked_to_this_year = set()
        self.befriended_this_year = set()
        self.sexual_partners = set()
        # Prepare attributes representing events in this person's life
        self.birth = birth
        self.marriage = None
        self.marriages = []
        self.divorces = []
        self.moves = []  # From one home to another
        self.name_changes = []
        self.building_commissions = []  # Constructions of houses or buildings that they commissioned
        self.departure = None  # Leaving the city, i.e., leaving the simulation
        self.death = None
        # Set and prepare attributes pertaining to business affairs
        self.money = self._init_money()
        self.occupation = None
        self.occupations = []
        self.former_contractors = set()
        self.retired = False
        # Prepare misc attributes that get set by other methods
        self.home = None

    @staticmethod
    def _init_sex():
        """Determine the sex of this person."""
        if random.random() < 0.5:
            male = True
            female = False
        else:
            male = False
            female = True
        return male, female

    @staticmethod
    def _init_fertility(male, config):
        """Determine whether this person will be able to reproduce."""
        x = random.random()
        if male and x < config.male_infertility_rate:
            infertile = True
        elif not male and x < config.female_infertility_rate:
            infertile = True
        else:
            infertile = False
        return infertile

    @staticmethod
    def _init_sexuality(male, config):
        """Determine this person's sexuality."""
        x = random.random()
        if x < config.homosexuality_incidence:
            # Homosexual
            if male:
                attracted_to_men = True
                attracted_to_women = False
            else:
                attracted_to_men = False
                attracted_to_women = True
        elif x < config.homosexuality_incidence+config.bisexuality_incidence:
            # Bisexual
            attracted_to_men = True
            attracted_to_women = True
        elif x < config.homosexuality_incidence+config.bisexuality_incidence+config.asexuality_incidence:
            # Asexual
            attracted_to_men = True
            attracted_to_women = True
        else:
            # Heterosexual
            if male:
                attracted_to_men = False
                attracted_to_women = True
            else:
                attracted_to_men = True
                attracted_to_women = False
        return attracted_to_men, attracted_to_women

    def _init_personality(self):
        """Determine this person's Big Five disposition.

        TODO: Have this affected by a person's sex."""
        openness_to_experience = self._init_big_5_o()
        conscientiousness = self._init_big_5_c()
        extroversion = self._init_big_5_e()
        agreeableness = self._init_big_5_a()
        neuroticism = self._init_big_5_n()
        return openness_to_experience, conscientiousness, extroversion, agreeableness, neuroticism

    def _init_big_5_o(self):
        """Initialize a value for the Big Five personality trait 'openness to experience'."""
        config = self.game.config
        if random.random() < config.big_5_o_heritability:
            # Inherit this trait (with slight variance)
            takes_after = random.choice([self.father, self.mother])
            openness_to_experience = random.normalvariate(
                takes_after.openness_to_experience, config.big_5_heritability_sd
            )
        else:
            # Generate from the population mean
            openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience < config.big_5_floor:
            openness_to_experience = -1.0
        elif openness_to_experience > config.big_5_cap:
            openness_to_experience = 1.0
        return openness_to_experience

    def _init_big_5_c(self):
        """Initialize a value for the Big Five personality trait 'conscientiousness'."""
        config = self.game.config
        if random.random() < config.big_5_c_heritability:
            takes_after = random.choice([self.father, self.mother])
            conscientiousness = random.normalvariate(
                takes_after.conscientiousness, config.big_5_heritability_sd
            )
        else:
            conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness < config.big_5_floor:
            conscientiousness = -1.0
        elif conscientiousness > config.big_5_cap:
            conscientiousness = 1.0
        return conscientiousness

    def _init_big_5_e(self):
        """Initialize a value for the Big Five personality trait 'extroversion'."""
        config = self.game.config
        if random.random() < config.big_5_e_heritability:
            takes_after = random.choice([self.father, self.mother])
            extroversion = random.normalvariate(
                takes_after.extroversion, config.big_5_heritability_sd
            )
        else:
            extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion < config.big_5_floor:
            extroversion = -1.0
        elif extroversion > config.big_5_cap:
            extroversion = 1.0
        return extroversion

    def _init_big_5_a(self):
        """Initialize a value for the Big Five personality trait 'agreeableness'."""
        config = self.game.config
        if random.random() < config.big_5_a_heritability:
            takes_after = random.choice([self.father, self.mother])
            agreeableness = random.normalvariate(
                takes_after.agreeableness, config.big_5_heritability_sd
            )
        else:
            agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness < config.big_5_floor:
            agreeableness = -1.0
        elif agreeableness > config.big_5_cap:
            agreeableness = 1.0
        return agreeableness

    def _init_big_5_n(self):
        """Initialize a value for the Big Five personality trait 'neuroticism'."""
        config = self.game.config
        if random.random() < config.big_5_n_heritability:
            takes_after = random.choice([self.father, self.mother])
            neuroticism = random.normalvariate(
                takes_after.neuroticism, config.big_5_heritability_sd
            )
        else:
            neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism < config.big_5_floor:
            neuroticism = -1.0
        elif neuroticism > config.big_5_cap:
            neuroticism = 1.0
        return neuroticism

    def _init_memory(self):
        """Determine a person's base memory capability, given their parents'."""
        config = self.game.config
        if random.random() < config.memory_heritability:
            takes_after = random.choice([self.mother, self.father])
            memory = random.normalvariate(takes_after.memory, config.memory_heritability_sd)
        else:
            memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if self.male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor_at_birth:
            memory = config.memory_floor_at_birth
        return memory

    def _init_familial_attributes(self):
        """Populate lists representing this person's family members."""
        self._init_immediate_family()
        self._init_biological_immediate_family()
        self._init_extended_family()
        self._init_biological_extended_family()

    def _init_immediate_family(self):
        """Populate lists representing this person's (legal) immediate family."""
        self.grandparents = self.father.parents | self.mother.parents
        self.siblings = self.father.kids | self.mother.kids
        self.full_siblings = self.father.kids & self.mother.kids
        self.half_siblings = self.father.kids ^ self.mother.kids
        self.brothers = self.father.sons | self.mother.sons
        self.full_brothers = self.father.sons & self.mother.sons
        self.half_brothers = self.father.sons ^ self.mother.sons
        self.sisters = self.father.daughters | self.mother.daughters
        self.full_sisters = self.father.daughters & self.mother.daughters
        self.half_sisters = self.father.daughters ^ self.mother.daughters
        self.immediate_family = self.grandparents | self.parents | self.siblings

    def _init_biological_immediate_family(self):
        """Populate lists representing this person's immediate."""
        self.bio_parents = self.biological_mother, self.biological_father,
        self.bio_grandparents = self.biological_father.parents | self.biological_mother.parents
        self.bio_siblings = self.biological_father.kids | self.biological_mother.kids
        self.bio_full_siblings = self.biological_father.kids & self.biological_mother.kids
        self.bio_half_siblings = self.biological_father.kids ^ self.biological_mother.kids
        self.bio_brothers = self.biological_father.sons | self.biological_mother.sons
        self.bio_full_brothers = self.biological_father.sons & self.biological_mother.sons
        self.bio_half_brothers = self.biological_father.sons ^ self.biological_mother.sons
        self.bio_sisters = self.biological_father.daughters | self.biological_mother.daughters
        self.bio_full_sisters = self.biological_father.daughters & self.biological_mother.daughters
        self.bio_half_sisters = self.biological_father.daughters ^ self.biological_mother.daughters
        self.bio_immediate_family = self.bio_grandparents | self.bio_parents | self.bio_siblings

    def _init_extended_family(self):
        """Populate lists representing this person's (legal) extended family."""
        self.greatgrandparents = self.father.grandparents | self.mother.grandparents
        self.uncles = self.father.brothers | self.mother.brothers
        self.aunts = self.father.sisters | self.mother.sisters
        self.cousins = self.father.nieces | self.father.nephews | self.mother.nieces | self.mother.nephews
        self.nephews = self.father.grandsons | self.mother.grandsons
        self.nieces = self.father.granddaughters | self.mother.granddaughters
        self.ancestors = self.father.ancestors | self.mother.ancestors | self.parents
        self.extended_family = (
            self.greatgrandparents | self.immediate_family | self.uncles | self.aunts |
            self.cousins | self.nieces | self.nephews
        )

    def _init_biological_extended_family(self):
        """Populate lists representing this person's (legal) extended family."""
        self.bio_greatgrandparents = self.father.grandparents | self.mother.grandparents
        self.bio_uncles = self.father.brothers | self.mother.brothers
        self.bio_aunts = self.father.sisters | self.mother.sisters
        self.bio_cousins = self.father.nieces | self.father.nephews | self.mother.nieces | self.mother.nephews
        self.bio_nephews = self.father.grandsons | self.mother.grandsons
        self.bio_nieces = self.father.granddaughters | self.mother.granddaughters
        self.bio_ancestors = self.father.ancestors | self.mother.ancestors | self.parents
        self.bio_extended_family = (
            self.bio_greatgrandparents | self.bio_immediate_family | self.bio_uncles | self.bio_aunts |
            self.bio_cousins | self.bio_nieces | self.bio_nephews
        )

    def _init_update_familial_attributes_of_family_members(self):
        """Update familial attributes of myself and family members."""
        for member in self.immediate_family:
            member.immediate_family.add(self)
        for member in self.extended_family:
            member.extended_family.add(self)
        # Update for gender-specific familial attributes
        if self.male:
            for g in self.greatgrandparents:
                g.greatgrandsons.add(self)
            for g in self.grandparents:
                g.grandsons.add(self)
            for p in self.parents:
                p.sons.add(self)
            for u in self.uncles:
                u.nephews.add(self)
            for a in self.aunts:
                a.nephews.add(self)
            for b in self.full_brothers:
                b.full_brothers.add(self)
                b.brothers.add(self)
            for s in self.full_sisters:
                s.full_brothers.add(self)
                s.brothers.add(self)
            for b in self.half_brothers:
                b.half_brothers.add(self)
                b.brothers.add(self)
            for s in self.half_sisters:
                s.half_brothers.add(self)
                s.brothers.add(self)
        elif self.female:
            for g in self.greatgrandparents:
                g.greatgranddaughters.add(self)
            for g in self.grandparents:
                g.granddaughters.add(self)
            for p in self.parents:
                p.daughters.add(self)
            for u in self.uncles:
                u.nieces.add(self)
            for a in self.aunts:
                a.nieces.add(self)
            for b in self.full_brothers:
                b.full_sisters.add(self)
                b.sisters.add(self)
            for s in self.full_sisters:
                s.full_sisters.add(self)
                s.sisters.add(self)
            for b in self.half_brothers:
                b.half_sisters.add(self)
                b.sisters.add(self)
            for s in self.half_sisters:
                s.half_sisters.add(self)
                s.sisters.add(self)
        # Update for non-gender-specific familial attributes
        for g in self.greatgrandparents:
            g.greatgrandchildren.add(self)
        for g in self.grandparents:
            g.grandchildren.add(self)
        for p in self.parents:
            p.kids.add(self)
        for fs in self.full_siblings:
            fs.siblings.add(self)
            fs.full_siblings.add(self)
        for hs in self.half_siblings:
            hs.siblings.add(self)
            hs.half_siblings.add(self)
        for c in self.cousins:
            c.cousins.add(self)

    def _init_money(self):
        """Determine how much money this person has to start with."""
        return 0

    @property
    def age(self):
        """Return whether this person is at least 18 years old."""
        return self.game.year - self.birth_year

    @property
    def adult(self):
        """Return whether this person is at least 18 years old."""
        return self.age >= 18

    @property
    def present(self):
        """Return whether the person is alive and in the city."""
        if self.alive and not self.departure:
            return True
        else:
            return False

    @property
    def parents(self):
        """Return parents.

        The @property decorator is used so that this attribute can be dynamic to adoption.
        """
        return self.mother, self.father,

    @property
    def next_of_kin(self):
        """Return next of kin.

        A person's next of kin will make decisions about their estate and
        so forth upon the person's death.
        """
        assert not self.alive, "{} is dead, but a request was made for his next of kin."
        if self.spouse and self.spouse.present:
            next_of_kin = self.spouse
        elif self.mother and self.mother.present:
            next_of_kin = self.mother
        elif self.father and self.father.present:
            next_of_kin = self.father
        elif any(k for k in self.kids if k.adult and k.present):
            next_of_kin = next(k for k in self.kids if k.adult and k.present)
        elif any(f for f in self.immediate_family if f.adult and f.present):
            next_of_kin = next(f for f in self.immediate_family if f.adult and f.present)
        elif any(f for f in self.extended_family if f.adult and f.present):
            next_of_kin = next(f for f in self.extended_family if f.adult and f.present)
        elif any(f for f in self.friends if f.adult and f.present):
            next_of_kin = next(f for f in self.friends if f.adult and f.present)
        else:
            next_of_kin = random.choice(
                [r for r in self.city.residents if r.adult and r.present]
            )
        return next_of_kin

    @property
    def full_name(self):
        """Return a person's full name."""
        full_name = "{} {} {} {}".format(
            self.first_name.rep, self.middle_name.rep, self.last_name.rep, self.suffix
        )
        return full_name

    @property
    def full_name_without_suffix(self):
        """Return a person's full name sans suffix.

        This is used to determine whether a child has the same full name as their parent,
        which would necessitate them getting a suffix of their own to disambiguate.
        """
        full_name = "{} {} {} {}".format(
            self.first_name.rep, self.middle_name.rep, self.last_name.rep, self.suffix
        )
        return full_name

    @property
    def name(self):
        """Return a person's name."""
        name = "{} {} {}".format(self.first_name.rep, self.last_name.rep, self.suffix.rep)
        return name

    @property
    def nametag(self):
        """Return a person's name, appended with their tag, if any."""
        nametag = "{} {}".format(self.name, self.tag)
        return nametag

    @property
    def queer(self):
        """Return whether this person is not heterosexual."""
        if self.male and self.attracted_to_men:
            queer = True
        elif self.female and self.attracted_to_women:
            queer = True
        elif not self.attracted_to_men and not self.attracted_to_women:
            queer = True
        else:
            queer = False
        return queer

    def relation_to_me(self, person):
        """Return the primary (immediate) familial relation to another person, if any."""
        if person in self.greatgrandparents:
            if person.male:
                relation = 'Greatgrandfather'
            else:
                relation = 'Greatgrandmother'
        elif person in self.grandparents:
            if person.male:
                relation = 'Grandfather'
            else:
                relation = 'Grandmother'
        elif person is self.father:
            relation = 'Father'
        elif person is self.mother:
            relation = 'Mother'
        elif person in self.aunts:
            relation = 'Aunt'
        elif person in self.uncles:
            relation = 'Uncle'
        elif person in self.brothers:
            relation = 'Brother'
        elif person in self.sisters:
            relation = 'Sister'
        elif person in self.cousins:
            relation = 'Cousin'
        elif person in self.sons:
            relation = 'Son'
        elif person in self.daughters:
            relation = 'Daughter'
        elif person in self.nephews:
            relation = 'Nephew'
        elif person in self.nieces:
            relation = 'Niece'
        else:
            relation = None
        return relation

    def attracted_to(self, other_person):
        """Return whether this person is attracted to other_person.

        TODO: Have this be affected by other considerations, including appearance.
        """
        if other_person.male and self.attracted_to_men:
            attracted = True
        elif other_person.female and self.attracted_to_women:
            attracted = True
        else:
            attracted = False
        if other_person in self.extended_family:
            attracted = False
        return attracted

    def change_name(self, new_last_name, reason):
        """Change this person's (official) name."""
        lawyer = self.contract_person_of_certain_occupation(occupation=Lawyer)
        NameChange(subject=self, new_last_name=new_last_name, reason=reason)

    def marry(self, partner):
        """Marry partner."""
        assert(self.present and partner.present), "{} tried to marry {}, but one of them is dead or departed."
        Marriage(subjects=(self, partner))

    def divorce(self, partner):
        """Divorce partner."""
        assert(self.alive and partner.alive), "{} tried to divorce {}, but one of them is dead."
        assert(partner is self.spouse and partner.spouse is self), (
            "{} tried to divorce {}, whom they are not married to.".format(self.name, partner.name)
        )
        # The soon-to-be divorcees will decide together which lawyer to hire, because they are
        # technically still married (and spouses are considered as part of this method call)
        lawyer = self.contract_person_of_certain_occupation(occupation=Lawyer)
        Divorce(subjects=(self, partner), lawyer=lawyer)

    def give_birth(self):
        """Select a doctor and go to the hospital to give birth."""
        doctor = self.contract_person_of_certain_occupation(occupation=Doctor)
        doctor.deliver_baby(mother=self)

    def die(self, cause_of_death):
        """Die and get interred at the local cemetery."""
        mortician = self.next_of_kin.contract_person_of_certain_occupation(occupation=Mortician)
        mortician.inter_body(deceased=self, cause_of_death=cause_of_death)

    def move(self, new_home, reason):
        """Move to an apartment or home."""
        Move(subject=self, new_home=new_home, reason=reason)

    def pay(self, payee, amount):
        """Pay someone (for services rendered)."""
        if self.spouse:
            self.marriage.money -= amount
        else:
            self.money -= amount
        payee.money += amount

    def depart_city(self):
        """Depart the city (and thus the simulation), never to return."""
        Departure(subject=self)

    def contract_person_of_certain_occupation(self, occupation):
        """Find a person of a certain occupation.

        Currently, a person scores all the potential hires in town and then selects
        one of the top three. TODO: Probabilistically select from all potential hires
        using the scores to derive likelihoods of selecting each.
        """
        # If you or your spouse practice this occupation, DIY
        if isinstance(self.occupation, occupation):
            choice = self
        elif self.spouse and isinstance(self.spouse.occupation, occupation):
            choice = self.spouse
        # Otherwise, pick from the various people in town who do practice this occupation
        else:
            potential_hire_scores = self._rate_all_potential_contractors_of_certain_occupation(occupation=occupation)
            # Pick from top three
            top_three_choices = heapq.nlargest(3, potential_hire_scores, key=potential_hire_scores.get)
            if random.random() < 0.6:
                choice = top_three_choices[0]
            elif random.random() < 0.9:
                choice = top_three_choices[1]
            else:
                choice = top_three_choices[2]
        return choice

    def _rate_all_potential_contractors_of_certain_occupation(self, occupation):
        """Score all potential hires of a certain occupation."""
        pool = self.city.workers_of_trade(occupation)
        scores = {}
        for person in pool:
            my_score = self._rate_potential_contractor_of_certain_occupation(person=person)
            if self.spouse:
                spouse_score = self.spouse._rate_potential_contractor_of_certain_occupation(person=person)
            else:
                spouse_score = 0
            scores[person] = my_score + spouse_score
        return scores

    def _rate_potential_contractor_of_certain_occupation(self, person):
        """Score a potential hire of a certain occupation, with preference to family, friends, former hires.

        TODO: Have this be affected by personality (beyond what being a friend captures).
        """
        score = 0
        # Rate according to social reasons
        if person in self.immediate_family:
            score += self.game.config.preference_to_contract_immediate_family
        elif person in self.extended_family:  # elif because immediate family is subset of extended family
            score += self.game.config.preference_to_contract_extended_family
        if person in self.friends:
            score += self.game.config.preference_to_contract_friend
        elif person in self.known_people:
            score += self.game.config.preference_to_contract_known_person
        if person in self.former_contractors:
            score += self.game.config.preference_to_contract_former_contract
        # Multiply score according to this person's experience in this occupation
        score *= person.game.config.function_to_derive_score_multiplier_from_years_experience(
            years_experience=person.occupation.years_experience
        )
        return score

    def secure_home(self):
        """Find a home to move into.

        The person (and their spouse, if any) will decide between all the vacant
        homes and vacant lots (upon which they would build a new home) in the city.
        """
        chosen_home_or_lot = self._choose_vacant_home_or_vacant_lot()
        if chosen_home_or_lot:
            if isinstance(chosen_home_or_lot, Lot):
                # A vacant lot was chosen, so build
                home_to_move_into = self._commission_construction_of_a_house(lot=chosen_home_or_lot)
            else:
                # A vacant home was chosen
                home_to_move_into = self._purchase_home(home=chosen_home_or_lot)
        else:
            home_to_move_into = None  # The city is full; this will spark a departure
        return home_to_move_into

    def _commission_construction_of_a_house(self, lot):
        """Build a house to move into."""
        architect = self.contract_person_of_certain_occupation(occupation=Architect)
        if self.spouse:
            clients = {self, self.spouse}
        else:
            clients = {self}
        return architect.construct_house(clients=clients, lot=lot)

    def _purchase_home(self, home):
        """Purchase a house or apartment unit, with the help of a realtor."""
        realtor = self.contract_person_of_certain_occupation(occupation=Realtor)
        if self.spouse:
            clients = {self, self.spouse}
        else:
            clients = {self}
        return realtor.sell_home(clients=clients, home=home)

    def _choose_vacant_home_or_vacant_lot(self):
        """Choose a vacant home to move into or a vacant lot to build on.

        Currently, a person scores all the vacant homes/lots in town and then selects
        one of the top three. TODO: Probabilistically select from all homes/lots using the
        scores to derive likelihoods of selecting each.
        """
        home_and_lot_scores = self._rate_all_vacant_homes_and_vacant_lots()
        if len(home_and_lot_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, home_and_lot_scores, key=home_and_lot_scores.get)
            if random.random() < 0.6:
                choice = top_three_choices[0]
            elif random.random() < 0.9:
                choice = top_three_choices[1]
            else:
                choice = top_three_choices[2]
        elif home_and_lot_scores:
            choice = home_and_lot_scores[0]
        else:
            choice = None
        return choice

    def _rate_all_vacant_homes_and_vacant_lots(self):
        """Find a home to move into in a chosen neighborhood.

        By this method, a person appraises every vacant home and lot in the city for
        how much they would like to move or build there, given considerations to the people
        that live nearby it (this reasoning via self.score_potential_home_or_lot()). There is
        a penalty that makes people less willing to build a home on a vacant lot than to move
        into a vacant home.
        """
        scores = {}
        for home in self.city.vacant_homes:
            my_score = self._rate_potential_lot(lot=home.lot)
            if self.spouse:
                spouse_score = self.spouse.score_potential_home_or_lot(home_or_lot=home)
            else:
                spouse_score = 0
            scores[home] = my_score + spouse_score
        for lot in self.city.vacant_lots:
            my_score = self._rate_potential_lot(lot=lot)
            if self.spouse:
                spouse_score = self.spouse.score_potential_home_or_lot(home_or_lot=lot)
            else:
                spouse_score = 0
            scores[lot] = (
                (my_score + spouse_score) * self.game.config.penalty_for_having_to_build_a_home_vs_buying_one
            )
        return scores

    def _rate_potential_lot(self, lot):
        """Score the desirability of living at the location of a lot.

        TODO: Other considerations here.
        """
        config = self.game.config
        desire_to_live_near_family = self._determine_desire_to_move_near_family()
        # Score home for its proximity to family (either positively or negatively, depending); only
        # consider family members that are alive, in town, and not living with you already (i.e., kids)
        relatives_in_town = {
            f for f in self.extended_family if f.present and f.home is not self.home
        }
        score = 0
        for relative in relatives_in_town:
            relation_to_me = self.relation_to_me(person=relative)
            pull_toward_someone_of_that_relation = config.pull_to_live_near_family[relation_to_me]
            dist = relative.home.lot.get_dist_to(lot) + 1  # Since we're dividing by this next
            score += (desire_to_live_near_family * pull_toward_someone_of_that_relation) / dist
        # Score for proximity to friends (only positively)
        for friend in self.friends:
            dist = friend.home.lot.get_dist_to(lot) + 1
            score += config.pull_to_live_near_a_friend / dist
        return score

    def _determine_desire_to_move_near_family(self):
        """Decide how badly you want to move near/away from family.

        Currently, this relies on immutable personality traits, but eventually
        this desire could be made dynamic according to life events, etc.
        """
        config = self.game.config
        # People with personality C-, O+ most likely to leave home (source [1])
        base_desire_to_live_near_family = config.desire_to_live_near_family_base
        desire_to_live_near_family = self.big_5_c
        desire_to_live_away_from_family = self.big_5_o
        final_desire_to_live_near_family = (
            base_desire_to_live_near_family + desire_to_live_near_family - desire_to_live_away_from_family
        )
        if final_desire_to_live_near_family < config.desire_to_live_near_family_floor:
            final_desire_to_live_near_family = config.desire_to_live_near_family_floor
        elif final_desire_to_live_near_family > config.desire_to_live_near_family_cap:
            final_desire_to_live_near_family = config.desire_to_live_near_family_cap
        return final_desire_to_live_near_family


class PersonExNihilo(Person):
    """A person who is generated from nothing, i.e., who has no parents.

    This is a subclass of Person whose objects are people that enter the simulation
    from outside the city, either as city founders or as new hires for open positions
    that could not be filled by anyone currently in the city. Because these people don't
    have parents, a subclass is needed to override any attributes or methods that rely
    on inheritance.
    """

    def __init__(self, game, birth_year, assigned_male=False, assigned_female=False):
        super(PersonExNihilo, self).__init__(game, birth=None)
        # Overwrite birth year set by Person.__init__()
        self.birth_year = birth_year
        # Potentially overwrite sex set by Person.__init__()
        if assigned_male:
            self.male = True
            self.female = False
        elif assigned_female:
            self.male = False
            self.female = True
        # Potentially overwrite sexuality set by Person.__init__() (to ensure interest in opposite
        # sex consistent with marriages that are initiated in a top-down way during world gen)
        if self.game.year < self.game.config.year_city_gets_founded:
            if self.male:
                self.attracted_to_women = True
            elif self.female:
                self.attracted_to_men = True
        # Since they don't have a parent to name them, generate a name for this person
        self.first_name, self.middle_name, self.last_name, self.suffix = (
            self.init_name()
        )
        self.maiden_name = self.last_name
        self.named_for = None

    def init_name(self):
        """Generate a name for a primordial person who has no parents."""
        if self.male:
            first_name = Name(rep=Names.a_masculine_name(), progenitor=self, conceived_by=None)
            middle_name = Name(rep=Names.a_masculine_name(), progenitor=self, conceived_by=None)
        else:
            first_name = Name(rep=Names.a_feminine_name(), progenitor=self, conceived_by=None)
            middle_name = Name(rep=Names.a_feminine_name(), progenitor=self, conceived_by=None)
        last_name = Name(rep=Names.any_surname(), progenitor=self, conceived_by=None)
        suffix = ''
        return first_name, middle_name, last_name, suffix

    def _init_big_5_o(self):
        """Initialize a value for the Big Five personality trait 'openness to experience'."""
        config = self.game.config
        openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience < config.big_5_floor:
            openness_to_experience = -1.0
        elif openness_to_experience > config.big_5_cap:
            openness_to_experience = 1.0
        return openness_to_experience

    def _init_big_5_c(self):
        """Initialize a value for the Big Five personality trait 'conscientiousness'."""
        config = self.game.config
        conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness < config.big_5_floor:
            conscientiousness = -1.0
        elif conscientiousness > config.big_5_cap:
            conscientiousness = 1.0
        return conscientiousness

    def _init_big_5_e(self):
        """Initialize a value for the Big Five personality trait 'extroversion'."""
        config = self.game.config
        extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion < config.big_5_floor:
            extroversion = -1.0
        elif extroversion > config.big_5_cap:
            extroversion = 1.0
        return extroversion

    def _init_big_5_a(self):
        """Initialize a value for the Big Five personality trait 'agreeableness'."""
        config = self.game.config
        agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness < config.big_5_floor:
            agreeableness = -1.0
        elif agreeableness > config.big_5_cap:
            agreeableness = 1.0
        return agreeableness

    def _init_big_5_n(self):
        """Initialize a value for the Big Five personality trait 'neuroticism'."""
        config = self.game.config
        neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism < config.big_5_floor:
            neuroticism = -1.0
        elif neuroticism > config.big_5_cap:
            neuroticism = 1.0
        return neuroticism

    def _init_memory(self):
        """Determine this person's base memory capability, which will deteriorate with age."""
        config = self.game.config
        memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if self.male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor:
            memory = config.memory_floor
        return memory

    def _init_familial_attributes(self):
        """Do nothing because a PersonExNihilo has no family at the time of being generated.."""
        pass

    def _init_update_familial_attributes_of_family_members(self):
        """Do nothing because a PersonExNihilo has no family at the time of being generated.."""
        pass

    def _init_money(self):
        """Determine how much money this person has to start with."""
        return self.game.config.amount_of_money_generated_people_from_outside_city_start_with