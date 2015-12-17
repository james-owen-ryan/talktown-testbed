import random
from event import Event


class Conversation(Event):
    """A conversation between two characters in a city."""

    def __init__(self, initiator, recipient, phone_call=False, debug=True):
        """Initialize a Conversation object."""
        super(Conversation, self).__init__(game=initiator.game)
        self.dialogue_base = initiator.game.dialogue_base
        self.initiator = initiator
        self.recipient = recipient
        self.participants = [initiator, recipient]
        self.phone_call = phone_call
        self.locations = (self.initiator.location, self.recipient.location)
        self.debug = debug
        self.subject = None  # The subject of conversation at a given point
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
    def completed_turns(self):
        """Return all turns that have already been completed."""
        return [turn for turn in self.turns if hasattr(turn, 'line_of_dialogue')]

    @property
    def goals_not_on_hold(self):
        """Return a dictionary listing the active goals for each conversational party whose plans are not on hold."""
        goals_not_on_hold = {
            self.initiator: {goal for goal in self.goals[self.initiator] if not goal.plan.on_hold},
            self.recipient: {goal for goal in self.goals[self.recipient] if not goal.plan.on_hold}
        }
        return goals_not_on_hold

    def interlocutor_to(self, speaker):
        """Return the interlocutor to the given speaker."""
        return self.initiator if self.recipient is speaker else self.recipient

    def outline(self):
        """Outline the conversational frames underpinning this conversation, including the
        obligations and goals that they assert.
        """
        for frame in self.frames:
            frame.outline(n_tabs=1)

    def replay(self):
        """Replay the conversation by printing out each of its lines."""
        for turn in self.turns:
            print turn

    def transpire(self):
        """Carry out the entire conversation."""
        while not self.over:
            self.proceed()

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

    def target_move(self, move_name):
        """Select a line of dialogue that may be used to perform a targeted dialogue move."""
        lines_that_perform_this_move = [
            line for line in self.dialogue_base.all_lines_of_dialogue if
            move_name in line.moves and
            line.preconditions_satisfied(conversation_turn=self.turns[-1])
        ]
        # # Make sure to avoid lines that resolve obligations that you do not have
        # lines_that_resolve_this_obligation = [
        #     line for line in lines_that_resolve_this_obligation if not
        #     line.speaker_obligations_resolved -
        #     {o.name for o in self.conversation.obligations[self.conversation.speaker]}
        # ]
        selected_line = random.choice(lines_that_perform_this_move)
        return selected_line

    def target_topic(self, topics=None):
        """Select a line of dialogue that addresses one of the specified topics of conversation.

        If particular topics are specified, this method will target a line that addresses any one
        of them; otherwise, it will select a line that addresses any active topic.
        """
        # TODO MAYBE DO SEARCH BY ITERATING OVER TOPICS IN ORDER OF MOST RECENT TO LEAST RECENT
        topics = self.topics if not topics else topics
        lines_that_address_one_of_these_topics = [
            line for line in self.dialogue_base.all_lines_of_dialogue if
            line.topics_addressed & {topic.name for topic in topics} and
            line.preconditions_satisfied(conversation_turn=self)
        ]
        selected_line = random.choice(lines_that_address_one_of_these_topics)
        return selected_line

    def count_move_occurrences(self, acceptable_speakers, name):
        """Count the number of times the acceptable speakers have performed a dialogue move with the given name."""
        moves_meeting_the_specification = [
            move for move in self.moves if move.speaker in acceptable_speakers and move.name == name
        ]
        return len(moves_meeting_the_specification)


class Turn(object):
    """An utterance delivered by one character to another; a unit of conversation."""

    def __init__(self, conversation, speaker, targeted_obligation, targeted_goal):
        """Initialize an Turn object."""
        self.conversation = conversation
        self.speaker = speaker
        self.interlocutor = conversation.interlocutor_to(speaker)
        self.subject = conversation.subject
        self.targeted_obligation = targeted_obligation
        self.targeted_goal = targeted_goal
        self.index = len(conversation.turns)
        self.conversation.turns.append(self)
        self.line_of_dialogue = self._select_line_of_dialogue()
        self.realization = ''  # Dialogue template as it was filled in during this turn
        self._realize_line_of_dialogue()
        self._update_conversational_context()

    def __str__(self):
        """Return string representation."""
        return '{}: {}'.format(self.speaker.name, self.realization)

    def _select_line_of_dialogue(self):
        """Have the speaker select a line of dialogue to deploy on this turn."""
        # TODO ACTUALLY USE THE LINE'S PROBABILITIES HERE (EXCEPT THEY AREN'T PROPERLY RELATIVE?)
        if self.targeted_obligation:
            if self.conversation.debug:
                print "[{} is searching for a line that will resolve {}]".format(
                    self.conversation.speaker.first_name, self.targeted_obligation
                )
            return self.targeted_obligation.target()
        elif self.targeted_goal:
            if self.conversation.debug:
                print "[{} is searching for a line that will achieve {}]".format(
                    self.conversation.speaker.first_name, self.targeted_goal
                )
            return self.targeted_goal.target()
        elif self.conversation.topics:
            if self.conversation.debug:
                print "[{} is searching for a line that will address a relevant topic]".format(
                    self.speaker.first_name, self.targeted_goal
                )
            return self.conversation.target_topic()
        else:
            # Either engage in small talk or adopt a goal to end the conversation
            if random.random() < max(self.speaker.personality.extroversion, 0.05):
                return self.conversation.target_move(move_name='small talk')
            else:
                new_goal_to_end_conversation = Goal(
                    conversation=self.conversation, owner=self.speaker, name='END CONVERSATION'
                )
                self.conversation.goals[self.speaker].add(new_goal_to_end_conversation)
                self.targeted_goal = new_goal_to_end_conversation
                return self._select_line_of_dialogue()  # Which will now target the new goal

    def _realize_line_of_dialogue(self):
        """Display the line of dialogue on screen."""
        self.realization = self.line_of_dialogue.realize(conversation_turn=self)
        print '\n{}: {}\n'.format(self.speaker.name, self.realization)

    def _update_conversational_context(self):
        """Update the conversation state and have the interlocutor consider any propositions."""
        self._reify_dialogue_moves()
        self._instantiate_statements_for_propositions()
        self._change_subject_of_conversation()
        self._resolve_obligations()
        self._push_obligations()
        self._push_topics()
        self._satisfy_goals()

    def _reify_dialogue_moves(self):
        """Instantiate objects for the dialogue moves constituted by the delivery of this line."""
        for move_name in self.line_of_dialogue.moves:
            move_object = Move(speaker=self.speaker, name=move_name)
            self.conversation.moves.add(move_object)
            if self.conversation.debug:
                print '-- Reified {}'.format(move_object)

    def _instantiate_statements_for_propositions(self):
        """Instantiate and deliver Statement pieces of evidence for the propositions of the selected line."""
        pass

    def _change_subject_of_conversation(self):
        """Potentially change the subject of conversation according to the mark-up of the selected line."""
        speaker, interlocutor, subject = self.speaker, self.interlocutor, self.subject
        if self.line_of_dialogue.change_subject_to:
            new_subject = eval(self.line_of_dialogue.change_subject_to)
            self.conversation.subject = new_subject
            if self.conversation.debug:
                print '-- Changed subject to {}'.format('[hypothetical]' if not self.subject else self.subject.name)

    def _resolve_obligations(self):
        """Resolve any conversational obligations according to the mark-up of the selected line."""
        # Resolve speaker obligations
        for obligation_name in self.line_of_dialogue.speaker_obligations_resolved:
            if any(obligation for obligation in self.conversation.obligations[self.speaker] if
                   obligation.name == obligation_name):
                obligation_to_resolve = next(
                    obligation for obligation in self.conversation.obligations[self.speaker] if
                    obligation.name == obligation_name
                )
                self.conversation.obligations[self.speaker].remove(obligation_to_resolve)
                self.conversation.resolved_obligations[self.speaker].add(obligation_to_resolve)
                if self.conversation.debug:
                    print '-- Resolved "{}:{}"'.format(
                        obligation_to_resolve.obligated_party.name, obligation_to_resolve.name
                    )
        # Resolve interlocutor obligations
        for obligation_name in self.line_of_dialogue.interlocutor_obligations_resolved:
            if any(obligation for obligation in self.conversation.obligations[self.interlocutor] if
                   obligation.name == obligation_name):
                obligation_to_resolve = next(
                    obligation for obligation in self.conversation.obligations[self.interlocutor] if
                    obligation.name == obligation_name
                )
                self.conversation.obligations[self.interlocutor].remove(obligation_to_resolve)
                self.conversation.resolved_obligations[self.interlocutor].add(obligation_to_resolve)
                if self.conversation.debug:
                    print '-- Resolved "{}:{}"'.format(
                        obligation_to_resolve.obligated_party.name, obligation_to_resolve.name
                    )

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
            topic_object = Topic(name=topic_name)
            self.conversation.topics.add(topic_object)
            if self.conversation.debug:
                print '-- Pushed "{}"'.format(topic_object)

    def _satisfy_goals(self):
        """Satisfy any goals whose targeted move was constituted by the execution of this turn."""
        # Satisfy speaker goals
        for goal in self.conversation.goals[self.speaker]:
            if goal.achieved:
                self.conversation.goals[self.speaker].remove(goal)
                self.conversation.satisfied_goals[self.speaker].add(goal)
                if self.conversation.debug:
                    print '-- Satisfied {}'.format(goal)
        # Satisfy interlocutor goals
        for goal in self.conversation.goals[self.interlocutor]:
            if goal.achieved:
                self.conversation.goals[self.interlocutor].remove(goal)
                self.conversation.satisfied_goals[self.interlocutor].add(goal)
                if self.conversation.debug:
                    print '-- Satisfied {}'.format(goal)


class Move(object):
    """A dialogue move by a conversational party."""

    def __init__(self, conversation, speaker, name):
        """Initialize a Move object."""
        self.conversation = conversation
        self.speaker = speaker
        self.interlocutor = conversation.interlocutor_to(speaker)
        self.name = name

    def __str__(self):
        """Return string representation."""
        return "MOVE:{}:{}".format(self.speaker.name, self.name)

    def fire(self):
        """Change the world according to the illocutionary force of this move."""
        if self.name == 'storm off':
            self.conversation.over = True
        elif self.name == "end conversation":
            if self.conversation.count_move_occurrences(
                acceptable_speakers=(self.interlocutor,), name="end conversation"
            ):
                self.conversation.over = True


class Obligation(object):
    """A conversational obligation imposed on one conversational party by a line of dialogue."""

    def __init__(self, conversation, obligated_party, move_name):
        """Initialize an Obligation object."""
        self.conversation = conversation
        self.obligated_party = obligated_party
        self.move_name = move_name

    def __str__(self):
        """Return string representation."""
        return 'OBLIGATION:{}:{}'.format(self.obligated_party.name, self.move_name)

    def outline(self, n_tabs):
        """Outline this obligation for debugging purposes."""
        print '{}{}'.format('\t'*n_tabs, self)

    def target(self):
        """Select a line of dialogue that would resolve this obligation."""
        return self.conversation.target_move(move_name=self.move_name)


class Flouting(object):
    """A flouting of a conversational obligation, in the Gricean sense."""

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
        self.plan.execute()


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
        return 'STEP:{}:{}_{}{}'.format(
            self.owner.name,
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
        return self.conversation.target_move(move_name=self.move_name)


class Topic(object):
    """A topic of conversation that may be brought up or addressed by a line of dialogue."""

    def __init__(self, name):
        """Initialize an Topic object."""
        self.name = name

    def __str__(self):
        """Return string representation."""
        return "TOPIC:{}".format(self.name)


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