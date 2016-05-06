import json
import itertools
import os
import re
import random
import operator
import time
import pickle


PATH_TO_JSON_GRAMMAR_SPECIFICATION = (
    #'/Users/jamesryan/Desktop/Expressionist0.51/grammars/load/talktown-player-input_hair-queries-probabilistic.json'
    #'/Users/jamesryan/Desktop/IVA2016/talktown-grammar-used-in-iva-study.json'
    '/Users/jamesryan/Desktop/Expressionist0.51/grammars/load/talktown-aiide-study-2016.json'
)
CURRENT_DATE = time.strftime("%d%b%Y")  # In this format: 29Apr2016
DIRECTORY_TO_WRITE_OUT_TO = os.getcwd()
SYMBOLS_PICKLE_OUT_FILENAME = 'SYMBOLS-PICKLE_{current_date}'.format(current_date=CURRENT_DATE)
ONLY_RUNTIME_VARIABLE_TOKENS_PICKLE_OUT_FILENAME = 'RUNTIME_VAR_TOKENS-PICKLE_{current_date}'.format(
    current_date=CURRENT_DATE
)
ALL_TOKENS_PICKLE_OUT_FILENAME = 'ALL-TOKENS-PICKLE_{current_date}'.format(current_date=CURRENT_DATE)
TRACES_OUT_FILENAME = 'PLAYER-INPUT_HAIR_TRACES_{current_date}'.format(current_date=CURRENT_DATE)
DERIVATIONS_OUT_FILENAME = 'PLAYER-INPUT_HAIR_DERIVATIONS_{current_date}'.format(current_date=CURRENT_DATE)
# TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM = ['player appearance query']
# To expand *all* top-level symbols to generate training data, use this line instead:
TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM = 'ALL'
TARGETED_NUMBER_OF_TERMINAL_DERIVATIONS = 1000  # 1317888 produces roughly 1GB of training data (of traces)
BASE_EXPLORATION_BOOST = 1
EXPLORATION_BOOST_DECAY_RATE = 0.90
RANDOM_SEED = 0


class TrainingDataWriter(object):
    """A production system for generating training data from the JSON specifying an Expressionist grammar."""

    def __init__(self):
        """Initialize a Productionist object."""
        self.nonterminal_symbols = self._init_parse_json_grammar_specification(
            path_to_json_grammar_specification=PATH_TO_JSON_GRAMMAR_SPECIFICATION
        )
        self._init_resolve_symbol_references_in_all_production_rule_bodies()
        self._init_determine_which_production_rules_are_terminal_or_semiterminal()
        # Set top-level symbols, i.e., the symbols that will be expanded to produce
        # the training data (this is specified above as a global variable)
        if TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM == 'ALL':
            self.top_level_symbols = [symbol for symbol in self.nonterminal_symbols if symbol.top_level]
        else:
            self.top_level_symbols = [
                symbol for symbol in self.nonterminal_symbols if symbol.tag in TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM
            ]
        # This gets set by produce_and_write_out_a_trace() and then reset by
        # produce_and_write_out_a_derivation()
        self.out_file = None
        # Determine the total number of generable terminal derivations (summed across top-level
        # symbols only)
        self.total_generable_derivations = sum(
            s.total_number_of_generable_terminal_derivations() for s in self.top_level_symbols
        )
        # Set the random seed, which will ensure that the sampled derivation traces match up exactly
        # with the sampled derivations themselves
        random.seed(RANDOM_SEED)

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

    def _init_determine_which_production_rules_are_terminal_or_semiterminal(self):
        """Determine which production rules are terminal (yield a single string) or semiterminal (expand
        to a symbol that has terminal rules).

        These rules crucially allow for tractable sampling of very large Expressionist grammars.
        """
        # Check for terminal rules
        for symbol in self.nonterminal_symbols:
            for rule in symbol.production_rules:
                if len(rule.body) == 1 and type(rule.body[0]) is unicode:
                    rule.terminal = True
        # Check for semiterminal rules
        for symbol in self.nonterminal_symbols:
            for rule in symbol.production_rules:
                if any(s for s in rule.body if type(s) is not unicode and any(
                            r for r in s.production_rules if r.terminal)
                       ):
                    rule.semiterminal = True

    def write_out_pickled_symbol_and_token_serialization_dictionaries(self):
        """Write out pickled dictionaries that map all the nonterminal symbols and words appearing in this grammar
        to their serialization IDs."""
        # Write out a pickled dictionary mapping all nonterminal symbols in this grammar to
        # their serialization IDs
        nonterminal_symbol_to_serialization_id = {
            self.nonterminal_symbols[i].tag: i for i in xrange(len(self.nonterminal_symbols))
        }
        path_to_write_symbol_pickle_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=SYMBOLS_PICKLE_OUT_FILENAME
        )
        symbol_pickle_out_file = open(path_to_write_symbol_pickle_to, 'wb')
        pickle.dump(nonterminal_symbol_to_serialization_id, symbol_pickle_out_file)
        symbol_pickle_out_file.close()
        # Parse and tokenize all nonterminal symbols
        all_terminal_symbols = self._collect_all_terminal_symbols()
        runtime_variable_replacement_expressions, token_to_serialization_id = self._parse_and_tokenize_terminal_symbols(
            terminal_symbols=all_terminal_symbols
        )
        # Write out a pickled dictionary mapping all runtime variables to their replacement
        # expressions, e.g., 'PYTHON_EXPRESSION0'
        path_to_write_runtime_variables_pickle_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=ONLY_RUNTIME_VARIABLE_TOKENS_PICKLE_OUT_FILENAME
        )
        runtime_variables_pickle_out_file = open(path_to_write_runtime_variables_pickle_to, 'wb')
        pickle.dump(runtime_variable_replacement_expressions, runtime_variables_pickle_out_file)
        runtime_variables_pickle_out_file.close()
        # Write out a pickled dictionary mapping all unique tokens (including replacement expressions
        # for runtime variables) to their serialization IDs
        path_to_write_all_tokens_pickle_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=ALL_TOKENS_PICKLE_OUT_FILENAME
        )
        tokens_pickle_out_file = open(path_to_write_all_tokens_pickle_to, 'wb')
        pickle.dump(token_to_serialization_id, tokens_pickle_out_file)
        tokens_pickle_out_file.close()

    def _collect_all_terminal_symbols(self):
        """Return a set of all terminal symbols included in this grammar that are not fully composed of whitespace."""
        terminal_symbols = set()
        for nonterminal_symbol in self.nonterminal_symbols:
            for rule in nonterminal_symbol.production_rules:
                for symbol in rule.body:
                    if type(symbol) is unicode and symbol.strip():  # I.e., symbol is terminal and not just whitespace
                        terminal_symbols.add(symbol)
        return terminal_symbols

    @staticmethod
    def _parse_and_tokenize_terminal_symbols(terminal_symbols):
        """Return a set of all unique tokens appearing across all terminal symbols."""
        # Prepare some variables that we'll need
        characters_to_pad_with_whitespace = [',', '...', '!', '?', ':', '{', '}', '^']
        period_regular_expression = re.compile('(\w)\.')  # Periods can occur in ellipses, so need special detection
        runtime_variable_regular_expression = re.compile('(\[.*\])')
        runtime_variable_replacement_expressions = {}  # Expressions that are template gaps, e.g., [speaker.first_name]
        token_to_serialization_id = {}
        # Tokenize the terminal symbols
        for terminal_symbol in terminal_symbols:
            # Strip off whitespace padding
            preprocessed_terminal_symbol = terminal_symbol.strip()
            # Detect runtime variables and replace them with generic tokens
            runtime_variable_matches = runtime_variable_regular_expression.search(preprocessed_terminal_symbol)
            while runtime_variable_matches:
                if runtime_variable_matches.groups()[0] not in runtime_variable_replacement_expressions:
                    replacement_expression = 'PYTHON_EXPRESSION{}'.format(len(runtime_variable_replacement_expressions))
                    runtime_variable_replacement_expressions[runtime_variable_matches.groups()[0]] = (
                        replacement_expression
                    )
                    token_to_serialization_id[replacement_expression] = len(token_to_serialization_id)
                preprocessed_terminal_symbol = preprocessed_terminal_symbol.replace(
                    runtime_variable_matches.groups()[0],
                    runtime_variable_replacement_expressions[runtime_variable_matches.groups()[0]]
                )
                runtime_variable_matches = runtime_variable_regular_expression.match(preprocessed_terminal_symbol)
            # Add whitespace padding around the appropriate characters
            for character_to_pad in characters_to_pad_with_whitespace:
                preprocessed_terminal_symbol = preprocessed_terminal_symbol.replace(
                    character_to_pad, ' {} '.format(character_to_pad)
                )
            # Add whitespace padding around periods (this has to occur after the last step,
            # because periods can occur inside of ellipses)
            period_matches = period_regular_expression.search(preprocessed_terminal_symbol)
            while period_matches:
                character = period_matches.groups()[0]
                preprocessed_terminal_symbol = preprocessed_terminal_symbol.replace(
                    '{}.'.format(character), '{} .'.format(character)
                )
                period_matches = period_regular_expression.match(preprocessed_terminal_symbol)
            # Tokenize the preprocessed terminal symbol
            tokenized_terminal_symbol = preprocessed_terminal_symbol.split(' ')
            for token in tokenized_terminal_symbol:
                token = token.lower()
                if token != '' and token not in token_to_serialization_id:
                    token_to_serialization_id[token] = len(token_to_serialization_id)
        return runtime_variable_replacement_expressions, token_to_serialization_id

    def produce_lstm_training_data(self):
        """Produce all the files that constitute our training data."""
        print "Sampling {targeted_n} examples from a space out {generable_n} generable examples...".format(
            targeted_n=TARGETED_NUMBER_OF_TERMINAL_DERIVATIONS, generable_n=self.total_generable_derivations
        )
        self.produce_and_write_out_traces()
        # Reset the random seed
        random.seed(RANDOM_SEED)
        self.produce_and_write_out_terminal_derivations()

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
        self.out_file = open(path_to_write_out_to, 'w')
        one_percent_increment = TARGETED_NUMBER_OF_TERMINAL_DERIVATIONS / 100
        for i in xrange(TARGETED_NUMBER_OF_TERMINAL_DERIVATIONS):
            if i > 0 and i % one_percent_increment == 0:
                print "\t{}% complete".format(i/one_percent_increment)
            for symbol in self.top_level_symbols:
                symbol.probabilistically_expand(write_out=True, produce_trace=True)
        self.out_file.close()
        print "100% complete"

    def produce_and_write_out_terminal_derivations(self):
        """Produce and write out terminal derivations of our top-level symbols."""
        path_to_write_out_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=DERIVATIONS_OUT_FILENAME
        )
        self.out_file = open(path_to_write_out_to, 'w')
        one_percent_increment = TARGETED_NUMBER_OF_TERMINAL_DERIVATIONS/100
        for i in xrange(TARGETED_NUMBER_OF_TERMINAL_DERIVATIONS):
            if i > 0 and i % one_percent_increment == 0:
                print "\t{}% complete".format(i/one_percent_increment)
            for symbol in self.top_level_symbols:
                symbol.probabilistically_expand(write_out=True, produce_trace=False)
        self.out_file.close()
        print "100% complete"


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
        # This will hold the total number of terminal derivations of this symbol
        self.total_generable_derivations = None
        # Set exploration boost to the base value specified above as a global variable; we'll update
        # this over time as this symbol is expanded
        self.exploration_boost = BASE_EXPLORATION_BOOST

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

    def probabilistically_expand(self, write_out=False, produce_trace=False):
        """Probabilistically sample production rules by which this symbol may be expanded."""
        # Probabilistically select a production rule
        probabilistically_selected_rule = self._probabilistically_select_a_production_rule(self.production_rules)
        # Use the current exploration boost to update the application likelihoods for the
        # production rules that were *not* selected
        for rule in self.production_rules:
            if rule is not probabilistically_selected_rule:
                rule.application_likelihood += self.exploration_boost
        # Decay the exploration boost
        self.exploration_boost *= EXPLORATION_BOOST_DECAY_RATE
        # Expand this symbol using the selected production rule
        if produce_trace:
            return probabilistically_selected_rule.produce_and_write_out_a_trace(write_out=write_out)
        else:
            return probabilistically_selected_rule.produce_and_write_out_a_derivation(write_out=write_out)

    @staticmethod
    def _probabilistically_select_a_production_rule(rules):
        """Select a production rule probabilistically, given their application likelihoods."""
        # Determine the individual probabilities of each production rule, given the rules'
        # application likelihoods
        individual_probabilities = {}
        sum_of_all_application_rates = float(sum(rule.application_likelihood for rule in rules))
        for rule in rules:
            probability = rule.application_likelihood / sum_of_all_application_rates
            individual_probabilities[rule] = probability
        # Use those individual probabilities to associate each production rule with a specific
        # probability range, such that generating a random value between 0.0 and 1.0 will fall
        # into one and only one production rule's probability range
        probability_ranges = {}
        current_bound = 0.0
        for rule in rules:
            probability = individual_probabilities[rule]
            probability_range_for_this_rule = (current_bound, current_bound + probability)
            probability_ranges[rule] = probability_range_for_this_rule
            current_bound += probability
        # Make sure the last bound indeed extends to 1.0 (necessary because of
        # float rounding issues)
        last_rule_to_have_a_range_attributed = rules[-1]
        probability_ranges[last_rule_to_have_a_range_attributed] = (
            probability_ranges[last_rule_to_have_a_range_attributed][0], 1.0
        )
        # Now probabilistically select a rule
        x = random.random()
        probabilistically_selected_rule = next(
            rule for rule in rules if probability_ranges[rule][0] <= x <= probability_ranges[rule][1]
        )
        return probabilistically_selected_rule


class ProductionRule(object):
    """A production rule in a production system for in-game dialogue generation."""

    def __init__(self, training_data_writer, head, body_specification, application_rate):
        """Initialize a ProductionRule object.

        'head' is a nonterminal symbol constituting the left-hand side of this rule, while
        'body' is a sequence of symbols that this rule may be used to expand the head into.
        """
        self.training_data_writer = training_data_writer
        self.head = head
        self.body = None  # Gets set by TrainingDataWriter._init_resolve_symbol_references_in_a_rule_body()
        # These get set by TrainingDataWriter._init_determine_which_production_rules_are_terminal_or_semiterminal()
        self.terminal = False
        self.semiterminal = False
        self.body_specification = body_specification
        self.body_specification_str = ''.join(body_specification)
        # Application rates are attributed to rules in the Expressionist interface and, here,
        # they drive the probabilistic sampling of production rules (since it's often infeasible
        # to exhaustively produce all generable training data)
        self.application_rate = application_rate
        # This will hold the total number of terminal derivations generable by this production rule;
        # since there's no product() built-in function in Python that works like sum() does, we
        # have to use this ugly reduce thing
        self.total_generable_derivations = None
        # Prepare an application likelihood, which is the likelihood that this production rule will
        # be applied at any given decision point (in which it is a candidate) during the process;
        # specifically, we start with the rule's application and then alter this according to the
        # exploration boost and its associated decay rate (specified as global variables at the top
        # of this file)
        self.application_likelihood = application_rate

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

    def produce_and_write_out_a_trace(self, write_out=False):
        """Write out a derivation trace in the format specified for LSTM training.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{`Hi~}^` ~^interlocutor|first|name{`[speaker.belief(interlocutor, 'first name')]~}^`.~}
        for the terminal derivation "Hi, [speaker.belief(interlocutor, 'first name')]."
        """
        terminally_expanded_symbols_in_this_rule_body = []
        for symbol in self.body:
            if type(symbol) == unicode:  # Terminal symbol (no need to expand)
                terminally_expanded_symbols_in_this_rule_body.append(symbol)
            else:  # Nonterminal symbol that we must probabilistically expand
                terminal_expansion_of_that_symbol = symbol.probabilistically_expand(produce_trace=True)
                terminally_expanded_symbols_in_this_rule_body.append(terminal_expansion_of_that_symbol)
        # Return the expansion yielded by this rule, which is simply the concatenation of
        # the expansions of the symbols in its body
        expansion_yielded_by_this_rule = "{head}{{{partial_trace}}}".format(
            head='|'.join(self.head.tag.split()),
            partial_trace='^'.join(terminally_expanded_symbols_in_this_rule_body)
        )
        # Now concatenate these and prepend them with syntax indicating which nonterminal symbol
        # is the head of this rule; this will produce derivation traces in the format we want them in
        if not write_out:
            return expansion_yielded_by_this_rule
        else:
            self.training_data_writer.out_file.write("{}\n".format(expansion_yielded_by_this_rule))
            self.training_data_writer.out_file.flush()

    def produce_and_write_out_a_derivation(self, write_out=False):
        """Exhaustively produce all terminal derivations yielded by this rule for use as LSTM training data."""
        terminally_expanded_symbols_in_this_rule_body = []
        for symbol in self.body:
            if type(symbol) == unicode:  # Terminal symbol (no need to expand)
                terminally_expanded_symbols_in_this_rule_body.append(symbol)
            else:  # Nonterminal symbol that we must probabilistically expand
                terminal_expansion_of_that_symbol = symbol.probabilistically_expand(produce_trace=False)
                terminally_expanded_symbols_in_this_rule_body.append(terminal_expansion_of_that_symbol)
        # Return the expansion yielded by this rule, which is simply the concatenation of
        # the expansions of the symbols in its body
        expansion_yielded_by_this_rule = ''.join(terminally_expanded_symbols_in_this_rule_body)
        # Now concatenate these and prepend them with syntax indicating which nonterminal symbol
        # is the head of this rule; this will produce derivation traces in the format we want them in
        if not write_out:
            return expansion_yielded_by_this_rule
        else:
            self.training_data_writer.out_file.write("{}\n".format(expansion_yielded_by_this_rule))
            self.training_data_writer.out_file.flush()


if __name__ == "__main__":
    writer = TrainingDataWriter()
    # writer.write_out_pickled_symbol_and_token_serialization_dictionaries()
    writer.produce_lstm_training_data()
