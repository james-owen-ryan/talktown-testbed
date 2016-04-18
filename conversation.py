import random
import time
from event import Event
from evidence import Statement, Declaration, Lie, Eavesdropping
from belief import PersonMentalModel, DwellingPlaceModel, BusinessMentalModel


class Conversation(Event):
    """A conversation between two characters in a city."""

    def __init__(self, initiator, recipient, phone_call=False, debug=True):
        """Initialize a Conversation object."""
        super(Conversation, self).__init__(game=initiator.game)
        self.game = initiator.game
        self.productionist = self.game.productionist  # NLG module
        self.impressionist = self.game.impressionist  # NLU module
        self.productionist.debug = debug
        self.initiator = initiator
        self.recipient = recipient
        self.participants = [initiator, recipient]
        self.phone_call = phone_call
        self.locations = (self.initiator.location, self.recipient.location)
        self.debug = debug
        self.subject = Subject(conversation=self)  # The subject of conversation at a given point
        self.discontinued_subjects = set()  # Discontinued subjects of conversation
        self.turns = []  # A record of the conversation as an ordered list of its turns
        self.over = False  # Whether the conversation is over (gets set by Move.fire())
        # Obligations and goals -- these get populated as frames are inherited from
        self.obligations = {self.initiator: set(), self.recipient: set()}
        self.goals = {self.initiator: set(), self.recipient: set()}
        self.satisfied_goals = {self.initiator: set(), self.recipient: set()}
        # self.terminated_goals = {self.initiator: set(), self.recipient: set()}
        self.resolved_obligations = {self.initiator: set(), self.recipient: set()}
        self.topics = set()
        self.moves = set()  # A record of all dialogue moves, which are used as planning operators for goals
        # Inherit from conversational frames that pertain to the contexts of this conversation
        self.frames = set()
        self._init_inherit_from_frames()
        # Prepare containers for evidence objects that may be instantiated, depending on
        # whether knowledge is propagated as part of this conversation
        self.declarations = set()
        self.statements = set()
        self.lies = set()
        self.eavesdroppings = set()

        # TEST BLOCK
        initiator.mind.preoccupation = next(
            p for p in initiator.mind.mental_models if p.type == 'person' and initiator.belief(p, 'first name')
        )

    def __str__(self):
        """Return string representation."""
        s = (
            "Conversation between {initiator_name} and {recipient_name} at {location_name} on {date}.".format(
                initiator_name=self.initiator.name, recipient_name=self.recipient.name,
                location_name=self.initiator.location.name, date=self.date
            )
        )
        return s

    def _init_inherit_from_frames(self):
        """Inherit goals and initial obligations from conversational frames pertaining to the contexts
        of this conversation.
        """
        config = self.initiator.game.config
        for frame_name in config.conversational_frames:
            preconditions_satisfied = config.conversational_frames[frame_name]['preconditions'](
                conversation=self
            )
            if preconditions_satisfied:
                # Adopt frame
                frame = Frame(conversation=self, name=frame_name)
                self.frames.add(frame)
                # Inherit its obligations
                self.obligations[self.initiator] |= frame.obligations[self.initiator]
                self.obligations[self.recipient] |= frame.obligations[self.recipient]
                # Inherit its goals
                self.goals[self.initiator] |= frame.goals[self.initiator]
                self.goals[self.recipient] |= frame.goals[self.recipient]

    @property
    def speaker(self):
        """Return the current speaker."""
        if self.turns:
            return self.turns[-1].speaker
        else:
            return None

    @property
    def interlocutor(self):
        """Return the current interlocutor."""
        return self.interlocutor_to(self.speaker)

    @property
    def completed_turns(self):
        """Return all turns that have already been completed."""
        return [turn for turn in self.turns if hasattr(turn, 'line_of_dialogue')]

    @property
    def last_turn(self):
        """Return the last completed turn."""
        completed_turns = self.completed_turns
        return None if not completed_turns else completed_turns[-1]

    @property
    def last_speaker_turn(self):
        """Return the last turn completed by the current speaker."""
        all_completed_speaker_turns = [
            turn for turn in self.turns if hasattr(turn, 'line_of_dialogue') and turn.speaker is self.speaker
        ]
        if all_completed_speaker_turns:
            return all_completed_speaker_turns[-1]
        else:
            return None

    @property
    def last_interlocutor_turn(self):
        """Return the last turn completed by the current interlocutor."""
        all_completed_interlocutor_turns = [
            turn for turn in self.turns if hasattr(turn, 'line_of_dialogue') and turn.speaker is self.interlocutor
        ]
        if all_completed_interlocutor_turns:
            return all_completed_interlocutor_turns[-1]
        else:
            return None

    @property
    def goals_not_on_hold(self):
        """Return a dictionary listing the active goals for each conversational party whose plans are not on hold."""
        goals_not_on_hold = {
            self.initiator: {goal for goal in self.goals[self.initiator] if not goal.plan.on_hold},
            self.recipient: {goal for goal in self.goals[self.recipient] if not goal.plan.on_hold}
        }
        return goals_not_on_hold

    @property
    def speaker_subject_match(self):
        """Return the speaker's match for the subject of conversation, if any."""
        return self.subject.matches[self.speaker]

    def interlocutor_to(self, speaker):
        """Return the interlocutor to the given speaker."""
        return self.initiator if self.recipient is speaker else self.recipient

    def outline(self):
        """Outline the conversational frames underpinning this conversation, including the
        obligations and goals that they assert.
        """
        for frame in self.frames:
            frame.outline(n_tabs=1)

    def restart(self):
        """Return a new Conversation object with the same context as this one."""
        return Conversation(
            initiator=self.initiator, recipient=self.recipient, phone_call=self.phone_call, debug=self.debug
        )

    def replay(self):
        """Replay the conversation by printing out each of its lines."""
        for turn in self.turns:
            print turn

    def transpire(self):
        """Carry out the entire conversation."""
        while not self.over:
            if any(p for p in self.participants if p.player):
                time.sleep(0.6)
            self.proceed()
        # self.replay()
        for turn in self.turns:
            print '\n{}\n'.format(turn)

    def proceed(self):
        """Proceed with the conversation by advancing one turn."""
        if not self.over:
            next_speaker, targeted_obligation, targeted_goal = self.allocate_turn()
            Turn(
                conversation=self, speaker=next_speaker,
                targeted_obligation=targeted_obligation,
                targeted_goal=targeted_goal
            )

    def allocate_turn(self):
        """Allocate the next turn."""
        targeted_obligation = None
        targeted_goal = None
        # If both conversational parties have obligations, randomly allocate the turn
        if self.obligations[self.initiator] and self.obligations[self.recipient]:
            next_speaker = random.choice(self.participants)
            targeted_obligation = list(self.obligations[next_speaker])[0]
            if self.debug:
                print (
                    '[Both speakers currently have obligations. Randomly allocating turn according to {}]'.format(
                        targeted_obligation
                    )
                )
        # If the initiator has obligations, allocate the turn to them
        elif self.obligations[self.initiator]:
            next_speaker = self.initiator
            targeted_obligation = list(self.obligations[next_speaker])[0]
            if self.debug:
                print '[Allocating turn according to {}]'.format(targeted_obligation)
        # If the recipient has obligations, allocate the turn to them
        elif self.obligations[self.recipient]:
            next_speaker = self.recipient
            targeted_obligation = list(self.obligations[next_speaker])[0]
            if self.debug:
                print '[Allocating turn according to {}]'.format(targeted_obligation)
        # If both conversational parties have goals whose plans are not on hold, allocate randomly
        elif self.goals_not_on_hold[self.initiator] and self.goals_not_on_hold[self.recipient]:
            next_speaker = random.choice(self.participants)
            targeted_goal = list(self.goals_not_on_hold[next_speaker])[0]
        # If the initiator has a goal whose plan is not on hold, allocate to them
        elif self.goals_not_on_hold[self.initiator]:
            next_speaker = self.initiator
            targeted_goal = list(self.goals_not_on_hold[next_speaker])[0]
            if self.debug:
                print '[Allocating turn according to {}]'.format(targeted_goal)
        # If the recipient has a goal whose plan is not on hold, allocate to them
        elif self.goals_not_on_hold[self.recipient]:
            next_speaker = self.recipient
            targeted_goal = list(self.goals_not_on_hold[next_speaker])[0]
            if self.debug:
                print '[Allocating turn according to {}]'.format(targeted_goal)
        # If there are no obligations or unheld goals, probabilistically allocate the
        # turn with consideration given to the parties' relative extroversion values
        # TODO IMPROVE THE REASONING ABOUT ALLOCATION HERE
        else:
            if random.random() < 0.75:
                next_speaker = max(self.participants, key=lambda p: p.personality.extroversion)
            else:
                next_speaker = min(self.participants, key=lambda p: p.personality.extroversion)
            print '[No obligations or goals, so probabilistically allocated turn to {}]'.format(next_speaker.name)
        return next_speaker, targeted_obligation, targeted_goal

    def understand_player_utterance(self, player_utterance):
        """Request that Impressionist process a player's free-text dialogue input.

        This method will furnish an instantiated Impressionist.LineOfDialogue object, which will come
        with all of the necessary semantic and pragmatic information already attributed.
        """
        if self.debug:
            print "[A request has been made to Impressionist to process the player utterance '{}']".format(
                player_utterance
            )
        return self.impressionist.understand_player_utterance(player_utterance=player_utterance, conversation=self)

    def target_move(self, move_name):
        """Request that Productionist generate a line of dialogue that may be used to perform a
        targeted dialogue move.

        This method will furnish an instantiated Productionist.LineOfDialogue object, which will come
        with all of the necessary semantic and pragmatic information already attributed.
        """
        if self.debug:
            print "[A request has been made to Productionist to generate a line that will perform MOVE:{}]".format(
                move_name
            )
        return self.productionist.target_dialogue_move(move_name=move_name, conversation=self)

    def produce_batch_of_candidate_lines_that_perform_a_targeted_move(self, move_name):
        """Return a batch of four candidate lines that perform a dialogue move targeted by
        the player; the player may then select which of these lines to deploy.
        """
        candidate_lines = []
        number_of_generation_attempts = 0
        while len(candidate_lines) < 4 and number_of_generation_attempts < 99:
            next_candidate_line = self.productionist.target_dialogue_move(move_name=move_name, conversation=self)
            if (
                    next_candidate_line and
                    not any(l for l in candidate_lines if l.raw_line == next_candidate_line.raw_line)
            ):
                candidate_lines.append(next_candidate_line)
            number_of_generation_attempts += 1
        return candidate_lines

    def target_topic(self, topics=None):
        """Request that Productionist generate a line of dialogue that may be used to address one of the
        given topics of conversation.

        If particular topics are specified, this method will request a line that addresses any one
        of them; otherwise, it will request a line that addresses any active topic.
        """
        # TODO PUT TOPICS IN ORDER OF MOST RECENT TO LEAST RECENT
        if self.debug:
            print "[{} is requesting that Productionist generate a line that will address a topic]".format(
                self.speaker.first_name
            )
        topics = self.topics if not topics else topics
        topic_names = [topic.name for topic in topics]
        return self.productionist.target_topics_of_conversation(topic_names=topic_names, conversation=self)

    def count_move_occurrences(self, acceptable_speakers, name):
        """Count the number of times the acceptable speakers have performed a dialogue move with the given name."""
        moves_meeting_the_specification = [
            move for move in self.moves if move.speaker in acceptable_speakers and move.name == name
        ]
        return len(moves_meeting_the_specification)

    def earlier_move(self, speaker, name):
        """Return whether speaker has already performed a dialogue move with the given name."""
        relevant_speakers = self.participants if speaker == 'either' else (speaker,)
        return any(move for move in self.moves if move.speaker in relevant_speakers and move.name == name)

    def turns_since_earlier_move(self, speaker, name):
        """Return the number of turns that have been completed since speaker performed a dialogue
        move with the given name.
        """
        relevant_speakers = self.participants if speaker == 'either' else (speaker,)
        earlier_turns_that_performed_that_move = [
            turn for turn in self.completed_turns if any(
                move for move in turn.moves_performed if move.speaker in relevant_speakers and move.name == name
            )
        ]
        latest_such_turn = max(earlier_turns_that_performed_that_move, key=lambda t: t.index)
        turns_completed_since_that_turn = self.completed_turns[-1].index - latest_such_turn.index
        return turns_completed_since_that_turn

    def last_speaker_move(self, name):
        """Return whether the interlocutor's last move was one with the given name."""
        return self.speaker and self.last_speaker_turn.performed_move(name=name)

    def last_interlocutor_move(self, name):
        """Return whether the interlocutor's last move was one with the given name."""
        return self.last_interlocutor_turn and self.last_interlocutor_turn.performed_move(name=name)

    def turns_taken(self, speaker):
        """Return the number of turns taken so far by the given speaker."""
        return len([turn for turn in self.turns if turn.speaker is speaker])

    def has_obligation(self, conversational_party, move_name):
        """Return whether the conversational party currently has an obligation to perform a move with the given name."""
        return any(o for o in self.obligations[conversational_party] if o.move_name == move_name)

    def no_obligation(self, conversational_party, move_name):
        """Return whether the conversational party currently has no obligation to perform a move with the given name."""
        return not any(o for o in self.obligations[conversational_party] if o.move_name == move_name)

    def outstanding_obligations(self):
        """Return whether there are any outstanding conversational obligations."""
        return self.obligations[self.initiator] or self.obligations[self.recipient]

    def already_a_topic(self, name):
        """Return whether there is already an active topic with the given name."""
        return any(t for t in self.topics if t.name == name)

    def get_evidence_object(self, evidence_type, subject, source, recipient, eavesdropper=None):
        """Return an evidence object satisfying the given criteria, if one has already been instantiated."""
        if evidence_type == 'declaration':
            try:
                evidence_object = next(
                    d for d in self.declarations if d.subject == subject and d.source == source and
                    d.recipient == recipient
                )
            except StopIteration:
                evidence_object = None
        elif evidence_type == 'statement':
            try:
                evidence_object = next(
                    s for s in self.statements if s.subject == subject and s.source == source and
                    s.recipient == recipient
                )
            except StopIteration:
                evidence_object = None
        elif evidence_type == 'lie':
            try:
                evidence_object = next(
                    l for l in self.statements if l.subject == subject and l.source == source and
                    l.recipient == recipient
                )
            except StopIteration:
                evidence_object = None
        else:  # evidence_type == 'eavesdropping'
            try:
                evidence_object = next(
                    l for l in self.eavesdroppings if l.subject == subject and l.source == source and
                    l.recipient == recipient and eavesdropper == eavesdropper
                )
            except StopIteration:
                evidence_object = None
        return evidence_object


class Turn(object):
    """An utterance delivered by one character to another; a unit of conversation."""

    def __init__(self, conversation, speaker, targeted_obligation, targeted_goal):
        """Initialize an Turn object."""
        self.conversation = conversation
        self.speaker = speaker
        self.interlocutor = conversation.interlocutor_to(speaker)
        self.subject = conversation.subject
        self.propositions = set()
        self.targeted_obligation = targeted_obligation
        self.targeted_goal = targeted_goal
        self.moves_performed = set()
        self.topics_addressed = set()
        self.obligations_resolved = set()
        self.index = len(conversation.turns)
        self.conversation.turns.append(self)
        self.realization = ''  # Dialogue template as it was filled in during this turn
        if self.speaker.player:
            self.line_of_dialogue = self._process_player_dialogue_input()
        else:  # Speaker is an NPC
            self.line_of_dialogue = self._decide_what_to_say()
        self._realize_line_of_dialogue()
        self.eavesdropper = self._potentially_be_eavesdropped()
        self._update_conversation_state()

    def __str__(self):
        """Return string representation."""
        return '{}: {}'.format(self.speaker.name, self.realization)

    def _process_player_dialogue_input(self):
        """Process the player's free-text dialogue input to instantiate a line of dialogue."""
        # Ask the player to provide her next utterance
        raw_player_utterance = self._solicit_player_utterance()
        # Ask the conversation object associated with this turn to ask its Impressionist to
        # process this line; this will furnish an Impressionist.LineOfDialogue object that has
        # all the semantic and pragmatic information that we need, as well as a realize() method,
        # which will simply print out the player's utterance
        line_of_dialogue_object = self.conversation.understand_player_utterance(
            player_utterance=raw_player_utterance
        )
        return line_of_dialogue_object

    def _solicit_player_utterance(self):
        """Solicit free-text input from the player."""
        prompt = "\n{player_character_name}: ".format(player_character_name=self.speaker.name)
        raw_player_utterance = raw_input(prompt)
        print ''  # To closest_match the style of how NPC lines of dialogue are displayed
        return raw_player_utterance

    def _decide_what_to_say(self):
        """Have the speaker select a line of dialogue to deploy on this turn."""
        if self.targeted_obligation:
            selected_line = self.targeted_obligation.target()
        elif self.targeted_goal:
            if self.conversation.debug:
                print "[{} is searching for a line that will achieve {}]".format(
                    self.conversation.speaker.first_name, self.targeted_goal
                )
            selected_line = self.targeted_goal.target()
        elif self.conversation.topics:
            if self.conversation.debug:
                print "[{} is searching for a line that will address a relevant topic]".format(
                    self.speaker.first_name, self.targeted_goal
                )
            selected_line = self.conversation.target_topic()
        else:
            # Either engage in small talk or adopt a goal to end the conversation
            if random.random() < max(self.speaker.personality.extroversion, 0.05):
                selected_line = self.conversation.target_move(move_name='make small talk')
            else:
                new_goal_to_end_conversation = Goal(
                    conversation=self.conversation, owner=self.speaker, name='END CONVERSATION'
                )
                self.conversation.goals[self.speaker].add(new_goal_to_end_conversation)
                self.targeted_goal = new_goal_to_end_conversation
                selected_line = self._decide_what_to_say()  # Which will now target the new goal
        if selected_line is None:
            # You couldn't find a viable line, so just adopt and target a goal to
            # end the conversation
            new_goal_to_end_conversation = Goal(
                conversation=self.conversation, owner=self.speaker, name='END CONVERSATION'
            )
            self.targeted_goal = new_goal_to_end_conversation
            return self._decide_what_to_say()
        else:
            return selected_line

    def _realize_line_of_dialogue(self):
        """Display the line of dialogue on screen."""
        self.realization = self.line_of_dialogue.realize(conversation_turn=self)
        # If the speaker is an NPC, print their line out; if it's a player, the line
        # has already been made visible from the player typing it
        if not self.speaker.player:
            print '\n{name}: {line}\n'.format(name=self.speaker.name, line=self.realization)

    def _potentially_be_eavesdropped(self):
        """Potentially have the line of dialogue asserting this proposition be eavesdropped by a nearby character."""
        # TODO maybe affect this by how salient subject is to eavesdropper
        people_in_earshot = self.conversation.speaker.location.people_here_now - {self.speaker, self.interlocutor}
        eavesdropper = None if not people_in_earshot else random.choice(list(people_in_earshot))
        if eavesdropper and random.random() < self.speaker.game.config.chance_someone_eavesdrops_statement_or_lie:
            if self.conversation.debug:
                print '-- Eavesdropped by {}'.format(eavesdropper.name)
            return eavesdropper
        else:
            return None

    def _update_conversation_state(self):
        """Update the conversation state and have the interlocutor consider any propositions."""
        self._update_context()
        self._assert_propositions()
        self._reify_dialogue_moves()
        self._satisfy_goals()
        self._resolve_obligations()
        self._push_obligations()
        self._push_topics()
        self._address_topics()
        self._fire_dialogue_moves()

    def _update_context(self):
        """Update the common-ground conversational context, which holds information about the subject of
        conversation and other concerns.
        """
        self._update_subject_of_conversation()

    def _update_subject_of_conversation(self):
        """Update common-ground information surrounding the subject of conversation."""
        line = self.line_of_dialogue
        # Potentially discontinue the current subject of conversation
        if line.clear_subject_of_conversation:
            self.conversation.discontinued_subjects.add(self.conversation.subject)
            self.conversation.subject = Subject(conversation=self.conversation)
            self.subject = self.conversation.subject
        # Push new features regarding the subject
        subject_updates = [u[8:] for u in line.context_updates if u[:8] == 'subject:']
        self.conversation.subject.update(
            new_features=subject_updates,
            force_match_to_speaker_preoccupation=line.force_speaker_subject_match_to_speaker_preoccupation
        )

    def _assert_propositions(self):
        """Assert propositions about the world that are expressed by the content of the generated line."""
        for proposition_specification in self.line_of_dialogue.propositions:
            # TODO INFER LIES VIA VIOLATIONS REASONING (PROB SHOULD JUST HAVE SEPARATE LIE-CONDITIONS TAGSET)
            proposition_object = Proposition(
                conversation=self.conversation, this_is_a_lie=False, specification=proposition_specification
            )
            self.propositions.add(proposition_object)

    def _reify_dialogue_moves(self):
        """Instantiate objects for the dialogue moves performed on this turn."""
        for move_name in self.line_of_dialogue.moves:
            move_object = Move(conversation=self.conversation, speaker=self.speaker, name=move_name)
            self.conversation.moves.add(move_object)
            self.moves_performed.add(move_object)

    def _satisfy_goals(self):
        """Satisfy any goals whose targeted move was constituted by the execution of this turn."""
        # Satisfy speaker goals
        for goal in list(self.conversation.goals[self.speaker]):
            if goal.achieved:
                self.conversation.goals[self.speaker].remove(goal)
                self.conversation.satisfied_goals[self.speaker].add(goal)
                if self.conversation.debug:
                    print '-- Satisfied {}'.format(goal)
        # Satisfy interlocutor goals
        for goal in list(self.conversation.goals[self.interlocutor]):
            if goal.achieved:
                self.conversation.goals[self.interlocutor].remove(goal)
                self.conversation.satisfied_goals[self.interlocutor].add(goal)
                if self.conversation.debug:
                    print '-- Satisfied {}'.format(goal)

    def _resolve_obligations(self):
        """Resolve any conversational obligations according to the mark-up of the generated line."""
        # Resolve speaker obligations
        for move_name in self.line_of_dialogue.moves:
            if any(obligation for obligation in self.conversation.obligations[self.speaker] if
                   obligation.move_name == move_name):
                obligation_to_resolve = next(
                    obligation for obligation in self.conversation.obligations[self.speaker] if
                    obligation.move_name == move_name
                )
                self.conversation.obligations[self.speaker].remove(obligation_to_resolve)
                self.conversation.resolved_obligations[self.speaker].add(obligation_to_resolve)
                self.obligations_resolved.add(obligation_to_resolve)
                if self.conversation.debug:
                    print '-- Resolved {}'.format(obligation_to_resolve)
        # Resolve interlocutor obligations
        # TODO SUPPORT THIS ONCE YOU HAVE A USE CASE

    def _push_obligations(self):
        """Push new conversational obligations according to the mark-up of this line."""
        # Push speaker obligations
        for obligation_name in self.line_of_dialogue.speaker_obligations_pushed:
            obligation_object = Obligation(
                conversation=self.conversation, obligated_party=self.speaker, move_name=obligation_name
            )
            self.conversation.obligations[self.speaker].add(obligation_object)
            if self.conversation.debug:
                print '-- Pushed {}'.format(obligation_object)
        # Push interlocutor obligations
        for obligation_name in self.line_of_dialogue.interlocutor_obligations_pushed:
            obligation_object = Obligation(
                conversation=self.conversation, obligated_party=self.interlocutor, move_name=obligation_name
            )
            self.conversation.obligations[self.interlocutor].add(obligation_object)
            if self.conversation.debug:
                print '-- Pushed {}'.format(obligation_object)

    def _push_topics(self):
        """Push new topics of conversation according to the mark-up of this line."""
        for topic_name in self.line_of_dialogue.topics_pushed:
            if not any(t for t in self.conversation.topics if t.name == topic_name):
                topic_object = Topic(name=topic_name)
                self.conversation.topics.add(topic_object)
                self.topics_addressed.add(topic_object)
                if self.conversation.debug:
                    print '-- Pushed "{}"'.format(topic_object)

    def _address_topics(self):
        """Address topics of conversation according to the mark-up of this line."""
        for topic_name in self.line_of_dialogue.topics_addressed:
            try:
                topic_object = next(t for t in self.conversation.topics if t.name == topic_name)
                self.topics_addressed.add(topic_object)
                if self.conversation.debug:
                    print '-- Addressed "{}"'.format(topic_object)
            except StopIteration:  # Topic has not been introduced yet
                if self.speaker.player:  # If the speaker is a player character, let it slide
                    pass
                else:
                    raise Exception(
                        "{speaker} is attempting to address a topic ({topic}) that has not yet been introduced.".format(
                            speaker=self.speaker.name,
                            topic=topic_name
                        )
                    )

    def _fire_dialogue_moves(self):
        """Fire rules associated with the dialogue moves performed on this turn."""
        for move in self.moves_performed:
            move.fire()

    def performed_move(self, name):
        """Return whether this turn performed a move with the given name."""
        return any(m for m in self.moves_performed if m.name == name)

    def did_not_perform_move(self, name):
        """Return whether this turn did *not* perform a move with the given name."""
        return not any(m for m in self.moves_performed if m.name == name)

    def addressed_topic(self, name):
        """Return whether this turn addressed a topic with the given name."""
        return any(t for t in self.topics_addressed if t.name == name)

    def did_not_address_topic(self, name):
        """Return whether this turn did *not* address a topic with the given name."""
        return not any(t for t in self.topics_addressed if t.name == name)

    def resolved_obligation(self, name=None):
        """Return whether this turn resolved an obligation with the given name.

        If None is passed for 'name', this method will return whether this turn resolved *any* obligation.
        """
        if name:
            return any(o for o in self.obligations_resolved if o.name == name)
        else:
            return True if self.obligations_resolved else False


class Move(object):
    """A dialogue move by a conversational party."""

    def __init__(self, conversation, speaker, name):
        """Initialize a Move object."""
        self.conversation = conversation
        self.speaker = speaker
        self.interlocutor = conversation.interlocutor_to(speaker)
        self.name = name
        if conversation.debug:
            print '-- Performed {}'.format(self)

    def __str__(self):
        """Return string representation."""
        return "MOVE:{}:{}".format(self.speaker.name, self.name)

    def fire(self):
        """Change the world according to the illocutionary force of this move."""
        # If someone storms off, or both parties say goodbye (and neither has any
        # outstanding obligations), end the conversation
        if self.name == 'storm off':
            self.conversation.over = True
        elif self.name == "say goodbye back" and not self.conversation.outstanding_obligations():
            self.conversation.over = True


class Obligation(object):
    """A conversational obligation imposed on one conversational party by a line of dialogue."""

    def __init__(self, conversation, obligated_party, move_name):
        """Initialize an Obligation object."""
        self.conversation = conversation
        self.obligated_party = obligated_party
        self.move_name = move_name  # Name of the move that this obligates obligated_party to perform next

    def __str__(self):
        """Return string representation."""
        return 'OBLIGATION:{}:{}'.format(self.obligated_party.name, self.move_name)

    def outline(self, n_tabs):
        """Outline this obligation for debugging purposes."""
        print '{}{}'.format('\t'*n_tabs, self)

    def target(self):
        """Select a line of dialogue that would resolve this obligation."""
        return self.conversation.target_move(move_name=self.move_name)


class Proposition(object):
    """A proposition about the world asserted by the content of a line of dialogue."""

    def __init__(self, conversation, this_is_a_lie, specification):
        """Initialize a Proposition object."""
        self.conversation = conversation
        # Attribute speaker and interlocutor as source and recipient of this proposition, respectively
        self.source = conversation.speaker
        self.recipient = conversation.interlocutor
        # Parse the specification to resolve and assign our other crucial attributes
        self.subject = None
        self.feature_value = ''
        self.feature_object_itself = None
        self.feature_type = ''
        self._init_parse_specification(specification=specification)
        # Inherit eavesdropper of the current conversation turn, if any
        self.eavesdropper = conversation.turns[-1].eavesdropper
        # Instantiate and/or attribute evidence objects
        self.declaration = None
        self.statement = None
        self.lie = None
        self.eavesdropping = None
        # Print debug statement
        if conversation.debug:
            print '-- Asserting {}...'.format(self)
        # If they don't exist yet, establish mental models pertaining to the subject of this
        # proposition that will be owned by its source, recipient, and eavesdropper (if there
        # is one)
        self._establish_mental_models_of_subject()
        # Instantiate Declaration, Statement, Lie, and Eavesdropping evidence objects, as appropriate
        self._instantiate_and_or_attribute_evidence_objects(this_is_a_lie=this_is_a_lie)
        # Have the source, recipient, and eavesdropper (if any) of this proposition consider
        # adopting a belief in response to it by evaluating the appropriate pieces of evidence
        self._have_all_parties_consider_this_proposition_as_evidence()

    def __str__(self):
        """Return string representation."""
        return 'PROPOSITION:{feature_type}({subject}, "{feature_value}")'.format(
            feature_type=self.feature_type,
            subject=self.subject.name,
            feature_value=self.feature_value
        )

    def _init_parse_specification(self, specification):
        """Parse the specification for this proposition to set this object's individual specification attributes."""
        subject, feature_type, feature_value, feature_object_itself = specification.split(';')
        # Make sure the specification is well-formed
        assert 'subject=' in subject, 'Ill-formed proposition specification: {}'.format(specification)
        assert 'feature_type=' in feature_type, 'Ill-formed proposition specification: {}'.format(specification)
        assert 'feature_value=' in feature_value, 'Ill-formed proposition specification: {}'.format(specification)
        assert 'feature_object_itself=' in feature_object_itself, (
            'Ill-formed proposition specification: {}'.format(specification)
        )
        # Parse the individual elements of the specification
        subject_ref = subject[len('subject='):]
        feature_type = feature_type[len('feature_type='):]
        feature_value_ref = feature_value[len('feature_value='):]
        feature_object_itself_ref = feature_object_itself[len('feature_object_itself='):]
        # Evaluate the references to resolve to attributes for this object (this requires
        # us to pull in some variables from the conversational context)
        speaker, interlocutor, subject = (
            self.conversation.speaker, self.conversation.interlocutor, self.conversation.subject
        )
        self.subject = eval(subject_ref)
        self.feature_value = eval(feature_value_ref)
        self.feature_object_itself = eval(feature_object_itself_ref)
        # Feature type doesn't need to be evaluated (it's just a string), so attribute it as is
        self.feature_type = feature_type

    def _establish_mental_models_of_subject(self):
        """If necessary, reify mental models pertaining to the subject of this proposition that will be owned by its
        source, recipient, and eavesdropper (if any)."""
        if self.subject not in self.source.mind.mental_models:
            PersonMentalModel(owner=self.source, subject=self.subject, observation_or_reflection=None)
        if self.subject not in self.recipient.mind.mental_models:
            PersonMentalModel(owner=self.recipient, subject=self.subject, observation_or_reflection=None)
        if self.eavesdropper:
            if self.subject not in self.eavesdropper.mind.mental_models:
                PersonMentalModel(owner=self.eavesdropper, subject=self.subject, observation_or_reflection=None)

    def _instantiate_and_or_attribute_evidence_objects(self, this_is_a_lie):
        """Instantiate and/or attribute Declaration and Statement/Lie evidence objects."""
        self._instantiate_and_or_attribute_declaration_object()
        if self.conversation.debug:
            print "\t- Reified declaration piece of evidence"
        if this_is_a_lie:
            self._instantiate_and_or_attribute_lie_object()
            if self.conversation.debug:
                print "\t- Reified lie piece of evidence"
        else:
            self._instantiate_and_or_attribute_statement_object()
            if self.conversation.debug:
                print "\t- Reified statement piece of evidence"
        if self.eavesdropper:
            self._instantiate_and_or_adopt_eavesdropping_object()
            if self.conversation.debug:
                print "\t- Reified eavesdropping piece of evidence ({} eavesdropped)".format(
                    self.eavesdropper.name
                )

    def _instantiate_and_or_attribute_declaration_object(self):
        """Instantiate and/or attribute a Declaration object."""
        declaration_object = self.conversation.get_evidence_object(
            evidence_type='declaration', source=self.source, subject=self.subject, recipient=self.recipient,
        )
        if declaration_object:
            self.declaration = declaration_object
        else:
            declaration_object = Declaration(subject=self.subject, source=self.source, recipient=self.recipient)
            self.declaration = declaration_object
            self.conversation.declarations.add(declaration_object)

    def _instantiate_and_or_attribute_statement_object(self):
        """Instantiate and/or attribute a Statement object."""
        statement_object = self.conversation.get_evidence_object(
            evidence_type='statement', source=self.source, subject=self.subject, recipient=self.recipient,
        )
        if statement_object:
            self.statement = statement_object
        else:
            statement_object = Statement(subject=self.subject, source=self.source, recipient=self.recipient)
            self.statement = statement_object
            self.conversation.statements.add(statement_object)

    def _instantiate_and_or_attribute_lie_object(self):
        """Instantiate and/or attribute a Lie object."""
        lie_object = self.conversation.get_evidence_object(
            evidence_type='lie', source=self.source, subject=self.subject, recipient=self.recipient,
        )
        if lie_object:
            self.lie = lie_object
        else:
            lie_object = Lie(subject=self.subject, source=self.source, recipient=self.recipient)
            self.lie = lie_object
            self.conversation.lies.add(lie_object)

    def _instantiate_and_or_adopt_eavesdropping_object(self):
        """Instantiate and/or attribute a Eavesdropping object."""
        # Instantiate and/or attribute the object
        eavesdropping_object = self.conversation.get_evidence_object(
            evidence_type='eavesdropping', source=self.source, subject=self.subject, recipient=self.recipient,
            eavesdropper=self.eavesdropper
        )
        if eavesdropping_object:
            self.eavesdropping = eavesdropping_object
        else:
            eavesdropping_object = Eavesdropping(
                subject=self.subject, source=self.source, recipient=self.recipient, eavesdropper=self.eavesdropper
            )
            self.eavesdropping = eavesdropping_object
            self.conversation.eavesdroppings.add(eavesdropping_object)

    def _have_all_parties_consider_this_proposition_as_evidence(self):
        """Have the source, recipient, and eavesdropper (if any) of this proposition consider adopting a
        belief in response to it by evaluating the appropriate pieces of evidence
        """
        # Have the recipient consider the Statement object conveying this proposition
        self.recipient.mind.mental_models[self.subject].consider_new_evidence(
            feature_type=self.feature_type, feature_value=self.feature_value,
            feature_object_itself=self.feature_object_itself, new_evidence=self.statement
        )
        # Have the source of this proposition reinforce their own belief with a Declaration object
        self.source.mind.mental_models[self.subject].consider_new_evidence(
            feature_type=self.feature_type, feature_value=self.feature_value,
            feature_object_itself=self.feature_object_itself, new_evidence=self.declaration
        )
        # If someone is eavesdropping, have them consider this proposition via an Eavesdropping object
        if self.eavesdropping:
            self.eavesdropper.mind.mental_models[self.subject].consider_new_evidence(
                feature_type=self.feature_type, feature_value=self.feature_value,
                feature_object_itself=self.feature_object_itself, new_evidence=self.eavesdropping
            )
        if self.conversation.debug:
            print "\t- All conversational parties considered their new evidence"


class Violation(object):
    """A violate of a conversational obligation or norm by a conversational party."""

    def __init__(self):
        """Initialize a Violation of object."""
        pass


class Flouting(object):
    """An intentional violation of a conversational obligation or norm,

    This is an operationalization of the notion of a flouting in Grice's theory of
    the cooperative principle, which is famous in linguistic pragmatics."""

    def __init__(self):
        """Initialize a Flouting object."""
        pass


class Goal(object):
    """A conversational goal held by a conversational party."""

    def __init__(self, conversation, owner, name, required_number_of_occurrences=1):
        """Initialize a Goal object."""
        self.conversation = conversation
        self.owner = owner
        self.name = name
        self.required_number_of_occurrences = required_number_of_occurrences
        self.plan = Plan(goal=self)
        # Specification for the dialogue move that would satisfy this goal (and is thus
        # the last step in this goal's plan)
        self.move_acceptable_speakers = self.plan.steps[-1].move_acceptable_speakers
        self.move_name = self.plan.steps[-1].move_name

    def __str__(self):
        """Return string representation."""
        return 'GOAL:{}:{}{}'.format(
            self.owner.name,
            self.name,
            '' if self.required_number_of_occurrences == 1 else ' (x{})'.format(self.required_number_of_occurrences)
        )

    @property
    def achieved(self):
        """Return whether this step has been achieved."""
        move_occurrences_count = self.conversation.count_move_occurrences(
            acceptable_speakers=self.move_acceptable_speakers, name=self.move_name
        )
        if move_occurrences_count >= self.required_number_of_occurrences:
            return True
        else:
            return False

    def outline(self, n_tabs):
        """Outline this goal for debugging purposes."""
        print '{}{}'.format('\t'*n_tabs, self)
        self.plan.outline(n_tabs+1)

    def target(self):
        """Select a line of dialogue to target the achievement of this goal."""
        if self.conversation.debug:
            print "[{} is searching for a line that will resolve {}]".format(
                self.conversation.speaker.first_name, self
            )
        return self.plan.execute()


class Plan(object):
    """A plan to achieve a conversational goal in the form of a sequence of steps."""

    def __init__(self, goal):
        """Initialize a Plan object."""
        self.conversation = goal.conversation
        self.goal = goal
        self.steps = self._init_steps()

    def __str__(self):
        """Return string representation."""
        return "PLAN:{}".format(self.goal)

    def _init_steps(self):
        """Instantiate the steps in this plan according to the specifications of our config file.

        The steps of a plan will be a sequence of Step and Goal objects, the latter of which will
        have their own plans.
        """
        steps = []
        config = self.goal.owner.game.config
        for move_speaker_ref, move_name, required_number_of_occurrences in config.conversational_goals[self.goal.name]:
            if move_name in config.conversational_goals:
                # Instantiate a Goal object for this subgoal, whose own plan will automatically be instantiated
                steps.append(
                    Goal(
                        conversation=self.conversation, owner=self.goal.owner, name=move_name,
                        required_number_of_occurrences=required_number_of_occurrences
                    )
                )
            else:
                # Instantiate a Step object
                steps.append(
                    Step(
                        conversation=self.conversation, owner=self.goal.owner, move_speaker_ref=move_speaker_ref,
                        move_name=move_name, required_number_of_occurrences=required_number_of_occurrences
                    )
                )
        return steps

    @property
    def executed(self):
        """Return whether this plan has been fully executed, i.e., whether all its steps have been achieved."""
        return all(step.achieved for step in self.steps)

    @property
    def on_hold(self):
        """Return whether this plan is on hold due to its next step having to be constituted
        by the interlocutor performing some move.
        """
        next_step = next(step for step in self.steps if not step.achieved)
        whether_this_plan_is_on_hold = self.goal.owner not in next_step.move_acceptable_speakers
        return whether_this_plan_is_on_hold

    def outline(self, n_tabs):
        """Outline this plan for debugging purposes."""
        for step in self.steps:
            step.outline(n_tabs)

    def execute(self):
        """Execute the next step in this plan."""
        next_step = next(step for step in self.steps if not step.achieved)
        assert not self.on_hold, (
            "A call was made to the execute method of {}, but this plan is on hold.".format(self)
        )
        return next_step.target()


class Step(object):
    """A step in a conversational plan."""

    def __init__(self, conversation, owner, move_speaker_ref, move_name, required_number_of_occurrences):
        """Initialize a Step object."""
        self.conversation = conversation
        self.owner = owner
        self.move_acceptable_speakers = self._init_determine_acceptable_speakers(move_speaker_ref=move_speaker_ref)
        self.move_name = move_name
        self.required_number_of_occurrences = required_number_of_occurrences

    def __str__(self):
        """Return string representation."""
        return 'STEP:{}:{}{}'.format(
            '|'.join(s.name for s in self.move_acceptable_speakers),
            self.move_name,
            '' if self.required_number_of_occurrences == 1 else ' (x{})'.format(self.required_number_of_occurrences)
        )

    def _init_determine_acceptable_speakers(self, move_speaker_ref):
        """Return a tuple of the speakers who upon performing the specified dialogue move would cause
        this step to be achieved.
        """
        if move_speaker_ref == 'me':
            return self.owner,
        elif move_speaker_ref == 'them':
            return self.conversation.interlocutor_to(self.owner),
        elif move_speaker_ref == 'either':
            return tuple(self.conversation.participants)
        else:
            raise Exception("{} has an misformatted acceptable speaker {}".format(self, move_speaker_ref))

    @property
    def achieved(self):
        """Return whether this step has been achieved."""
        move_occurrences_count = self.conversation.count_move_occurrences(
            acceptable_speakers=self.move_acceptable_speakers, name=self.move_name
        )
        if move_occurrences_count >= self.required_number_of_occurrences:
            return True
        else:
            return False

    def outline(self, n_tabs):
        """Outline this plan for debugging purposes."""
        print '{}{}'.format('\t'*n_tabs, self)

    def target(self):
        """Select a line of dialogue to target the achievement of this step."""
        if self.conversation.debug:
            print "[{} is searching for a line that will realize {}]".format(
                self.conversation.speaker.first_name, self
            )
        return self.conversation.target_move(move_name=self.move_name)


class Topic(object):
    """A topic of conversation that may be brought up or addressed by a line of dialogue."""

    def __init__(self, name):
        """Initialize an Topic object."""
        self.name = name

    def __str__(self):
        """Return string representation."""
        return "TOPIC:{}".format(self.name)


class Subject(object):
    """A subject of conversation (either a person or place) that is represented as a collection of
    features that conversants may use to access a mental model of that person or place.
    """

    def __init__(self, conversation, entity_type='person'):
        """Initialize a Subject object."""
        self.conversation = conversation
        self.entity_type = entity_type
        # A set of features of the form '[feature_type]:[feature_value]', e.g., 'hair_color=red'
        self.features = set()
        # The conversants' respective closest matches for the subject of conversation, given
        # the features in context (may be None if there are no matches)
        self.matches = {conversation.initiator: None, conversation.recipient: None}

    def update(self, new_features, force_match_to_speaker_preoccupation):
        """Update the subject of conversation, given a new set of features that have been pushed into context."""
        # Parse the features into tuples of the form (feature_type, feature_value), where
        # feature_type is correctly formatted (i.e., spaces instead of underscores)
        if new_features:
            parsed_features = set()
            for feature in new_features:
                feature_type, feature_value = feature.split('=')
                # Replace underscores in feature_type with whitespace to make person.mind.closest_match() work
                feature_type = feature_type.replace('_', ' ')
                # Evaluate the feature_value reference, which may be something like
                # "speaker.belief(speaker.mind.preoccupation, 'first name')"
                feature_value = self._realize_feature_value(
                    conversation=self.conversation, feature_value=feature_value
                )
                parsed_features.add((feature_type, feature_value))
            self.features |= parsed_features
            for conversant in self.matches:
                self.matches[conversant] = conversant.mind.closest_match(
                    features=self.features, entity_type=self.entity_type
                )
            if force_match_to_speaker_preoccupation:
                self.matches[self.conversation.speaker] = self.conversation.speaker.mind.preoccupation

    @staticmethod
    def _realize_feature_value(conversation, feature_value):
        """Evaluate the specification for a feature value to realize it."""
        # Prepare local variables that will allow us to realize this value
        speaker, interlocutor, subject = conversation.speaker, conversation.interlocutor, None
        try:
            return str(eval(feature_value))
        except NameError:  # Feature value is already a string, e.g., the 'f' in 'sex=f'
            return feature_value


class Frame(object):
    """A Minskian frame for a conversational context, e.g., a phone call."""

    def __init__(self, conversation, name):
        """Initialize a Frame object."""
        self.conversation = conversation
        self.name = name
        self.obligations = self._reify_obligations()
        self.goals = self._reify_goals()

    def __str__(self):
        """Return string representation."""
        return 'FRAME:{}'.format(self.name)

    def _reify_obligations(self):
        """Instantiate objects for the conversational obligations specified for this frame in our config file."""
        initiator = self.conversation.initiator
        recipient = self.conversation.recipient
        config = initiator.game.config
        # Slurp up obligation specifications from config
        obligations = {initiator: set(), recipient: set()}
        for obligation_name in config.conversational_frames[self.name]['obligations']['initiator']:
            obligations[initiator].add(
                Obligation(conversation=self.conversation, obligated_party=initiator, move_name=obligation_name)
            )
        for obligation_name in config.conversational_frames[self.name]['obligations']['recipient']:
            obligations[recipient].add(
                Obligation(conversation=self.conversation, obligated_party=recipient, move_name=obligation_name)
            )
        return obligations

    def _reify_goals(self):
        """Instantiate objects for the conversational goals specified for this frame in our config file."""
        initiator = self.conversation.initiator
        recipient = self.conversation.recipient
        config = initiator.game.config
        # Slurp up goal specifications from config
        goals = {initiator: set(), recipient: set()}
        for goal_name in config.conversational_frames[self.name]['goals']['initiator']:
            goals[initiator].add(Goal(conversation=self.conversation, owner=initiator, name=goal_name))
        for goal_name in config.conversational_frames[self.name]['goals']['recipient']:
            goals[recipient].add(Goal(conversation=self.conversation, owner=recipient, name=goal_name))
        return goals

    def outline(self, n_tabs):
        """Outline the obligations and goals imposed by this frame."""
        print '{}{}'.format('\t'*n_tabs, self)
        for obligation in self.obligations[self.conversation.initiator] | self.obligations[self.conversation.recipient]:
            obligation.outline(n_tabs+1)
        for goal in self.goals[self.conversation.initiator] | self.goals[self.conversation.recipient]:
            goal.outline(n_tabs+1)