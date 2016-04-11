import sys
import json
import itertools
import random


class Productionist(object):
    """A production system for in-game dialogue generation.

    Objects of this class operate over a probabilistic context-free generative grammar exported by
    Expressionist according to requests originating from a game system. As such, it can be thought of
    as an interface between the game engine and an Expressionist grammar.
    """

    def __init__(self, game, debug=False):
        """Initialize a Productionist object."""
        self.game = game
        self.debug = debug
        self.nonterminal_symbols = self._init_parse_json_grammar_specification(
            path_to_json_grammar_specification=game.config.path_to_json_grammar_specification
        )
        self._init_resolve_symbol_references_in_all_production_rule_bodies()
        self._init_attribute_backward_chaining_and_forward_chaining_rules_to_symbols()
        self.move_satisficers = self._init_structure_symbols_according_to_dialogue_moves_they_satisfice()
        self.topic_satisficers = self._init_structure_symbols_according_to_topics_they_satisfice()
        # This method is used to collect all the nonterminal symbols that were expanded
        # in the production of a complete dialogue template, which a LineOfDialogue object
        # will need in order to inherit all the mark-up of these symbols
        self.symbols_expanded_to_produce_the_dialogue_template = set()

    @staticmethod
    def _init_parse_json_grammar_specification(path_to_json_grammar_specification):
        """Parse a JSON grammar specification exported by Expressionist to instantiate symbols and rules."""
        # Parse the JSON specification to build a dictionary data structure
        symbol_objects = []
        grammar_dictionary = json.loads(open(path_to_json_grammar_specification).read())
        nonterminal_symbol_specifications = grammar_dictionary['nonterminals']
        for tag, nonterminal_symbol_specification in nonterminal_symbol_specifications.iteritems():
            top_level = nonterminal_symbol_specification['deep']
            production_rules_specification = nonterminal_symbol_specification['rules']
            raw_markup = nonterminal_symbol_specification['markup']
            symbol_object = NonterminalSymbol(
                tag=tag, top_level=top_level, raw_markup=raw_markup,
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
        """Resolve all symbol references in the body of this rule to point to actual NonterminalSymbol objects."""
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

    def _init_attribute_backward_chaining_and_forward_chaining_rules_to_symbols(self):
        """Attribute to symbols their backward-chaining rules and forward-chaining rules.

        A backward-chaining rule of a symbol is a production rule whose body (i.e., right-hand
        side) the symbol appears in. A forward-chaining rule of a symbol is then a production rule
        whose head (i.e., left-hand side) *is* that symbol.
        """
        # Collect all production rules specified in the grammar
        all_production_rules_in_the_grammar = []
        for nonterminal_symbol in self.nonterminal_symbols:
            for production_rule in nonterminal_symbol.production_rules:
                all_production_rules_in_the_grammar.append(production_rule)
        # Attribute to each symbol its backward-chaining and forward-chaining rules
        for rule in all_production_rules_in_the_grammar:
            rule.head.forward_chaining_rules.append(rule)
            for symbol in rule.body:
                if type(symbol) is NonterminalSymbol:
                    symbol.backward_chaining_rules.append(rule)

    def _init_structure_symbols_according_to_dialogue_moves_they_satisfice(self):
        """Return a dictionary mapping dialogue-move names to the symbols that satisfice them.

        By 'satisficing' a dialogue move, I mean that if a symbol were to be expanded in the
        construction of a line of dialogue, that line of dialogue could then be used to perform
        that dialogue move upon being deployed in a conversation. I use the language of satisficing
        because the act of dialogue construction here is a search task that targets either a dialogue
        move or a topic to address, and especially because we are not employing any notion of which
        symbols best perform which dialogue moves (i.e., a symbol simply performs or does not perform
        a move).
        """
        move_satisficers = {}
        for symbol in self.nonterminal_symbols:
            for move_name in symbol.moves:
                if move_name not in move_satisficers:
                    move_satisficers[move_name] = set()
                move_satisficers[move_name].add(symbol)
        return move_satisficers

    def _init_structure_symbols_according_to_topics_they_satisfice(self):
        """Return a dictionary mapping topic names to the symbols that satisfice them."""
        topic_satisficers = {}
        for symbol in self.nonterminal_symbols:
            for topic_name in symbol.topics_addressed:
                if topic_name not in topic_satisficers:
                    topic_satisficers[topic_name] = set()
                topic_satisficers[topic_name].add(symbol)
        return topic_satisficers

    def target_dialogue_move(self, move_name, conversation):
        """Attempt to construct a line of dialogue that would perform the given dialogue move.

        This act of dialogue construction is rendered as a search task over the tree specified
        by a grammar authored in Expressionist. Specifically, we target individual symbols that
        are annotated as performing the desired dialogue move, attempting to successfully
        terminally backward-chain (i.e., follow production rules *backward* until we reach a
        top-level symbol) and successfully terminally forward-chain (i.e., follow production
        rules *forward* until we reach an expansion containing no nonterminal symbols). The
        notion of success here is articulated by the Conversation object that calls this method,
        but generally it will constrain this search procedure such that no symbol with
        unsatisfied preconditions (given the state of the conversation/world, which we have
        access to via the Conversation object's attributes) may be expanded at any point.
        """
        # Collect all symbols that satisfice this move (see above or ctrl+f for more explanation)
        satisficing_symbols = list(self.move_satisficers[move_name])
        # Randomly shuffle this list (to promote conversational variability)
        random.shuffle(satisficing_symbols)
        # Iteratively attempt to successfully build a line of dialogue by backward-chaining
        # and forward-chaining from this symbol
        for symbol in satisficing_symbols:
            raw_dialogue_template_built_by_targeting_this_symbol = self._target_symbol(
                symbol=symbol, conversation=conversation
            )
            if raw_dialogue_template_built_by_targeting_this_symbol:  # Will be None if targeting was unsuccessful
                # Reify the template as a LineOfDialogue object and return that
                line_of_dialogue_object = LineOfDialogue(
                    raw_line=raw_dialogue_template_built_by_targeting_this_symbol,
                    symbols_expanded_to_produce_this_template=self.symbols_expanded_to_produce_the_dialogue_template,
                    conversation=conversation
                )
                self._reset_temporary_attributes()
                return line_of_dialogue_object
            self._reset_temporary_attributes()
        if self.debug:
            print "Productionist could not generate a line of dialogue that performs the move {}".format(move_name)

    def target_topics_of_conversation(self, topic_names, conversation):
        """Attempt to construct a line of dialogue that would address the given topic.

        This act of dialogue construction is rendered as a search task over the tree specified
        by a grammar authored in Expressionist. Specifically, we target individual symbols that
        are annotated as addressing the desired topic of conversation, attempting to successfully
        terminally backward-chain (i.e., follow production rules *backward* until we reach a
        top-level symbol) and successfully terminally forward-chain (i.e., follow production
        rules *forward* until we reach an expansion containing no nonterminal symbols). The
        notion of success here is articulated by the Conversation object that calls this method,
        but generally it will constrain this search procedure such that no symbol with
        unsatisfied preconditions (given the state of the conversation/world, which we have
        access to via the Conversation object's attributes) may be expanded at any point.
        """
        # Collect all symbols that satisfice this move (see above or ctrl+f for more explanation)
        satisficing_symbols = set()
        for topic_name in topic_names:
            satisficing_symbols |= self.topic_satisficers[topic_name]
        satisficing_symbols = list(satisficing_symbols)
        # Randomly shuffle this list (to promote conversational variability)
        random.shuffle(satisficing_symbols)
        # Iteratively attempt to successfully build a line of dialogue by backward-chaining
        # and forward-chaining from this symbol
        for symbol in satisficing_symbols:
            raw_dialogue_template_built_by_targeting_this_symbol = self._target_symbol(
                symbol=symbol, conversation=conversation
            )
            if raw_dialogue_template_built_by_targeting_this_symbol:  # Will be None if targeting was unsuccessful
                # Reify the template as a LineOfDialogue object and return that
                line_of_dialogue_object = LineOfDialogue(
                    raw_line=raw_dialogue_template_built_by_targeting_this_symbol,
                    symbols_expanded_to_produce_this_template=self.symbols_expanded_to_produce_the_dialogue_template,
                    conversation=conversation
                )
                self._reset_temporary_attributes()
                return line_of_dialogue_object
            self._reset_temporary_attributes()
        if self.debug:
            print "Productionist could not generate a line of dialogue that addresses the topics {}".format(
                ' ,'.join(topic_name for topic_name in topic_names)
            )

    def _target_symbol(self, symbol, conversation):
        """Attempt to successfully terminally backward-chain and forward-chain from this symbol.

        If successful, this method will return a LineOfDialogue object, which is a templated
        line of dialogue that may be filled in and deployed during a conversation. If this
        method fails at any point, it will immediately return None.
        """
        if self.debug:
            print "Targeting symbol {}...".format(symbol)
        # Attempt forward chaining first
        partial_raw_template_built_by_forward_chaining = self._forward_chain_from_symbol(
            symbol=symbol, conversation=conversation, symbol_is_the_targeted_symbol=True
        )
        if not partial_raw_template_built_by_forward_chaining:
            if self.debug:
                print "Could not successfully forward chain from the targeted symbol {}".format(symbol)
            return None
        if self.debug:
            print "Successfully forward chained from targeted symbol {} all the way to terminal expansion {}".format(
                symbol, symbol.expansion
            )
        # Forward chaining was successful, so now attempt backward chaining, unless the
        # targeted symbol is a top-level symbol, in which case we can return the template
        # we built by forward-chaining
        if symbol.top_level:
            if self.debug:
                print "Targeted symbol {} is a top-level symbol, so we can skip backward chaining".format(symbol)
            top_level_symbol_that_we_successfully_backward_chained_to = symbol
        else:
            if self.debug:
                print "Now I will attempt to backward chain from the targeted symbol {}".format(symbol)
            top_level_symbol_that_we_successfully_backward_chained_to = (
                self._backward_chain_from_symbol(symbol=symbol, conversation=conversation)
            )
            if not top_level_symbol_that_we_successfully_backward_chained_to:
                return None
        complete_raw_template = self._retrace_backward_and_forward_chains_to_generate_a_complete_template(
            start_symbol=top_level_symbol_that_we_successfully_backward_chained_to,
            conversation=conversation
        )
        return complete_raw_template

    def _forward_chain_from_symbol(self, symbol, conversation, retracing_chains=False,
                                   symbol_is_the_targeted_symbol=False):
        """Attempt to successfully terminally forward-chain from the given symbol, i.e.,
        attempt to terminally expand a symbol.

        If successful, this method will return a string constituting a partial dialogue
        template pertaining to the portion of a prospective complete line of dialogue
        that would include everything including and beyond the expansion of the targeted
        symbol. If this method fails at any point, it will immediately return None.
        """
        if self.debug:
            print "Attempting to forward chain from symbol {}...".format(symbol)
        # First check for whether this symbol's preconditions are satisfied and whether
        # the use of its expansion in a line of dialogue would cause a conversational
        # violation to be incurred
        if symbol.currently_violated(conversation=conversation):
            return None
        candidate_production_rules = symbol.forward_chaining_rules
        # If one of these production rules is already known to be on a chain, we can just pick
        # that one mindlessly, since we already know that's the route to go
        try:
            rule_on_our_chain = next(r for r in candidate_production_rules if r.viable)
            return self._target_production_rule(
                rule=rule_on_our_chain, conversation=conversation, retracing_chains=retracing_chains
            )
        except StopIteration:
            pass
        # Sort the candidate production rules probabilistically by utilizing their application rates
        candidate_production_rules = self._probabilistically_sort_production_rules(rules=candidate_production_rules)
        # Iterate over these rules, attempting to utilize them successfully; return
        # a template snippet if a rule may be utilized successfully
        for production_rule in candidate_production_rules:
            terminal_expansion_yielded_by_firing_that_production_rule = (
                self._target_production_rule(
                    rule=production_rule, conversation=conversation, retracing_chains=retracing_chains
                )
            )
            if terminal_expansion_yielded_by_firing_that_production_rule:
                # Save this successful terminal expansion of this symbol, in case we
                # need it later (so that we don't reduplicate this completed effort)
                symbol.expansion = terminal_expansion_yielded_by_firing_that_production_rule
                # If the symbol we're forward chaining from is a top-level symbol and is
                # the symbol that we are ultimately targeting, then save the production rule
                # that allowed us to terminally expand it, since we'll need this information
                # when we go back through the forward chain to collect all the mark-up of
                # the symbols we expanded on the chain (for the LineOfDialogue object we
                # end up instantiating to inherit)
                if symbol.top_level and symbol_is_the_targeted_symbol:
                    if self.debug:
                        print "Added production rule {} to the chain".format(production_rule)
                    production_rule.viable = True
                return terminal_expansion_yielded_by_firing_that_production_rule
        # If we tried every production rule and failed to return a terminal expansion,
        # then we must give up on this symbol by returning None
        if self.debug:
            print "Failed to forward chain from symbol {}".format(symbol)
        return None

    def _backward_chain_from_symbol(self, symbol, conversation):
        """Attempt to successfully terminally backward-chain from the given symbol.

        If successful, this method will return a string constituting a partial dialogue
        template pertaining to the portion of a prospective complete line of dialogue
        that would include everything up to the targeted symbol. If this method fails
        at any point, it will immediately return None.
        """
        if self.debug:
            print "Attempting to backward chain from symbol {}...".format(symbol)
        if symbol.top_level:
            # Make sure this symbol doesn't violate any preconditions, since this hasn't
            # been checked yet during backward chaining
            if not symbol.currently_violated(conversation=conversation):
                if self.debug:
                    print "Reached top-level symbol {}, so backward chaining is done".format(symbol)
                return symbol
        candidate_production_rules = symbol.backward_chaining_rules
        # Sort the candidate production rules probabilistically by utilizing their application rates
        candidate_production_rules = self._probabilistically_sort_production_rules(rules=candidate_production_rules)
        for production_rule in candidate_production_rules:
            this_production_rule_successfully_fired = (
                self._target_production_rule(rule=production_rule, conversation=conversation)
            )
            if this_production_rule_successfully_fired:
                production_rule.viable = True
                # Set breadcrumbs so that we can reconstruct our path if this backward chain
                # is successful (by 'reconstruct our path', I mean fire all the production rules
                # along our successful backward chain until we've generated a complete dialogue template)
                top_level_symbol_we_successfully_chained_back_to = (
                    self._backward_chain_from_symbol(production_rule.head, conversation=conversation)
                )
                if top_level_symbol_we_successfully_chained_back_to:
                    if self.debug:
                        print "Added production rule {} to the chain".format(production_rule)
                    return top_level_symbol_we_successfully_chained_back_to
        if self.debug:
            print "Failed to backward chain from symbol {}".format(symbol)
        return None

    def _retrace_backward_and_forward_chains_to_generate_a_complete_template(self, start_symbol, conversation):
        """Retrace successfully terminal backward and forward chains to generate a complete dialogue template.

        In this method, we traverse the production-rule chains that we have already successfully
        discovered to generate a complete line of dialogue (and to accumulate all the mark-up that
        it will inherit from the symbols that are expanded along these chains).
        """
        self.symbols_expanded_to_produce_the_dialogue_template = {start_symbol}
        if self.debug:
            print "Retraversing now from top-level symbol {}".format(start_symbol)
        first_breadcrumb = next(rule for rule in start_symbol.production_rules if rule.viable)
        return self._target_production_rule(rule=first_breadcrumb, conversation=conversation, retracing_chains=True)

    def _target_production_rule(self, rule, conversation, retracing_chains=False):
        """Attempt to terminally expand this rule's head."""
        if self.debug:
            if rule.viable:
                print "Retracing our chains via rule {}".format(rule)
            else:
                print "Targeting production rule {}...".format(rule)
        terminally_expanded_symbols_in_this_rule_body = []
        for symbol in rule.body:
            if type(symbol) == unicode:  # Terminal symbol (no need to expand)
                terminally_expanded_symbols_in_this_rule_body.append(symbol)
            elif symbol.expansion and not retracing_chains:
                # Nonterminal symbol that we already successfully expanded earlier
                return symbol.expansion
            else:  # Nonterminal symbol that we have not yet successfully expanded
                terminal_expansion_of_that_symbol = (
                    self._forward_chain_from_symbol(
                        symbol=symbol, conversation=conversation, retracing_chains=retracing_chains
                    )
                )
                if terminal_expansion_of_that_symbol:
                    if retracing_chains:
                        self.symbols_expanded_to_produce_the_dialogue_template.add(symbol)
                        if self.debug:
                            print "Traversed through symbol {}".format(symbol)
                    terminally_expanded_symbols_in_this_rule_body.append(terminal_expansion_of_that_symbol)
                else:
                    if self.debug:
                        print "Abandoning production rule {}".format(rule)
                    return None
        # You successfully expanded all the symbols in this rule body
        rule.viable = True
        expansion_yielded_by_this_rule = ''.join(terminally_expanded_symbols_in_this_rule_body)
        return expansion_yielded_by_this_rule

    def _probabilistically_sort_production_rules(self, rules):
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
            probability = rule.application_rate/sum_of_all_application_rates
            individual_probabilities[rule] = probability
        # Use those individual probabilities to associate each production rule with a specific
        # probability range, such that generating a random value between 0.0 and 1.0 will fall
        # into one and only one production rule's probability range
        probability_ranges = {}
        current_bound = 0.0
        for rule in rules:
            probability = individual_probabilities[rule]
            probability_range_for_this_rule = (current_bound, current_bound+probability)
            probability_ranges[rule] = probability_range_for_this_rule
            current_bound += probability
        # Make sure the last bound indeed extends to 1.0 (necessary because of
        # float rounding issues)
        last_rule_to_have_a_range_attributed = rules[-1]
        probability_ranges[last_rule_to_have_a_range_attributed] = (
            probability_ranges[last_rule_to_have_a_range_attributed][0], 1.0
        )
        return probability_ranges

    def _reset_temporary_attributes(self):
        """Clear all temporary symbol and rule attributes that we set during this generation session."""
        for symbol in self.nonterminal_symbols:
            symbol.expansion = None
            for rule in symbol.production_rules:
                rule.viable = False
        self.symbols_expanded_to_produce_the_dialogue_template = set()

    def find_symbol(self, symbol_name):
        """Return a symbol with the given name."""
        try:
            return next(s for s in self.nonterminal_symbols if s.tag == symbol_name)
        except StopIteration:
            print "I could not find a symbol with that name."

    def produce_lstm_training_data(self):
        """Produce all the files constituting LSTM training data."""
        self.produce_all_derivation_traces_for_lstm_training_data(omit_derivation_snippets=True)
        # Clear out data saved during the last process
        for symbol in self.nonterminal_symbols:
            symbol.all_derivation_traces = []
        self.produce_all_derivation_traces_for_lstm_training_data(omit_derivation_snippets=False)
        self.produce_all_terminal_derivations_for_lstm_training()

    def produce_all_derivation_traces_for_lstm_training_data(self, omit_derivation_snippets=False):
        """Exhaustively produce all terminal derivations in the grammar for LSTM training data.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{<Hi>},< >,interlocutor|first|name{<[speaker.belief(interlocutor, 'first name')]>}}
        """
        outfile_derivation_snippet = (
            'TRACES-WITHOUT-DERIVATIONS' if omit_derivation_snippets else 'TRACES-WITH-DERIVATIONS'
        )
        path_to_write_out_to = '/Users/jamesryan/Desktop/dialogue_lstm_training_data_{}_26Feb2016'.format(
            outfile_derivation_snippet
        )
        out_file = open(path_to_write_out_to, 'w')
        top_level_symbols = [symbol for symbol in self.nonterminal_symbols if symbol.top_level]
        for symbol in top_level_symbols:
            print "Deriving LSTM training data ({}) for top-level symbol '{}'".format(
                outfile_derivation_snippet, symbol
            )
            for derivation_trace in symbol.produce_all_derivation_traces_for_lstm_training_data(
                    omit_derivation_snippets=omit_derivation_snippets
            ):
                out_file.write('{}\n'.format(derivation_trace))
            out_file.flush()
        out_file.close()

    def produce_all_terminal_derivations_for_lstm_training(self):
        """Exhaustively produce all terminal derivations generable by this grammar as part of the LSTM training data."""
        path_to_write_out_to = '/Users/jamesryan/Desktop/dialogue_lstm_training_data_ALL-DERIVATIONS_26Feb2016'
        out_file = open(path_to_write_out_to, 'w')
        top_level_symbols = [symbol for symbol in self.nonterminal_symbols if symbol.top_level]
        for symbol in top_level_symbols:
            print "Deriving LSTM training data (ALL DERIVATIONS) for top-level symbol '{}'".format(symbol)
            for derivation in symbol.produce_all_terminal_derivations_for_lstm_training():
                out_file.write('{}\n'.format(derivation))
            out_file.flush()
        out_file.close()


class NonterminalSymbol(object):
    """A symbol in a production system for in-game dialogue generation."""

    def __init__(self, tag, top_level, raw_markup, production_rules_specification):
        """Initialize a NonterminalSymbol object."""
        self.tag = tag
        # If a terminal expansion of this symbol constitutes a complete line of dialogue, then
        # this is a top-level symbol
        self.top_level = top_level
        # Prepare annotation sets that will be populated (as appropriate) by _init_parse_markup()
        self.preconditions = set()
        self.conditional_violations = set()
        self.propositions = set()
        self.moves = set()  # The dialogue moves constituted by the delivery of this line
        self.speaker_obligations_pushed = set()  # Line asserts speaker conversational obligations
        self.interlocutor_obligations_pushed = set()  # Line asserts interlocutor conversational obligations
        self.topics_pushed = set()  # Line introduces a new topic of conversation
        self.topics_addressed = set()  # Line addresses a topic of conversation
        self.clear_subject_of_conversation = False  # Line clears subject of conversation to allow asserting a new one
        self.force_speaker_subject_match_to_speaker_preoccupation = False  # Line forces a speaker subject match
        self.context_updates = set()  # Line updates the conversational context, e.g., w.r.t. subject of conversation
        self._init_parse_markup(raw_markup=raw_markup)
        self.production_rules = self._init_reify_production_rules(production_rules_specification)
        # These attributes are used to perform live generation of a dialogue template from the
        # grammar specification, which is done using backward-chaining and forward-chaining
        # to check for precondition violations and other preclusions; they get set by
        # Productionist._init_attribute_backward_chaining_and_forward_chaining_rules_to_symbols()
        self.backward_chaining_rules = []
        self.forward_chaining_rules = []
        # This attribute will hold the successful expansion of this symbol during a
        # generation procedure; we keep track of this so as to not reduplicate expansion
        # efforts while we are firing production rules during backward- and forward-chaining,
        # which could happen if two rules have the same symbol in their rule bodies
        self.expansion = None
        # This attribute will hold LSTM training data produced by this symbol, so that we do
        # not reduplicate efforts while we are generating a training set; see
        # NonterminalSymbol.produce_all_derivation_traces_for_lstm_training_data() for more information
        self.all_derivation_traces = []
        # This attribute will hold all terminal derivations of this symbol, so that we do
        # not reduplicate efforts while we are generating LSTM training data; see
        # NonterminalSymbol.produce_all_terminal_derivations_for_lstm_training() for more information
        self.all_terminal_derivations = []

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
                    if tag == "CLEAR SUBJECT":
                        self.clear_subject_of_conversation = True
                    if tag == "FORCE SPEAKER SUBJECT MATCH TO SPEAKER PREOCCUPATION":
                        self.force_speaker_subject_match_to_speaker_preoccupation = True
                    elif tag:
                        self.context_updates.add(tag)
                elif tagset == "EffectConditions":
                    pass  # TODO
                elif tagset == "ChangeSubjectTo":
                    pass  # TODO REMOVE THIS TAGSET
                else:
                    raise Exception('Unknown tagset encountered: {}'.format(tagset))

    def _init_reify_production_rules(self, production_rules_specification):
        """Instantiate ProductionRule objects for the rules specified in production_rules_specification."""
        production_rule_objects = []
        for rule_specification in production_rules_specification:
            body = rule_specification['expansion']
            application_rate = rule_specification['app_rate']
            production_rule_objects.append(
                ProductionRule(head=self, body_specification=body, application_rate=application_rate)
            )
        return production_rule_objects

    @property
    def all_markup(self):
        """Return all the annotations attributed to this symbol."""
        all_markup = (
            self.preconditions | self.conditional_violations | self.propositions |
            self.context_updates | self.moves | self.speaker_obligations_pushed |
            self.interlocutor_obligations_pushed | self.topics_pushed | self.topics_addressed
        )
        return list(all_markup)

    def currently_violated(self, conversation):
        """Return whether this symbol is currently violated, i.e., whether it has an unsatisfied
        precondition or would incur a conversational violation if deployed at this time."""
        if conversation.speaker.player:  # Let the player say anything currently, i.e., return False
            return False
        if (self.conversational_violations(conversation=conversation) or
                not self.preconditions_satisfied(conversation=conversation)):
            if conversation.productionist.debug:
                # Express why the symbol is currently violated
                print "Symbol {} is currently violated".format(self)
                conversational_violations = self.conversational_violations(conversation=conversation)
                for conversational_violation in conversational_violations:
                    print '\t{}'.format(conversational_violation)
                unsatisfied_preconditions = (
                    p for p in self.preconditions if p.evaluate(conversation=conversation) is False
                )
                for unsatisfied_precondition in unsatisfied_preconditions:
                    print '\t{}'.format(unsatisfied_precondition)
            return True
        # Symbol is not currently violated, so return False
        return False

    def preconditions_satisfied(self, conversation):
        """Return whether this line's preconditions are satisfied given the state of the world."""
        return all(precondition.evaluate(conversation=conversation) for precondition in self.preconditions)

    def conversational_violations(self, conversation):
        """Return a list of names of conversational violations that will be incurred if this line is deployed now."""
        violations_incurred = [
            potential_violation.name for potential_violation in self.conditional_violations if
            potential_violation.evaluate(conversation=conversation)
        ]
        return violations_incurred

    def produce_all_derivation_traces_for_lstm_training_data(self, omit_derivation_snippets=False):
        """Return all terminal derivations of this symbol in the format specified for LSTM training.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{`Hi~}^` ~^interlocutor|first|name{`[speaker.belief(interlocutor, 'first name')]~}^`.~}
        for the terminal derivation "Hi, [speaker.belief(interlocutor, 'first name')]."
        """
        if not self.all_derivation_traces:
            all_terminal_derivations_in_lstm_training_data_format = []
            for rule in self.production_rules:
                all_terminal_derivations_in_lstm_training_data_format += (
                    rule.produce_all_derivation_traces_for_lstm_training_data(
                        omit_derivation_snippets=omit_derivation_snippets
                    )
                )
            self.all_derivation_traces = all_terminal_derivations_in_lstm_training_data_format
        return self.all_derivation_traces

    def produce_all_terminal_derivations_for_lstm_training(self):
        """Exhaustively produce all terminal derivations of this symbol for use as part of the LSTM training data."""
        if not self.all_terminal_derivations:
            all_terminal_derivations = []
            for rule in self.production_rules:
                all_terminal_derivations += rule.produce_all_terminal_derivations_for_lstm_training()
            self.all_terminal_derivations = all_terminal_derivations
        return self.all_terminal_derivations


class ProductionRule(object):
    """A production rule in a production system for in-game dialogue generation."""

    def __init__(self, head, body_specification, application_rate):
        """Initialize a ProductionRule object.

        'head' is a nonterminal symbol constituting the left-hand side of this rule, while
        'body' is a sequence of symbols that this rule may be used to expand the head into.
        """
        self.head = head
        self.body = None  # Gets set by Productionist._init_resolve_symbol_references_in_a_rule_body()
        self.body_specification = body_specification
        self.body_specification_str = ''.join(body_specification)
        self.application_rate = application_rate
        # This attribute will mark whether this production rule successfully fired during the
        # backward-chaining routine of a generation procedure; we keep track of this because
        # after we have successfully terminally backward-chained and forward-chained, we need
        # to remember the rules on those chains in order to construct the final dialogue template
        self.viable = False

    def __str__(self):
        """Return string representation."""
        return '{} --> {}'.format(self.head, self.body_specification_str)

    def produce_all_derivation_traces_for_lstm_training_data(self, omit_derivation_snippets=False):
        """Return all terminal derivations yielded by this rule in the format specified for LSTM training.

        LSTM stands for long short-term memory, which is a variant of deep learning that
        James and Adam Summerville are going to explore using as a way of mapping
        arbitrary player inputs to symbolic traces in an Expressionist grammar, which
        would allow us to attribute dialogue moves, etc., to the arbitrary player inputs.

        The format we have settled on for LSTM training expresses traces for terminal derivations, e.g.,
        greet{greeting|word{`Hi~}^` ~^interlocutor|first|name{`[speaker.belief(interlocutor, 'first name')]~}^`.~}
        for the terminal derivation "Hi, [speaker.belief(interlocutor, 'first name')]."
        """
        # Assemble the Cartesian product of all terminal derivations for all symbols in
        # this rule body; because nonterminal symbols are represented as a raw unicode string, we
        # can't call the same method for each symbol, so we just append the syntax for demarcating
        # them in the LSTM training-data format that we have devised; if omit_derivation_snippets ==
        # True, then we don't even include the terminal symbols
        if omit_derivation_snippets:
            cartesian_product_of_all_symbols_in_this_rule_body = itertools.product(*[
                symbol.produce_all_derivation_traces_for_lstm_training_data(
                    omit_derivation_snippets=omit_derivation_snippets
                )
                for symbol in self.body if type(symbol) is not unicode
            ])
        else:
            cartesian_product_of_all_symbols_in_this_rule_body = itertools.product(*[
                ['`{}~'.format(symbol)] if type(symbol) is unicode else
                symbol.produce_all_derivation_traces_for_lstm_training_data(
                    omit_derivation_snippets=omit_derivation_snippets
                )
                for symbol in self.body
            ])
        # Now concatenate these and prepend them with syntax indicating which nonterminal symbol
        # is the head of this rule; this will produce derivation traces in the format we want them in
        all_terminal_derivations_in_lstm_training_data_format = []
        for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body:
            trace_in_the_lstm_format = "{head}{{{partial_trace}}}".format(
                head='|'.join(self.head.tag.split()),
                partial_trace='^'.join(cartesian_product)
            )
            all_terminal_derivations_in_lstm_training_data_format.append(trace_in_the_lstm_format)
        return all_terminal_derivations_in_lstm_training_data_format

    def produce_all_terminal_derivations_for_lstm_training(self):
        """Exhaustively produce all terminal derivations yielded by this rule for use as LSTM training data."""
        # Assemble the Cartesian product of all terminal derivations for all symbols in
        # this rule body; because nonterminal symbols are represented as a raw unicode string, we
        # can't call the same method for each symbol
        cartesian_product_of_all_symbols_in_this_rule_body = itertools.product(*[
            [symbol] if type(symbol) is unicode else symbol.produce_all_terminal_derivations_for_lstm_training()
            for symbol in self.body
        ])
        # Now concatenate these to produce actual terminal derivations
        all_terminal_derivations = []
        for cartesian_product in cartesian_product_of_all_symbols_in_this_rule_body:
            terminal_derivation = ''.join(cartesian_product)
            all_terminal_derivations.append(terminal_derivation)
        return all_terminal_derivations


class LineOfDialogue(object):
    """A line of dialogue that may be used during a conversation."""

    def __init__(self, raw_line, symbols_expanded_to_produce_this_template, conversation):
        """Initialize a LineOfDialogue object."""
        self.raw_line = raw_line
        self.symbols = symbols_expanded_to_produce_this_template
        self.template = self._init_prepare_template(raw_line=raw_line)
        # Prepare annotation attributes
        self.conversational_violations = set()
        self.propositions = set()
        self.moves = set()  # The dialogue moves constituted by the delivery of this line
        self.speaker_obligations_pushed = set()  # Line asserts speaker conversational obligations
        self.interlocutor_obligations_pushed = set()  # Line asserts interlocutor conversational obligations
        self.topics_pushed = set()  # Line introduces a new topic of conversation
        self.topics_addressed = set()  # Line addresses a topic of conversation
        self.clear_subject_of_conversation = False  # Line clears subject of conversation to allow asserting a new one
        self.force_speaker_subject_match_to_speaker_preoccupation = False  # Line forces a speaker subject match
        self.context_updates = set()  # Line updates the conversational context, e.g., the subject of conversation
        self._init_inherit_markup(conversation=conversation)

    def __str__(self):
        """Return the raw template characterizing this line of dialogue."""
        return self.raw_line

    @staticmethod
    def _init_prepare_template(raw_line):
        """Prepare a templated line of dialogue from a raw specification for one.

        The template returned by this method will specifically be an ordered list
        of StaticElement and Gap objects, the latter of which will be filled in
        according to
        """
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

    def _init_inherit_markup(self, conversation):
        """Inherit the mark-up of all the symbols that were expanded in the construction of this dialogue template."""
        for symbol in self.symbols:
            self.conversational_violations |= set(symbol.conversational_violations(conversation=conversation))
            self.propositions |= symbol.propositions
            self.moves |= symbol.moves
            self.speaker_obligations_pushed |= symbol.speaker_obligations_pushed
            self.interlocutor_obligations_pushed |= symbol.interlocutor_obligations_pushed
            self.topics_pushed |= symbol.topics_pushed
            self.topics_addressed |= symbol.topics_addressed
            self.clear_subject_of_conversation = symbol.clear_subject_of_conversation
            self.force_speaker_subject_match_to_speaker_preoccupation = (
                symbol.force_speaker_subject_match_to_speaker_preoccupation
            )
            self.context_updates |= symbol.context_updates

    def realize(self, conversation_turn):
        """Return a filled-in template according to the world state during the current conversation turn."""
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
        conversation, speaker, interlocutor, subject = (
            conversation_turn.conversation,
            conversation_turn.speaker, conversation_turn.interlocutor,
            conversation_turn.subject.matches[conversation_turn.speaker]
        )
        return str(eval(self.specification))


class Condition(object):
    """A condition super class that is inherited from by Precondition and ViolationCondition."""

    def __init__(self, condition):
        """Initialize a Condition object."""
        self.condition = condition
        self.test = eval(condition)  # The condition is literally a lambda function
        self.arguments = self._init_parse_condition_for_its_arguments(condition=condition)

    @staticmethod
    def _init_parse_condition_for_its_arguments(condition):
        """Parse this condition's specification (a lambda function) to gather the arguments that it requires."""
        index_of_end_of_arguments = condition.index(':')
        arguments = condition[:index_of_end_of_arguments]
        arguments = arguments[len('lambda '):]  # Excise 'lambda ' prefix
        arguments = arguments.split(', ')
        return arguments

    def evaluate(self, conversation):
        """Evaluate this condition given the state of the world at the beginning of a conversation turn."""
        # If the current speaker is a human player, don't even worry about
        # evaluating preconditions, i.e., let them say whatever
        if conversation.speaker.player:
            return True
        # Instantiate all the arguments we might need as local variables
        speaker = conversation.speaker
        interlocutor = conversation.interlocutor
        subject = conversation.subject.matches[conversation.speaker]
        # Prepare the list of arguments by evaluating to bind them to the needed local variables
        realized_arguments = [eval(argument) for argument in self.arguments]
        # Return a boolean indicating whether this precondition is satisfied
        try:
            return self.test(*realized_arguments)
        except (ValueError, AttributeError):
            raise Exception('Cannot evaluate the precondition {}'.format(self.condition))


class Precondition(Condition):
    """A precondition for expanding a symbol to generate a line of dialogue."""

    def __init__(self, tag):
        """Initialize a Precondition object."""
        super(Precondition, self).__init__(condition=tag)

    def __str__(self):
        """Return a string specifying the lambda function itself."""
        return self.condition


class ConditionalViolation(Condition):
    """A conversational violation that may be incurred, pending the evaluation of its conditions,
    if a symbol is expanded to generate a line of dialogue.
    """

    def __init__(self, tag):
        """Initialize a ConditionalViolation object."""
        self.name, condition = tag.split('<--')
        super(ConditionalViolation, self).__init__(condition=condition)

    def __str__(self):
        """Return string representation."""
        return '{} <-- {}'.format(self.name, self.condition)