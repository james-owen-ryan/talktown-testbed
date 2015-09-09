import random
import string

# TODO LIST GRAVESTONES IN THE CEMETERY


NUMERAL_TO_WORD = {
    1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
    6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
    11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
    15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
    18: 'eighteen', 19: 'nineteen', 20: 'twenty',
}


class Game(object):
    """A Bad News gameplay instance."""

    def __init__(self, sim):
        """Initialize a Game object."""
        self.sim = sim  # A city simulation generated by game.py
        self.city = sim.city
        self.player = Player(game=self)
        self.deceased_character = self.select_deceased_character()
        self.player.location = self.deceased_character.location
        self.deceased_character.die('Unknown causes')
        self.next_of_kin = self.deceased_character.next_of_kin
        self.player.observe()
        # TODO INITIAL EXPOSITION RIGHT NOW

    def select_deceased_character(self):
        """Prepare the soon-to-be deceased character whose next-of-kin the
        player will be tasked with notifying.

        Currently, this method just randomly picks a person who has had an occupation at some
        point, has both friends and extended family in town, and is currently home alone.
        """
        potential_selections = [
            p for p in self.city.residents if p.location is p.home and
            len(p.location.people_here_now) == 1 and
            p.occupations and
            p.friends and
            p.extended_family
        ]
        return random.choice(potential_selections)

    def sketch_interlocutor(self):
        """Give a basic outline of the current interlocutor."""
        print '\n'
        interlocutor = self.player.interlocutor
        broader_skin_tone = {
            'black': 'dark', 'brown': 'dark',
            'beige': 'light', 'pink': 'light',
            'white': 'light',
        }
        for feature_type in (
            'full name', 'age', 'purpose here', 'extroversion', 'agreeableness', 'neuroticism',
            'openness', 'conscientiousness', 'moved to town', 'marital status', 'home address',
            'job status', 'workplace', 'workplace address', 'job title', 'job shift', 'skin color',
            'hair color', 'hair length', 'tattoo', 'scar', 'birthmark', 'freckles', 'glasses',
        ):
            if feature_type == 'skin color':
                feature_value = broader_skin_tone[interlocutor.face.skin.color]
            elif feature_type in ('extroversion', 'agreeableness', 'neuroticism', 'openness', 'conscientiousness'):
                feature_value = interlocutor.personality.component_str(component_letter=feature_type[0])
            elif feature_type == "moved to town":
                if interlocutor.birth and interlocutor.birth.city is self.city:
                    feature_value = "birth"
                else:
                    feature_value = str(interlocutor.moves[0].year)
            elif feature_type == "age":
                feature_value = str(interlocutor.age)
            elif feature_type == "full name":
                feature_value = interlocutor.full_name
            elif feature_type == "purpose here":
                feature_value = interlocutor.whereabouts.current_occasion
            else:
                feature_value = interlocutor.get_feature(feature_type)
            if feature_type == 'job status' and feature_value in ('retired', 'unemployed'):
                extra = ' (since {})'.format(
                    'always' if not interlocutor.occupations else interlocutor.occupations[-1].terminus.year
                )
            elif feature_type == 'workplace' and interlocutor.occupation:
                extra = ' (since {})'.format(interlocutor.occupation.start_date)
            elif feature_type == 'home address':
                extra = ' (since {})'.format(interlocutor.moves[-1].year)
            else:
                extra = ''
            print "{feature_type}: {value}{extra}".format(
                feature_type=feature_type.capitalize(),
                value=feature_value,
                extra=extra
            )
        print '\n'


class Player(object):
    """A collection of data and affordances surrounding a player's interaction with a Bad News game world."""

    def __init__(self, game):
        """Initialize a Player object."""
        self.game = game
        self.city = game.city
        self.location = None  # Gets set by game
        self.outside = False  # Since you start in the deceased character's home
        self.people_i_know_by_name = set()
        self.houses_i_know_by_name = set()
        self.salient_person_who_lives_in_a_house = {}
        self.last_address_i_heard = None
        self.last_unit_number_i_heard = None
        self.last_block_i_heard = None
        self.interlocutor = None
        self.current_subject_of_conversation = None  # Name of whom player and interlocutor are currently talking about

    @property
    def buildings_on_this_block(self):
        """Return a list of the buildings on the player's current block."""
        block = self.location if self.location.type == 'block' else self.location.block
        return [b for b in self.city.buildings if b.block is block]

    def goto(self, address=None):
        """Move the player to a location with the given address.

        If no location exists at this address, move them simply to the associated block.
        """
        if not address:
            address = self.last_address_i_heard
        try:
            if ' (Unit' in address:
                address = address.split(' (Unit')[0]
            house_number = int(address[:3])
            street_object = self._find_street_object(address)
            self.location = next(
                b for b in self.city.buildings if b.house_number == house_number and
                b.block.street is street_object
            )
            self.outside = True
            self.observe()
        except StopIteration:
            # Arrive then at that block
            house_number = int(address[:3])
            block_number = int(address[0] + '00')
            street_object = self._find_street_object(address)
            block_object = next(b for b in self.city.blocks if b.number == block_number and b.street is street_object)
            print "Arriving at the {}, you find no building with the house number {}.\n".format(
                block_object, house_number
            )
            self.goto_block(block=block_object)

    def _find_street_object(self, address):
        """Complete a potentially abridged street name."""
        street_name = address[4:].lower()
        if street_name[-3:] == "ave":
            street_name += 'nue'
        elif street_name[-4:] == "ave.":
            street_name = street_name[:-1] + 'nue'
        elif street_name[-2:] == 'st':
            street_name += 'reet'
        elif street_name[-4:] == "st.":
            street_name = street_name[:-1] + 'reet'
        street_object = next(s for s in self.city.streets if s.name.lower() == street_name.lower())
        return street_object

    def goto_block(self, block=None):
        """Move the character to the given block."""
        if not block:
            block = self.last_block_i_heard
        if type(block) == str:
            try:
                block = next(b for b in self.city.blocks if str(block) == b)
            except StopIteration:
                raise Exception('There is no {}'.format(block))
        self.location = block
        self.outside = True
        self.observe()

    def move(self, direction):
        """Move to an adjacent block."""
        if self.location.type != 'block':
            self.location = self.location.block
        try:
            direction = direction.lower()
        except AttributeError:  # int or something weird was passed as direction and will get caught anyway
            pass
        available_directions = ('n', 's') if self.location.street.direction in ('N', 'S') else ('e', 'w')
        if direction not in ('n', 'e', 's', 'w'):
            print "\nThat is not a valid direction. Please choose from among the following options: N, S, E, W.\n"
        elif direction not in available_directions:
            direction_to_name = {'w': 'west', 'e': 'east', 's': 'south', 'n': 'north'}
            print "\n{street_name} runs {direction1} to {direction2}.\n".format(
                street_name=self.location.street.name,
                direction1=direction_to_name[available_directions[0]],
                direction2=direction_to_name[available_directions[1]],
            )
        else:
            index_of_this_block_on_street = self.location.street.blocks.index(self.location)
            index_of_new_block = (
                index_of_this_block_on_street+1 if direction in ('n', 'e') else index_of_this_block_on_street-1
            )
            if index_of_new_block < 0 or index_of_new_block == len(self.location.street.blocks):
                direction_to_adj = {'w': 'western', 'e': 'eastern', 's': 'southern', 'n': 'northern'}
                print "\nYou are already at the {direction_adj} terminus of {street_name}.\n".format(
                    direction_adj=direction_to_adj[direction],
                    street_name=self.location.street.name
                )
            else:
                # Go to the new block
                new_block = self.location.street.blocks[index_of_new_block]
                self.goto_block(block=new_block)

    def approach(self, house_number=None):
        """Move the player to the building on her current block with the given house number."""
        if self.location.__class__.__name__ != 'Block':
            self.location = self.location.block
        building_to_approach = None
        if not house_number:
            if len(self.location.buildings) == 1:
                building_to_approach = list(self.location.buildings)[0]
            else:
                print "\nYou need to specify a house number to approach.\n"
        else:
            try:
                building_to_approach = next(b for b in self.location.buildings if b.house_number == house_number)
            except StopIteration:
                print "\nThere is no building on this block with the house number {}\n".format(house_number)
        if building_to_approach:
            self.location = building_to_approach
            self.outside = True
            self.observe()

    def approach_apt(self, unit_number=None):
        """Move the player to the unit of the apartment she is currently outside with the given unit number."""
        if self.location.__class__.__name__ == "Apartment":
            self.location = self.location.complex
        if not unit_number:
            unit_number = self.last_unit_number_i_heard
        self.location = self.location.units[unit_number-1]
        self.outside = True  # Make sure elsewhere to check for outside + location being an apartment unit
        self.observe()

    def enter(self, house_number=None):
        """Enter a building."""
        if not house_number:
            # Then attempt to enter the building you are outside of
            if not self.location.locked:
                self.outside = False
                self.observe()
            elif self.location.lot.tract:
                print 'The gate is locked.'
            else:
                print 'The door is locked.'
        else:
            if self.location.__class__.__name__ != 'Block':
                self.location = self.location.block
            building_to_approach = next(b for b in self.location.buildings if b.house_number == house_number)
            self.location = building_to_approach
            if not self.location.locked:
                self.outside = False
                self.observe()
            elif self.location.lot.tract:
                print 'The gate is locked.'
            else:
                print 'The door is locked.'

    def enter_apt(self, unit_number=None):
        """Enter a building."""
        if not unit_number:
            # Then attempt to enter the apartment unit you are standing outside of
            if not self.location.locked:
                self.outside = False
                self.observe()
            else:
                print 'The door is locked.'
        else:
            if self.location.__class__.__name__ != 'ApartmentComplex':
                self.location = self.location.complex
            apartment_unit_to_approach = next(a for a in self.location.units if a.unit_number == unit_number)
            self.location = apartment_unit_to_approach
            if not self.location.locked:
                self.outside = False
                self.observe()
            else:
                print 'The door is locked.'

    def exit(self):
        """Exit a building."""
        self.outside = True
        self.observe()

    def go_outside(self):
        """Go into the street and the observe the block you are on."""
        self.outside = True
        self.location = self.location.block
        self.observe()

    def observe(self):
        """Describe the player's current setting."""
        if self.outside:  # Interior scenes
            if self.location.type == 'block':
                scene = self._describe_the_block_player_is_on()
            elif self.location.__class__.__name__ == 'House':
                scene = self._describe_house_exterior()
            elif self.location.__class__.__name__ == 'Apartment':
                scene = self._describe_apartment_unit_exterior()
            elif self.location.__class__.__name__ == 'ApartmentComplex':
                scene = self._describe_apartment_complex_exterior()
            else:  # Business
                scene = self._describe_business_exterior()
        else:  # Exterior scenes
            if self.location.type == 'residence':
                scene = self._describe_home_interior()
            else:
                scene = self._describe_business_interior()
        print "\n{}\n".format(scene)

    def address(self, addressee=None):
        """Address person with the given name here, or else the only person here."""
        if addressee is not None:
            if type(addressee) == str:
                name = addressee
                address_number = None
            else:
                address_number = addressee
                name = None
        else:
            name = None
            address_number = None
        if self.location.people_here_now:
            if len(self.location.people_here_now) == 1:
                self.interlocutor = list(self.location.people_here_now)[0]
                print "\nYou are talking to {age_and_gender_nominal} with {appearance}.\n".format(
                    age_and_gender_nominal=self.interlocutor.age_and_gender_description,
                    appearance=self.interlocutor.basic_appearance_description
                )
                self.game.sketch_interlocutor()
            else:
                if any(p for p in self.location.people_here_now if p.name == name):
                    self.interlocutor = next(p for p in self.location.people_here_now if p.name == name)
                    print "\nYou are talking to {age_and_gender_nominal} with {appearance}.\n".format(
                        age_and_gender_nominal=self.interlocutor.age_and_gender_description,
                        appearance=self.interlocutor.basic_appearance_description
                    )
                    self.game.sketch_interlocutor()
                elif any(p for p in self.location.people_here_now if p.temp_address_number == address_number):
                    self.interlocutor = next(
                        p for p in self.location.people_here_now if p.temp_address_number == address_number
                    )
                    print "\nYou are talking to {age_and_gender_nominal} with {appearance}.\n".format(
                        age_and_gender_nominal=self.interlocutor.age_and_gender_description,
                        appearance=self.interlocutor.basic_appearance_description
                    )
                    self.game.sketch_interlocutor()
                else:
                    print "\nI'm not sure whom you met.\n".format(name)
        else:
            print '\nNo one is here.\n'.format(name)

    def ask(self, interlocutor=None, subject=None, feature_type=None):
        """Ask interlocutor about subject's feature of the given type."""
        interlocutor = interlocutor if interlocutor else self.interlocutor
        subject = subject if subject else self.current_subject_of_conversation
        self.current_subject_of_conversation = subject
        if type(subject) is str:
            if len(subject.split()) == 3:
                first_name, last_name, suffix = subject.split()
            else:
                first_name, last_name = subject.split()
                suffix = None
        else:
            first_name, last_name, suffix = subject.first_name, subject.last_name, subject.suffix
        # See if the interlocutor has a mental model whose first name and last name
        # match whom the player is asking about
        interlocutor.potential_matches = interlocutor.mind.search_by_name(
            first_name=first_name, last_name=last_name, suffix=suffix
        )
        print "\n{} matches\n".format(len(interlocutor.potential_matches))

    def ask_to_list(self):
        """Ask interlocutor to list their potential matches to the player's question."""
        for potential_match in self.interlocutor.potential_matches:
            print

    def remember(self):
        """Remember the name of the person you are talking to."""
        self.people_i_know_by_name.add(self.interlocutor)

    def _describe_the_block_player_is_on(self):
        """Describe the block that the player is on."""
        buildings_on_this_block = [lot.building for lot in self.location.lots if lot.building]
        if buildings_on_this_block:
            buildings_str = self._describe_buildings_on_block()
            if len(buildings_on_this_block) > 1:
                scene = "You are on the {}. There are {} buildings here:\n{}".format(
                    self.location, NUMERAL_TO_WORD[len(buildings_on_this_block)], buildings_str
                )
            else:
                scene = "You are on the {}. There is one building here:\n{}".format(
                    self.location, buildings_str
                )
        else:
            scene = "You are on the {}. There are no buildings here.".format(self.location)
        return scene

    def _describe_buildings_on_block(self):
        """Generate a pretty-printable description of buildings on the block the player is on."""
        description = ""
        buildings_on_this_block = [lot.building for lot in self.location.lots if lot.building]
        for building in buildings_on_this_block:
            description += '\n\t'
            if building.__class__.__name__ in ('Bar', 'Restaurant'):
                description += '{}\tA {} whose sign reads "{}"'.format(
                    building.lot.house_number, building.__class__.__name__.lower(), building.sign
                )
            elif building.__class__.__name__ == 'House':
                if self.game.sim.time_of_day == 'night':
                    lights_on = ' with its lights on' if building.people_here_now else ' with its lights off'
                else:
                    lights_on = ''
                if building in self.houses_i_know_by_name:
                    lights_on = ','+lights_on if lights_on else ''
                    "{}\t{}'s house{}".format(
                        building.lot.house_number, self.salient_person_who_lives_in_a_house[building].name,
                        lights_on
                    )
                else:
                    description += '{}\tA private residence{}'.format(
                        building.lot.house_number, lights_on
                    )
            else:  # A business that's not a bar or restaurant
                if building.__class__.__name__ == 'Farm':
                    description += '{house_number}\tA farm'.format(
                        house_number=building.house_number
                    )
                else:
                    description += '{house_number}\tA {gated_area_or_company} whose sign reads "{sign}"'.format(
                        house_number=building.lot.house_number,
                        gated_area_or_company='gated area' if building.lot.tract else 'company',
                        sign=building.sign
                    )
        return description

    def _describe_house_exterior(self):
        """Describe the house whose doorstep the player is standing on."""
        if self.location in self.houses_i_know_by_name:
            whose_house = "{person_i_know_lives_here}'s house".format(
                person_i_know_lives_here=self.salient_person_who_lives_in_a_house[self.location].name
            )
        else:
            whose_house = "a house"
        if len(self.location.people_here_now) > 3:
            noise_of_activity_inside = "a bustle of activity inside"
        elif self.location.people_here_now:
            noise_of_activity_inside = "a faint noise inside"
        else:
            noise_of_activity_inside = "nothing inside"
        if self.game.sim.time_of_day == "night":
            scene = (
                "You are at the doorstep of {whose_house} at {address}. "
                "Its lights are {lights_on}, its door is {door_locked}, and you hear {noise_of_activity_inside}.".format(
                    whose_house=whose_house,
                    address=self.location.address,
                    lights_on="on" if self.location.people_here_now else "off",
                    door_locked="locked" if self.location.locked else "unlocked",
                    noise_of_activity_inside=noise_of_activity_inside
                )
            )
        else:
            scene = (
                "You are at the doorstep of {whose_house} at {address}. "
                "Its door is {door_locked} and you hear {noise_of_activity_inside}.".format(
                    whose_house=whose_house,
                    address=self.location.address,
                    door_locked="locked" if self.location.locked else "unlocked",
                    noise_of_activity_inside=noise_of_activity_inside
                )
            )
        return scene

    def _describe_apartment_unit_exterior(self):
        """Describe the apartment unit whose door the player is standing at."""
        if self.location in self.houses_i_know_by_name:
            whose_apartment = "{person_i_know_lives_here}'s apartment, unit #{unit_number}".format(
                person_i_know_lives_here=self.salient_person_who_lives_in_a_house[self.location].name,
                unit_number=self.location.unit_number
            )
        else:
            whose_apartment = "unit #{unit_number}".format(unit_number=self.location.unit_number)
        if len(self.location.people_here_now) > 3:
            noise_of_activity_inside = "a bustle of activity inside"
        elif self.location.people_here_now:
            noise_of_activity_inside = "a faint noise inside"
        else:
            noise_of_activity_inside = "nothing"
        if self.location.locked and self.location.people_here_now:
            conjunction = ', but'
        else:
            conjunction = ' and'
        scene = (
            "You are in a hallway standing outside the door of {whose_apartment} of {apartment_complex}. "
            "Its door is {door_locked}{conjunction} you hear {noise_of_activity_inside}.".format(
                whose_apartment=whose_apartment,
                apartment_complex=self.location.complex.name,
                door_locked="locked" if self.location.locked else "unlocked",
                conjunction=conjunction,
                noise_of_activity_inside=noise_of_activity_inside
            )
        )
        return scene

    def _describe_apartment_complex_exterior(self):
        """Describe the apartment complex, particularly its intercom system, that the player is outside of."""
        try:
            janitor_in_lobby = next(e for e in self.location.working_right_now if e[0] == 'janitor')
        except StopIteration:
            janitor_in_lobby = None
        if janitor_in_lobby:
            lobby_str = ", but there is a janitor in the lobby"
        else:
            lobby_str = " and the lobby is empty"
        scene = (
            "You are outside {complex_name} at {address}. Its entrance is locked{lobby_str}. There "
            "are {n_options} options listed on the intercom system:\n{intercom_index}".format(
                complex_name=self.location.name,
                address=self.location.address,
                lobby_str=lobby_str,
                n_options=len(self.location.units)+1,
                intercom_index=self._describe_apartment_complex_intercom()
            )
        )
        return scene

    def _describe_apartment_complex_intercom(self):
        """Describe the apartment complex's intercom system, listing units and names."""
        intercom_description = ""
        for unit in self.location.units:
            if unit.owners:
                all_surnames_among_owners = {owner.last_name for owner in unit.owners}
                owner_str = '/'.join(all_surnames_among_owners)
            else:
                owner_str = '--'
            intercom_description += '\n\t#{unit_no}\t{owners_surnames}'.format(
                unit_no=unit.unit_number,
                owners_surnames=owner_str
            )
        intercom_description += "\n\n\t#99\tOffice"
        return intercom_description

    def _describe_business_exterior(self):
        """Describe the business a player is outside of."""
        if len(self.location.people_here_now) > 8:
            n_people_inside = "many people"
        elif len(self.location.people_here_now) > 4:
            n_people_inside = "several people"
        elif len(self.location.people_here_now) > 1:
            n_people_inside = "a few people"
        elif self.location.people_here_now:
            # A single person -- if it's a janitor, be more specific and
            # explicitly say that
            if self.location.working_right_now and self.location.working_right_now[0][0] == 'janitor':
                n_people_inside = "a janitor"
            else:
                n_people_inside = "a person"
        else:
            n_people_inside = "no one"
        if self.location.locked and self.location.people_here_now:
            conjunction = ', but'
        else:
            conjunction = ' and'
        scene = (
            "You are at the entrance of {business_name} at {address}. "
            "Its {gate_or_door} is {door_locked}{conjunction} you see {n_people_inside} "
            "{inside_or_on_premises}.".format(
                business_name=self.location.name if self.location.__class__.__name__ != 'Farm' else 'a farm',
                address=self.location.address,
                gate_or_door="gate" if self.location.lot.tract else "door",
                door_locked="locked" if self.location.locked else "unlocked",
                conjunction=conjunction,
                n_people_inside=n_people_inside,
                inside_or_on_premises="on the premises" if self.location.lot.tract else "inside"
            )
        )
        return scene

    def _describe_home_interior(self):
        """Describe the interior of a house that the player is in."""
        if self.location in self.houses_i_know_by_name:
            house_noun_phrase = "the {house_or_apartment} of {person_i_know_lives_here}".format(
                house_or_apartment="home" if self.location.house else "apartment",
                person_i_know_lives_here=self.salient_person_who_lives_in_a_house[self.location].name
            )
        else:
            house_noun_phrase = "a {house_or_apartment}".format(
                house_or_apartment="home" if self.location.house else "apartment"
            )
        if len(self.location.people_here_now) > 14:
            people_here_intro = "There are very many people here:\n".format(
                len(self.location.people_here_now)
            )
        elif len(self.location.people_here_now) > 7:
            people_here_intro = "There are many people here:\n"
        elif len(self.location.people_here_now) > 1:
            people_here_intro = "There are {number_word} people here:\n".format(
                number_word=NUMERAL_TO_WORD[len(self.location.people_here_now)]
            )
        elif self.location.people_here_now:
            people_here_intro = "There is a single person here:\n"
        else:
            people_here_intro = "There is no one here."
        scene = (
            "You are inside {house_noun_phrase} at {address}. "
            "{people_here_intro}{people_present_description}".format(
                house_noun_phrase=house_noun_phrase,
                address=self.location.address,
                people_here_intro=people_here_intro,
                people_present_description=self._describe_people_in_business()
            )
        )
        return scene

    def _describe_people_in_home(self):
        """Describe the individuals currently situated in a residence that the player is in."""
        people_present_description = ""
        people_here_now = list(self.location.people_here_now)
        for i in xrange(len(people_here_now)):
            person = people_here_now[i]
            person.temp_address_number = i
            if person in self.people_i_know_by_name:
                people_present_description += '\n\t{i}\t{persons_name}'.format(
                    i=person.temp_address_number,
                    persons_name=person.name
                )
            else:
                people_present_description += '\n\t{i}\t{age_gender} with {appearance}'.format(
                    i=person.temp_address_number,
                    age_gender=person.age_and_gender_description,
                    appearance=person.basic_appearance_description
                ).capitalize()
        return people_present_description

    def _describe_business_interior(self):
        """Describe the interior of a business that the player is in."""
        if len(self.location.people_here_now) > max(NUMERAL_TO_WORD):
            people_here_intro = "There are {number} people here:\n".format(
                number=len(self.location.people_here_now)
            )
        elif len(self.location.people_here_now) > 7:
            people_here_intro = "There are many people here:\n"
        elif len(self.location.people_here_now) > 1:
            people_here_intro = "There are {number_word} people here:\n".format(
                number_word=NUMERAL_TO_WORD[len(self.location.people_here_now)]
            )
        elif self.location.people_here_now:
            people_here_intro = "There is a single person here:\n"
        else:
            people_here_intro = "There is no one here."
        scene = (
            "You are {inside_or_on_premises_of} {business_name} at {address}. "
            "{people_here_intro}{people_present_description}".format(
                inside_or_on_premises_of='on the premises of' if self.location.lot.tract else 'inside',
                business_name=self.location.name if self.location.__class__.__name__ != 'Farm' else 'a farm',
                address=self.location.address,
                people_here_intro=people_here_intro,
                people_present_description=self._describe_people_in_business()
            )
        )
        return scene

    def _describe_people_in_business(self):
        """Describe the individuals currently situated in a residence that the player is in."""
        people_present_description = ""
        people_here_now = list(self.location.people_here_now)
        # List people working here first (sorted by job level)
        people_here_now.sort(
            key=lambda p: (p.routine.working,
                           0 if not p.occupation or not p.routine.working else p.occupation.level),
            reverse=True
        )
        for i in xrange(len(people_here_now)):
            person = people_here_now[i]
            person.temp_address_number = i
            if (self.game.sim.time_of_day == 'day' and self.location.__class__.__name__ == 'School' and
                    person.whereabouts.date[(self.game.sim.ordinal_date, 0)].occasion == 'school'):
                occupation_if_working = ' (student)'
            else:
                occupation_if_working = ' ({})'.format(person.occupation.vocation) if person.routine.working else ''
            if person in self.people_i_know_by_name:
                people_present_description += '\n\t{i}\t{persons_name}{occupation_if_working}'.format(
                    i=person.temp_address_number,
                    persons_name=person.name,
                    occupation_if_working=occupation_if_working

                )
            else:
                people_present_description += '\n\t{i}\t{age_gender} with {appearance}{occupation_if_working}'.format(
                    i=person.temp_address_number,
                    age_gender=person.age_and_gender_description,
                    appearance=person.basic_appearance_description,
                    occupation_if_working=occupation_if_working
                ).capitalize()
        return people_present_description

    def ring(self):
        """Print exposition surrounding the ringing of a doorbell."""
        answerer = self._determine_who_answers_buzzer_or_doorbell(dwelling_place=self.location)
        verb_phrase = 'comes to the gate' if self.location.lot.tract else 'answers the door'
        if answerer in self.people_i_know_by_name:
            print '\n{answerer_name} {answers}.\n'.format(
                answerer_name=answerer.name,
                answers=verb_phrase
            ).capitalize()
        elif answerer:
            print '\n{age_and_gender} with {appearance} {answers}.\n'.format(
                age_and_gender=answerer.age_and_gender_description,
                appearance=answerer.basic_appearance_description,
                answers=verb_phrase
            ).capitalize()
        else:
            print '\nNo one {answers}.\n'.format(
                answers=verb_phrase
            )
        self.interlocutor = answerer
        self.game.sketch_interlocutor()

    def knock(self):
        """Print exposition surrounding the knocking of a house's door."""
        self.ring()

    def buzz(self, unit_number):
        """Print exposition surrounding the buzzing of an apartment unit."""
        self.last_unit_number_i_heard = unit_number
        if unit_number == 99:
            answerer = self._buzz_apartment_complex_office()
        else:
            apartment_unit_buzzed = self.location.units[unit_number-1]
            answerer = self._determine_who_answers_buzzer_or_doorbell(
                dwelling_place=apartment_unit_buzzed
            )
        if answerer:
            print '{} speaks into the intercom.'.format(
                answerer.age_and_gender_description
            ).capitalize()
        else:
            print 'No one answers.'
        self.interlocutor = answerer

    def _buzz_apartment_complex_office(self):
        """Buzz the office of an apartment complex.

        If a secretary is working, they will answer; else, if a landlord is working, they
        will answer; else, no one will answer.
        """
        # This buzzes the office -- if a secretary or landlord is working,
        # have them answer
        try:
            answerer = next(e for e in self.location.working_right_now if e[0] == 'secretary')[1]
        except StopIteration:
            try:
                answerer = next(e for e in self.location.working_right_now if e[0] == 'landlord')[1]
            except StopIteration:
                answerer = None
        return answerer

    @staticmethod
    def _determine_who_answers_buzzer_or_doorbell(dwelling_place):
        """Return a random person who is here to come to the door."""
        if not dwelling_place.people_here_now:
            return None
        else:
            # See if any adults who live here are home -- if any are, return the most
            # extroverted person among them
            adults_who_live_here_who_are_home = [
                p for p in dwelling_place.people_here_now if p.adult and p.home is dwelling_place
            ]
            if adults_who_live_here_who_are_home:
                return max(adults_who_live_here_who_are_home, key=lambda q: q.personality.extroversion)
            else:
                # See if any adults are here, and if any are, return the most extroverted of them
                adults_here = [p for p in dwelling_place.people_here_now if p.adult]
                if adults_here:
                    return max(adults_here, key=lambda p: p.personality.extroversion)
                else:
                    # See if anyone who lives here and is at least five years old is home; if
                    # there is, return the oldest one
                    people_here_who_live_here = [
                        p for p in dwelling_place.people_here_now if p.home is dwelling_place and
                        p.age > 4
                    ]
                    if people_here_who_live_here:
                        return max(people_here_who_live_here, key=lambda p: p.age)
                    else:
                        # See if anyone above age 4 is here; if there is, return the oldest one
                        people_here_above_age_four = [
                            p for p in dwelling_place.people_here_now if p.age > 4
                        ]
                        if people_here_above_age_four:
                            return max(people_here_above_age_four, key=lambda p: p.age)
                        else:
                            return None

    @property
    def i(self):
        """Wrapper for self.interlocutor."""
        return self.interlocutor