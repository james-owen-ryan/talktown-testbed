import random
import heapq
from corpora import Names
from event import *
from config import Config


class Person(object):
    """A person living in a city of a gameplay instance."""

    def __init__(self, mother, father, birth_year=None, assigned_male=False, assigned_female=False):
        """Construct a Person object."""
        # Set location and gameplay instance
        self.game = self.mother.city.game
        self.city = self.mother.city
        # Set parents
        self.mother = mother
        self.father = father
        # Set year of birth
        if birth_year:
            self.birth_year = birth_year
        else:
            self.birth_year = self.game.year
        # Set sex (unless it's assigned as part of world gen)
        if assigned_male:
            self.male = True
            self.female = False
        elif assigned_female:
            self.male = False
            self.female = True
        else:
            self.male, self.female = self.init_sex()
        # Set name
        if not self.mother:
            self.first_name, self.middle_name, self.last_name, self.suffix = (
                self.prim_init_name(male=self.male)
            )
        elif self.mother:
            self.first_name, self.middle_name, self.last_name, self.suffix = (
                self.mother.name_child(child=self, father=father)
            )
        self.maiden_name = self.last_name
        self.tag = ''  # Allows players to tag characters with arbitrary strings
        # Set misc attributes
        self.alive = True
        # Set biological characteristics
        self.infertile = self.init_fertility(male=self.male, config=self.game.config)
        self.attracted_to_men, self.attracted_to_women = (
            self.init_sexuality(male=self.male, config=self.game.config)
        )
        if assigned_male:  # Assure interest in opposite sex in support of world gen
            self.attracted_to_women = True
        elif assigned_female:
            self.attracted_to_men = True
        # Set personality
        if not self.mother:
            self.big_5_o, self.big_5_c, self.big_5_e, self.big_5_a, self.big_5_n = (
                self.prim_init_personality()
            )
        elif self.mother:
            self.big_5_o, self.big_5_c, self.big_5_e, self.big_5_a, self.big_5_n = (
                self.init_personality(mother=self.mother, father=self.father)
            )
        # Set mental attributes
        if not self.mother:
            self.memory = self.prim_init_memory(male=self.male, config=self.game.config)
        elif self.mother:
            self.memory = self.init_memory(
                male=self.male, mother=self.mother, father=self.father, config=self.game.config
            )
        # Familial attributes that get populated by self.init_familial_attributes() as appropriate
        self.ancestors = set()
        self.descendants = set()
        self.immediate_family = set()
        self.extended_family = set()
        self.greatgrandparents = set()
        self.grandparents = set()
        self.parents = set()
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
        # Set familial attributes; update those of family members
        if self.mother:
            self.init_familial_attributes()
            self.init_update_familial_attributes_of_family_members()
        # Set attributes representing this person's interpersonal relationships.
        self.spouse = None
        self.friends = set()
        self.known_people = set()
        self.known_by = set()
        self.first_met = {}
        self.last_saw = {}
        self.talked_to_this_year = set()
        self.befriended_this_year = set()
        self.sexual_partners = set()
        # Set attributes representing events in this person's life
        self.marriage = None
        self.marriages = []
        self.divorces = []
        self.moves = []  # From one home to another
        self.name_changes = []
        self.departure = None
        self.building_commissions = []  # Constructions of houses or buildings that they commissioned
        # Set attributes pertaining to business affairs
        if not self.mother:
            self.money = self.game.config.amount_of_money_generated_people_from_outside_city_start_with
        else:
            self.money = 0
        self.occupation = None
        self.occupations = []
        self.former_contractors = set()
        self.retired = False
        # Misc attributes that get set by other methods
        self.home = None
        self.lives_with_parents = False  # Gets set by Event.MoveIn.__init__()
        # Move into mother's home
        self.move_in(self.mother.home)

    @staticmethod
    def init_sex():
        """Determine the sex of this person."""
        if random.random() < 0.5:
            male = True
            female = False
        else:
            male = False
            female = True
        return male, female

    @staticmethod
    def init_fertility(male, config):
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
    def init_sexuality(male, config):
        """Determine this person's sexuality."""
        x = random.random()
        if x < config.homosexuality_incidence:
            # Homosexual
            if male:
                attracted_to_men = True
                attracted_to_women = False
            elif not male:
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
            elif not male:
                attracted_to_men = True
                attracted_to_women = False
        return attracted_to_men, attracted_to_women

    @staticmethod
    def init_personality(mother, father, config):
        """Determine this person's Big Five disposition, given their parents'.

        TODO: Have this affected by a person's sex."""
        # Openness to experience
        if random.random() < config.big_5_o_heritability:
            # Inherit this trait (with slight variance)
            takes_after = random.choice([father, mother])
            openness_to_experience = random.normalvariate(
                takes_after.openness_to_experience, config.big_5_heritability_sd
            )
        else:
            # Generate from the population mean
            openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience > 1:
            openness_to_experience = 1.0
        elif openness_to_experience < -1:
            openness_to_experience = -1.0
        # Conscientiousness
        if random.random() < config.big_5_c_heritability:
            takes_after = random.choice([father, mother])
            conscientiousness = random.normalvariate(
                takes_after.conscientiousness, config.big_5_heritability_sd
            )
        else:
            conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness > 1:
            conscientiousness = 1.0
        elif conscientiousness < -1:
            conscientiousness = -1.0
        # Extroversion
        if random.random() < config.big_5_e_heritability:
            takes_after = random.choice([father, mother])
            extroversion = random.normalvariate(
                takes_after.extroversion, config.big_5_heritability_sd
            )
        else:
            extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion > 1:
            extroversion = 1.0
        elif extroversion < -1:
            extroversion = -1.0
        # Agreeableness
        if random.random() < config.big_5_a_heritability:
            takes_after = random.choice([father, mother])
            agreeableness = random.normalvariate(
                takes_after.agreeableness, config.big_5_heritability_sd
            )
        else:
            agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness > 1:
            agreeableness = 1.0
        elif agreeableness < -1:
            extroversion = -1.0
        # Neuroticism
        if random.random() < config.big_5_n_heritability:
            takes_after = random.choice([father, mother])
            neuroticism = random.normalvariate(
                takes_after.neuroticism, config.big_5_heritability_sd
            )
        else:
            neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism > 1:
            neuroticism = 1.0
        elif neuroticism < -1:
            neuroticism = -1.0
        return openness_to_experience, conscientiousness, extroversion, agreeableness, neuroticism

    @staticmethod
    def init_memory(male, mother, father, config):
        """Determine a person's base memory capability, given their parents'."""
        if random.random() < config.memory_heritability:
            takes_after = random.choice([mother, father])
            memory = random.normalvariate(takes_after.memory, config.memory_heritability_sd)
        else:
            memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor_at_birth:
            memory = config.memory_floor_at_birth
        return memory

    def init_familial_attributes(self):
        """Populate lists representing this person's family members."""
        self.greatgrandparents = self.father.grandparents | self.mother.grandparents
        self.grandparents = self.father.parents | self.mother.parents
        self.parents = {self.father, self.mother}
        self.uncles = self.father.brothers | self.mother.brothers
        self.aunts = self.father.sisters | self.mother.sisters
        self.siblings = self.father.kids | self.mother.kids
        self.full_siblings = self.father.kids & self.mother.kids
        self.half_siblings = self.father.kids ^ self.mother.kids
        self.brothers = self.father.sons | self.mother.sons
        self.full_brothers = self.father.sons & self.mother.sons
        self.half_brothers = self.father.sons ^ self.mother.sons
        self.sisters = self.father.daughters | self.mother.daughters
        self.full_sisters = self.father.daughters & self.mother.daughters
        self.half_sisters = self.father.daughters ^ self.mother.daughters
        self.cousins = self.father.nieces | self.father.nephews | self.mother.nieces | self.mother.nephews
        self.nephews = self.father.grandsons | self.mother.grandsons
        self.nieces = self.father.granddaughters | self.mother.granddaughters
        self.ancestors = self.father.ancestors | self.mother.ancestors | self.parents
        self.immediate_family = self.grandparents | self.parents | self.siblings
        self.extended_family = (
            self.greatgrandparents | self.immediate_family | self.uncles | self.aunts |
            self.cousins | self.nieces | self.nephews
        )

    def init_update_familial_attributes_of_family_members(self):
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

    @staticmethod
    def prim_init_name(male):
        """Generate a name for a primordial person who has no parents."""
        if male:
            first_name = Names.a_masculine_name()
            middle_name = Names.a_masculine_name()
        elif not male:
            first_name = Names.a_feminine_name()
            middle_name = Names.a_feminine_name()
        last_name = Names.any_surname()
        suffix = ''
        return first_name, middle_name, last_name, suffix

    @staticmethod
    def prim_init_personality(config):
        """Generate values for each of the Big Five personality traits."""
        # Openness to experience
        openness_to_experience = random.normalvariate(config.big_5_o_mean, config.big_5_sd)
        if openness_to_experience > 1:
            openness_to_experience = 1.0
        elif openness_to_experience < -1:
            openness_to_experience = -1.0
        # Conscientiousness
        conscientiousness = random.normalvariate(config.big_5_c_mean, config.big_5_sd)
        if conscientiousness > 1:
            conscientiousness = 1.0
        elif conscientiousness < -1:
            conscientiousness = -1.0
        # Extroversion
        extroversion = random.normalvariate(config.big_5_e_mean, config.big_5_sd)
        if extroversion > 1:
            extroversion = 1.0
        elif extroversion < -1:
            extroversion = -1.0
        # Agreeableness
        agreeableness = random.normalvariate(config.big_5_a_mean, config.big_5_sd)
        if agreeableness > 1:
            agreeableness = 1.0
        elif agreeableness < -1:
            extroversion = -1.0
        # Neuroticism
        neuroticism = random.normalvariate(config.big_5_n_mean, config.big_5_sd)
        if neuroticism > 1:
            neuroticism = 1.0
        elif neuroticism < -1:
            neuroticism = -1.0
        return openness_to_experience, conscientiousness, extroversion, agreeableness, neuroticism

    @staticmethod
    def prim_init_memory(male, config):
        """Determine this person's base memory capability, which will deteriorate with age."""
        memory = random.normalvariate(config.memory_mean, config.memory_sd)
        if male:  # Men have slightly worse memory (studies show)
            memory -= config.memory_sex_diff
        if memory > config.memory_cap:
            memory = config.memory_cap
        elif memory < config.memory_floor:
            memory = config.memory_floor
        return memory

    @property
    def full_name(self):
        """Return a person's full name."""
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

    def contract_person_of_certain_occupation(self, occupation):
        """Find a person of a certain occupation.

        Currently, a person scores all the potential hires in town and then selects
        one of the top three. TODO: Probabilistically select from all potential hires
        using the scores to derive likelihoods of selecting each.
        """
        potential_hire_scores = self.rate_all_potential_contractors_of_certain_occupation(occupation=occupation)
        # Pick from top three
        top_three_choices = heapq.nlargest(3, potential_hire_scores, key=potential_hire_scores.get)
        if random.random() < 0.6:
            choice = top_three_choices[0]
        elif random.random() < 0.9:
            choice = top_three_choices[1]
        else:
            choice = top_three_choices[2]
        return choice

    def rate_all_potential_contractors_of_certain_occupation(self, occupation):
        """Score all potential hires of a certain occupation."""
        pool = self.city.workers_of_trade(occupation)
        scores = {}
        for person in pool:
            my_score = self.rate_potential_contractor_of_certain_occupation(person=person)
            if self.spouse:
                spouse_score = self.spouse.rate_potential_contractor_of_certain_occupation(person=person)
            else:
                spouse_score = 0
            scores[person] = my_score + spouse_score
        return scores

    def rate_potential_contractor_of_certain_occupation(self, person):
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

    def choose_vacant_home_or_vacant_lot(self):
        """Choose a vacant home to move into or a vacant lot to build on.

        Currently, a person scores all the vacant homes/lots in town and then selects
        one of the top three. TODO: Probabilistically select from all homes/lots using the
        scores to derive likelihoods of selecting each.
        """
        home_and_lot_scores = self.rate_all_vacant_homes_and_vacant_lots()
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

    def rate_all_vacant_homes_and_vacant_lots(self):
        """Find a home to move into in a chosen neighborhood.

        By this method, a person appraises every vacant home and lot in the city for
        how much they would like to move or build there, given considerations to the people
        that live nearby it (this reasoning via self.score_potential_home_or_lot()). There is
        a penalty that makes people less willing to build a home on a vacant lot than to move
        into a vacant home.
        """
        scores = {}
        for home in self.city.vacant_homes:
            my_score = self.rate_potential_lot(lot=home.lot)
            if self.spouse:
                spouse_score = self.spouse.score_potential_home_or_lot(home_or_lot=home)
            else:
                spouse_score = 0
            scores[home] = my_score + spouse_score
        for lot in self.city.vacant_lots:
            my_score = self.rate_potential_lot(lot=lot)
            if self.spouse:
                spouse_score = self.spouse.score_potential_home_or_lot(home_or_lot=lot)
            else:
                spouse_score = 0
            scores[lot] = (
                (my_score + spouse_score) * self.game.config.penalty_for_having_to_build_a_home_vs_buying_one
            )
        return scores

    def rate_potential_lot(self, lot):
        """Score the desirability of living at the location of a lot.

        TODO: Other considerations here.
        """
        config = self.game.config
        desire_to_live_near_family = self.determine_desire_to_move_near_family()
        score = 0
        # Score home for its proximity to family (either positively or negatively, depending)
        for kid in self.kids:
            # Don't consider kids that still live with you here
            if kid.home is not self.home:
                dist = kid.home.lot.get_dist_to(lot) + 1  # Since we're dividing by this next
                score += (desire_to_live_near_family * config.pull_to_live_near_a_child) / dist
        for parent in self.parents:
            dist = parent.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_parent) / dist
        for grandchild in self.grandchildren:
            dist = grandchild.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_grandchild) / dist
        for sibling in self.siblings:
            dist = sibling.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_sibling) / dist
        for grandparent in self.grandparents:
            dist = grandparent.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_grandparent) / dist
        for greatgrandparent in self.greatgrandparents:
            dist = greatgrandparent.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_greatgrandparent) / dist
        for niece in self.nieces:
            dist = niece.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_niece_or_nephew) / dist
        for nephew in self.nephews:
            dist = nephew.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_niece_or_nephew) / dist
        for aunt in self.aunts:
            dist = aunt.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_an_aunt_or_uncle) / dist
        for uncle in self.uncles:
            dist = uncle.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_an_aunt_or_uncle) / dist
        for cousin in self.cousins:
            dist = cousin.home.lot.get_dist_to(lot)
            score += (desire_to_live_near_family * config.pull_to_live_near_a_first_cousin) / dist
        # Score for proximity to friends (only positively)
        for friend in self.friends:
            dist = friend.home.lot.get_dist_to(lot)
            score += config.pull_to_live_near_a_friend / dist
        return score

    def determine_desire_to_move_near_family(self):
        """Decide how badly you want to move near/away from family."""
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

    def change_name(self, new_last_name, reason):
        """Change this person's (official) name."""
        NameChange(subject=self, new_last_name=new_last_name, reason=reason)

    def marry(self, partner):
        """Marry partner."""
        assert(self.alive and partner.alive), "{} tried to marry {}, but one of them is dead."
        Marriage(subjects=(self, partner))

    def divorce(self, partner):
        """Divorce partner."""
        assert(self.alive and partner.alive), "{} tried to divorce {}, but one of them is dead."
        assert(partner is self.spouse and partner.spouse is self), (
            "{} tried to divorce {}, whom they are not married to.".format(self.name, partner.name)
        )
        Divorce(subjects=(self, partner))

    def secure_home(self):
        """Find a home to move into.

        The person (and their spouse, if any) will decide between all the vacant
        homes and vacant lots (upon which they would build a new home) in the city.
        """
        chosen_home_or_lot = self.choose_vacant_home_or_vacant_lot()
        if chosen_home_or_lot:
            if isinstance(chosen_home_or_lot, Lot):
                # A vacant lot was chosen, so build
                home_to_move_into = self.commission_construction_of_a_house()
            else:
                # A vacant home was chosen
                home_to_move_into = chosen_home_or_lot
        else:
            home_to_move_into = None  # The city is full; this will spark a departure
        return home_to_move_into

    def commission_construction_of_a_house(self, lot):
        """Build a house to move into."""
        architect = self.contract_person_of_certain_occupation(occupation=Architect)
        if self.spouse:
            clients = {self, self.spouse}
        else:
            clients = {self}
        return architect.construct_house(clients=clients, lot=lot)

    def purchase_home(self, home):
        """Purchase a house or apartment unit, with the help of a realtor."""
        realtor = self.contract_person_of_certain_occupation(occupation=Realtor)
        if self.spouse:
            clients = {self, self.spouse}
        else:
            clients = {self}
        return realtor.sell_home(clients=clients, home=home)

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