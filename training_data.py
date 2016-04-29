import json
import itertools
import os
import random
import operator


PATH_TO_JSON_GRAMMAR_SPECIFICATION = (
    '/Users/jamesryan/Desktop/Expressionist0.51/grammars/load/talktown-player-input_hair-queries-probabilistic.json'
    #'/Users/jamesryan/Desktop/IVA2016/talktown-grammar-used-in-iva-study.json'
)
DIRECTORY_TO_WRITE_OUT_TO = os.getcwd()
TRACES_OUT_FILENAME = 'PLAYER-INPUT_HAIR_TRACES_28Apr2016'
DERIVATIONS_OUT_FILENAME = 'PLAYER-INPUT_HAIR_DERIVATIONS_28Apr2016'
# TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM = ['player appearance query']
# To expand *all* top-level symbols to generate training data, use this line instead:
TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM = 'ALL'
VERBOSE = 2  # Whether the process will display progress text (0=No, 1=Verbose, 2=Very Verbose)
SAMPLING_RATE = 0.13  # Tuned to produce ~1GB-sized trace output file (the actual rate is not really interpretable)
RANDOM_SEED = 0


class TrainingDataWriter(object):
    """A production system for generating training data from the JSON specifying an Expressionist grammar."""

    def __init__(self):
        """Initialize a Productionist object."""
        self.nonterminal_symbols = self._init_parse_json_grammar_specification(
            path_to_json_grammar_specification=PATH_TO_JSON_GRAMMAR_SPECIFICATION
        )
        self._init_resolve_symbol_references_in_all_production_rule_bodies()
        self._init_determine_which_production_rules_are_terminal()
        # Set top-level symbols, i.e., the symbols that will be expanded to produce
        # the training data (this is specified above as a global variable)
        if TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM == 'ALL':
            self.top_level_symbols = [symbol for symbol in self.nonterminal_symbols if symbol.top_level]
        else:
            self.top_level_symbols = [
                symbol for symbol in self.nonterminal_symbols if symbol.tag in TOP_LEVEL_SYMBOLS_TO_GENERATE_FROM
            ]
        # This gets set by produce_and_write_out_traces() and then reset by
        # produce_and_write_out_terminal_derivations()
        self.out_file = None
        # Determine the total number of generable terminal derivations (summed across top-level
        # symbols only)
        self.total_generable_derivations = sum(
            s.total_number_of_generable_terminal_derivations() for s in self.top_level_symbols
        )
        # Determine the total number of terminal derivations generable by the top-level symbols of
        # our source grammar, which we can use to determine a sampling rate that will produce approximately
        # the desired number of terminal derivations (as specified by a global variable set above)
        self.sampling_rate = SAMPLING_RATE
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

    def _init_determine_which_production_rules_are_terminal(self):
        """Determine which production rules are terminal, e.g., yield a single string.

        These rules crucially allow for tractable sampling of very large Expressionist grammars.
        """
        for symbol in self.nonterminal_symbols:
            for rule in symbol.production_rules:
                if len(rule.body) == 1 and type(rule.body[0]) is unicode:
                    rule.terminal = True

    def produce_lstm_training_data(self):
        """Produce all the files that constitute our training data."""
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
        for symbol in self.top_level_symbols:
            symbol.produce_and_write_out_traces(write_out=True)
        self.out_file.close()

    def produce_and_write_out_terminal_derivations(self):
        """Produce and write out terminal derivations of our top-level symbols."""
        path_to_write_out_to = "{dir}/{filename}".format(
            dir=DIRECTORY_TO_WRITE_OUT_TO, filename=DERIVATIONS_OUT_FILENAME
        )
        self.out_file = open(path_to_write_out_to, 'w')
        for symbol in self.top_level_symbols:
            symbol.produce_and_write_out_terminal_derivations(write_out=True)
        self.out_file.close()

    def probabilistically_sort_production_rules(self, rules):
        """Sort a collection of production rules probabilistically by utilizing their application rates.

        Because the application rates of a group of rules are only relative to one another
        if those rules have the same head (which is not a guarantee when backward chaining),
        we need to probabilistically sort rules within rule-head groups first, and then we really
        have no viable option except randomly shuffling the head groups (while retaining the
        probabilistically determined orderings within each head group)
        """
        probabilistic_sort = []
        # Assemble all the rule heads
        rule_heads = list({rule.head for rule in rules})
        # Randomly shuffle the rule heads (we have no way deciding how to order the
        # rule-head groups, since the application rates of rules in different groups
        # only mean anything relative to the other rules in that same group, not to
        # rules in other groups)
        random.shuffle(rule_heads)
        # Probabilistically sort each head group
        for head in rule_heads:
            rules_sharing_this_head = [rule for rule in rules if rule.head is head]
            probabilistic_sort_of_this_head_group = (
                self._probabilistically_sort_a_rule_head_group(rules=rules_sharing_this_head)
            )
            probabilistic_sort += probabilistic_sort_of_this_head_group
        return probabilistic_sort

    def _probabilistically_sort_a_rule_head_group(self, rules):
        """Probabilistically sort a collection of production rules that share the same rule head.

        This method works by fitting a probability range to each of the given set of rules, rolling
        a random number and selecting the rule whose range it falls within, and then repeating this
        on the set of remaining rules, and so forth until every rule has been selecting.
        """
        probabilistic_sort = []
        remaining_rules = list(rules)
        while len(remaining_rules) > 1:
            probability_ranges = (
                self._fit_probability_distribution_to_rules_according_to_their_application_rates(rules=remaining_rules)
            )
            x = random.random()
            probabilistically_selected_rule = next(
                rule for rule in remaining_rules if probability_ranges[rule][0] <= x <= probability_ranges[rule][1]
            )
            probabilistic_sort.append(probabilistically_selected_rule)
            remaining_rules.remove(probabilistically_selected_rule)
        # Add the only rule that's left (no need to fit a probability distribution to
        # this set containing just one rule)
        last_one_to_be_selected = remaining_rules[0]
        probabilistic_sort.append(last_one_to_be_selected)
        return probabilistic_sort

    @staticmethod
    def _fit_probability_distribution_to_rules_according_to_their_application_rates(rules):
        """Return a dictionary mapping each of the rules to a probability range."""
        # Determine the individual probabilities of each production rule, given the
        # rules' application rates
        individual_probabilities = {}
        sum_of_all_application_rates = float(sum(rule.application_rate for rule in rules))
        for rule in rules:
            probability = rule.application_rate / sum_of_all_application_rates
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
        return probability_ranges


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

    def produce_and_write_out_traces(self, write_out=None):
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
        # Probabilistically sample a subset of terminal production rules (rules that yield a single string, since
        # these constitute our degree of freedom in sampling), and append this to all nonterminal
        # production rules
        sampled_production_rules = [rule for rule in self.production_rules if not rule.terminal]
        # Using the sampling rate specified at the top of this file, determine how many terminal
        # production rules we'll sample right now
        number_of_rules_to_sample = int(round(SAMPLING_RATE*len(self.production_rules)))
        number_of_rules_to_sample = max(1, number_of_rules_to_sample)  # Make sure at least one rule will be sampled
        # Probabilistically sort the production rules
        probabilistically_sorted_production_rules = (
            self.training_data_writer.probabilistically_sort_production_rules(rules=self.production_rules)
        )
        # Sample the first N rules in this probabilistically sorted list, where
        # N = number_of_rules_to_sample
        sampled_production_rules += probabilistically_sorted_production_rules[:number_of_rules_to_sample]
        # If False is passed for the write_out argument, the derivation traces produced here
        # pertain to a symbol that is not top-level, which means that the traces will not be written
        # out (but rather will end up as substrings of the traces for actual terminal derivations,
        # which *will* be written out)
        if not write_out:
            sampled_derivation_traces = []
            for rule in sampled_production_rules:
                sampled_derivation_traces += (
                    rule.produce_and_write_out_traces(write_out=None)
                )
            return sampled_derivation_traces
        else:
            for rule in sampled_production_rules:
                rule.produce_and_write_out_traces(write_out=write_out)

    def produce_and_write_out_terminal_derivations(self, write_out=False):
        """Exhaustively produce all terminal derivations of this symbol for use as part of the LSTM training data."""
        if VERBOSE > 0:
            print "\tProducing derivations for nonterminal symbol '{symbol}'".format(symbol=self)
        # Sample a subset of terminal production rules (rules that yield a single string, since
        # these constitute our degree of freedom in sampling), and append this to all nonterminal
        # production rules
        production_rules_to_sample = []
        for rule in self.production_rules:
            if not rule.terminal:
                production_rules_to_sample.append(rule)
            elif random.random() < self.training_data_writer.sampling_rate:
                production_rules_to_sample.append(rule)
        if not production_rules_to_sample:  # Make sure we're sampling at least one production rule
            production_rules_to_sample.append(self.production_rules[0])
        # If False passed for the 'write_out' argument, the derivations produced here
        # pertain to a symbol that is not top-level, which means that the derivations will not be
        # written out (but rather will end up as substrings of actual terminal derivations that
        # *will* be written out)
        if not write_out:
            sampled_terminal_derivations = []
            for rule in production_rules_to_sample:
                sampled_terminal_derivations += rule.produce_and_write_out_terminal_derivations(write_out=None)
            return sampled_terminal_derivations
        else:
            for rule in production_rules_to_sample:
                rule.produce_and_write_out_terminal_derivations(write_out=write_out)


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
        self.terminal = False  # Gets set by TrainingDataWriter._init_determine_which_production_rules_are_terminal()
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

    def produce_and_write_out_traces(self, write_out=False):
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
        if not write_out:
            return (
                "{head}{{{partial_trace}}}".format(
                    head='|'.join(self.head.tag.split()),
                    partial_trace='^'.join(cartesian_product)
                ) for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body
            )
        else:
            for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body:
                self.training_data_writer.out_file.write(
                    "{}\n".format(
                        "{head}{{{partial_trace}}}".format(
                            head='|'.join(self.head.tag.split()),
                            partial_trace='^'.join(cartesian_product)
                        )
                    )
                )
                self.training_data_writer.out_file.flush()

    def produce_and_write_out_terminal_derivations(self, write_out=None):
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
        # these terminal derivations (signaled by whether True is passed for the 'write_out'
        # argument), return a generator containing all of them
        if not write_out:
            return (
                ''.join(cartesian_product) for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body
            )
        # Otherwise, let's write these out right now
        for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body:
            self.training_data_writer.out_file.write('{}\n'.format(''.join(cartesian_product)))
            self.training_data_writer.out_file.flush()


if __name__ == "__main__":
    writer = TrainingDataWriter()
    writer.produce_lstm_training_data()
