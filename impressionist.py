import json
from productionist import Precondition, ConditionalViolation


class Impressionist(object):
    """An NLU module for in-game dialogue understanding."""

    def __init__(self, game, debug=False):
        """Initialize an Impressionist object."""
        self.game = game
        self.debug = debug
        self.nonterminal_symbols = self._init_parse_json_grammar_specification(
            path_to_json_grammar_specification=game.config.path_to_dialogue_nlu_json_grammar_specification
        )

    @staticmethod
    def _init_parse_json_grammar_specification(path_to_json_grammar_specification):
        """Parse a JSON grammar specification exported by Expressionist to instantiate nonterminal symbols."""
        # Parse the JSON specification to build a dictionary data structure
        symbol_objects = []
        grammar_dictionary = json.loads(open(path_to_json_grammar_specification).read())
        nonterminal_symbol_specifications = grammar_dictionary['nonterminals']
        for tag, nonterminal_symbol_specification in nonterminal_symbol_specifications.iteritems():
            raw_markup = nonterminal_symbol_specification['markup']
            symbol_object = NonterminalSymbol(tag=tag, raw_markup=raw_markup)
            symbol_objects.append(symbol_object)
        return symbol_objects

    def understand_player_utterance(self, player_utterance, conversation):
        """Understand the player's utterance to return a fully specified line of dialogue."""
        # Preprocess the utterance
        preprocessed_player_utterance = self._preprocess_player_utterance(raw_player_utterance=player_utterance)
        # Using our LSTM RNN, decode the player's utterance into a predicted Expressionist
        # trace that could have generated it
        predicted_trace = self._decode_player_utterance(player_utterance=preprocessed_player_utterance)
        # Instantiate a LineOfDialogue object for this utterance and trace; this object's
        # __init__() method will parse the trace to inherit mark-up from the symbols embedded
        # within it, and it will also be responsible for furnishing the utterance as a line of
        # dialogue that will be deployed in the actual conversation
        line_of_dialogue_object = LineOfDialogue(
            utterance_that_the_player_composed=player_utterance, predicted_trace=predicted_trace,
            conversation=conversation
        )
        # Return this line object to the Conversation object that called this method
        return line_of_dialogue_object

    @staticmethod
    def _preprocess_player_utterance(raw_player_utterance):
        """Preprocess a player utterance according to the LSTM decoder's expectations."""
        # Prepend and append whitespace
        preprocessed_player_utterance = " {raw_player_utterance} ".format(raw_player_utterance=raw_player_utterance)
        # Separate punctuation with whitespace (to make each their own token)
        for punctuation_symbol in (',', ".", "?", "!", "..."):
            preprocessed_player_utterance = (
                preprocessed_player_utterance.replace(punctuation_symbol, ' {}'.format(punctuation_symbol))
            )
        return preprocessed_player_utterance

    def _decode_player_utterance(self, player_utterance):
        """Using our LSTM model, decode the player utterance into a predicted Expressionist trace."""
        # THIS CAN'T BE DONE UNTIL WE SETTLE ON AN ELEGANT WAY OF INCORPORATING TENSORFLOW
        # INTO THE TALK OF THE TOWN FRAMEWORK

    def furnish_nonterminal_symbols(self, symbol_references):
        """Furnish actual NonterminalSymbol objects for each of the provided symbol references.

        @param symbol_references: A list of symbol references (i.e., symbol tags).
        """
        actual_symbol_objects = set()
        for symbol_reference in symbol_references:
            try:
                symbol_object = next(s for s in self.nonterminal_symbols if s.tag.lower() == symbol_reference.lower())
                actual_symbol_objects.add(symbol_object)
            except StopIteration:
                raise Exception(
                    "Impressionist encountered a strange symbol reference: {symbol_ref}".format(
                        symbol_ref=symbol_reference
                    )
                )
        return actual_symbol_objects


class NonterminalSymbol(object):
    """A symbol in an NLU system for in-game dialogue understanding.

    This class is very similar to productionist.NonterminalSymbol, but excludes concerns
    that pertain only to NLG issues and includes concerns not included in that class that
    pertain to NLU concerns. The classes could potentially be merged into one, but my
    feeling is that it's easier to have them teased apart (even though they will end up
    having code in common).
    """

    def __init__(self, tag, raw_markup):
        """Initialize a NonterminalSymbol object."""
        self.tag = tag
        # Prepare annotation sets that will be populated (as appropriate) by _init_parse_markup()
        self.preconditions = set()
        self.conditional_violations = set()
        self.propositions = set()
        self.change_subject_to = ''  # Raw Python snippet that when executed will change the subject of conversation
        self.moves = set()  # The dialogue moves constituted by the delivery of this line
        self.speaker_obligations_pushed = set()  # Line asserts speaker conversational obligations
        self.interlocutor_obligations_pushed = set()  # Line asserts interlocutor conversational obligations
        self.topics_pushed = set()  # Line introduces a new topic of conversation
        self.topics_addressed = set()  # Line addresses a topic of conversation
        self._init_parse_markup(raw_markup=raw_markup)

    def __str__(self):
        """Return string representation."""
        return '[[{tag}]]'.format(tag=self.tag)

    def _init_parse_markup(self, raw_markup):
        """Instantiate and attribute objects for the annotations attributed to this symbol."""
        for tagset in raw_markup:
            for tag in raw_markup[tagset]:
                if tagset == "Preconditions":
                    self.preconditions.add(Precondition(tag=tag))
                elif tagset == "ViolationConditions":
                    self.conditional_violations.add(ConditionalViolation(tag=tag))
                elif tagset == "Propositions":
                    self.propositions.add(tag)
                # Acts, goals, obligations, and topics are reified as objects during a conversation, but
                # here are only represented as a tag
                elif tagset == "Moves":
                    self.moves.add(tag)
                elif tagset == "PushObligation":  # Obligations pushed onto interlocutor
                    self.interlocutor_obligations_pushed.add(tag)
                elif tagset == "PushSpeakerObligation":  # Obligations pushed onto speaker (by their own line)
                    self.speaker_obligations_pushed.add(tag)
                elif tagset == "PushTopic":
                    self.topics_pushed.add(tag)
                elif tagset == "AddressTopic":
                    self.topics_addressed.add(tag)
                elif tagset == "Context":
                    pass
                elif tagset == "EffectConditions":
                    pass  # TODO
                elif tagset == "ChangeSubjectTo":
                    pass  # TODO REMOVE THIS TAGSET
                elif tagset == "UserStudyQueryArguments":
                    pass  # This one is currently for LSTM training only
                else:
                    raise Exception('Unknown tagset encountered: {}'.format(tagset))

    @property
    def all_markup(self):
        """Return all the annotations attributed to this symbol."""
        all_markup = (
            self.preconditions | self.conditional_violations | self.propositions |
            {self.change_subject_to} | self.moves | self.speaker_obligations_pushed |
            self.interlocutor_obligations_pushed | self.topics_pushed | self.topics_addressed
        )
        return list(all_markup)

    def conversational_violations(self, conversation):
        """Return a list of names of conversational violations that will be incurred if this line is deployed now."""
        violations_incurred = [
            potential_violation.name for potential_violation in self.conditional_violations if
            potential_violation.evaluate(state=conversation)
        ]
        return violations_incurred


class LineOfDialogue(object):
    """A line of dialogue that may be used during a conversation."""

    def __init__(self, utterance_that_the_player_composed, predicted_trace, conversation):
        """Initialize a LineOfDialogue object.

        @param utterance_that_the_player_composed: The very string that the player submitted as her utterance.
        @param predicted_trace: The output of our LSTM RNN, given line_that_player_composed as input.
                                More specifically, this is a predicted Expressionist trace that could
                                have generated the utterance that the player submitted.
        @param conversation: The Conversation object representing the conversation that this line of
                             dialogue will be deployed in. This object holds all the conversation state
                             that we need to access to recognize state-dependent conversational violations,
                             etc., that may be attributed to this line. It will also provide access to
                             an Impressionist object, which is necessary to furnish the NonterminalSymbol
                             objects that will be associated with this object (and will be utilized to
                             attribute all its symbolic markup).
        """
        self.body = utterance_that_the_player_composed
        self.predicted_trace = predicted_trace
        self.symbols = self._init_parse_predicted_trace(impressionist=conversation.impressionist)
        # Prepare annotation attributes
        self.conversational_violations = set()
        self.propositions = set()
        self.change_subject_to = ''  # Raw Python snippet that when executed will change the subject of conversation
        self.moves = set()  # The dialogue moves constituted by the delivery of this line
        self.speaker_obligations_pushed = set()  # Line asserts speaker conversational obligations
        self.interlocutor_obligations_pushed = set()  # Line asserts interlocutor conversational obligations
        self.topics_pushed = set()  # Line introduces a new topic of conversation
        self.topics_addressed = set()  # Line addresses a topic of conversation
        self._init_inherit_markup(conversation=conversation)

    def __str__(self):
        """Return the raw template characterizing this line of dialogue."""
        return self.body

    def _init_parse_predicted_trace(self, impressionist):
        """Parse our RNN's predicted Expressionist trace for this line to produce a set of nonterminal
        symbols that will be associated to it (which we will use as keys to access the symbolic mark-up
        that will be attributed to the line so that the NPC who hears it can actually understand it).

        This method currently assumed traces that are formatted like this one:
                greet { greet|back { greet|back|immediately { greeting|word { } ^ expressive|punct {
                expressive|punct>extroverted { } } } } }
        """
        # Parse out the symbol references themselves
        symbol_references = {
            symbol_ref for symbol_ref in self.predicted_trace.split(' ') if
            '{' not in symbol_ref and '}' not in symbol_ref and '^' not in symbol_ref
        }
        # Reformat the symbol references (which will be formatted like, e.g., 'greet|back|immediately')
        # to match the formatting they will have in the Impressionist object's 'nonterminal_symbols'
        # listing (e.g., 'greet back immediately')
        symbol_references = {' '.join(symbol_ref.split('|')) for symbol_ref in symbol_references}
        # Ask an Impressionist object for a list of the actual NonterminalSymbols corresponding to these
        # symbol references (which hold all the symbolic mark-up that we're after)
        symbol_objects = impressionist.furnish_nonterminal_symbols(symbol_references=symbol_references)
        # Return this list of symbol objects
        return symbol_objects

    def _init_inherit_markup(self, conversation):
        """Inherit the mark-up of all the symbols that were expanded in the construction of this dialogue template."""
        assert len({s.change_subject_to for s in self.symbols if s.change_subject_to}) < 2, (
            "Line of dialogue {} is inheriting from symbols with contradicting 'change_subject_to' annotations."
        )
        for symbol in self.symbols:
            self.conversational_violations |= set(symbol.conversational_violations(conversation=conversation))
            self.propositions |= symbol.propositions
            self.change_subject_to = symbol.change_subject_to if symbol.change_subject_to else self.change_subject_to
            self.moves |= symbol.moves
            self.speaker_obligations_pushed |= symbol.speaker_obligations_pushed
            self.interlocutor_obligations_pushed |= symbol.interlocutor_obligations_pushed
            self.topics_pushed |= symbol.topics_pushed
            self.topics_addressed |= symbol.topics_addressed

    def realize(self, conversation_turn=None):
        """Return the very line that the player composed.

        Note: This method exists to maintain an equivalent interface to objects of the
        classes Productionist.LineOfDialogue and Impressionist.LineOfDialogue, so that
        Conversation objects can call LineOfDialogue.realize() without needing to know
        which type of LineOfDialogue object is being referenced. This is why the method
        takes the argument 'conversation_turn'.
        """
        return self.body