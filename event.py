import random
from person import Person
from city import Lot
from business import *
from residence import *
from occupation import *


class Marriage(object):
    """A marriage between two people in a city."""

    def __init__(self, subjects):
        """Construct a Marriage object."""
        self.subjects = subjects
        self.year = self.subjects[0].city.game.year
        self.names_at_time_of_marriage = (self.subjects[0].name, self.subjects[1].name)
        self.update_newlywed_attributes()
        self.have_one_spouse_and_possibly_stepchildren_take_the_others_name()
        home_they_will_move_into = self.decide_where_newlyweds_will_live()
        self.move_spouses_and_any_kids_in_together(home_they_will_move_into=home_they_will_move_into)

    def __str__(self):
        """Return string representation."""
        return "Marriage between {} and {} in {}".format(
            self.names_at_time_of_marriage[0], self.names_at_time_of_marriage[1], self.year
        )

    def update_newlywed_attributes(self):
        """Update newlywed attributes that pertain to marriage concerns."""
        spouse1, spouse2 = self.subjects
        config = spouse1.game.config
        spouse1.marriages.append(self)
        spouse2.marriages.append(self)
        spouse1.married = True
        spouse2.married = True
        spouse1.single = False
        spouse2.single = False
        spouse1.spouse = spouse2
        spouse2.spouse = spouse1
        spouse1.immediate_family.add(spouse2)
        spouse2.immediate_family.add(spouse1)
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
            if random.random() < 0.1:
                spouse_who_may_take_name.change_name(new_last_name=other_spouse.last_name, reason=self)
        if random.random() < config.chance_stepchildren_take_stepparent_name:
            for stepchild in spouse_who_may_take_name.kids:
                if stepchild.age <= config.age_after_which_stepchildren_will_not_take_stepparent_name:
                    stepchild.change_name(new_last_name=other_spouse.last_name, reason=self)

    def decide_where_newlyweds_will_live(self):
        """Decide where the newlyweds will live.

        This may require that they find a vacant lot to build a home on."""
        # If one of the newlyweds has their own place, have them move in there
        if any(s for s in self.subjects if s is s.home.owner):
            home_they_will_move_into = next(s for s in self.subjects if s is s.home.owner).home
        else:
            # If they both live at home, have them find a vacant home to move into
            # or a vacant lot to build on (it doesn't matter which person the method is
            # called for -- both will take part in the decision making)
            newlyweds = self.subjects[0]
            chosen_home_or_lot = newlyweds.choose_vacant_home_or_vacant_lot()
            if isinstance(chosen_home_or_lot, Lot):  # They chose a vacant lot
                architect = newlyweds.hire_person_of_certain_occupation(occupation=Architect)
                home_they_will_move_into = architect.construct_building(
                    client=newlyweds, lot=chosen_home_or_lot, type_of_building=House
                )
            else:  # They chose a vacant home
                home_they_will_move_into = chosen_home_or_lot
        return home_they_will_move_into

    def move_spouses_and_any_kids_in_together(self, home_they_will_move_into):
        """Move the two newlyweds (and any kids) in together."""
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
        for family_member in family_members_that_will_move:
            family_member.move(new_home=home_they_will_move_into, reason=self)


class NameChange(object):
    """A (legal) name change someone makes."""

    def __init__(self, subject, new_last_name, reason):
        """Construct a NameChange object."""
        self.subject = subject
        self.old_last_name = subject.last_name
        self.new_last_name = new_last_name
        self.old_name = subject.name
        # Actually change the name
        subject.last_name = new_last_name
        self.new_name = subject.name
        self.reason = reason  # Likely will point to a Marriage object
        subject.name_changes.append(self)

    def __str__(self):
        """Return string representation."""
        return "Name change by which {} became known as {}".format(
            self.old_name, self.new_name
        )


class Move(object):
    """A move from one home into another, or from no home to a home."""

    def __init__(self, subject, new_home, reason):
        """Construct a Move object."""
        self.subject = subject
        self.old_home = subject.home  # May be None if newborn or person moved from outside the city
        self.new_home = new_home
        self.year = self.subject.city.game.year
        self.reason = reason  # Likely will point to a Marriage object
        # Actually move the person
        subject.home = new_home


class BuildingConstruction(object):
    """Construction of a building."""

    def __init__(self, architect, client, lot, type_of_building):
        """Construct a BuildingConstruction object."""
        self.city = architect.city
        self.client = client
        self.construction_firm = architect.company
        self.architect = architect
        self.builders = self.construction_firm.construction_workers
        self.lot = lot
        self.year = self.city.year
        self.building = type_of_building(lot=lot, construction=self)

    def remunerate(self):
        """Have client remunerate architect and construction workers for services rendered."""
        config = self.city.game.config
        # Pay owner of the company
        self.client.pay(
            payee=self.construction_firm.owner, amount=config.compensation_for_construction_firm_owner
        )
        # Pay architect
        self.client.pay(payee=self.architect, amount=config.compensation_for_architect)
        # Pay construction workers
        for construction_worker in self.construction_firm.construction_workers:
            self.client.pay(payee=construction_worker, amount=config.compensation_for_construction_worker)




