import random
import heapq
from corpora import Names
import event
from name import Name
from personality import Personality
from mind import Mind
import occupation
from face import Face
from routine import Routine


class Person(object):
    """A person living in a city of a gameplay instance."""

    def __init__(self, game, birth):
        """Initialize a Person object."""
        # Set location and gameplay instance
        self.game = game
        self.birth = birth
        if birth:
            self.city = self.birth.city
            if self.city:
                self.city.residents.add(self)
            # Set parents
            self.biological_mother = birth.biological_mother
            self.mother = birth.mother
            self.biological_father = birth.biological_father
            self.father = birth.father
            # Set year of birth
            self.birth_year = birth.year
        else:  # PersonExNihilo
            self.city = None
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
        self.home = None  # Must come before setting routine
        # Set biological characteristics
        self.infertile = self._init_fertility(male=self.male, config=self.game.config)
        self.attracted_to_men, self.attracted_to_women = (
            self._init_sexuality()
        )
        # Set face
        self.face = Face(person=self)
        # Set personality
        self.personality = Personality(person=self)
        # Set mental attributes (just memory currently)
        self.mind = Mind(person=self)
        # Set daily routine
        self.routine = Routine(person=self)
        # Prepare name attributes that get set by event.Birth._name_baby() (or PersonExNihilo._init_name())
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
        self.relationships = {}
        self.first_met = {}
        self.last_saw = {}
        self.talked_to_this_year = set()
        self.befriended_this_year = set()
        self.love_interest = None
        self.sexual_partners = set()
        # Prepare attributes pertaining to pregnancy
        self.impregnated_by = None
        self.conception_date = None  # Year of conception
        # Prepare attributes representing events in this person's life
        self.birth = birth
        self.adoption = None
        self.marriage = None
        self.marriages = []
        self.divorces = []
        self.adoptions = []
        self.moves = []  # From one home to another
        self.name_changes = []
        self.building_commissions = set()  # Constructions of houses or buildings that they commissioned
        self.departure = None  # Leaving the city, i.e., leaving the simulation
        self.death = None
        # Set and prepare attributes pertaining to business affairs
        self.money = self._init_money()
        self.occupation = None
        self.occupations = []
        self.former_contractors = set()
        self.retired = False
        # Prepare attributes pertaining to education
        self.college_graduate = False
        # Prepare attributes pertaining to dynamic emotional considerations
        self.grieving = False  # After spouse dies

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

    def _init_sexuality(self):
        """Determine this person's sexuality."""
        config = self.game.config
        x = random.random()
        if x < config.homosexuality_incidence:
            # Homosexual
            if self.male:
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
            if self.male:
                attracted_to_men = False
                attracted_to_women = True
            else:
                attracted_to_men = True
                attracted_to_women = False
        return attracted_to_men, attracted_to_women

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
        self.bio_parents = set([self.biological_mother, self.biological_father])
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
    def full_name(self):
        """Return a person's full name."""
        if self.suffix:
            full_name = "{0} {1} {2} {3}".format(
                self.first_name, self.middle_name, self.last_name, self.suffix
            )
        else:
            full_name = "{0} {1} {2}".format(
                self.first_name, self.middle_name, self.last_name
            )
        return full_name

    @property
    def full_name_without_suffix(self):
        """Return a person's full name sans suffix.

        This is used to determine whether a child has the same full name as their parent,
        which would necessitate them getting a suffix of their own to disambiguate.
        """
        full_name = "{0} {1} {2}".format(
            self.first_name, self.middle_name, self.last_name
        )
        return full_name

    @property
    def name(self):
        """Return a person's name."""
        if self.suffix:
            name = "{0} {1} {2}".format(self.first_name, self.last_name, self.suffix)
        else:
            name = "{0} {1}".format(self.first_name, self.last_name)
        return name

    @property
    def nametag(self):
        """Return a person's name, appended with their tag, if any."""
        if self.tag:
            nametag = "{0} {1}".format(self.name, self.tag)
        else:
            nametag = self.name
        return nametag

    @property
    def age(self):
        """Return whether this person is at least 18 years old."""
        return self.game.year - self.birth_year

    @property
    def adult(self):
        """Return whether this person is at least 18 years old."""
        return self.age >= 18

    @property
    def pregnant(self):
        """Return whether this person is pregnant."""
        if self.impregnated_by:
            return True
        else:
            return False

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
        return set([parent for parent in (self.mother, self.father) if parent])

    @property
    def next_of_kin(self):
        """Return next of kin.

        A person's next of kin will make decisions about their estate and
        so forth upon the person's death.
        """
        assert not self.alive, "{0} is dead, but a request was made for his next of kin."
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
    def nuclear_family(self):
        """Return this person's nuclear family."""
        nuclear_family = set([self])
        if self.spouse:
            nuclear_family.add(self.spouse)
        for kid in self.spouse.kids & self.kids if self.spouse else self.kids:
            if kid.home is self.home:
                nuclear_family.add(kid)
        return nuclear_family

    @property
    def friends(self):
        """Return the friends this person has (in their own conception)."""
        friends = [
            person for person in self.relationships if self.relationships[person].type == "friendship"
        ]
        return friends

    @property
    def enemies(self):
        """Return the enemies this person has (in their own conception)."""
        enemies = [
            person for person in self.relationships if self.relationships[person].type == "enmity"
        ]
        return enemies

    @property
    def acquaintances(self):
        """Return the acquaintances this person has."""
        acquaintances = [
            person for person in self.relationships if self.relationships[person].type == "acquaintance"
        ]
        return acquaintances

    @property
    def coworkers(self):
        """Return this person's coworkers."""
        if self.occupation:
            coworkers = self.occupation.company.employees - set([self])
        else:
            coworkers = set()
        return coworkers

    @property
    def neighbors(self):
        """Return this person's neighbors, i.e., people living or working on neighboring lots."""
        neighbors = self.home.lot.neighboring_residents
        # If you live in an apartment complex, add in the other people who live
        # in it too (these won't be captured by the above command)
        if self.home.apartment:
            neighbors_in_the_same_complex = self.home.complex.residents - self.home.residents
            neighbors |= neighbors_in_the_same_complex
        return neighbors

    @property
    def neighbors_and_their_neighbors(self):
        """Return this person's neighbors, as well as those people's neighbors."""
        neighbors = self.home.lot.neighboring_residents_and_their_neighboring_residents
        # If you live in an apartment complex, add in the other people who live
        # in it too (these won't be captured by the above command)
        if self.home.apartment:
            neighbors_in_the_same_complex = self.home.complex.residents - self.home.residents
            neighbors |= neighbors_in_the_same_complex
        return neighbors

    @property
    def major_life_events(self):
        """Return the major events of this person's life."""
        events = [self.birth, self.adoption]
        events += self.moves
        events += [job.hiring for job in self.occupations]
        events += self.marriages
        events += [kid.birth for kid in self.kids]
        events += self.divorces
        events += self.name_changes
        events += list(self.building_commissions)
        events += [self.departure, self.death]
        while None in events:
            events.remove(None)
        events.sort(key=lambda ev: ev.year)  # Sort chronologically
        return events

    def feature_of_type(self, feature_type):
        """Return this person's feature of the given type."""
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

    def change_name(self, new_last_name, reason):
        """Change this person's (official) name."""
        lawyer = self.contract_person_of_certain_occupation(occupation_in_question=occupation.Lawyer)
        if lawyer:
            lawyer.occupation.file_name_change(person=self, new_last_name=new_last_name, reason=reason)
        else:
            event.NameChange(subject=self, new_last_name=new_last_name, reason=reason, lawyer=None)

    def fall_in_love(self, person):
        """Fall in love with person."""
        self.love_interest = person

    def fall_out_of_love(self):
        """Fall out of love."""
        self.love_interest = None

    def have_sex(self, partner, protection):
        """Have sex with partner."""
        config = self.game.config
        self.sexual_partners.add(partner)
        partner.sexual_partners.add(self)
        if random.random() < config.chance_person_falls_in_love_after_sex:
            self.fall_in_love(person=partner)
        if random.random() < config.chance_person_falls_in_love_after_sex:
            partner.fall_in_love(person=self)
        if self.male != partner.male and not self.pregnant and not partner.pregnant:
            if (not protection) or random.random() < config.chance_protection_does_not_work:
                self._determine_whether_pregnant(partner=partner)

    def _determine_whether_pregnant(self, partner):
        """Determine whether self or partner is now pregnant."""
        config = self.game.config
        # Determine whether child is conceived
        female_partner = self if self.female else partner
        chance_of_conception = config.function_to_determine_chance_of_conception(
            female_age=female_partner.age
        )
        if random.random() < chance_of_conception:
            female_partner.impregnated_by = self if female_partner is partner else partner
            female_partner.conception_date = self.game.year

    def marry(self, partner):
        """Marry partner."""
        assert(self.present and partner.present), "{0} tried to marry {1}, but one of them is dead or departed."
        event.Marriage(subjects=(self, partner))

    def divorce(self, partner):
        """Divorce partner."""
        assert(self.alive and partner.alive), "{0} tried to divorce {1}, but one of them is dead."
        assert(partner is self.spouse and partner.spouse is self), (
            "{0} tried to divorce {1}, whom they are not married to.".format(self.name, partner.name)
        )
        # The soon-to-be divorcees will decide together which lawyer to hire, because they are
        # technically still married (and spouses are considered as part of this method call)
        lawyer = self.contract_person_of_certain_occupation(occupation_in_question=occupation.Lawyer)
        lawyer.occupation.file_divorce(clients=(self, partner,))

    def give_birth(self):
        """Select a doctor and go to the hospital to give birth."""
        doctor = self.contract_person_of_certain_occupation(occupation_in_question=occupation.Doctor)
        if doctor:
            doctor.occupation.deliver_baby(mother=self)
        else:
            event.Birth(mother=self, doctor=None)

    def die(self, cause_of_death):
        """Die and get interred at the local cemetery."""
        mortician = self.next_of_kin.contract_person_of_certain_occupation(occupation_in_question=occupation.Mortician)
        mortician.occupation.inter_body(deceased=self, cause_of_death=cause_of_death)

    def move(self, new_home, reason):
        """Move to an apartment or home."""
        event.Move(subjects=tuple(self.nuclear_family), new_home=new_home, reason=reason)

    def pay(self, payee, amount):
        """Pay someone (for services rendered)."""
        if self.spouse:
            self.marriage.money -= amount
        else:
            self.money -= amount
        payee.money += amount

    def depart_city(self):
        """Depart the city (and thus the simulation), never to return."""
        event.Departure(subject=self)

    def contract_person_of_certain_occupation(self, occupation_in_question):
        """Find a person of a certain occupation.

        Currently, a person scores all the potential hires in town and then selects
        one of the top three. TODO: Probabilistically select from all potential hires
        using the scores to derive likelihoods of selecting each.
        """
        if self.city:
            pool = list(self.city.workers_of_trade(occupation_in_question))
        else:  # PersonExNihilo who backstory is currently being retconned
            pool = []
        if pool:
            # If you or your spouse practice this occupation, DIY
            if isinstance(self.occupation, occupation_in_question):
                choice = self
            elif self.spouse and isinstance(self.spouse.occupation, occupation_in_question):
                choice = self.spouse
            # Otherwise, pick from the various people in town who do practice this occupation
            else:
                potential_hire_scores = self._rate_all_potential_contractors_of_certain_occupation(pool=pool)
                if len(potential_hire_scores) >= 3:
                    # Pick from top three
                    top_three_choices = heapq.nlargest(3, potential_hire_scores, key=potential_hire_scores.get)
                    if random.random() < 0.6:
                        choice = top_three_choices[0]
                    elif random.random() < 0.9:
                        choice = top_three_choices[1]
                    else:
                        choice = top_three_choices[2]
                else:
                    choice = max(potential_hire_scores)
        else:
            # This should only ever happen at the very beginning of a city's history where all
            # business types haven't been built in town yet
            choice = None
        return choice

    def _rate_all_potential_contractors_of_certain_occupation(self, pool):
        """Score all potential hires of a certain occupation."""
        scores = {}
        for person in pool:
            scores[person] = self._rate_potential_contractor_of_certain_occupation(person=person)
        return scores

    def _rate_potential_contractor_of_certain_occupation(self, person):
        """Score a potential hire of a certain occupation, with preference to family, friends, former hires.

        TODO: Have this be affected by personality (beyond what being a friend captures).
        """
        score = 0
        # Rate according to social reasons
        if self.spouse:
            people_involved_in_this_decision = (self, self.spouse)
        else:
            people_involved_in_this_decision = (self,)
        for decision_maker in people_involved_in_this_decision:
            if person in decision_maker.immediate_family:
                score += decision_maker.game.config.preference_to_contract_immediate_family
            elif person in decision_maker.extended_family:  # elif because immediate family is subset of extended family
                score += decision_maker.game.config.preference_to_contract_extended_family
            if person in decision_maker.friends:
                score += decision_maker.game.config.preference_to_contract_friend
            elif person in decision_maker.acquaintances:
                score += decision_maker.game.config.preference_to_contract_acquaintance
            if person in decision_maker.enemies:
                score += decision_maker.game.config.dispreference_to_hire_enemy
            if person in decision_maker.former_contractors:
                score += decision_maker.game.config.preference_to_contract_former_contract
        # Multiply score according to this person's experience in this occupation
        score *= person.game.config.function_to_derive_score_multiplier_bonus_for_experience(
            years_experience=person.occupation.years_experience
        )
        return score

    def purchase_home(self, purchasers, home):
        # TEMP THING DUE TO CIRCULAR DEPENDENCY -- SEE RESIDENCE.PY -- TODO
        event.HomePurchase(subjects=purchasers, home=home, realtor=None)

    def secure_home(self):
        """Find a home to move into.

        The person (and their spouse, if any) will decide between all the vacant
        homes and vacant lots (upon which they would build a new home) in the city.
        """
        chosen_home_or_lot = self._choose_vacant_home_or_vacant_lot()
        if chosen_home_or_lot:
            if chosen_home_or_lot in self.city.vacant_lots:
                # A vacant lot was chosen, so build
                home_to_move_into = self._commission_construction_of_a_house(lot=chosen_home_or_lot)
            elif chosen_home_or_lot in self.city.vacant_homes:
                # A vacant home was chosen
                home_to_move_into = self._purchase_home(home=chosen_home_or_lot)
            else:
                raise Exception("A person is attempting to secure a lot or home that is not known to be vacant.")
        else:
            home_to_move_into = None  # The city is full; this will spark a departure
        return home_to_move_into

    def _commission_construction_of_a_house(self, lot):
        """Build a house to move into."""
        architect = self.contract_person_of_certain_occupation(occupation_in_question=occupation.Architect)
        if self.spouse:
            clients = (self, self.spouse,)
        else:
            clients = (self,)
        return architect.occupation.construct_house(clients=clients, lot=lot)

    def _purchase_home(self, home):
        """Purchase a house or apartment unit, with the help of a realtor."""
        realtor = self.contract_person_of_certain_occupation(occupation_in_question=occupation.Realtor)
        if self.spouse:
            clients = (self, self.spouse,)
        else:
            clients = (self,)
        return realtor.occupation.sell_home(clients=clients, home=home)

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
        """Rate all vacant homes and vacant lots."""
        scores = {}
        for home in self.city.vacant_homes:
            my_score = self.rate_potential_lot(lot=home.lot)
            if self.spouse:
                spouse_score = self.spouse.rate_potential_lot(lot=home.lot)
            else:
                spouse_score = 0
            scores[home] = my_score + spouse_score
        for lot in self.city.vacant_lots:
            my_score = self.rate_potential_lot(lot=lot)
            if self.spouse:
                spouse_score = self.spouse.rate_potential_lot(lot=lot)
            else:
                spouse_score = 0
            scores[lot] = (
                (my_score + spouse_score) * self.game.config.penalty_for_having_to_build_a_home_vs_buying_one
            )
        return scores

    def rate_potential_lot(self, lot):
        """Rate the desirability of living at the location of a lot.

        By this method, a person appraises a vacant home or lot in the city for
        how much they would like to move or build there, given considerations to the people
        that live nearby it (this reasoning via self.score_potential_home_or_lot()). There is
        a penalty that makes people less willing to build a home on a vacant lot than to move
        into a vacant home.
        """
        config = self.game.config
        desire_to_live_near_family = self._determine_desire_to_move_near_family()
        # Score home for its proximity to family (either positively or negatively, depending); only
        # consider family members that are alive, in town, and not living with you already (i.e., kids)
        relatives_in_town =  set([
            f for f in self.extended_family if f.present and f.home is not self.home
        ])
        score = 0
        for relative in relatives_in_town:
            relation_to_me = self.relation_to_me(person=relative)
            pull_toward_someone_of_that_relation = config.pull_to_live_near_family[relation_to_me]
            dist = self.city.getDistFrom(relative.home.lot,lot) + 1.0  # To avoid ZeroDivisionError
            score += (desire_to_live_near_family * pull_toward_someone_of_that_relation) / dist
        # Score for proximity to friends (only positively)
        for friend in self.friends:
            dist =  self.city.getDistFrom(friend.home.lot,lot) + 1.0
            score += config.pull_to_live_near_a_friend / dist
        # Score for proximity to workplace (only positively) -- will be only criterion for person
        # who is new to the city (and thus knows no one there yet)
        if self.occupation:
            dist = self.city.getDistFrom(self.occupation.company.lot,lot) + 1.0
            score += config.pull_to_live_near_workplace / dist
        return score

    def _determine_desire_to_move_near_family(self):
        """Decide how badly you want to move near/away from family.

        Currently, this relies on immutable personality traits, but eventually
        this desire could be made dynamic according to life events, etc.
        """
        config = self.game.config
        # People with personality C-, O+ most likely to leave home (source [1])
        base_desire_to_live_near_family = config.desire_to_live_near_family_base
        desire_to_live_near_family = self.personality.conscientiousness
        desire_to_live_away_from_family = self.personality.openness_to_experience
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
    on inheritance. Additionally, a family (i.e., a PersonExNihilo spouse and possibly Person
    children) may be generated for a person of this class.
    """

    def __init__(self, game, job_opportunity_impetus, spouse_already_generated, this_person_is_the_founder=False):
        super(PersonExNihilo, self).__init__(game, birth=None)
        # Potentially overwrite sex set by Person.__init__()
        if spouse_already_generated:
            self._override_sex(spouse=spouse_already_generated)
            self._override_sexuality(spouse=spouse_already_generated)
        # Overwrite birth year set by Person.__init__()
        if this_person_is_the_founder:  # The person who founds the city -- there are special requirements for them
            self.game.founder = self
            self.birth_year = self._init_birth_year_of_the_founder()
        elif spouse_already_generated and spouse_already_generated is self.game.founder:
            self.birth_year = self._init_birth_year(job_level=None, founders_spouse=True)
        else:
            job_level = self.game.config.job_levels[job_opportunity_impetus]
            self.birth_year = self._init_birth_year(job_level=job_level)
        # Since they don't have a parent to name them, generate a name for this person (if
        # they get married outside the city, this will still potentially change, as normal)
        self.first_name, self.middle_name, self.last_name, self.suffix = (
            self._init_name()
        )
        self.maiden_name = self.last_name
        self.named_for = None
        # If this person is being hired for a high job level, retcon that they have
        # a college education -- do the same for the city founder
        if job_opportunity_impetus and self.game.config.job_levels[job_opportunity_impetus] > 3:
            self.college_graduate = True
        elif this_person_is_the_founder:
            self.college_graduate = True
        # Potentially generate and retcon a family that this person will have
        # had prior to moving into the city
        if this_person_is_the_founder:
            self._init_generate_the_founders_family()
        elif not spouse_already_generated:
            chance_of_having_family = (
                self.game.config.function_to_determine_chance_person_ex_nihilo_starts_with_family(age=self.age)
            )
            if random.random() < chance_of_having_family:
                self._init_generate_family(job_opportunity_impetus=job_opportunity_impetus)
        # Finally, move this person (and family, if any) into the city
        # if not this_person_is_the_founder and not spouse_already_generated:
        #     self.move_into_the_city(hiring_that_instigated_move=job_opportunity_impetus)

    @staticmethod
    def _override_sex(spouse):
        """Assign the sex of this person to ensure compatibility with their spouse.."""
        if spouse.attracted_to_men:
            male, female = True, False
        else:
            male, female = False, True
        return male, female

    @staticmethod
    def _override_sexuality(spouse):
        """Assign the sex of this person to ensure compatibility with their spouse.."""
        if spouse.male:
            attracted_to_men, attracted_to_women = True, False
        else:
            attracted_to_men, attracted_to_women = False, True
        return attracted_to_men, attracted_to_women

    def _init_name(self):
        """Generate a name for a primordial person who has no parents."""
        if self.male:
            first_name = Name(value=Names.a_masculine_name(), progenitor=self, conceived_by=(), derived_from=())
            middle_name = Name(value=Names.a_masculine_name(), progenitor=self, conceived_by=(), derived_from=())
        else:
            first_name = Name(value=Names.a_feminine_name(), progenitor=self, conceived_by=(), derived_from=())
            middle_name = Name(value=Names.a_feminine_name(), progenitor=self, conceived_by=(), derived_from=())
        last_name = Name(value=Names.any_surname(), progenitor=self, conceived_by=(), derived_from=())
        suffix = ''
        return first_name, middle_name, last_name, suffix

    def _init_birth_year_of_the_founder(self):
        """Generate a birth year for the founder of the city."""
        config = self.game.config
        age_at_current_year_of_sim = config.age_of_city_founder
        birth_year = self.game.true_year - age_at_current_year_of_sim
        return birth_year

    def _init_birth_year(self, job_level, founders_spouse=False):
        """Generate a birth year for this person that is consistent with the job level they/spouse will get."""
        config = self.game.config
        if not founders_spouse:
            age_at_current_year_of_sim = config.function_to_determine_person_ex_nihilo_age_given_job_level(
                job_level=job_level
            )
        else:
            age_at_current_year_of_sim = config.age_of_city_founders_spouse
        birth_year = self.game.true_year - age_at_current_year_of_sim
        return birth_year

    def _init_familial_attributes(self):
        """Do nothing because a PersonExNihilo has no family at the time of being generated.."""
        pass

    def _init_update_familial_attributes_of_family_members(self):
        """Do nothing because a PersonExNihilo has no family at the time of being generated.."""
        pass

    def _init_money(self):
        """Determine how much money this person has to start with."""
        return self.game.config.amount_of_money_generated_people_from_outside_city_start_with

    def _init_generate_the_founders_family(self):
        """Generate and retcon a family that the founder will have prior to the city being founded.

        This family will develop into the very rich family that Player 2 and his or her
        cronies belong to.
        """
        config = self.game.config
        # Force this person to have a ton of money
        self.money = config.money_city_founder_starts_with
        # Force heterosexuality and fertility -- we are rigging things so that a very large
        # family develops as this person's progeny
        self.infertile = False
        if self.male:
            self.attracted_to_women = True
        else:
            self.attracted_to_men = True
        spouse = PersonExNihilo(
            game=self.game, job_opportunity_impetus=None, spouse_already_generated=self
        )
        spouse.infertile = False
        self.fall_in_love(spouse)
        spouse.fall_in_love(self)
        self._init_retcon_marriage(spouse=spouse)
        self._init_retcon_births_of_children()

    def _init_generate_family(self, job_opportunity_impetus):
        """Generate and retcon a family that this person will take with them into the city."""
        spouse = PersonExNihilo(
            game=self.game, job_opportunity_impetus=job_opportunity_impetus, spouse_already_generated=self
        )
        self.fall_in_love(spouse)
        spouse.fall_in_love(self)
        self._init_retcon_marriage(spouse=spouse)
        self._init_retcon_births_of_children()

    def _init_retcon_marriage(self, spouse):
        """Jump back in time to instantiate a marriage that began outside the city."""
        config = self.game.config
        # Change actual game year to marriage year, instantiate a Marriage object
        marriage_date = self.birth_year + (
            random.normalvariate(
                config.person_ex_nihilo_age_at_marriage_mean, config.person_ex_nihilo_age_at_marriage_sd
            )
        )
        if (
            # Make sure spouses aren't too young for marriage and that marriage isn't slated
            # to happen after the city has been founded
            marriage_date - self.birth_year < config.person_ex_nihilo_age_at_marriage_floor or
            marriage_date - spouse.birth_year < config.person_ex_nihilo_age_at_marriage_floor or
            marriage_date >= self.game.true_year
        ):
            # If so, don't bother regenerating -- just set marriage year to last year and move on
            marriage_date = self.game.true_year - 1
        self.game.year = int(round(marriage_date))
        self.marry(spouse)

    def _init_retcon_births_of_children(self):
        """Simulate from marriage to the present day for children potentially being born."""
        config = self.game.config
        # Simulate sex (and thus potentially birth) in marriage thus far
        for year in xrange(self.marriage.year, self.game.true_year+1):
            # If someone is pregnant and due this year, have them give birth
            if self.pregnant or self.spouse.pregnant:
                pregnant_one = self if self.pregnant else self.spouse
                if pregnant_one.conception_date < year:
                    pregnant_one.give_birth()
            self.game.year = year
            chance_they_are_trying_to_conceive_this_year = (
                config.function_to_determine_chance_married_couple_are_trying_to_conceive(
                    n_kids=len(self.marriage.children_produced)
                )
            )
            if self is self.game.founder:  # Try to force large family to develop
                chance_they_are_trying_to_conceive_this_year += config.boost_to_the_founders_conception_chance
            if random.random() < chance_they_are_trying_to_conceive_this_year:
                self.have_sex(partner=self.spouse, protection=False)
            else:
                self.have_sex(partner=self.spouse, protection=True)

    def move_into_the_city(self, hiring_that_instigated_move):
        """Move into the city in which gameplay takes place."""
        self.city = self.game.city
        self.city.residents.add(self)
        new_home = self.secure_home()
        self.move(new_home=new_home, reason=hiring_that_instigated_move)