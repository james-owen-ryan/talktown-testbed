import random
from name import Name
from person import Person
from corpora import Names
from residence import House


class Adoption(object):
    """An adoption of a child by a person(s) who is/are not their biological parent."""

    def __init__(self, subject, adoptive_parents):
        """Initialize an Adoption object.

        @param subject: The adoptee.
        @param adoptive_parents: The adoptive parent(s).
        """
        self.year = subject.year
        self.city = adoptive_parents[0].city  # May be None if parents not in the city yet
        self.subject = subject
        self.adoptive_parents = adoptive_parents


class Birth(object):
    """A birth of a person."""

    def __init__(self, mother, doctor):
        """Initialize a Birth object."""
        self.year = mother.game.year
        self.city = mother.city
        self.biological_mother = mother
        self.mother = mother
        self.biological_father = mother.impregnated_by
        self.father = self.mother.spouse if self.mother.spouse and self.mother.spouse.male else None
        if self.father and self.father is not self.biological_father:
            self.adoption = Adoption(subject=self.subject, adoptive_parents=(self.father,))
        self.subject = Person(game=mother.game, birth=self)
        if self.biological_father is self.mother.spouse:
            self.mother.marriage.children_produced.add(self.subject)
        self.doctor = doctor
        self._name_baby()
        if self.doctor:  # There won't be a doctor if the birth happened outside the city
            self.hospital = doctor.company
            self.nurses = {
                position for position in self.hospital.employees if
                position.__class__.__name__ == 'Nurse'
            }
            self.doctor.baby_deliveries.add(self)
            self._remunerate()
        else:
            self.hospital = None
            self.nurses = set()

    def _update_mother_attributes(self):
        """Update attributes of the mother that are affected by this birth."""
        self.mother.conception_date = None
        self.mother.impregnated_by = None

    def _name_baby(self):
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
        self.subject.maiden_name = self.subject.last_name

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
            self.father.last_name, self.mother.last_name
        )
        # Check if this child will be the progenitor of this hyphenated surname, i.e.,
        # whether an older sibling has already been given it
        if any(k for k in self.mother.marriage.children_produced if k.maiden_name == hyphenated_last_name):
            older_sibling_with_hyphenated_surname = next(
                k for k in self.mother.marriage.children_produced if k.maiden_name == hyphenated_last_name
            )
            hyphenated_surname_object = older_sibling_with_hyphenated_surname.maiden_name
        else:
            # Instantiate a new Name object with this child as the progenitor
            hyphenated_surname_object = Name(
                hyphenated_last_name, progenitor=self.subject, conceived_by=self.subject.parents,
                derived_from=(self.mother.last_name, self.father.last_name,)
            )
        return hyphenated_surname_object

    def _decide_first_name(self, potential_namegivers):
        """Return what will be the baby's first name."""
        config = self.subject.game.config
        if potential_namegivers and random.random() < config.chance_child_inherits_first_name:
            first_name_namegiver = random.choice(potential_namegivers)
            first_name = first_name_namegiver.first_name
        else:
            first_name_namegiver = None
            first_name_rep = Names.a_masculine_name() if self.subject.male else Names.a_feminine_name()
            first_name = Name(
                value=first_name_rep, progenitor=self.subject, conceived_by=self.subject.parents, derived_from=()
            )
        return first_name, first_name_namegiver

    def _decide_middle_name(self, potential_namegivers):
        """Return what will be the baby's first name."""
        config = self.subject.game.config
        if potential_namegivers and random.random() < config.chance_child_inherits_middle_name:
            middle_name_namegiver = random.choice(potential_namegivers)
            middle_name = middle_name_namegiver.first_name
        else:
            middle_name_namegiver = None
            middle_name_rep = Names.a_masculine_name() if self.subject.male else Names.a_feminine_name()
            middle_name = Name(
                value=middle_name_rep, progenitor=self.subject, conceived_by=self.subject.parents, derived_from=()
            )
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

    def _remunerate(self):
        """Have parents pay hospital for services rendered."""
        config = self.mother.game.config
        service_rendered = self.__class__
        # Pay doctor
        self.mother.pay(
            payee=self.doctor.person,
            amount=config.compensations[service_rendered][self.doctor.__class__]
        )
        # Pay nurses
        for nurse in self.nurses:
            self.mother.pay(
                payee=nurse.person,
                amount=config.compensations[service_rendered][nurse.__class__]
            )


class BusinessConstruction(object):
    """Construction of the building where a business is headquartered.

    This must be preceded by the business being founded -- the business makes the
    call to instantiate one of these objects -- where in a HouseConstruction the
    direction is opposite: a HouseConstruction object makes the call to instantiate
    a House object.
    """

    def __init__(self, subject, business, architect):
        """Initialize a BusinessConstruction object."""
        self.year = subject.game.year
        self.subject = subject
        self.architect = architect
        self.business = business
        if self.architect:
            self.construction_firm = architect.company
            self.builders = set([
                position for position in self.construction_firm.employees if
                position.__class__.__name__ == 'ConstructionWorker'
            ])
            self._remunerate()
            self.architect.building_constructions.add(self)
        else:
            self.construction_firm = None
            self.builders = set()
        self.subject.building_commissions.add(self)

    def _remunerate(self):
        """Have client pay construction firm for services rendered."""
        config = self.subject.game.config
        service_rendered = self.__class__
        # Pay owner of the company
        self.subject.pay(
            payee=self.construction_firm.owner.person,
            amount=config.compensations[service_rendered][self.construction_firm.owner.__class__]
        )
        # Pay architect
        self.subject.pay(
            payee=self.architect.person,
            amount=config.compensations[service_rendered][self.architect.__class__]
        )
        # Pay construction workers
        for construction_worker in self.builders:
            self.subject.pay(
                payee=construction_worker.person,
                amount=config.compensations[service_rendered][construction_worker.__class__]
            )


class Death(object):
    """A death of a person in the city."""

    def __init__(self, subject, mortician, cause_of_death):
        """Initialize a Death object."""
        self.year = subject.game.year
        self.city = subject.city
        self.subject = self.subject
        self.cause = cause_of_death
        self.mortician = mortician
        self.cemetery = self.mortician.company
        self.next_of_kin = subject.next_of_kin
        subject.city.population.remove(subject)
        subject.city.deceased.add(subject)
        self._update_attributes_of_deceased_and_spouse()
        self._vacate_job_position_of_the_deceased()
        if self.city:
            # Death shouldn't be possibly outside the city, but I'm doing
            # this to be consistent with other event classes
            self._remunerate()
            self.cemetery_plot = self._inter_the_body()
            self.mortician.bodies_interred.add(self)
        else:
            self.cemetery_plot = None

    def _update_attributes_of_deceased_and_spouse(self):
        config = self.subject.game.config
        self.subject.alive = False
        if self.subject.marriage:
            widow = self.subject.spouse
            widow.marriage.terminus = self
            widow.marriage = None
            widow.spouse = None
            widow.widowed = True
            widow.grieving = True
            widow.chance_of_remarrying = config.function_to_derive_chance_spouse_changes_name_back(
                years_married=self.subject.marriage.duration
            )

    def _vacate_job_position_of_the_deceased(self):
        """Vacate the deceased's job position, if any."""
        if self.subject.occupation:
            self.subject.occupation.terminate(reason=self)

    def _inter_the_body(self):
        """Inter the body at the local cemetery."""
        return self.cemetery.inter_person(person=self.subject)

    def _remunerate(self):
        """Have deceased's next of kin pay mortician for services rendered."""
        config = self.subject.game.config
        service_rendered = self.__class__
        # Pay mortician
        self.next_of_kin.pay(
            payee=self.mortician.person,
            amount=config.compensations[service_rendered][self.mortician.__class__]
        )


class Departure(object):
    """A departure by which someone leaves the city (i.e., leaves the simulation)."""

    def __init__(self, subject):
        """Initialize a Departure object."""
        self.year = subject.game.year
        self.subject = subject
        subject.city.population.remove(subject)
        subject.city.departed.add(subject)
        subject.departure = self
        self._vacate_job_position_of_the_departed()

    def _vacate_job_position_of_the_departed(self):
        """Vacate the departed's job position, if any."""
        if self.subject.occupation:
            self.subject.occupation.terminate(reason=self)


class Divorce(object):
    """A divorce between two people in the city."""

    def __init__(self, subjects, lawyer):
        """Initialize a divorce object."""
        self.year = subjects[0].game.year
        self.city = subjects[0].city
        self.subjects = subjects
        self.lawyer = lawyer
        self.marriage = subjects[0].marriage
        self.marriage.terminus = self
        self._update_divorcee_attributes()
        self._have_divorcees_split_up_money()
        self._have_a_spouse_and_possibly_kids_change_name_back()
        if self.city:
            # Divorce isn't currently possible outside a city, but still
            # doing this to be consistent with other event classes
            self.law_firm = lawyer.company
            self.lawyer.divorces_filed.add(self)
            self._decide_and_enact_new_living_arrangements()
            self._remunerate()
        else:
            self.law_firm = None

    def __str__(self):
        """Return string representation."""
        return "Divorce of {} and {} in {}".format(
            self.subjects[0].name, self.subjects[1].name, self.year
        )

    def _update_divorcee_attributes(self):
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
        self._have_divorcees_fall_out_of_love(divorcees=self.subjects, config=config)

    @staticmethod
    def _have_divorcees_fall_out_of_love(divorcees, config):
        """Make the divorcees (probably) lose each other as their strongest love interests."""
        spouse1, spouse2 = divorcees
        if random.random() < config.chance_a_divorcee_falls_out_of_love:
            spouse1.fall_out_of_love()
        if random.random() < config.chance_a_divorcee_falls_out_of_love:
            spouse2.fall_out_of_love()

    def _have_divorcees_split_up_money(self):
        """Have the divorcees split their money up (50/50)."""
        money_to_split_up = self.marriage.money
        amount_given_to_each = money_to_split_up / 2
        self.subjects[0].money = amount_given_to_each
        self.subjects[1].money = amount_given_to_each

    def _have_a_spouse_and_possibly_kids_change_name_back(self):
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

    def _decide_and_enact_new_living_arrangements(self):
        """Handle the full pipeline from discussion to one spouse (and possibly kids) moving out."""
        spouse_who_will_move_out = self._decide_who_will_move_out()
        kids_who_will_move_out_also = self._decide_which_kids_will_move_out()
        family_members_who_will_move = {spouse_who_will_move_out} | kids_who_will_move_out_also
        home_spouse_will_move_to = self._decide_where_spouse_moving_out_will_live(
            spouse_who_will_move=spouse_who_will_move_out
        )
        self._move_spouse_and_possibly_kids_out(
            home_spouse_will_move_to=home_spouse_will_move_to, family_members_who_will_move=family_members_who_will_move
        )

    def _decide_who_will_move_out(self):
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

    def _decide_which_kids_will_move_out(self, spouse_moving):
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
    def _decide_where_spouse_moving_out_will_live(spouse_who_will_move):
        """Decide where the spouse who is moving out will live.

        This may require that they find a vacant lot to build a home on.
        """
        home_spouse_will_move_into = spouse_who_will_move.secure_home()
        return home_spouse_will_move_into

    def _move_spouse_and_possibly_kids_out(self, home_spouse_will_move_to, family_members_who_will_move):
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

    def _remunerate(self):
        """Have divorcees pay law firm for services rendered."""
        config = self.subjects[0].game.config
        service_rendered = self.__class__
        # Pay owner of the law firm -- divorcees split the cost 50/50
        amount_due_to_owner = config.compensations[service_rendered][self.law_firm.owner.__class__]
        amount_due_to_lawyer = config.compensations[service_rendered][self.lawyer.__class__]
        for divorcee in self.subjects:
            divorcee.pay(
                payee=self.law_firm.owner.person,
                amount=amount_due_to_owner/2
            )
            divorcee.pay(
                payee=self.lawyer.person,
                amount=amount_due_to_lawyer/2
            )


class Hiring(object):
    """A hiring of a person by a company to serve in a specific occupational role.

    TODO: Add in data about who they beat out for the job.
    """

    def __init__(self, subject, company, occupation):
        """Initialize a Hiring object."""
        self.year = subject.game.year
        self.subject = subject
        self.company = company
        self.old_occupation = subject.occupation
        self.occupation = occupation
        # Determine whether this was a promotion
        if self.old_occupation and self.old_occupation.company is self.company:
            self.promotion = True
        else:
            self.promotion = False
        self.occupation.hiring = self


class HomePurchase(object):
    """A purchase of a home by a person or couple, with the help of a realtor."""

    def __init__(self, subjects, home, realtor):
        """Initialize a HomePurchase object."""
        self.year = subjects[0].game.year
        self.city = subjects[0].city
        self.subjects = subjects
        self.home = home
        self.home.transactions.append(self)
        self.realtor = realtor
        self._transfer_ownership()
        if realtor:
            self.realty_firm = realtor.company
            self._remunerate()
            self.realtor.home_sales.add(self)
        else:  # No realtor when setting initial owners as people who built the home
            self.realty_firm = None

    def _transfer_ownership(self):
        """Transfer ownership of this house to its new owners."""
        self.home.former_owners |= set(self.home.owners)
        self.home.owners = self.subjects
        self.home.transactions.append(self)

    def _remunerate(self):
        """Have subject pay realty firm for services rendered."""
        config = self.subjects[0].game.config
        service_rendered = self.__class__
        # Pay owner of the realty firm
        self.subjects[0].pay(
            payee=self.realty_firm.owner.person,
            amount=config.compensations[service_rendered][self.realty_firm.owner.__class__]
        )
        # Pay realtor
        self.subjects[0].pay(
            payee=self.realtor.person,
            amount=config.compensations[service_rendered][self.realtor.__class__]
        )


class HouseConstruction(object):
    """Construction of a house."""

    def __init__(self, subjects, architect, lot):
        """Initialize a HouseConstruction object."""
        self.year = subjects[0].game.year
        self.subjects = subjects
        self.architect = architect
        self.house = House(lot=lot, construction=self)
        if self.architect:
            self.construction_firm = architect.company
            self.builders = {
                position for position in self.construction_firm.employees if
                position.__class__.__name__ == 'ConstructionWorker'
            }
            self._remunerate()
            self.architect.building_constructions.add(self)
        else:
            self.construction_firm = None
            self.builders = set()
        for subject in self.subjects:
            subject.building_commissions.add(self)

    def _remunerate(self):
        """Have client pay construction firm for services rendered."""
        config = self.subjects[0].game.config
        service_rendered = self.__class__
        # Pay owner of the company
        self.subjects[0].pay(
            payee=self.construction_firm.owner.person,
            amount=config.compensations[service_rendered][self.construction_firm.owner.__class__]
        )
        # Pay architect
        self.subjects[0].pay(
            payee=self.architect.person,
            amount=config.compensations[service_rendered][self.architect.__class__]
        )
        # Pay construction workers
        for construction_worker in self.builders:
            self.subjects[0].pay(
                payee=construction_worker.person,
                amount=config.compensations[service_rendered][construction_worker.__class__]
            )


class Marriage(object):
    """A marriage between two people in the city."""

    def __init__(self, subjects):
        """Initialize a Marriage object."""
        self.year = subjects[0].game.year
        self.city = subjects[0].city
        self.subjects = subjects
        self.names_at_time_of_marriage = (self.subjects[0].name, self.subjects[1].name)
        self.name_changes = []  # Gets set by NameChange object, as appropriate
        self.terminus = None  # May point to a Divorce or Death object, as determined by self.terminate()
        self.money = None  # Gets set by self._have_newlyweds_pool_money_together()
        self.children_produced = set()  # Gets set by Birth objects, as appropriate
        self._update_newlywed_attributes()
        self._have_newlyweds_pool_money_together()
        self._have_one_spouse_and_possibly_stepchildren_take_the_others_name()
        if self.city:
            self._decide_and_enact_new_living_arrangements()
            # If they're not in the city yet (marriage between two PersonsExNihilo during
            # world generation), living arrangements will be made once they move into it
        self.will_hyphenate_child_surnames = self._decide_whether_children_will_get_hyphenated_names()

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

    def _update_newlywed_attributes(self):
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
        self._cease_grieving_of_former_spouses(newlyweds=self.subjects)
        self._cease_feelings_for_former_love_interests(newlyweds=self.subjects, config=config)

    @staticmethod
    def _cease_grieving_of_former_spouses(newlyweds):
        """Make the newlyweds stop grieving former spouses, if applicable."""
        if any(newlywed for newlywed in newlyweds if newlywed.grieving):
            for newlywed in newlyweds:
                newlywed.grieving = False

    @staticmethod
    def _cease_feelings_for_former_love_interests(newlyweds, config):
        """Make the newlyweds (probably) have each other as their strongest love interests."""
        spouse1, spouse2 = newlyweds
        x = random.random()
        if x < config.chance_a_newlywed_keeps_former_love_interest:
            # Only spouse1 guaranteed to have fallen in love
            spouse1.fall_in_love(person=spouse2)
        elif x < config.chance_a_newlywed_keeps_former_love_interest * 2:
            spouse2.fall_in_love(person=spouse1)
        else:
            spouse1.fall_in_love(person=spouse2)
            spouse2.fall_in_love(person=spouse1)

    def _have_newlyweds_pool_money_together(self):
        """Have the newlyweds combine their money holdings into a single account."""
        self.money = self.subjects[0].money + self.subjects[1].money
        self.subjects[0].money = 0
        self.subjects[1].money = 0

    def _have_one_spouse_and_possibly_stepchildren_take_the_others_name(self):
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

    def _decide_and_enact_new_living_arrangements(self):
        """Handle the full pipeline from finding a place to moving into it."""
        home_they_will_move_into = self._decide_where_newlyweds_will_live()
        self._move_spouses_and_any_kids_in_together(home_they_will_move_into=home_they_will_move_into)

    def _decide_where_newlyweds_will_live(self):
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

    def _move_spouses_and_any_kids_in_together(self, home_they_will_move_into):
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
                if kid.present and kid.home is spouse1.home:
                    family_members_that_will_move.add(kid)
        if home_they_will_move_into is not spouse2.home:
            # Have (non-adult) children of spouse1, if any, also move too
            for kid in spouse2.kids:
                if kid.present and not kid.marriage and kid.home is spouse2.home:
                    family_members_that_will_move.add(kid)
        if home_they_will_move_into:
            for family_member in family_members_that_will_move:
                family_member.move(new_home=home_they_will_move_into, reason=self)
        else:
            for family_member in family_members_that_will_move:
                family_member.depart_city()

    def _decide_whether_children_will_get_hyphenated_names(self):
        """Decide whether any children resulting from this marriage will get hyphenated names.

        TODO: Have this be affected by newlywed personalities.
        """
        if self.subjects[0].last_name != self.subjects[1].last_name:  # First, make sure they have different surnames
            config = self.subjects[0].game.config
            if any(s for s in self.subjects if s.last_name.hyphenated):
                choice = False
            elif random.random() < config.chance_newlyweds_decide_children_will_get_hyphenated_surname:
                choice = True
            else:
                choice = False
        else:
            choice = False
        return choice


class Move(object):
    """A move from one home into another, or from no home to a home."""

    def __init__(self, subjects, new_home, reason):
        """Initialize a Move object."""
        self.year = subjects[0].game.year
        self.subjects = subjects
        self.old_home = self.subjects[0].home  # May be None if newborn or person moved from outside the city
        self.new_home = new_home
        if self.old_home:
            self.old_home.move_outs.append(self)
        self.new_home.move_ins.append(self)
        self.reason = reason  # Will (likely) point to an Occupation object, or else a Marriage or Divorce object
        # Actually move the person(s)
        for person in self.subjects:
            # Move out of old home, if any
            if person.home:
                person.home.residents.remove(person)
                person.home.former_residents.add(person)
            # Move into new home
            person.home = new_home
            new_home.residents.add(person)
            person.moves.append(self)
            # Add yourself to city residents, if you moved from outside the city
            person.city = person.game.city
            person.game.city.residents.add(person)


class NameChange(object):
    """A (legal) name change someone makes."""

    def __init__(self, subject, new_last_name, reason, lawyer):
        """Initialize a NameChange object."""
        self.year = subject.game.year
        self.city = subject.city
        self.subject = subject
        self.old_last_name = subject.last_name
        self.new_last_name = new_last_name
        self.old_name = subject.name
        self.lawyer = lawyer
        # Actually change the name
        subject.last_name = new_last_name
        self.new_name = subject.name
        self.reason = reason  # Likely will point to a Marriage or Divorce object
        if isinstance(reason, Marriage):
            reason.name_changes.append(self)
        subject.name_changes.append(self)
        if self.city:
            self.law_firm = lawyer
            self.lawyer.filed_name_changes.add(self)
        else:
            self.law_firm = None

    def __str__(self):
        """Return string representation."""
        return "Name change by which {} became known as {}".format(
            self.old_name, self.new_name
        )

    def _remunerate(self):
        """Have name changer pay law firm for services rendered."""
        config = self.subject.game.config
        service_rendered = self.__class__
        # Pay owner of the law firm
        self.subject.pay(
            payee=self.law_firm.owner.person,
            amount=config.compensations[service_rendered][self.law_firm.owner.__class__]
        )
        # Pay lawyer
        self.subject.pay(
            payee=self.lawyer.person,
            amount=config.compensations[service_rendered][self.lawyer.__class__]
        )



