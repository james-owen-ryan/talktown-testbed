import random
from config import Config
from corpora import Names
from person import Person
from city import Lot
from business import *
from residence import *
from occupation import *
from name import Name


class Birth(object):
    """A birth of a person in the city."""

    def __init__(self, mother, doctor):
        """Initialize a Birth object."""
        self.year = mother.game.year
        self.biological_mother = mother
        self.mother = mother
        self.biological_father = mother.impregnated_by
        self.father = self.mother.spouse if self.mother.spouse and self.mother.spouse.male else None
        if self.father and self.father is not self.biological_father:
            self.adoption = Adoption(subject=self.subject, adoptive_parents=(self.father,))
        self.doctor = doctor
        self.doctor.baby_deliveries.append(self)
        self.hospital = doctor.company
        self.subject = Person(game=mother.game, birth=self)
        if self.biological_father is self.mother.spouse:
            self.mother.marriage.children_produced.add(self.subject)

    def init_update_mother_attributes(self):
        """Update attributes of the mother that are affected by this birth."""
        self.mother.pregnant = False
        self.mother.conception_date = None
        self.mother.impregnated_by = None

    def name_baby(self):
        """Name the baby.

        TODO: Support a child inheriting a person's middle name as their own
        first or middle name.
        """
        config = self.subject.game.config
        if self.subject.male and random.random() < config.chance_son_inherits_fathers_exact_name:
            self.subject.first_name = self.father.first_name
            self.subject.middle_name = self.father.middle_name
            self.subject.suffix = self._get_suffix()
            self.subject.named_for = self.father, self.father,
        else:
            if self.subject.male:
                potential_namegivers = self._get_potential_male_namegivers()
            else:
                potential_namegivers = self._get_potential_female_namegivers()
            self.subject.first_name, first_name_namegiver = (
                self._decide_first_name(potential_namegivers=potential_namegivers)
            )
            self.subject.middle_name, middle_name_namegiver = (
                self._decide_middle_name(potential_namegivers=potential_namegivers)
            )
            self.subject.suffix = ''
            self.subject.named_for = first_name_namegiver, middle_name_namegiver,
        self.subject.last_name = self._decide_last_name()

    def _decide_last_name(self):
        """Return what will be the baby's last name."""
        if self.mother.marriage:
            if self.mother.marriage.will_hyphenate_child_surnames:
                last_name = self._get_hyphenated_last_name()
            else:
                last_name = self.father.last_name
        else:
            last_name = self.mother.last_name
        return last_name

    def _get_hyphenated_last_name(self):
        """Get a hyphenated last name for the child, if the parents have decided to attribute one."""
        hyphenated_last_name = "{}-{}".format(
            self.mother.last_name.rep
        )
        # Check if this child will be the progenitor of this hyphenated surname, i.e.,
        # whether an older sibling has already been given it
        if any(k for k in self.mother.marriage.children_produced if k.maiden_name.rep == hyphenated_last_name):
            older_sibling_with_hyphenated_surname = next(
                k for k in self.mother.marriage.children_produced if k.maiden_name.rep == hyphenated_last_name
            )
            hyphenated_surname_object = older_sibling_with_hyphenated_surname.maiden_name
        else:
            # Instantiate a new Name object with this child as the progenitor
            hyphenated_surname_object = Name(
                rep=hyphenated_last_name, progenitor=self.subject, conceived_by=self.subject.parents,
                derived_from=(self.mother.last_name, self.father.last_name,)
            )
        return hyphenated_surname_object

    def _decide_first_name(self, potential_namegivers):
        """Return what will be the baby's first name."""
        config = self.subject.game.config
        if random.random() < config.chance_child_inherits_first_name:
            first_name_namegiver = random.choice(potential_namegivers)
            first_name = first_name_namegiver.first_name
        else:
            first_name_namegiver = None
            first_name_rep = Names.a_masculine_name() if self.subject.male else Names.a_feminine_name()
            first_name = Name(rep=first_name_rep, progenitor=self.subject, conceived_by=self.subject.parents)
        return first_name, first_name_namegiver

    def _decide_middle_name(self, potential_namegivers):
        """Return what will be the baby's first name."""
        config = self.subject.game.config
        if random.random() < config.chance_child_inherits_middle_name:
            middle_name_namegiver = random.choice(potential_namegivers)
            middle_name = middle_name_namegiver.first_name
        else:
            middle_name_namegiver = None
            middle_name_rep = Names.a_masculine_name() if self.subject.male else Names.a_feminine_name()
            middle_name = Name(rep=middle_name_rep, progenitor=self.subject, conceived_by=self.subject.parents)
        return middle_name, middle_name_namegiver

    def _get_potential_male_namegivers(self):
        """Return a set of men on the father's side of the family whom the child may be named for."""
        config = self.subject.game.config
        namegivers = []
        for parent in self.subject.parents:
            # Add the child's legal father
            if parent.male:
                namegivers += [parent] * config.frequency_of_naming_after_father
            # Add the child's (legal) great/grandfathers
            if parent.father:
                namegivers += [parent.father] * config.frequency_of_naming_after_grandfather
                if parent.father.father:
                    namegivers += [parent.father.father] * config.frequency_of_naming_after_greatgrandfather
                if parent.mother.father:
                    namegivers += [parent.mother.father] * config.frequency_of_naming_after_greatgrandfather
            # Add a random sampling child's uncles and great uncles
            namegivers += random.sample(parent.brothers, random.randint(0, len(parent.brothers)))
            namegivers += random.sample(parent.uncles, random.randint(0, len(parent.uncles)))
        return namegivers

    def _get_potential_female_namegivers(self):
        """Return a set of women on the father's side of the family whom the child may be named for."""
        config = self.subject.game.config
        namegivers = []
        for parent in self.subject.parents:
            # Add the child's mother
            if parent.female:
                namegivers += [parent] * config.frequency_of_naming_after_mother
            # Add the child's (legal) great/grandmothers
            if parent.mother:
                namegivers += [parent.mother] * config.frequency_of_naming_after_grandmother
                if parent.father.mother:
                    namegivers += [parent.father.mother] * config.frequency_of_naming_after_greatgrandmother
                if parent.mother.mother:
                    namegivers += [parent.mother.mother] * config.frequency_of_naming_after_greatgrandmother
            # Add a random sampling child's aunts and great aunts
            namegivers += random.sample(parent.sisters, random.randint(0, len(parent.sisters)))
            namegivers += random.sample(parent.aunts, random.randint(0, len(parent.aunts)))
        return namegivers

    def _get_suffix(self):
        """Return a suffix if the person shares their parent's full name, else an empty string."""
        son, father = self.subject, self.subject.father
        increment_suffix = {
            '': 'II', 'II': 'III', 'III': 'IV', 'IV': 'V', 'V': 'VI',
            'VI': 'VII', 'VII': 'VIII', 'VIII': 'IX', 'IX': 'X'
        }
        if son.full_name_without_suffix == father.full_name_without_suffix:
            suffix = increment_suffix[father.suffix]
        else:
            suffix = ''
        return suffix

    def remunerate(self):
        """Have parents pay hospital for services rendered."""
        config = self.mother.game.config
        service_rendered = self.__class__
        # Pay owner of the hospital
        self.mother.pay(
            payee=self.hospital.owner,
            amount=config.compensations[service_rendered][Owner]
        )
        # Pay doctor
        self.mother.pay(
            payee=self.doctor,
            amount=config.compensations[service_rendered][Doctor]
        )
        # Pay construction workers
        for nurse in self.hospital.nurses:
            self.mother.pay(
                payee=nurse,
                amount=config.compensations[service_rendered][Nurse]
            )


class Death(object):
    """A death of a person in the city."""

    def __init__(self, subject, mortician):
        """Initialize a Death object."""


        self.alive = False
        self.dead = True
        self.cod = cod
        self.year = self.world.year

        # Make gravestone

        gravestone = None

        # Update demographic registries
        self.city.residents.remove(self.subject)
        self.city.deceased.add(self.subject)

        if self.married:
            self.spouse.married = False
            self.spouse.widowed = True
            self.spouse.single = True
            self.marriage_timeline[-1] = (self.marriage_timeline[-1][:-7] +
                                          str(self.death_year) +
                                          ' (death)')
            self.spouse.marriage_timeline[-1] = (
                                     self.spouse.marriage_timeline[-1][:-7] +
                                     str(self.death_year) +
                                     ' (death)')
            # Spouse now grieving

            self.spouse.grieving = True
            years_married = self.world.year-self.marriage_date
            self.spouse.remarry_chance = 1.0/(int(years_married)+4)


class Adoption(object):
    """An adoption of a child by a person(s) who is/are not their biological parent."""

    def __init__(self, subject, adoptive_parents):
        """Initialize an Adoption object.

        @param subject: The adoptee.
        @param adoptive_parents: The adoptive parent(s).
        """
        self.subject = subject
        self.adoptive_parents = adoptive_parents


class Marriage(object):
    """A marriage between two people in the city."""

    def __init__(self, subjects):
        """Initialize a Marriage object."""
        self.subjects = subjects
        self.year = self.subjects[0].city.game.year
        self.names_at_time_of_marriage = (self.subjects[0].name, self.subjects[1].name)
        self.name_changes = []  # Gets set by NameChange object, as appropriate
        self.terminus = None  # May point to a Divorce or Death object
        self.money = None  # Gets set by self.have_newlyweds_pool_money_together()
        self.children_produced = set()  # Gets set by Birth objects, as appropriate
        self.update_newlywed_attributes()
        self.have_newlyweds_pool_money_together()
        self.have_one_spouse_and_possibly_stepchildren_take_the_others_name()
        self.decide_and_enact_new_living_arrangements()
        self.will_hyphenate_child_surnames = self.decide_whether_children_will_get_hyphenated_names()

    def __str__(self):
        """Return string representation."""
        return "{}-year marriage between {} and {}".format(
            self.duration, self.names_at_time_of_marriage[0], self.names_at_time_of_marriage[1]
        )

    @property
    def duration(self):
        """Return the duration of this marriage."""
        if self.terminus:
            duration = self.terminus.year - self.year
        else:
            duration = self.subjects[0].game.year-self.year
        return duration

    def update_newlywed_attributes(self):
        """Update newlywed attributes that pertain to marriage concerns."""
        spouse1, spouse2 = self.subjects
        config = spouse1.game.config
        spouse1.marriage = self
        spouse2.marriage = self
        spouse1.marriages.append(self)
        spouse2.marriages.append(self)
        spouse1.spouse = spouse2
        spouse2.spouse = spouse1
        spouse1.immediate_family.add(spouse2)
        spouse2.immediate_family.add(spouse1)
        spouse1.extended_family |= spouse2.extended_family
        spouse2.extended_family |= spouse1.extended_family
        self.cease_grieving_of_former_spouses(newlyweds=self.subjects)
        self.cease_feelings_for_former_love_interests(newlyweds=self.subjects, config=config)

    @staticmethod
    def cease_grieving_of_former_spouses(newlyweds):
        """Make the newlyweds stop grieving former spouses, if applicable."""
        if any(newlywed for newlywed in newlyweds if newlywed.grieving):
            for newlywed in newlyweds:
                newlywed.grieving = False

    @staticmethod
    def cease_feelings_for_former_love_interests(newlyweds, config):
        """Make the newlyweds (probably) have each other as their strongest love interests."""
        spouse1, spouse2 = newlyweds
        x = random.random()
        if x < config.chance_newlyweds_keep_former_love_interests:
            spouse1.love_interest = spouse2
        elif x < config.chance_newlyweds_keep_former_love_interests * 2:
            spouse2.love_interest = spouse1
        else:
            spouse1.love_interest = spouse2
            spouse2.love_interest = spouse1

    def have_newlyweds_pool_money_together(self):
        """Have the newlyweds combine their money holdings into a single account."""
        self.money = self.subjects[0].money + self.subjects[1].money
        self.subjects[0].money = 0
        self.subjects[1].money = 0

    def have_one_spouse_and_possibly_stepchildren_take_the_others_name(self):
        """Have one spouse (potentially) take the other's name.

        TODO: Have this be affected by the newlyweds' personalities."""
        config = self.subjects[0].game.config
        if any(newlywed for newlywed in self.subjects if newlywed.female):
            spouse_who_may_take_name = next(newlywed for newlywed in self.subjects if newlywed.female)
        else:
            spouse_who_may_take_name = self.subjects[0]
        other_spouse = next(newlywed for newlywed in self.subjects if newlywed is not spouse_who_may_take_name)
        if spouse_who_may_take_name.last_name is not other_spouse.last_name:
            if random.random() < config.chance_one_newlywed_takes_others_name:
                spouse_who_may_take_name.change_name(new_last_name=other_spouse.last_name, reason=self)
        if random.random() < config.chance_stepchildren_take_stepparent_name:
            for stepchild in spouse_who_may_take_name.kids:
                if stepchild.age <= config.age_after_which_stepchildren_will_not_take_stepparent_name:
                    stepchild.change_name(new_last_name=other_spouse.last_name, reason=self)

    def decide_and_enact_new_living_arrangements(self):
        """Handle the full pipeline from finding a place to moving into it."""
        home_they_will_move_into = self.decide_where_newlyweds_will_live()
        self.move_spouses_and_any_kids_in_together(home_they_will_move_into=home_they_will_move_into)

    def decide_where_newlyweds_will_live(self):
        """Decide where the newlyweds will live.

        This may require that they find a vacant lot to build a home on.
        """
        # If one of the newlyweds has their own place, have them move in there
        if any(s for s in self.subjects if s is s.home.owner):
            home_they_will_move_into = next(s for s in self.subjects if s is s.home.owner).home
        else:
            # If they both live at home, have them find a vacant home to move into
            # or a vacant lot to build on (it doesn't matter which person the method is
            # called for -- both will take part in the decision making)
            home_they_will_move_into = self.subjects[0].secure_home()
        return home_they_will_move_into

    def move_spouses_and_any_kids_in_together(self, home_they_will_move_into):
        """Move the two newlyweds (and any kids) in together.

        Note: The family will depart the city (and thus the simulation) if they are
        unable to secure housing.
        """
        spouse1, spouse2 = self.subjects
        family_members_that_will_move = set()
        if home_they_will_move_into is not spouse1.home:
            # Have (non-adult) children of spouse1, if any, also move too
            family_members_that_will_move.add(spouse1)
            for kid in spouse1.kids:
                if kid.alive and kid.home is spouse1.home:
                    family_members_that_will_move.add(kid)
        if home_they_will_move_into is not spouse2.home:
            # Have (non-adult) children of spouse1, if any, also move too
            for kid in spouse2.kids:
                if kid.alive and not kid.married and kid.home is spouse2.home:
                    family_members_that_will_move.add(kid)
        if home_they_will_move_into:
            for family_member in family_members_that_will_move:
                family_member.move(new_home=home_they_will_move_into, reason=self)
        else:
            for family_member in family_members_that_will_move:
                family_member.depart_city()

    def decide_whether_children_will_get_hyphenated_names(self):
        """Decide whether any children resulting from this marriage will get hyphenated names.

        TODO: Have this be affected by newlywed personalities.
        """
        config = self.subjects[0].game.config
        if any(s for s in self.subjects if s.last_name.hyphenated):
            choice = False
        elif random.random() < config.chance_newlyweds_decide_children_will_get_hyphenated_surname:
            choice = True
        else:
            choice = False
        return choice


class Divorce(object):
    """A divorce between two people in the city."""

    def __init__(self, subjects):
        """Initialize a divorce object."""
        self.subjects = subjects
        self.marriage = subjects[0].marriage
        self.year = subjects[0].game.year
        self.marriage.terminus = self
        self.update_divorcee_attributes()
        self.have_divorcees_split_up_money()
        self.have_a_spouse_and_possibly_kids_change_name_back()
        self.decide_and_enact_new_living_arrangements()

    def __str__(self):
        """Return string representation."""
        return "Divorce of {} and {} in {}".format(
            self.subjects[0].name, self.subjects[1].name, self.year
        )

    def update_divorcee_attributes(self):
        """Update divorcee attributes that pertain to marriage concerns."""
        spouse1, spouse2 = self.subjects
        config = spouse1.game.config
        spouse1.marriage = None
        spouse2.marriage = None
        spouse1.spouse = None
        spouse2.spouse = None
        spouse1.divorces.append(self)
        spouse2.divorces.append(self)
        spouse1.immediate_family.remove(spouse2)
        spouse2.immediate_family.remove(spouse1)
        # Revert each back to their own extended families
        spouse1.extended_family = (
            spouse1.greatgrandparents | spouse1.immediate_family | spouse1.uncles | spouse1.aunts |
            spouse1.cousins | spouse1.nieces | spouse1.nephews
        )
        spouse2.extended_family = (
            spouse2.greatgrandparents | spouse2.immediate_family | spouse2.uncles | spouse2.aunts |
            spouse2.cousins | spouse2.nieces | spouse2.nephews
        )
        self.have_divorcees_fall_out_of_love(divorcees=self.subjects, config=config)

    @staticmethod
    def have_divorcees_fall_out_of_love(divorcees, config):
        """Make the divorcees (probably) lose each other as their strongest love interests."""
        spouse1, spouse2 = divorcees
        if random.random() < config.chance_a_divorcee_falls_out_of_love:
            spouse1.love_interest = None
        if random.random() < config.chance_a_divorcee_falls_out_of_love:
            spouse2.love_interest = None

    def have_divorcees_split_up_money(self):
        """Have the divorcees split their money up (50/50)."""
        money_to_split_up = self.marriage.money
        amount_given_to_each = money_to_split_up / 2
        self.subjects[0].money = amount_given_to_each
        self.subjects[1].money = amount_given_to_each

    def have_a_spouse_and_possibly_kids_change_name_back(self):
        """Have a spouse and kids potentially change their names back."""
        config = self.subjects[0].game.config
        chance_of_a_name_reversion = config.function_to_derive_chance_spouse_changes_name_back(
            years_married=self.marriage.duration
        )
        if random.random() < chance_of_a_name_reversion:
            for name_change in self.marriage.name_changes:
                name_change.subject.change_name(
                    subject=name_change.subject, new_last_name=name_change.old_last_name, reason=self
                )

    def decide_and_enact_new_living_arrangements(self):
        """Handle the full pipeline from discussion to one spouse (and possibly kids) moving out."""
        spouse_who_will_move_out = self.decide_who_will_move_out()
        kids_who_will_move_out_also = self.decide_which_kids_will_move_out()
        family_members_who_will_move = {spouse_who_will_move_out} | kids_who_will_move_out_also
        home_spouse_will_move_to = self.decide_where_spouse_moving_out_will_live(
            spouse_who_will_move=spouse_who_will_move_out
        )
        self.move_spouse_and_possibly_kids_out(
            home_spouse_will_move_to=home_spouse_will_move_to, family_members_who_will_move=family_members_who_will_move
        )

    def decide_who_will_move_out(self):
        """Decide which of the divorcees will move out."""
        spouse1, spouse2 = self.subjects
        config = spouse1.game.config
        if spouse1.male:
            if random.random() < config.chance_a_male_divorcee_is_one_who_moves_out:
                spouse_who_will_move_out = spouse1
            else:
                spouse_who_will_move_out = spouse2
        elif spouse2.male:
            if random.random() < config.chance_a_male_divorcee_is_one_who_moves_out:
                spouse_who_will_move_out = spouse2
            else:
                spouse_who_will_move_out = spouse2
        else:
            spouse_who_will_move_out = spouse1
        return spouse_who_will_move_out

    def decide_which_kids_will_move_out(self, spouse_moving):
        """Decide which kids will also be moving out, if any.

        This currently only has stepkids to the spouse who is staying move out
        along with the spouse who is moving out (who in this case would be their only
        biological parent in the marriage).
        """
        spouse_staying = next(s for s in self.subjects if s is not spouse_moving)
        # In case of a blended family, have kids go with their own parent (these
        # will be empty sets otherwise)
        living_with_spouse_moving = spouse_moving.kids - spouse_staying.kids
        # Have any kids they had together stay in the home with that spouse
        return living_with_spouse_moving

    @staticmethod
    def decide_where_spouse_moving_out_will_live(spouse_who_will_move):
        """Decide where the spouse who is moving out will live.

        This may require that they find a vacant lot to build a home on.
        """
        home_spouse_will_move_into = spouse_who_will_move.secure_home()
        return home_spouse_will_move_into

    def move_spouse_and_possibly_kids_out(self, home_spouse_will_move_to, family_members_who_will_move):
        """Move the two newlyweds (and any kids) in together.

        Note: The spouse/kids will depart the city (and thus the simulation) if they are
        unable to secure housing.
        """
        if home_spouse_will_move_to:
            for family_member in family_members_who_will_move:
                family_member.move(new_home=home_spouse_will_move_to, reason=self)
        else:
            for family_member in family_members_who_will_move:
                family_member.depart_city()


class NameChange(object):
    """A (legal) name change someone makes."""

    def __init__(self, subject, new_last_name, reason):
        """Initialize a NameChange object."""
        self.subject = subject
        self.old_last_name = subject.last_name
        self.new_last_name = new_last_name
        self.old_name = subject.name
        # Actually change the name
        subject.last_name = new_last_name
        self.new_name = subject.name
        self.reason = reason  # Likely will point to a Marriage object
        if isinstance(reason, Marriage):
            reason.name_changes.append(self)
        subject.name_changes.append(self)

    def __str__(self):
        """Return string representation."""
        return "Name change by which {} became known as {}".format(
            self.old_name, self.new_name
        )


class Move(object):
    """A move from one home into another, or from no home to a home."""

    def __init__(self, subject, new_home, reason):
        """Initialize a Move object."""
        self.subject = subject
        self.old_home = subject.home  # May be None if newborn or person moved from outside the city
        self.new_home = new_home
        self.old_home.move_outs.append(self)
        self.old_home.move_ins.append(self)
        self.year = self.subject.city.game.year
        self.reason = reason  # Likely will point to a Marriage or Divorce object
        # Actually move the person
        subject.home = new_home


class HomePurchase(object):
    """A purchase of a home by a person or couple, with the help of a realtor."""

    def __init__(self, clients, home, realtor):
        """Initialize a HomePurchase object."""
        self.clients = clients
        self.home = home
        self.home.transactions.append(self)
        self.realtor = realtor
        self.realty_firm = realtor.company
        self.realtor.home_sales.append(self)
        self.transfer_ownership()
        # Pay the realtor
        self.remunerate()

    def transfer_ownership(self):
        """Transfer ownership of this house to its new owners."""
        self.home.owners = self.clients

    def remunerate(self):
        """Have subject remunerate realty firm for services rendered."""
        config = self.clients[0].game.config
        service_rendered = self.__class__
        # Pay owner of the realty firm
        self.clients[0].pay(
            payee=self.realty_firm.owner,
            amount=config.compensations[service_rendered][Owner]
        )
        # Pay realtor
        self.clients[0].pay(
            payee=self.realtor,
            amount=config.compensations[service_rendered][Realtor]
        )


class Departure(object):
    """A departure by which someone leaves the city (i.e., leaves the simulation)."""

    def __init__(self, subject):
        """Initialize a Departure object."""
        self.subject = subject
        self.year = subject.game.year
        subject.city.residents.remove(subject)
        subject.city.departed.add(subject)
        subject.departure = self


class Hiring(object):
    """A hiring of a person by a company to serve in a specific occupational role."""

    def __init__(self, subject, company, occupation):
        """Initialize a Hiring object."""
        self.subject = subject
        self.company = company
        self.old_occupation = subject.occupation
        self.occupation = occupation
        self.year = self.subject.city.game.year
        # Determine whether this was a promotion
        if subject.occupation and subject.occupation.company is company:
            self.promotion = True
        else:
            self.promotion = False
        # Terminate the person's former occupation, if any
        if subject.occupation:
            subject.occupation.terminate()
        occupation(person=subject, company=company, hiring=self)
        # If this person had a former occupation, have the company that
        # they worked for fill that now vacant position
        if self.old_occupation:
            position_that_is_now_vacant = self.old_occupation.__class__
            self.old_occupation.company.hire(occupation=position_that_is_now_vacant)


class HouseConstruction(object):
    """Construction of a house."""

    def __init__(self, clients, architect, lot):
        """Initialize a HouseConstruction object."""
        self.clients = clients
        self.construction_firm = architect.company
        self.architect = architect
        self.architect.house_constructions.append(self)
        self.builders = self.construction_firm.construction_workers
        self.lot = lot
        self.year = self.clients[0].game.year
        self.house = House(lot=lot, construction=self)

    def remunerate(self):
        """Have client remunerate construction firm for services rendered."""
        config = self.clients[0].game.config
        service_rendered = self.__class__
        # Pay owner of the company
        self.clients[0].pay(
            payee=self.construction_firm.owner,
            amount=config.compensations[service_rendered][Owner]
        )
        # Pay architect
        self.clients[0].pay(
            payee=self.architect,
            amount=config.compensations[service_rendered][Architect]
        )
        # Pay construction workers
        for construction_worker in self.construction_firm.construction_workers:
            self.clients[0].pay(
                payee=construction_worker,
                amount=config.compensations[service_rendered][ConstructionWorker]
            )


class BuildingConstruction(object):
    """Construction of a building."""

    def __init__(self, client, architect, lot, type_of_building):
        """Initialize a BuildingConstruction object."""
        self.client = client
        self.construction_firm = architect.company
        self.architect = architect
        self.architect.building_constructions.append(self)
        self.builders = self.construction_firm.construction_workers
        self.lot = lot
        self.year = self.client.game.year
        self.building = type_of_building(lot=lot, construction=self)

    def remunerate(self):
        """Have client remunerate construction firm for services rendered."""
        config = self.client.game.config
        service_rendered = self.__class__
        # Pay owner of the company
        self.client.pay(
            payee=self.construction_firm.owner,
            amount=config.compensations[service_rendered][Owner]
        )
        # Pay architect
        self.client.pay(
            payee=self.architect,
            amount=config.compensations[service_rendered][Architect]
        )
        # Pay construction workers
        for construction_worker in self.construction_firm.construction_workers:
            self.client.pay(
                payee=construction_worker,
                amount=config.compensations[service_rendered][ConstructionWorker]
            )
