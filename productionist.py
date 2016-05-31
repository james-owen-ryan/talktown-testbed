import json
import random


class Productionist(object):
    """A production system for in-game natural language generation from an Expressionist grammar.

    Objects of this class operate over a probabilistic context-free generative grammar exported by
    Expressionist according to requests originating from a game system. As such, it can be thought of
    as an interface between the game engine and an Expressionist grammar.

    Subclasses inherit the base functionality of this class, but instantiate their own nuances
    pertaining to the specific generation tasks that they carry out (e.g., dialogue generation
    vs. thought generation). Most often, these concerns will bear out in the specific mark-up
    including in the Expressionist grammars that they operate over.
    """

    def __init__(self, game, debug=False):
        """Initialize a Productionist object."""
        self.game = game
        self.debug = debug
        if self.__class__ is DialogueGenerator:
            path_to_json_grammar_specification = game.config.path_to_dialogue_nlg_json_grammar_specification
        else:
            path_to_json_grammar_specification = game.config.path_to_thought_nlg_json_grammar_specification
        self.nonterminal_symbols = self._init_parse_json_grammar_specification(
            path_to_json_grammar_specification=path_to_json_grammar_specification
        )
        self._init_resolve_symbol_references_in_all_production_rule_bodies()
        self._init_attribute_backward_chaining_and_forward_chaining_rules_to_symbols()
        # This method is used to collect all the nonterminal symbols that were expanded
        # in the production of a terminal derivation, which reified LineOfDialogue and
        # Thought objects will need in order to inherit all the mark-up of these symbols
        self.symbols_expanded_to_produce_the_terminal_derivation = set()

    def _init_parse_json_grammar_specification(self, path_to_json_grammar_specification):
        """Parse a JSON grammar specification exported by Expressionist to instantiate symbols and rules."""
        # Parse the JSON specification to build a dictionary data structure
        symbol_objects = []
        grammar_dictionary = json.loads(open(path_to_json_grammar_specification).read())
        nonterminal_symbol_specifications = grammar_dictionary['nonterminals']
        for tag, nonterminal_symbol_specification in nonterminal_symbol_specifications.iteritems():
            top_level = nonterminal_symbol_specification['deep']
            production_rules_specification = nonterminal_symbol_specification['rules']
            raw_markup = nonterminal_symbol_specification['markup']
            nonterminal_symbol_class_to_use = (
                DialogueNonterminalSymbol if self.__class__ is DialogueGenerator else ThoughtNonterminalSymbol
            )
            symbol_object = nonterminal_symbol_class_to_use(
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
                if isinstance(symbol, NonterminalSymbol):
                    symbol.backward_chaining_rules.append(rule)

    def target_markup(self, markup_lambda_expression, symbol_sort_evaluation_function, state, rule_evaluation_metric):
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

        @param markup_lambda_expression: A lambda expression whose sole argument is a nonterminal symbol and
                                         that returns True if the nonterminal symbol has the desired markup.
        @param symbol_sort_evaluation_function: A lambda expression that can be used for the 'key' keyword argument
                                              in the call to sort a list of viable nonterminal symbols (i.e., ones
                                              that have the desired markup). This allows us to iterate over viable
                                              symbols in order of appeal.
        @param state: An object representing the state that symbol preconditions should be checked against in
                      order to potentially expand the given symbol.
        @param rule_evaluation_metric: A lambda expression that determines the probability of application associated
                                        with each of a symbol's production rules; this allows us to probabilistically
                                        target production rules when we're doing forward- and backward-chaining
        """
        # Collect all satisficing symbols, i.e., ones have the desired markup and
        # thus satisfy the  given markup_lambda_expression
        satisficing_symbols = [s for s in self.nonterminal_symbols if markup_lambda_expression(s)]
        # Randomly shuffle these symbols, which will mean that ties in the sort we are about
        # to do will be ordered differently across different generation instances
        random.shuffle(satisficing_symbols)
        # Sort this list according to the given symbol_sort_lambda_expression (for
        # dialogue, this will be simply produce a random sort)
        satisficing_symbols.sort(key=lambda ss: symbol_sort_evaluation_function(ss), reverse=True)
        # Iteratively attempt to successfully build a line of dialogue by backward-chaining
        # and forward-chaining from this symbol
        for symbol in satisficing_symbols:
            raw_derivation_built_by_targeting_this_symbol = self._target_symbol(
                symbol=symbol, state=state, rule_evaluation_metric=rule_evaluation_metric
            )
            if raw_derivation_built_by_targeting_this_symbol:  # Will be None if targeting was unsuccessful
                return raw_derivation_built_by_targeting_this_symbol
            self._reset_temporary_attributes()
        if self.debug:
            print "Productionist could not generate a derivation satisfying the expression {}".format(
                markup_lambda_expression
            )

    def _target_symbol(self, symbol, state, rule_evaluation_metric):
        """Attempt to successfully terminally backward-chain and forward-chain from this symbol.

        If successful, this method will return a LineOfDialogue object, which is a templated
        line of dialogue that may be filled in and deployed during a conversation. If this
        method fails at any point, it will immediately return None.
        """
        if self.debug:
            print "Targeting symbol {}...".format(symbol)
        # Attempt forward chaining first
        partial_raw_template_built_by_forward_chaining = self._forward_chain_from_symbol(
            symbol=symbol, state=state, rule_evaluation_metric=rule_evaluation_metric,
            symbol_is_the_targeted_symbol=True
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
            top_level_symbol_that_we_successfully_backward_chained_to = self._backward_chain_from_symbol(
                symbol=symbol, state=state, rule_evaluation_metric=rule_evaluation_metric
            )
            if not top_level_symbol_that_we_successfully_backward_chained_to:
                return None
        complete_raw_template = self._retrace_backward_and_forward_chains_to_generate_a_complete_template(
            start_symbol=top_level_symbol_that_we_successfully_backward_chained_to,
            state=state, rule_evaluation_metric=rule_evaluation_metric
        )
        return complete_raw_template

    def _forward_chain_from_symbol(self, symbol, state, rule_evaluation_metric, retracing_chains=False,
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
        if symbol.currently_violated(state=state):
            return None
        candidate_production_rules = symbol.forward_chaining_rules
        # If one of these production rules is already known to be on a chain, we can just pick
        # that one mindlessly, since we already know that's the route to go
        try:
            rule_on_our_chain = next(r for r in candidate_production_rules if r.viable)
            return self._target_production_rule(
                rule=rule_on_our_chain, state=state, rule_evaluation_metric=rule_evaluation_metric,
                retracing_chains=retracing_chains
            )
        except StopIteration:
            pass
        # Sort the candidate production rules probabilistically by utilizing their application rates
        candidate_production_rules = self._probabilistically_sort_production_rules(
            rules=candidate_production_rules, rule_evaluation_metric=rule_evaluation_metric
        )
        # Iterate over these rules, attempting to utilize them successfully; return
        # a template snippet if a rule may be utilized successfully
        for production_rule in candidate_production_rules:
            terminal_expansion_yielded_by_firing_that_production_rule = self._target_production_rule(
                rule=production_rule, state=state, rule_evaluation_metric=rule_evaluation_metric,
                retracing_chains=retracing_chains
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

    def _backward_chain_from_symbol(self, symbol, state, rule_evaluation_metric):
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
            if not symbol.currently_violated(state=state):
                if self.debug:
                    print "Reached top-level symbol {}, so backward chaining is done".format(symbol)
                return symbol
        candidate_production_rules = symbol.backward_chaining_rules
        # Sort the candidate production rules probabilistically by utilizing their application rates
        candidate_production_rules = self._probabilistically_sort_production_rules(
            rules=candidate_production_rules, rule_evaluation_metric=rule_evaluation_metric
        )
        for production_rule in candidate_production_rules:
            this_production_rule_successfully_fired = (
                self._target_production_rule(
                    rule=production_rule, state=state, rule_evaluation_metric=rule_evaluation_metric
                )
            )
            if this_production_rule_successfully_fired:
                production_rule.viable = True
                # Set breadcrumbs so that we can reconstruct our path if this backward chain
                # is successful (by 'reconstruct our path', I mean fire all the production rules
                # along our successful backward chain until we've generated a complete dialogue template)
                top_level_symbol_we_successfully_chained_back_to = (
                    self._backward_chain_from_symbol(
                        production_rule.head, state=state, rule_evaluation_metric=rule_evaluation_metric
                    )
                )
                if top_level_symbol_we_successfully_chained_back_to:
                    if self.debug:
                        print "Added production rule {} to the chain".format(production_rule)
                    return top_level_symbol_we_successfully_chained_back_to
        if self.debug:
            print "Failed to backward chain from symbol {}".format(symbol)
        return None

    def _retrace_backward_and_forward_chains_to_generate_a_complete_template(self, start_symbol, state,
                                                                             rule_evaluation_metric):
        """Retrace successfully terminal backward and forward chains to generate a complete dialogue template.

        In this method, we traverse the production-rule chains that we have already successfully
        discovered to generate a complete line of dialogue (and to accumulate all the mark-up that
        it will inherit from the symbols that are expanded along these chains).
        """
        self.symbols_expanded_to_produce_the_terminal_derivation = {start_symbol}
        if self.debug:
            print "Retraversing now from top-level symbol {}".format(start_symbol)
        first_breadcrumb = next(rule for rule in start_symbol.production_rules if rule.viable)
        return self._target_production_rule(
            rule=first_breadcrumb, state=state, retracing_chains=True, rule_evaluation_metric=rule_evaluation_metric
        )

    def _target_production_rule(self, rule, state, rule_evaluation_metric, retracing_chains=False):
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
                terminal_expansion_of_that_symbol = self._forward_chain_from_symbol(
                    symbol=symbol, state=state, retracing_chains=retracing_chains,
                    rule_evaluation_metric=rule_evaluation_metric
                )
                if terminal_expansion_of_that_symbol:
                    if retracing_chains:
                        self.symbols_expanded_to_produce_the_terminal_derivation.add(symbol)
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

    def _probabilistically_sort_production_rules(self, rules, rule_evaluation_metric):
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
            probabilistic_sort_of_this_head_group = self._probabilistically_sort_a_rule_head_group(
                rules=rules_sharing_this_head, rule_evaluation_metric=rule_evaluation_metric
            )
            probabilistic_sort += probabilistic_sort_of_this_head_group
        return probabilistic_sort

    def _probabilistically_sort_a_rule_head_group(self, rules, rule_evaluation_metric):
        """Probabilistically sort a collection of production rules that share the same rule head.

        This method works by fitting a probability range to each of the given set of rules, rolling
        a random number and selecting the rule whose range it falls within, and then repeating this
        on the set of remaining rules, and so forth until every rule has been selecting.
        """
        probabilistic_sort = []
        remaining_rules = list(rules)
        while len(remaining_rules) > 1:
            probability_ranges = self._fit_probability_distribution_to_rules_according_to_an_evaluation_metric(
                rules=remaining_rules, rule_evaluation_metric=rule_evaluation_metric
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
    def _fit_probability_distribution_to_rules_according_to_an_evaluation_metric(rules, rule_evaluation_metric):
        """Return a dictionary mapping each of the rules to a probability range.

        @param rules: The rules that this method will fit a probability distribution to.
        """
        # Determine the individual probabilities of each production rule, given our
        # rule evaluation metric
        individual_probabilities = {}
        sum_of_all_scores = float(sum(rule_evaluation_metric(rule) for rule in rules))
        for rule in rules:
            probability = rule_evaluation_metric(rule)/sum_of_all_scores
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
        self.symbols_expanded_to_produce_the_terminal_derivation = set()

    def find_symbol(self, symbol_name):
        """Return a symbol with the given name."""
        try:
            return next(s for s in self.nonterminal_symbols if s.tag == symbol_name)
        except StopIteration:
            print "I could not find a symbol with that name."


class NonterminalSymbol(object):
    """A symbol in a production system for in-game dialogue generation."""

    def __init__(self, tag, top_level, raw_markup, production_rules_specification):
        """Initialize a NonterminalSymbol object."""
        self.tag = tag
        # If a terminal expansion of this symbol constitutes a complete line of dialogue, then
        # this is a top-level symbol
        self.top_level = top_level
        # Reify production rules for expanding this symbol
        self.production_rules = self._init_reify_production_rules(production_rules_specification)
        # Prepare annotation sets that will be populated (as appropriate) by _init_parse_markup()
        self.preconditions = set()
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
        # Parse markup
        self._init_parse_markup(raw_markup=raw_markup)

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
                ProductionRule(head=self, body_specification=body, application_rate=application_rate)
            )
        return production_rule_objects

    def _init_parse_markup(self, raw_markup):
        """This method gets overwritten by subclasses to this class."""
        pass


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

    def evaluate(self, state):
        """Evaluate this condition given the state of the world at the beginning of a conversation turn."""
        # Use duck typing to check for whether this state capsule is a Conversation
        # object (in the case of dialogue generation) or a Person object (in the case
        # of thought generation)
        if state.__class__.__name__ is 'Conversation':
            # If the current speaker is a human player, don't even worry about
            # evaluating preconditions, i.e., let them say whatever
            if state.speaker.player:
                return True
            # Instantiate all the arguments we might need as local variables
            conversation = state
            speaker = state.speaker
            interlocutor = state.interlocutor
            subject = state.subject.matches[state.speaker]
        elif state.__class__.__name__ in ('Person', 'PersonExNihilo'):
            thinker = state
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


class StaticElement(object):
    """A static element in a templated terminal derivation."""

    def __init__(self, text):
        """Initialize a StaticElement object."""
        self.text = text

    def __str__(self):
        """Return the text of this static element."""
        return self.text

    def realize(self, state):
        """Realize a StaticElement object simply by returning its text."""
        return self.text


class Gap(object):
    """A gap in a templated terminal derivation."""

    def __init__(self, specification):
        """Initialize a Gap object."""
        self.specification = specification

    def __str__(self):
        """Return the specification for filling in this gap."""
        return self.specification

    def realize(self, state):
        """Fill in this gap according to the world state during a conversation turn."""
        # Use duck typing to check for whether this state capsule is a ConversationTurn
        # object (in the case of dialogue generation) or a Person object (in the case
        # of thought generation); then prepare local variables that will allow us to
        # fill in this gap
        if state.__class__.__name__ is 'Conversation':
            conversation, speaker, interlocutor, subject = (
                state,
                state.speaker, state.interlocutor,
                state.subject.matches[state.speaker]
            )
        elif state.__class__.__name__ in ('Person', 'PersonExNihilo'):
            thinker = state
        return str(eval(self.specification))


class DialogueGenerator(Productionist):
    """A subclass to Productionist that handles dialogue-specific concerns.

    For instance, this class affords the targeting of a generated line performing a
    specific dialogue move or addressing a specific topic of conversation.
    """

    def __init__(self, game):
        """Initialize a DialogueGenerator object."""
        super(DialogueGenerator, self).__init__(game)

    def target_dialogue_move(self, conversation, move_name):
        """Attempt to generate a line of dialogue that performs a dialogue move with the given name."""
        # Attempt to produce a raw derivation with the desired markup, i.e., that
        # it performs the given dialogue move
        raw_derivation_built_by_targeting_this_symbol = self.target_markup(
            markup_lambda_expression=lambda symbol: move_name in symbol.moves,
            symbol_sort_evaluation_function=lambda symbol: random.random(),
            state=conversation, rule_evaluation_metric=lambda rule: rule.application_rate
        )
        # Reify the template as a LineOfDialogue object and return that
        line_of_dialogue_object = LineOfDialogue(
            raw_template=raw_derivation_built_by_targeting_this_symbol,
            symbols_expanded_to_produce_this_template=self.symbols_expanded_to_produce_the_terminal_derivation,
            conversation=conversation
        )
        # Reset any temporary attributes that we utilized during this generation procedure
        self._reset_temporary_attributes()
        return line_of_dialogue_object

    def target_topics_of_conversation(self, conversation, topic_names):
        """Attempt to generate a line of dialogue that addresses a topic with the given name.

        @param conversation: The conversation in which the requested generated line will be delivered.
        @param topic_names: A set of names of topics of conversation, at least one which the requested
                            generated line should address.
        """
        # Attempt to produce a raw derivation with the desired markup, i.e., that
        # it performs the given dialogue move
        raw_derivation_built_by_targeting_this_symbol = self.target_markup(
            markup_lambda_expression=lambda symbol: topic_names & symbol.topics_addressed,
            symbol_sort_evaluation_function=lambda symbol: random.random(),
            state=conversation, rule_evaluation_metric=lambda rule: rule.application_rate
        )
        # Reify the template as a LineOfDialogue object and return that
        line_of_dialogue_object = LineOfDialogue(
            raw_template=raw_derivation_built_by_targeting_this_symbol,
            symbols_expanded_to_produce_this_template=self.symbols_expanded_to_produce_the_terminal_derivation,
            conversation=conversation
        )
        # Reset any temporary attributes that we utilized during this generation procedure
        self._reset_temporary_attributes()
        return line_of_dialogue_object


class DialogueNonterminalSymbol(NonterminalSymbol):
    """A subclass of NonterminalSymbol that pertains specifically to dialogue concerns."""

    def __init__(self, tag, top_level, raw_markup, production_rules_specification):
        """Initialize a DialogueNonterminalSymbol object."""
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
        super(DialogueNonterminalSymbol, self).__init__(tag, top_level, raw_markup, production_rules_specification)

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
                elif tagset == "UserStudyQueryArguments":
                    pass  # This one is currently only used for producing training data
                else:
                    raise Exception('Unknown tagset encountered: {}'.format(tagset))

    @property
    def all_markup(self):
        """Return all the annotations attributed to this symbol."""
        all_markup = (
            self.preconditions | self.conditional_violations | self.propositions |
            self.context_updates | self.moves | self.speaker_obligations_pushed |
            self.interlocutor_obligations_pushed | self.topics_pushed | self.topics_addressed
        )
        return list(all_markup)

    def currently_violated(self, state):
        """Return whether this symbol is currently violated, i.e., whether it has an unsatisfied
        precondition or would incur a conversational violation if deployed at this time."""
        if state.speaker.player:  # Let the player say anything currently, i.e., return False
            return False
        if (self.conversational_violations(conversation=state) or
                not self.preconditions_satisfied(conversation=state)):
            if state.productionist.debug:
                # Express why the symbol is currently violated
                print "Symbol {} is currently violated".format(self)
                conversational_violations = self.conversational_violations(conversation=state)
                for conversational_violation in conversational_violations:
                    print '\t{}'.format(conversational_violation)
                unsatisfied_preconditions = (
                    p for p in self.preconditions if p.evaluate(state=state) is False
                )
                for unsatisfied_precondition in unsatisfied_preconditions:
                    print '\t{}'.format(unsatisfied_precondition)
            return True
        # Symbol is not currently violated, so return False
        return False

    def preconditions_satisfied(self, conversation):
        """Return whether this line's preconditions are satisfied given the state of the world."""
        return all(precondition.evaluate(state=conversation) for precondition in self.preconditions)

    def conversational_violations(self, conversation):
        """Return a list of names of conversational violations that will be incurred if this line is deployed now."""
        violations_incurred = [
            potential_violation.name for potential_violation in self.conditional_violations if
            potential_violation.evaluate(state=conversation)
            ]
        return violations_incurred


class LineOfDialogue(object):
    """A line of dialogue that may be used during a conversation."""

    def __init__(self, raw_template, symbols_expanded_to_produce_this_template, conversation):
        """Initialize a LineOfDialogue object."""
        self.raw_template = raw_template
        self.nonterminal_symbols = symbols_expanded_to_produce_this_template
        self.template = self._init_prepare_template(raw_line=raw_template)
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
        return self.raw_template

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
        for symbol in self.nonterminal_symbols:
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

    def realize(self, conversation):
        """Return a filled-in template according to the world state during the current conversation turn."""
        return ''.join(element.realize(state=conversation) for element in self.template)


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


        ###################
        # THOUGHT CLASSES #
        ###################


class ThoughtGenerator(Productionist):
    """A subclass to Productionist that handles thought-specific concerns.

    For instance, this class affords the targeting of a generated thought that is elicited
    by a set of symbol stimuli encountered by a character going about the world.
    """

    def __init__(self, game):
        """Initialize a ThoughtGenerator object."""
        # These are set as needed by target_association() to hold temporary information
        self.thinker = None
        self.stimuli = {}
        self.nonrepeatable_symbols = set()
        super(ThoughtGenerator, self).__init__(game)

    def target_association(self, thinker, stimuli):
        """Attempt to generate a line of dialogue that performs a dialogue move with the given name."""
        if self.debug:
            print "Attempting to elicit thought given the stimuli: {stimuli}...".format(
                stimuli=', '.join("{signal} ({strength})".format(
                    signal=signal, strength=strength) for signal, strength in stimuli.iteritems()
                )
            )
        self.thinker = thinker
        self.stimuli = stimuli
        self.nonrepeatable_symbols = self._collect_nonrepeatable_symbols()
        markup_lambda_expression = (
            lambda symbol: {pair[0] for pair in symbol.signals} & {pair[0] for pair in self.stimuli.iteritems()}
        )
        # Attempt to produce a raw derivation with the desired markup, i.e., one that has
        # a good matching between the symbols associated with it and the stimuli (i.e., the
        # weighted_symbol_set)
        raw_derivation_built_by_targeting_this_symbol = self.target_markup(
            markup_lambda_expression=markup_lambda_expression,
            symbol_sort_evaluation_function=self.evaluate_nonterminal_symbol,
            state=thinker,
            rule_evaluation_metric=self.evaluate_production_rule
        )
        # Reify the template as a Thought object and return that
        thought_object = Thought(
            raw_template=raw_derivation_built_by_targeting_this_symbol,
            symbols_expanded_to_produce_this_template=self.symbols_expanded_to_produce_the_terminal_derivation,
            thinker=thinker
        )
        # Reset any temporary attributes that we utilized during this generation procedure
        self._reset_temporary_attributes()
        return thought_object

    def _collect_nonrepeatable_symbols(self):
        """Collect all nonterminal symbols that cannot be expanded during this generation instance (because
        that would produce awkward repetition.
        """
        nonrepeatable_symbols_recently_expanded_by_thinker = set()
        for recent_thought in self.thinker.mind.recent_thoughts:
            for symbol in recent_thought.nonterminal_symbols:
                if symbol.nonrepeatable:
                    nonrepeatable_symbols_recently_expanded_by_thinker.add(symbol)
        return nonrepeatable_symbols_recently_expanded_by_thinker

    def evaluate_nonterminal_symbol(self, nonterminal_symbol):
        """Score a nonterminal symbol for the strength of its association with a set of stimuli."""
        config = self.game.config
        score = 0
        for stimulus_signal, stimulus_signal_weight in self.stimuli.iteritems():
            for symbol_signal, _ in nonterminal_symbol.signals:  # _ stands for symbol_signal_weight (now ignored)
                # Reward for matching signals (commensurately to the weight for that
                # signal that is packaged up in the stimuli)
                if stimulus_signal == symbol_signal:
                    score += stimulus_signal_weight
                # Penalize for all stimulus signals that are not associated with the
                # nonterminal symbol (but not vice versa)
                if not any(s for s in nonterminal_symbol.signals if stimulus_signal == s[0]):
                    score -= stimulus_signal_weight
                # Penalize for symbol having already been expanded by this person to
                # produce a recent thought
                if nonterminal_symbol in self.nonrepeatable_symbols:
                    score -= config.penalty_for_expanding_nonrepeatable_symbol_in_thought
        return score

    def evaluate_production_rule(self, rule):
        """Score a production rule for the strength of its association with a set of stimuli."""
        # Determine the score according to the associational strength of the symbols in its body
        score = sum(0 if type(s) is unicode else self.evaluate_nonterminal_symbol(s) for s in rule.body)
        return score


class ThoughtNonterminalSymbol(NonterminalSymbol):
    """A subclass of NonterminalSymbol that pertains specifically to thought concerns."""

    def __init__(self, tag, top_level, raw_markup, production_rules_specification):
        """Initialize a DialogueNonterminalSymbol object."""
        self.signals = []  # A list of (signal, weight) tuples
        self.effects = set()
        super(ThoughtNonterminalSymbol, self).__init__(tag, top_level, raw_markup, production_rules_specification)

    def _init_parse_markup(self, raw_markup):
        """Instantiate and attribute objects for the annotations attributed to this symbol."""
        for tagset in raw_markup:
            for tag in raw_markup[tagset]:
                if tagset == "precondition":
                    self.preconditions.add(Precondition(tag=tag))
                elif tagset == "signal":
                    symbol, weight = tag.split()
                    weight = float(weight)
                    symbol_weight_tuple = (symbol, weight)
                    self.signals.append(symbol_weight_tuple)
                elif tagset == "effect":
                    self.effects.add(tag)
                else:
                    raise Exception('Unknown tagset encountered: {}'.format(tagset))

    @property
    def all_markup(self):
        """Return all the annotations attributed to this symbol."""
        all_markup = self.preconditions | self.signals | self.effects
        return list(all_markup)

    def currently_violated(self, state):
        """Return whether this symbol is currently violated, i.e., whether it has an unsatisfied
        precondition or would incur a conversational violation if deployed at this time."""
        return not self.preconditions_satisfied(thinker=state)

    def preconditions_satisfied(self, thinker):
        """Return whether this line's preconditions are satisfied given the state of the world."""
        return all(precondition.evaluate(state=thinker) for precondition in self.preconditions)


class Thought(object):
    """A thought that may enter the mind of a character."""

    def __init__(self, raw_template, symbols_expanded_to_produce_this_template, thinker):
        """Initialize a Thought object."""
        self.thinker = thinker
        self.raw_template = raw_template
        self.nonterminal_symbols = symbols_expanded_to_produce_this_template
        self.template = self._init_prepare_template(raw_line=raw_template)
        # Prepare annotation attributes
        self.signals = {}  # A dictionary mapping signal names to their strengths
        self.effects = set()
        self._init_inherit_markup()

    def __str__(self):
        """Return string representation."""
        return 'A thought ("{raw_template}"), produced in the mind of {owner}'.format(
            raw_template=self.raw_template,
            owner=self.thinker.name,
            # date=self.thinker.game.date[0].lower() + self.thinker.game.date[1:]
        )

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

    def _init_inherit_markup(self):
        """Inherit the mark-up of all the symbols that were expanded in the construction of this dialogue template."""
        config = self.thinker.game.config
        for symbol in self.nonterminal_symbols:
            self.effects |= symbol.effects
            for signal, strength in symbol.signals:
                signal = self.evaluate_runtime_signal(signal=signal)
                if signal not in self.signals:
                    self.signals[signal] = 0
                self.signals[signal] += config.strength_increase_to_thought_signal_for_nonterminal_signal_annotation
            # JOR 05-17-16: THIS WAS THE ORIGINAL FINAL LINE FOR ACTUALLY TOTALLING UP THE SIGNAL SCORES
            # BY TALLYING THE ANNOTATIONS FOR EACH NONTERMINAL SYMBOL EXPANDED TO PRODUCE THIS THOUGHT
            #     self.signals[signal] += strength

    def evaluate_runtime_signal(self, signal):
        """Evaluate a runtime signal, e.g., '[id(thinker.boss)]'."""
        thinker = self.thinker  # Needed to evaluate the signal, if it's truly a runtime signal
        try:
            return str(eval(signal))
        except NameError:  # It's not a runtime variable, but just a regular string, so return that
            return signal

    def realize(self):
        """Return a filled-in template according to the world state during the current conversation turn."""
        return ''.join(element.realize(state=self.thinker) for element in self.template)

    def execute(self):
        """Register the effects of this thought on its thinker."""
        # Update voltages of the signal receptors in the thinker's mind (this makes signals
        # associated with this thought more salient to the thinker merely by virtue of the thinker
        # having thunk this thought)
        self.thinker.mind.update_receptor_voltages_and_synapse_weights(voltage_updates=self.signals)
        # Execute the literal effects associated with this thought
        for effect in self.effects:
            effect(thinker=self.thinker)()
