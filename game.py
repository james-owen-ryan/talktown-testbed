from config import Config
from person import *
from business import *
from city import *
import datetime


class Game(object):
    """A gameplay instance."""

    def __init__(self):
        """Initialize a Game object."""
        # This gets incremented each time a new person is born/generated,
        # which affords a persistent ID for each person
        self.current_person_id = 0
        self.current_place_id = 0
        self.config = Config()
        self.year = self.config.date_city_gets_founded[0]
        self.true_year = self.config.date_city_gets_founded[0]  # True year never gets changed during retconning
        self.ordinal_date = datetime.date(*self.config.date_city_gets_founded).toordinal()  # Days since 01-01-0001
        self.month = datetime.date(*self.config.date_city_gets_founded).month
        self.day = datetime.date(*self.config.date_city_gets_founded).day
        self.ordinal_date_that_gameplay_begins = (
            datetime.date(*self.config.date_gameplay_begins).toordinal()
        )
        self.time_of_day = "day"
        self.date = self.get_date()
        self.city = None
        # Prepare a listing of all in-game events, which will facilitate debugging later
        self.events = []
        # A game's event number allows the precise ordering of events that
        # happened on the same timestep -- every time an event happens, it requests an
        # event number from Game.assign_event_number(), which also increments the running counter
        self.event_number = 0
        # Prepare a listing of all people born on each day -- this is used to
        # age people on their birthdays; we start with (2, 29) initialized because
        # we need to perform a check every March 1 to ensure that all leap-year babies
        # celebrate their birthday that day on non-leap years
        self.birthdays = {(2, 29): set()}
        # Prepare various Talk of the Town variables
        self.founder = None  # The person who founds the city -- gets set by self.establish_setting()
        self.lover = None
        self.pc = None

        # self.establish_setting()
        # self._sim_and_save_a_week_of_timesteps()

    @property
    def random_person(self):
        """Return a random person living in the city of this gameplay instance."""
        return random.choice(list(self.city.residents))

    def recent_events(self):
        """Pretty-print the last five in-game events."""
        for recent_event in self.events[-5:]:
            print recent_event

    def establish_setting(self):
        """Establish the city in which this gameplay instance will take place."""
        # Generate a city plan with at least two tracts
        self.city = City(self)
        while len(self.city.tracts) < 2:
            self.city = City(self)
        # Have families establish farms on all of the city tracts except one,
        # which will be a cemetery
        for i in xrange(len(self.city.tracts)-2):
            farmer = PersonExNihilo(game=self, job_opportunity_impetus=Farmer, spouse_already_generated=None)
            Farm(owner=farmer)
            # farmer.move_into_the_city(hiring_that_instigated_move=farmer.occupation)  # SHOULD BE ABLE TO DELETE THIS
        # For the last tract, potentially have a quarry or coal mine instead of a farm
        if random.random() < self.config.chance_of_a_coal_mine_at_time_of_town_founding:
            owner = PersonExNihilo(game=self, job_opportunity_impetus=Owner, spouse_already_generated=None)
            CoalMine(owner=owner)
            self.city.mayor = owner  # TODO actual mayor stuff
        elif random.random() < self.config.chance_of_a_quarry_at_time_of_town_founding:
            owner = PersonExNihilo(game=self, job_opportunity_impetus=Owner, spouse_already_generated=None)
            Quarry(owner=owner)
            self.city.mayor = owner  # TODO actual mayor stuff
        else:
            farmer = PersonExNihilo(game=self, job_opportunity_impetus=Farmer, spouse_already_generated=None)
            Farm(owner=farmer)
            self.city.mayor = farmer  # TODO actual mayor stuff
        # Name the city -- has to come before the cemetery is instantiated,
        # so that the cemetery can be named after it
        self.city.name = self._generate_name_for_city()
        # Establish a cemetery -- it doesn't matter who the owner is for
        # public institutions like a cemetery, it will just be used as a
        # reference with which to access this game instance
        Cemetery(owner=self.random_person)
        # Now simulate to a week before gameplay
        n_days_until_gameplay_begins = self.ordinal_date_that_gameplay_begins-self.ordinal_date
        n_days_until_hi_fi_sim_begins = n_days_until_gameplay_begins - 7
        n_timesteps_until_hi_fi_sim_begins = n_days_until_hi_fi_sim_begins * 2
        self.enact_lo_fi_simulation(n_timesteps=n_timesteps_until_hi_fi_sim_begins)
        # Now simulate at full fidelity for the remaining week
        while self.ordinal_date < self.ordinal_date_that_gameplay_begins:
            self.enact_hi_fi_simulation()
            print "{} days remain until gameplay begins".format(
                self.ordinal_date_that_gameplay_begins-self.ordinal_date
            )
        # Simulate the night in question, on which the founder dies
        self.enact_hi_fi_simulation()

    def _generate_name_for_city(self):
        """Generate a name for the city."""
        if random.random() < self.config.chance_city_gets_named_for_founder:
            name = self.city.mayor.last_name
        else:
            name = Names.a_place_name()
        return name

    def _select_player_character(self):
        if any(k for k in self.founder.kids | self.founder.grandchildren if k.present):
            player_character = next(
                k for k in self.founder.kids | self.founder.grandchildren if k.present
            )
        else:
            player_character = random.choice([p for p in self.city.residents if p.adult])
        return player_character

    def _determine_initial_evidence_about_lover_appearance(self):
        true_and_false_values = [True, True, True, False, False]
        feature_types_of_initial_evidence = ["head shape", "hair color", "hair length", "eye color", "nose shape"]
        random.shuffle(true_and_false_values)
        initial_evidence = {}
        for i in xrange(len(feature_types_of_initial_evidence)):
            feature_type = feature_types_of_initial_evidence[i]
            true_feature = str(self.lover.get_feature(feature_type=feature_type))
            true_or_false = true_and_false_values[i]
            if true_or_false is True:
                initial_evidence[feature_type] = true_feature
            else:
                # Mutate the true feature into a false one
                x = random.random()
                mutated_feature = next(  # See config.py to understand what this is doing
                    mutation[1] for mutation in self.config.memory_mutations[feature_type][true_feature] if
                    mutation[0][0] <= x <= mutation[0][1]
                )
                initial_evidence[feature_type] = mutated_feature
        if initial_evidence["hair color"] == "blonde":  # Don't make them assume female lover
            initial_evidence["hair color"] = "blond(e)"
        if initial_evidence["hair length"] == "bald":
            hair_str = "a bald head"
        elif initial_evidence["hair length"] == "medium":
            hair_str = "medium-length {0} hair".format(initial_evidence["hair color"])
        else:
            hair_str = "{0} {1} hair".format(initial_evidence["hair length"], initial_evidence["hair color"])
        initial_evidence_str = (
            "a {0}-shaped head, {1}, a {2} nose, and {3} eyes".format(
                initial_evidence["head shape"], hair_str, initial_evidence["nose shape"],
                initial_evidence["eye color"],
            )
        )
        return initial_evidence, initial_evidence_str

    def assign_event_number(self, new_event):
        """Assign an event number to some event, to allow for precise ordering of events that happened same timestep.

        Also add the event to a listing of all in-game events; this facilitates debugging.
        """
        self.events.append(new_event)
        self.event_number += 1
        return self.event_number

    @staticmethod
    def get_random_day_of_year(year):
        """Return a randomly chosen day in the given year."""
        ordinal_date_on_jan_1_of_this_year = datetime.date(year, 1, 1).toordinal()
        ordinal_date = (
            ordinal_date_on_jan_1_of_this_year + random.randint(0, 365)
        )
        datetime_object = datetime.date.fromordinal(ordinal_date)
        month, day = datetime_object.month, datetime_object.day
        return month, day, ordinal_date

    def get_date(self, ordinal_date=None):
        """Return a pretty-printed date for ordinal date."""
        if not ordinal_date:
            ordinal_date = self.ordinal_date
        year = datetime.date.fromordinal(ordinal_date).year
        month = datetime.date.fromordinal(ordinal_date).month
        day = datetime.date.fromordinal(ordinal_date).day
        month_ordinals_to_names = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
            8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        date = "{} of {} {}, {}".format(
            # Note: for retconning, the time of day will always be whatever the actual time of day
            # is at the beginning of the true simulation ("day", I assume), but this shouldn't matter
            self.time_of_day.title(), month_ordinals_to_names[month], day, year
        )
        return date

    def get_knowledge(self, owner_id, subject_id):
        """Return this person's knowledge about another person's feature of the given type.

        @param owner_id: The owner of this knowledge.
        @param subject_id: The subject of this knowledge.
        """
        owner = next(r for r in self.city.residents if r.id == owner_id)
        subject = next(r for r in self.city.residents if r.id == subject_id)
        all_features_of_knowledge_about_a_person = [
            'eye horizontal settedness', 'birthmark', 'job title', 'eye shape', 'hair color', 'head size',
            'home', 'scar', 'sunglasses', 'tattoo', 'nose shape', 'job shift', 'ear angle', 'home block',
            'mouth size', 'freckles', 'eye size', 'first name', 'skin color', 'ear size', 'middle name',
            'nose size', 'home address', 'eye vertical settedness', 'facial hair style', 'hair length',
            'eyebrow color', 'last name', 'head shape', 'eyebrow size', 'eye color', 'workplace', 'glasses',
            'location that night', 'rep'
        ]
        owners_knowledge_about_subject = set()
        for feature in all_features_of_knowledge_about_a_person:
            if owner.get_knowledge_about_person(subject, feature):
                owners_knowledge_about_subject.add(
                    (feature, owner.get_knowledge_about_person(subject, feature))
                )
        return owners_knowledge_about_subject

    def get_people_a_person_knows_of(self, owner_id):
        """Return the IDs for every person who a person knows about (has a mental model for)."""
        owner = next(r for r in self.city.residents if r.id == owner_id)
        ids_of_these_people = set([])
        for person in owner.mind.mental_models:
            if person.type == "person" and person is not owner:  # Not a mental model of a business or dwelling place
                ids_of_these_people.add(person.id)
        return ids_of_these_people

    def enact_lo_fi_simulation(self, n_timesteps=51122):
        """Simulate the passing of a chunk of time at a lower fidelity than the simulation during gameplay."""
        last_simulated_day = self.ordinal_date
        chance_of_a_day_being_simulated = 0.005
        for i in xrange(n_timesteps):
            self._advance_time()
            # Potentially have a new business open or an existing business close
            self.potentially_establish_a_new_business()
            self.potentially_shut_down_businesses()
            # Simulate births, even if this day will not actually be simulated
            for person in list(self.city.residents):
                if person.pregnant:
                    if self.ordinal_date >= person.due_date:
                        if self.time_of_day == 'day':
                            if random.random() < 0.5:
                                person.give_birth()
                        else:
                            person.give_birth()
                # if person.ready_to_work and not person.occupation:
                #     # If this person's father owns a farm, go to work on the farm
                #     if person.father and person.father.occupation.company
            if random.random() < chance_of_a_day_being_simulated:
                # Potentially build new businesses
                for person in list(self.city.residents):
                    if person.marriage:
                        chance_they_are_trying_to_conceive_this_year = (
                            self.config.function_to_determine_chance_married_couple_are_trying_to_conceive(
                                n_kids=len(person.marriage.children_produced)
                            )
                        )
                        chance_they_are_trying_to_conceive_this_year /= chance_of_a_day_being_simulated*365
                        if random.random() < chance_they_are_trying_to_conceive_this_year:
                            person.have_sex(partner=person.spouse, protection=False)
                        elif random.random() < self.config.chance_a_divorce_happens_some_timestep:
                            lawyer = person.contract_person_of_certain_occupation(occupation_in_question=Lawyer)
                            lawyer = None if not lawyer else lawyer.occupation
                            Divorce(subjects=(person, person.spouse), lawyer=lawyer)
                    if person.age > max(72, random.random() * 100):
                        # TODO make this era-accurate (i.e., different death rates in 1910 than in 1970)
                        if person is not self.founder:
                            person.die(cause_of_death="Natural causes")
                    elif person.occupation and person.age > max(65, random.random() * 100):
                        person.retire()
                    # elif random.random() < 0.01:  # I THINK NOT HAVING ELIF IS WHAT CAUSED THE WEIRD DTH/DPT ERRORS
                    #     if person is not self.founder and person not in self.founder.kids | self.founder.grandchildren:
                    #         person.depart_city()
                    elif person.ready_to_work and not person.occupation and not (person.female and person.kids_at_home):
                        if random.random() < 0.03:
                            person.find_work()
                        elif person.age > 22 and person.male if self.year > 1920 else True:
                            person.college_graduate = True
                    elif (person.male and person.occupation and person not in person.home.owners and
                          random.random() > 0.005):
                        person.move_out_of_parents()
                days_since_last_simulated_day = self.ordinal_date-last_simulated_day
                # Reset all Relationship interacted_this_timestep attributes
                for person in list(self.city.residents):
                    for other_person in person.relationships:
                        person.relationships[other_person].interacted_this_timestep = False
                # Have people go to the location they will be at this timestep
                for person in list(self.city.residents):
                    person.routine.enact()
                # Have people observe their surroundings, which will cause knowledge to
                # build up, and have them socialize with other people also at that location --
                # this will cause relationships to form/progress and knowledge to propagate
                for person in list(self.city.residents):
                    # Person may have married (during an earlier iteration of this loop) and
                    # then immediately departed because the new couple could not find home,
                    # so we still have to make sure they actually live in the city currently before
                    # having them socialize
                    if person in self.city.residents:
                        if person.age > 3:
                            # person.observe()
                            person.socialize(missing_timesteps_to_account_for=days_since_last_simulated_day*2)
                last_simulated_day = self.ordinal_date

    def potentially_establish_a_new_business(self):
        """Potentially have a new business get constructed in town."""
        config = self.config
        # If there's less than 30 vacant homes in this city and no apartment complex
        # yet, have one open up
        if len(self.city.vacant_lots) < 30 and not self.city.businesses_of_type('ApartmentComplex'):
            owner = self._determine_who_will_establish_new_business(business_type=ApartmentComplex)
            ApartmentComplex(owner=owner)
        elif random.random() < config.chance_a_business_opens_some_timestep:
            all_business_types = Business.__subclasses__()
            type_of_business_that_will_open = None
            tries = 0
            while not type_of_business_that_will_open:
                tries += 1
                randomly_selected_type = random.choice(all_business_types)
                advent, demise, min_pop = config.business_types_advent_demise_and_minimum_population[
                    randomly_selected_type
                ]
                # Check if the business type is era-appropriate
                if advent < self.year < demise and self.city.population > min_pop:
                    # Check if there aren't already too many businesses of this type in town
                    max_number_for_this_type = config.max_number_of_business_types_at_one_time[randomly_selected_type]
                    if (len(self.city.businesses_of_type(randomly_selected_type.__name__)) <
                            max_number_for_this_type):
                        # Lastly, if this is a business that only forms on a tract, make sure
                        # there is a vacant tract for it to be established upon
                        need_tract = randomly_selected_type in config.companies_that_get_established_on_tracts
                        if (need_tract and self.city.vacant_tracts) or not need_tract:
                            type_of_business_that_will_open = randomly_selected_type
                if self.city.population < 50 or tries > 10:  # Just not ready for more businesses yet -- grow naturally
                    break
            if type_of_business_that_will_open in config.public_company_types:
                type_of_business_that_will_open(owner=self.city.mayor)
            elif type_of_business_that_will_open:
                owner = self._determine_who_will_establish_new_business(business_type=type_of_business_that_will_open)
                type_of_business_that_will_open(owner=owner)

    def _determine_who_will_establish_new_business(self, business_type):
        """Select a person who will establish a new business of the given type."""
        config = self.config
        occupation_type_for_owner_of_this_type_of_business = (
            config.owner_occupations_for_each_business_type[business_type]
        )
        if occupation_type_for_owner_of_this_type_of_business in config.occupations_requiring_college_degree:
            if any(p for p in self.city.residents if p.college_graduate and not p.occupations and
                   config.employable_as_a[occupation_type_for_owner_of_this_type_of_business](applicant=p)):
                # Have a fresh college graduate in town start up a dentist office or whatever it is
                owner = next(p for p in self.city.residents if p.college_graduate and not p.occupations and
                             config.employable_as_a[occupation_type_for_owner_of_this_type_of_business](applicant=p))
            else:
                # Have someone from outside the city come in
                owner = PersonExNihilo(
                    game=self, job_opportunity_impetus=occupation_type_for_owner_of_this_type_of_business,
                    spouse_already_generated=None
                )
        else:
            if config.job_levels[occupation_type_for_owner_of_this_type_of_business] < 3:
                # Have a young person step up and start their career as a tradesman
                if any(p for p in g.city.residents if p.ready_to_work and not p.occupations and
                       config.employable_as_a[occupation_type_for_owner_of_this_type_of_business](applicant=p)):
                    owner = next(p for p in g.city.residents if p.ready_to_work and not p.occupations and
                       config.employable_as_a[occupation_type_for_owner_of_this_type_of_business](applicant=p))
                # Have any unemployed person in town try their hand at running a business
                elif any(p for p in g.city.residents if not p.retired and not p.occupation and
                         config.employable_as_a[occupation_type_for_owner_of_this_type_of_business](applicant=p)):
                    owner = next(p for p in g.city.residents if not p.retired and not p.occupation and
                         config.employable_as_a[occupation_type_for_owner_of_this_type_of_business](applicant=p))
                else:
                    # Have someone from outside the city come in
                    owner = PersonExNihilo(
                        game=self, job_opportunity_impetus=occupation_type_for_owner_of_this_type_of_business,
                        spouse_already_generated=None
                    )
            else:
                # Have someone from outside the city come in
                owner = PersonExNihilo(
                    game=self, job_opportunity_impetus=occupation_type_for_owner_of_this_type_of_business,
                    spouse_already_generated=None
                )
        return owner

    def potentially_shut_down_businesses(self):
        """Potentially have a new business get constructed in town."""
        config = self.config
        chance_a_business_shuts_down_this_timestep = config.chance_a_business_closes_some_timestep
        chance_a_business_shuts_down_on_timestep_after_its_demise = (
            # Once its anachronistic, like a Dairy in 1960
            config.chance_a_business_shuts_down_on_timestep_after_its_demise
        )
        for business in list(self.city.companies):
            if business.demise <= self.year:
                if random.random() < chance_a_business_shuts_down_on_timestep_after_its_demise:
                    if business.__class__ not in config.public_company_types:
                        business.go_out_of_business(reason=None)
            elif random.random() < chance_a_business_shuts_down_this_timestep:
                if business.__class__ not in config.public_company_types:
                    if not (
                        # Don't shut down an apartment complex with people living in it,
                        # or an apartment complex that's the only one in town
                        business.__class__ is ApartmentComplex and business.residents or
                        len(self.city.businesses_of_type('ApartmentComplex')) == 1
                    ):
                        business.go_out_of_business(reason=None)

    def enact_hi_fi_simulation(self, timestep_during_gameplay=False):
        """Advance to the next day/night cycle."""
        self._advance_time()
        # this_is_the_night_in_question = (
        #     self.ordinal_date == self.ordinal_date_that_the_founder_dies and self.time_of_day == "night"
        # )
        # Decay all beliefs from the time passing since yesterday
        if self.time_of_day == "day":
            # NOTE: COULD PROBABLY SPEED UP THINGS IN POLISHED GAME BY
            # PUTTING CODE FOR THIS ROUTINE DIRECTLY HERE
            for person in self.city.residents:
                for belief in person.all_belief_facets:
                    belief.decay_strength()
        # Reset all Relationship interacted_this_timestep attributes
        for person in self.city.residents:
            for other_person in person.relationships:
                person.relationships[other_person].interacted_this_timestep = False
        # Have people go to the location they will be at this timestep
        for person in self.city.residents:
            if not (timestep_during_gameplay and person is self.pc):  # Don't sim where the PC is
                person.routine.enact()
                # if this_is_the_night_in_question:
                #     self.lover.location.people_here_now.remove(self.lover)
                #     self.lover.location = self.founder.home
                #     self.lover.location.people_here_now.add(self.lover)
        # Have people observe their surroundings, which will cause knowledge to
        # build up, and have them socialize with other people also at that location --
        # this will cause relationships to form/progress and knowledge to propagate
        for person in self.city.residents:
            if not (timestep_during_gameplay and person is self.pc):
                if person.age > 3:
                    person.observe()
                    person.socialize()
        # Deteriorate people's mental models from time passing
        for person in self.city.residents:
            if not (timestep_during_gameplay and person is self.pc):
                for thing in list(person.mind.mental_models):
                    # People's mental models of themselves, their homes, and their workplaces don't deteriorate
                    if thing not in {person, person.home, None if not person.occupation else person.occupation.company}:
                        person.mind.mental_models[thing].deteriorate()
                if self.ordinal_date == self.ordinal_date_that_gameplay_begins:
                    person.reflect()
                    # if person is self.lover:
                    #     # Have them invent an alibi for where they were, in case
                    #     # the PC encounters them and asks, in which case we don't
                    #     # want them to just admit to being at the founder's home
                    #     date = (self.ordinal_date_that_the_founder_dies, 1)
                    #     if random.random() < 0.5:
                    #         fake_alibi = person.home
                    #     else:
                    #         fake_alibi = random.choice(list(self.city.companies))
                    #     fake_reflection = Reflection(subject=self.lover, source=self.lover)
                    #     person.mind.mental_models[person].whereabouts.date[date] = Facet(
                    #         value=fake_alibi.name, owner=self.lover, subject=self.lover,
                    #         feature_type="whereabouts", initial_evidence=fake_reflection,
                    #         predecessor=None, parent=None, object_itself=fake_alibi
                    #     )
            # But also have them reflect accurately on their own features --
            # COMMENTED OUT FOR NOW BECAUSE IT GETS MUCH FASTER WITHOUT THIS
            # if person.age > 3:
            #     person.reflect()

    def _advance_time(self):
        """Advance time of day and date, if it's a new day."""
        self.time_of_day = "night" if self.time_of_day == "day" else "day"
        if self.time_of_day == "day":
            self.ordinal_date += 1
            new_date_tuple = datetime.date.fromordinal(self.ordinal_date)
            if new_date_tuple.year != self.year:
                # Happy New Year
                self.true_year = new_date_tuple.year
                self.year = new_date_tuple.year
                print self.year, len(self.city.vacant_lots), len(self.city.vacant_homes), self.city.pop
            self.month = new_date_tuple.month
            self.day = new_date_tuple.day
            self.date = self.get_date()
            # Age any present (not dead, not departed) character whose birthday is today
            if (self.month, self.day) not in self.birthdays:
                self.birthdays[(self.month, self.day)] = set()
            else:
                for person in self.birthdays[(self.month, self.day)]:
                    if person.present:
                        person.grow_older()
                # Don't forget leap-year babies
                if (self.month, self.day) == (3, 1):
                    for person in self.birthdays[(2, 29)]:
                        if person.present:
                            person.grow_older()

        else:
            self.date = self.get_date()

    def save_data(self, filename_suffix="_day1"):
        import pickle
        # Pickle up city and building stuff
        streets = self.city.getStreets()
        blocks = self.city.getBlocks()
        lots = self.city.getLots()
        businesses = self.city.getBusinesses()
        apartments = self.city.getApartments()
        houses = self.city.getHouses()
        pickle.dump(streets, open('/Users/jamesryan/Desktop/TOTT_states/streets' + filename_suffix + '.dat', 'wb'))
        pickle.dump(blocks, open('/Users/jamesryan/Desktop/TOTT_states/blocks' + filename_suffix + '.dat', 'wb'))
        pickle.dump(lots, open('/Users/jamesryan/Desktop/TOTT_states/lots' + filename_suffix + '.dat', 'wb'))
        pickle.dump(businesses, open('/Users/jamesryan/Desktop/TOTT_states/businesses' + filename_suffix + '.dat', 'wb'))
        pickle.dump(apartments, open('/Users/jamesryan/Desktop/TOTT_states/apartments' + filename_suffix + '.dat', 'wb'))
        pickle.dump(houses, open('/Users/jamesryan/Desktop/TOTT_states/houses' + filename_suffix + '.dat', 'wb'))
        # Generate people_dict
        people_dict = {}
        for person in self.city.residents:
            faceStr = person.face.faceStr
            first_name = str(person.first_name)
            last_name = str(person.last_name)
            suffix = person.suffix
            people_dict[person.id] = {
                "faceStr": faceStr,
                "first_name": first_name,
                "last_name": last_name,
                "suffix": suffix,
                "people_known_of": set([p.id for p in person.mind.mental_models if p.type == "person"]),
                "location": person.location.id,
                "get_knowledge": {}
            }
            for other_person in person.mind.mental_models:
                if other_person.type == "person":
                    owner = person
                    subject = other_person
                    all_features_of_knowledge_about_a_person = [
                        'eye horizontal settedness', 'birthmark', 'job title', 'eye shape', 'hair color', 'head size',
                        'home', 'scar', 'sunglasses', 'tattoo', 'nose shape', 'job shift', 'ear angle', 'home block',
                        'mouth size', 'freckles', 'eye size', 'first name', 'skin color', 'ear size', 'middle name',
                        'nose size', 'home address', 'eye vertical settedness', 'facial hair style', 'hair length',
                        'eyebrow color', 'last name', 'head shape', 'eyebrow size', 'eye color', 'workplace', 'glasses',
                        'location that night', 'rep'
                    ]
                    owners_knowledge_about_subject = set()
                    for feature in all_features_of_knowledge_about_a_person:
                        if owner.get_knowledge_about_person(subject, feature):
                            owners_knowledge_about_subject.add(
                                (feature, str(owner.get_knowledge_about_person(subject, feature)))
                            )
                    people_dict[person.id]["get_knowledge"][other_person.id] = owners_knowledge_about_subject
        # Pickle people_dict
        pickle.dump(people_dict,  open('/Users/jamesryan/Desktop/TOTT_states/people' + filename_suffix + '.dat', 'wb'))

    def find(self, name):
        """Return person living in this city with that name."""
        if any(p for p in self.city.residents if p.name == name):
            people_named_this = [p for p in self.city.residents if p.name == name]
            if len(people_named_this) > 1:
                print '\nWarning: Multiple {} residents are named {}; returning a complete list\n'.format(
                    self.city.name, name
                )
                return people_named_this
            else:
                return people_named_this[0]
        else:
            raise Exception('There is no one in {} named {}'.format(self.city.name, name))

    def find_deceased(self, name):
        """Return deceased person with that name."""
        if any(p for p in self.city.deceased if p.name == name):
            people_named_this = [p for p in self.city.deceased if p.name == name]
            if len(people_named_this) > 1:
                print '\nWarning: Multiple {} residents are named {}; returning a complete list\n'.format(
                    self.city.name, name
                )
                return people_named_this
            else:
                return people_named_this[0]
        else:
            raise Exception('There is no one named {} who died in {]'.format(name, self.city.name))

    def find_by_hex(self, hex_value):
        """Return person whose ID in memory has the given hex value."""
        int_of_hex = int(hex_value, 16)
        try:
            person = next(
                p for p in self.city.residents | self.city.deceased | self.city.departed if
                id(p) == int_of_hex
            )
            return person
        except StopIteration:
            raise Exception('There is no one with that hex ID')


g = Game()
g.establish_setting()