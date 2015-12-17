import re
import random


PATH_TO_DIALOGUE_TSV_FILE = '/Users/jamesryan/Desktop/Projects/Personal/anytown/content/dialogue.tsv'


class DialogueBase(object):
    """A base of templated dialogue that characters may select from."""

    def __init__(self):
        """Initialize a DialogueBase object."""
        # Lines of dialogue are organized according to their discourse acts
        self.discourse_acts = set()  # Gets populated by parse_tsv_file()
        self.parse_tsv_file()

    def parse_tsv_file(self):
        """Parse a TSV file specifying a database of dialogue."""
        tsv_lines = open(PATH_TO_DIALOGUE_TSV_FILE, 'r').readlines()
        del tsv_lines[0]  # Delete header
        # Collect all discourse acts
        discourse_act_names = {line.split('\t')[0] for line in tsv_lines}
        for discourse_act_name in discourse_act_names:
            self.discourse_acts.add(DiscourseAct(name=discourse_act_name[2:-2]))
        for tsv_line in tsv_lines:
            # Just instantiating a LineOfDialogue object will add it to its
            # respective DiscourseAct's 'lines_of_dialogue' listing
            LineOfDialogue(tsv_line=tsv_line, dialogue_base=self)

    @property
    def all_lines_of_dialogue(self):
        """Return a set of all lines of dialogue in the database."""
        all_lines = set()
        for discourse_act in self.discourse_acts:
            all_lines |= discourse_act.lines_of_dialogue
        return all_lines


class DiscourseAct(object):
    """A discourse act characterizing the impact of a line of dialogue."""

    def __init__(self, name):
        """Initializing a DiscourseAct object."""
        self.name = name
        self.lines_of_dialogue = set()

    def __str__(self):
        """Return the name of this discourse act."""
        return self.name.capitalize()


class LineOfDialogue(object):
    """A line of dialogue that may be used during a conversation."""

    def __init__(self, tsv_line, dialogue_base):
        """Initialize a LineOfDialogue object."""
        # Prepare the markup sets
        self.preconditions = set()
        self.propositions = set()
        self.change_subject_to = ''  # Raw Python snippet that when executed will change the subject of conversation
        self.moves = set()  # The dialogue moves constituted by the delivery of this line
        self.speaker_obligations_pushed = set()  # Line asserts speaker conversational obligations
        self.interlocutor_obligations_pushed = set()  # Line asserts interlocutor conversational obligations
        self.topics_pushed = set()  # Line introduces a new topic of conversation
        self.topics_addressed = set()  # Line addresses a topic of conversation
        self.ends_conversation = False  # Whether the line ends a conversation upon being delivered
        # Parse the TSV line specifying this line of dialogue
        discourse_act_name, raw_line, raw_markup, probability_range = tsv_line.strip('\r\n').split('\t')
        discourse_act_name = discourse_act_name[2:-2]  # Parse out the double brackets surrounding the discourse act
        self.discourse_act = next(
            discourse_act for discourse_act in dialogue_base.discourse_acts if
            discourse_act.name == discourse_act_name
        )
        self.discourse_act.lines_of_dialogue.add(self)
        self.raw_line = raw_line
        self.template = self._prepare_template(raw_line=raw_line)
        self.probability_range = probability_range
        # Parse the markup, specifically
        raw_markup = raw_markup.split('^')
        self._init_parse_markup(raw_markup=raw_markup)

    def __str__(self):
        """Print the template characterizing this line of dialogue."""
        return self.raw_line

    def _init_parse_markup(self, raw_markup):
        """Parse the markup attributed to this line of dialogue during its authoring."""
        for annotation in raw_markup:
            if annotation:
                index_of_split = annotation.index(':')
                tagset = annotation[:index_of_split]
                tag = annotation[index_of_split+1:]
                if tagset == "Preconditions":
                    self.preconditions.add(Precondition(tag=tag))
                elif tagset == "Propositions":
                    self.propositions.add(Proposition(tag=tag))
                elif tagset == "ChangeSubjectTo":
                    self.change_subject_to = tag
                # Acts, goals, obligations, and topics are reified as objects during a conversation, but
                # here are only represented as a tag
                elif tagset == "Moves":
                    self.moves.add(tag)
                elif tagset == "OnlyIfObligated":
                    # This specifies that this line have a precondition enforcing that it only
                    # be deployed when its potential speaker is obligated to perform one of the
                    # discourse moves that it performs
                    only_if_obligated_precondition = (
                        'lambda conversation, speaker: any(o for o in conversation.obligations[speaker] if ' +
                        '{o.move_name} and self.moves)'
                    )
                    self.preconditions.add(
                        Precondition(tag=only_if_obligated_precondition)
                    )
                elif tagset == "PushObligation":  # Obligations pushed onto interlocutor
                    self.interlocutor_obligations_pushed.add(tag)
                elif tagset == "PushSpeakerObligation":  # Obligations pushed onto speaker (by their own line)
                    self.speaker_obligations_pushed.add(tag)
                elif tagset == "PushTopic":
                    self.topics_pushed.add(tag)
                elif tagset == "AddressTopic":
                    self.topics_addressed.add(tag)
                else:
                    raise Exception('Unknown tagset encountered: {}'.format(tagset))

    @staticmethod
    def _prepare_template(raw_line):
        """Prepare a templated line of dialogue from a raw specification for one."""
        template = []  # An ordered list of StaticElements and Gaps
        while '[' in raw_line:
            index_of_opening_bracket = raw_line.index('[')
            # Process next static element
            next_static_element = raw_line[:index_of_opening_bracket]
            if next_static_element:
                template.append(StaticElement(text=next_static_element))
            # Process next gap
            index_of_closing_bracket = raw_line.index(']')
            next_gap = raw_line[index_of_opening_bracket+1:index_of_closing_bracket]
            template.append(Gap(specification=next_gap))
            # Excise the processed elements
            raw_line = raw_line[index_of_closing_bracket+1:]
        # Process the trailing static element, if any
        if raw_line:
            template.append(StaticElement(text=raw_line))
        return template

    def preconditions_satisfied(self, conversation_turn):
        """Return whether this line's preconditions are satisfied given the state of the world."""
        return all(precondition.evaluate(conversation_turn=conversation_turn) for precondition in self.preconditions)

    def realize(self, conversation_turn):
        """Return a filled-in template according to the world state during a conversation turn."""
        return ''.join(element.realize(conversation_turn=conversation_turn) for element in self.template)


class StaticElement(object):
    """A static element in a templated line of dialogue."""

    def __init__(self, text):
        """Initialize a StaticElement object."""
        self.text = text

    def __str__(self):
        """Return the text of this static element."""
        return self.text

    def realize(self, conversation_turn):
        """Realize a StaticElement object simply by returning its text."""
        return self.text


class Gap(object):
    """A gap in a templated line of dialogue."""

    def __init__(self, specification):
        """Initialize a Gap object."""
        self.specification = specification

    def __str__(self):
        """Return the specification for filling in this gap."""
        return self.specification

    def realize(self, conversation_turn):
        """Fill in this gap according to the world state during a conversation turn."""
        # Prepare local variables that will allow us to fill in this gap
        speaker, interlocutor, subject = (
            conversation_turn.speaker, conversation_turn.interlocutor, conversation_turn.subject
        )
        return eval(self.specification)


class Precondition(object):
    """A precondition for the use of a line of dialogue."""

    def __init__(self, tag):
        """Initialize a Precondition object."""
        self.specification = tag
        self.test = eval(tag)  # The tag is literally a lambda function
        self.arguments = self._init_parse_function_for_its_arguments(function=tag)

    def __str__(self):
        """Return the lambda function itself."""
        return self.specification

    @staticmethod
    def _init_parse_function_for_its_arguments(function):
        """Parse this precondition's lambda function to gather the arguments that it requires."""
        index_of_end_of_arguments = function.index(':')
        arguments = function[:index_of_end_of_arguments]
        arguments = arguments[len('lambda '):]  # Excise 'lambda ' prefix
        arguments = arguments.split(', ')
        return arguments

    def evaluate(self, conversation_turn):
        """Evaluate this precondition given the state of the world at the beginning of a conversation turn."""
        # Instantiate all the arguments we might need as local variables
        speaker = conversation_turn.speaker
        interlocutor = conversation_turn.interlocutor
        subject = conversation_turn.subject
        conversation = conversation_turn.conversation
        # Prepare the list of arguments by evaluating to the needed local variables
        filled_in_arguments = [eval(argument) for argument in self.arguments]
        # Return a boolean indicating whether this precondition is satisfied
        try:
            return self.test(*filled_in_arguments)
        except ValueError:
            raise Exception('Cannot evaluate the precondition {}'.format(self.specification))
        except AttributeError:
            raise Exception('Cannot evaluate the precondition {}'.format(self.specification))


class Proposition(object):
    """A proposition about the world asserted by a line of dialogue."""

    def __init__(self, tag):
        """Initialize an Proposition object."""
        self.content = tag