import json
import itertools
import os
import random
import operator


# PATH_TO_JSON_GRAMMAR_SPECIFICATION = '/Users/jamesryan/Desktop/Expressionist0.51/grammars/load/talktown.json'
PATH_TO_JSON_GRAMMAR_SPECIFICATION = '/Users/jamesryan/Desktop/Expressionist0.51/grammars/load/talktown-user_study_training.json'
DIRECTORY_TO_WRITE_OUT_TO = os.getcwd()
TRACES_OUT_FILENAME = 'PLAYER-INPUT_HAIR-TRACES_18Apr2016'
DERIVATIONS_OUT_FILENAME = 'PLAYER-INPUT_HAIR-DERIVATIONS_18Apr2016'
TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM = ['player appearance query']
# To expand *all* top-level symbols to generate training data, use this line instead:
# TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM = 'ALL'
VERBOSE = 2  # Whether the process will display progress text (0=No, 1=Verbose, 2=Very Verbose)
NUMBER_OF_TERMINAL_DERIVATIONS_TO_TARGET = 1000000  # Determines sampling rate


class TrainingDataWriter(object):
    """A production system for generating training data from the JSON specifying an Expressionist grammar."""

    def __init__(self):
        """Initialize a Productionist object."""
        self.nonterminal_symbols = self._init_parse_json_grammar_specification(
            path_to_json_grammar_specification=PATH_TO_JSON_GRAMMAR_SPECIFICATION
        )
        self._init_resolve_symbol_references_in_all_production_rule_bodies()
        # Set top-level symbols, i.e., the symbols that will be expanded to produce
        # the training data (this is specified above as a global variable)
        if TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM == 'ALL':
            self.top_level_symbols = [symbol for symbol in self.nonterminal_symbols if symbol.top_level]
        else:
            self.top_level_symbols = [
                symbol for symbol in self.nonterminal_symbols if symbol.tag in TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM
            ]
        # This will increment as terminal derivation/traces are written out; it's specifically
        # used to ensure that the terminal derivations that are sampled will also be sampled
        # during the exportation of traces (so that the two training-data files match up perfectly)
        self.current_derivation_index = -1
        # Determine the total number of terminal derivations generable by the top-level symbols of
        # our source grammar, which we can use to determine a sampling rate that will produce approximately
        # the desired number of terminal derivations (as specified by a global variable set above)
        self.sampling_indices = self._init_determine_which_terminal_derivations_will_be_sampled()

    def _init_parse_json_grammar_specification(self, path_to_json_grammar_specification):
        """Parse a JSON grammar specification exported by Expressionist to instantiate symbols and rules."""
        # Parse the JSON specification to build a dictionary data structure
        symbol_objects = []
        grammar_dictionary = json.loads(open(path_to_json_grammar_specification).read())
        nonterminal_symbol_specifications = grammar_dictionary['nonterminals']
        for tag, nonterminal_symbol_specification in nonterminal_symbol_specifications.iteritems():
            top_level = nonterminal_symbol_specification['deep']
            production_rules_specification = nonterminal_symbol_specification['rules']
            symbol_object = NonterminalSymbol(
                training_data_writer=self, tag=tag, top_level=top_level,
                production_rules_specification=production_rules_specification
            )
            symbol_objects.append(symbol_object)
        return symbol_objects

    def _init_resolve_symbol_references_in_all_production_rule_bodies(self):
        """Resolve all symbol references in production rule bodies to point to actual symbol objects."""
        for symbol in self.nonterminal_symbols:
            for rule in symbol.production_rules:
                self._init_resolve_symbol_references_in_a_rule_body(production_rule=rule)

    def _init_resolve_symbol_references_in_a_rule_body(self, production_rule):
        """Resolve all symbol references in the body of the given rule to point to actual NonterminalSymbol objects."""
        rule_body_specification = list(production_rule.body_specification)
        rule_body_with_resolved_symbol_references = []
        for symbol_reference in rule_body_specification:
            if symbol_reference[:2] == '[[' and symbol_reference[-2:] == ']]':
                # We've encountered a reference to a nonterminal symbol, so we need to resolve this
                # reference and append to the list that we're building the nonterminal symbol itself
                symbol_tag = symbol_reference[2:-2]
                symbol_object = next(symbol for symbol in self.nonterminal_symbols if symbol.tag == symbol_tag)
                rule_body_with_resolved_symbol_references.append(symbol_object)
            else:
                # We've encountered a terminal symbol, so we can just append this string itself
                # to the list that we're building
                rule_body_with_resolved_symbol_references.append(symbol_reference)
            production_rule.body = rule_body_with_resolved_symbol_references

    def _init_determine_which_terminal_derivations_will_be_sampled(self):
        """Determine a sampling rate, i.e., the probability of writing out a given terminal derivation/trace."""
        # First, determine the total number of terminal variations generable by the top-level
        # symbols of our source grammar
        total_generable_derivations = sum(
            symbol.total_number_of_generable_terminal_derivations() for symbol in self.top_level_symbols
        )
        # Now sample N indices from this range, where N is the targeted number o terminal derivations
        # to write out in the training data (which was specified above as a global variable)
        sampling_indices = random.sample(xrange(total_generable_derivations), NUMBER_OF_TERMINAL_DERIVATIONS_TO_TARGET)
        return sampling_indices

    def produce_lstm_training_data(self):
        """Produce all the files that constitute our training data."""
        self.produce_and_write_out_traces()
        self._clear_temporary_data()
        self.produce_and_write_out_terminal_derivations()

    def _clear_temporary_data(self):
        """Clear out temporary data that may have been associated with symbols during the last generation procedure."""
        self.current_derivation_index = -1
        for symbol in self.nonterminal_symbols:
            symbol.all_derivation_traces = []
            symbol.all_terminal_derivations = []

    def produce_and_write_out_traces(self):
        """Produce and write out traces for terminal derivations of our top-level symbols.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{<Hi>},< >,interlocutor|first|name{<[speaker.belief(interlocutor, 'first name')]>}}
        """
        # Determine the path to write out to (using global variables specified at the top of this file)
        path_to_write_out_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=TRACES_OUT_FILENAME
        )
        out_file = open(path_to_write_out_to, 'w')
        for symbol in self.top_level_symbols:
            symbol.produce_and_write_out_traces(out_file=out_file)
        out_file.close()

    def produce_and_write_out_terminal_derivations(self):
        """Produce and write out terminal derivations of our top-level symbols."""
        path_to_write_out_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=DERIVATIONS_OUT_FILENAME
        )
        out_file = open(path_to_write_out_to, 'w')
        for symbol in self.top_level_symbols:
            symbol.produce_and_write_out_terminal_derivations(out_file=out_file)
        out_file.close()


class NonterminalSymbol(object):
    """A symbol in a production system for in-game dialogue generation."""

    def __init__(self, training_data_writer, tag, top_level, production_rules_specification):
        """Initialize a NonterminalSymbol object."""
        self.training_data_writer = training_data_writer
        self.tag = tag
        # If a terminal expansion of this symbol constitutes a complete line of dialogue, then
        # this is a top-level symbol
        self.top_level = top_level
        self.production_rules = self._init_reify_production_rules(production_rules_specification)
        # This attribute will hold LSTM training data produced by this symbol, so that we do
        # not reduplicate efforts while we are generating a training set; see
        # NonterminalSymbol.produce_and_write_out_traces() for more information
        self.all_derivation_traces = []
        # This attribute will hold all terminal derivations of this symbol, so that we do
        # not reduplicate efforts while we are generating LSTM training data; see
        # NonterminalSymbol.produce_and_write_out_terminal_derivations() for more information
        self.all_terminal_derivations = []
        # This will hold the total number of terminal derivations of this symbol
        self.total_generable_derivations = None

    def __str__(self):
        """Return string representation."""
        return '[[{tag}]]'.format(tag=self.tag)

    def _init_reify_production_rules(self, production_rules_specification):
        """Instantiate ProductionRule objects for the rules specified in production_rules_specification."""
        production_rule_objects = []
        for rule_specification in production_rules_specification:
            body = rule_specification['expansion']
            application_rate = rule_specification['app_rate']
            production_rule_objects.append(
                ProductionRule(
                    training_data_writer=self.training_data_writer, head=self, body_specification=body,
                    application_rate=application_rate
                )
            )
        return production_rule_objects

    def total_number_of_generable_terminal_derivations(self):
        """Determine the total number of terminal derivations generable by this production rule."""
        if not self.total_generable_derivations:
            self.total_generable_derivations = sum(
                rule.total_number_of_generable_terminal_derivations() for rule in self.production_rules
            )
        return self.total_generable_derivations

    def produce_and_write_out_traces(self, out_file=None):
        """Return all terminal derivations of this symbol in the format specified for LSTM training.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{`Hi~}^` ~^interlocutor|first|name{`[speaker.belief(interlocutor, 'first name')]~}^`.~}
        for the terminal derivation "Hi, [speaker.belief(interlocutor, 'first name')]."
        """
        if VERBOSE > 0:
            print "\tProducing traces for nonterminal symbol '{symbol}'".format(symbol=self)
        # If there's nothing passed for the out_file argument, the derivation traces produced here
        # pertain to a symbol that is not top-level, which means that the traces will not be written
        # out (but rather will end up as substrings of the traces for actual terminal derivations,
        # which *will* be written out)
        if not out_file:
            if not self.all_derivation_traces:
                all_terminal_derivations_in_lstm_training_data_format = []
                for rule in self.production_rules:
                    all_terminal_derivations_in_lstm_training_data_format += (
                        rule.produce_and_write_out_traces(out_file=None)
                    )
                self.all_derivation_traces = all_terminal_derivations_in_lstm_training_data_format
            return self.all_derivation_traces
        else:
            for rule in self.production_rules:
                rule.produce_and_write_out_traces(out_file=out_file)

    def produce_all_terminal_derivations_for_lstm_training(self, out_file):
        """Exhaustively produce all terminal derivations of this symbol for use as part of the LSTM training data."""
        if VERBOSE > 0:
            print "\tProducing derivations for nonterminal symbol '{symbol}'".format(symbol=self)
        # If there's nothing passed for the out_file argument, the derivations produced here
        # pertain to a symbol that is not top-level, which means that the derivations will not be
        # written out (but rather will end up as substrings of actual terminal derivations that
        # *will* be written out)
        if not out_file:
            if not self.all_terminal_derivations:
                all_terminal_derivations = []
                for rule in self.production_rules:
                    all_terminal_derivations += rule.produce_and_write_out_terminal_derivations(out_file=None)
                self.all_terminal_derivations = all_terminal_derivations
            return self.all_terminal_derivations
        else:
            for rule in self.production_rules:
                rule.produce_and_write_out_terminal_derivations(out_file=out_file)


class ProductionRule(object):
    """A production rule in a production system for in-game dialogue generation."""

    def __init__(self, training_data_writer, head, body_specification, application_rate):
        """Initialize a ProductionRule object.

        'head' is a nonterminal symbol constituting the left-hand side of this rule, while
        'body' is a sequence of symbols that this rule may be used to expand the head into.
        """
        self.training_data_writer = training_data_writer
        self.head = head
        self.body = None  # Gets set by Productionist._init_resolve_symbol_references_in_a_rule_body()
        self.body_specification = body_specification
        self.body_specification_str = ''.join(body_specification)
        # Application rates currently aren't used in producing training data, but they perhaps *could* be
        # used to modify the sampling rate such that more likely derivations are written out more often
        self.application_rate = application_rate
        # This will hold the total number of terminal derivations generable by this production rule;
        # since there's no product() built-in function in Python that works like sum() does, we
        # have to use this ugly reduce thing
        self.total_generable_derivations = None

    def __str__(self):
        """Return string representation."""
        return '{head} --> {body}'.format(head=self.head, body=self.body_specification_str)

    def total_number_of_generable_terminal_derivations(self):
        """Determine the total number of terminal derivations generable by this production rule."""
        if not self.total_generable_derivations:
            self.total_generable_derivations = reduce(
                operator.mul, (
                    symbol.total_number_of_generable_terminal_derivations() if type(symbol) is not unicode else 1
                    for symbol in self.body), 1
            )
        return self.total_generable_derivations

    def produce_and_write_out_traces(self, out_file=None):
        """Return all terminal derivations yielded by this rule in the format specified for LSTM training.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{`Hi~}^` ~^interlocutor|first|name{`[speaker.belief(interlocutor, 'first name')]~}^`.~}
        for the terminal derivation "Hi, [speaker.belief(interlocutor, 'first name')]."
        """
        if VERBOSE == 2:
            print "\tProducing traces for production rule {rule_name}".format(rule_name=self)
        # Assemble the Cartesian product of all terminal derivations for all symbols in
        # this rule body; because nonterminal symbols are represented as a raw unicode string, we
        # can't call the same method for each symbol, so we just append the syntax for demarcating
        # them in the LSTM training-data format that we have devised; if omit_derivation_snippets ==
        # True, then we don't even include the terminal symbols
        cartesian_product_of_all_symbols_in_this_rule_body = itertools.product(*[
            symbol.produce_and_write_out_traces() for symbol in self.body if type(symbol) is not unicode
        ])
        # Now concatenate these and prepend them with syntax indicating which nonterminal symbol
        # is the head of this rule; this will produce derivation traces in the format we want them in
        if not out_file:
            return (
                "{head}{{{partial_trace}}}".format(
                    head='|'.join(self.head.tag.split()),
                    partial_trace='^'.join(cartesian_product)
                ) for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body
            )
        else:
            for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body:
                training_data_writer = self.training_data_writer
                if training_data_writer.current_derivation_index in training_data_writer.sampling_indices:
                    out_file.write(
                        "{}\n".format(
                            "{head}{{{partial_trace}}}".format(
                                head='|'.join(self.head.tag.split()),
                                partial_trace='^'.join(cartesian_product)
                            )
                        )
                    )
                    out_file.flush()
                training_data_writer.current_derivation_index += 1

    def produce_and_write_out_terminal_derivations(self, out_file=None):
        """Exhaustively produce all terminal derivations yielded by this rule for use as LSTM training data."""
        if VERBOSE == 2:
            print "\tProducing derivations for production rule {rule_name}".format(rule_name=self)
        # Assemble the Cartesian product of all terminal derivations for all symbols in
        # this rule body; because nonterminal symbols are represented as a raw unicode string, we
        # can't call the same method for each symbol
        cartesian_product_of_all_symbols_in_this_rule_body = itertools.product(*[
            [symbol] if type(symbol) is unicode else symbol.produce_and_write_out_terminal_derivations()
            for symbol in self.body
        ])
        # Now concatenate these to produce actual terminal derivations; if we aren't writing out
        # these terminal derivations (signaled by whether something is passed for the 'out_file'
        # argument), return a generator containing all of them
        if not out_file:
            return (
                ''.join(cartesian_product) for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body
            )
        # Otherwise, let's write these out right now
        for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body:
            training_data_writer = self.training_data_writer
            if training_data_writer.current_derivation_index in training_data_writer.sampling_indices:
                out_file.write('{}\n'.format(''.join(cartesian_product)))
                out_file.flush()
            training_data_writer.current_derivation_index += 1


if __name__ == "__main__":
    writer = TrainingDataWriter()
    writer.produce_lstm_training_data()
