import random


class Grammar:
    def __init__(self):
        self.VN = {'S', 'R', 'L'}
        self.VT = {'a', 'b', 'c', 'd', 'e', 'f'}
        self.P = {
            'S': ['aS', 'bS', 'cR', 'dL'],
            'R': ['dL', 'e'],
            'L': ['fL', 'eL', 'd']
        }
        self.start_symbol = 'S'

    def generate_string_with_derivation(self, max_length=10):
        def generate_helper(symbol, current_length, derivation_so_far):
            if current_length >= max_length:
                return None, None

            if symbol in self.VT:
                return symbol, []

            productions = self.P.get(symbol, [])
            if not productions:
                return None, None

            production = random.choice(productions)
            result = ''
            derivation_steps = [f"{symbol}→{production}"]

            for s in production:
                part_string, part_derivation = generate_helper(s, current_length + len(result),
                                                               derivation_so_far + derivation_steps)
                if part_string is None:
                    return None, None
                result += part_string
                derivation_steps.extend(part_derivation)

            return result, derivation_steps

        string, derivation = generate_helper(self.start_symbol, 0, [])
        if string is None:
            return None, None
        return string, ' '.join(derivation)

    def generate_strings_with_derivation(self, count=5, max_length=10):
        strings = []
        derivations = []
        attempts = 0
        max_attempts = count * 10

        while len(strings) < count and attempts < max_attempts:
            string, derivation = self.generate_string_with_derivation(max_length)
            if string and len(string) <= max_length:
                strings.append(string)
                derivations.append(derivation)
            attempts += 1

        return strings, derivations

    def classify_grammar(self):
        is_type_3 = True
        is_type_2 = True
        is_type_1 = True

        for lhs, rhs_list in self.P.items():
            for rhs in rhs_list:
                # Check if the grammar is not Type 3
                if not (len(rhs) == 1 and rhs in self.VT) and not (len(rhs) == 2 and rhs[0] in self.VT and rhs[1] in self.VN):
                    is_type_3 = False

                # Check if the grammar is not Type 2
                if not (len(lhs) == 1 and lhs in self.VN):
                    is_type_2 = False

                # Check if the grammar is not Type 1
                if not (len(lhs) <= len(rhs)):
                    is_type_1 = False

        if is_type_3:
            return "Type 3 (Regular Grammar)"
        elif is_type_2:
            return "Type 2 (Context-Free Grammar)"
        elif is_type_1:
            return "Type 1 (Context-Sensitive Grammar)"
        else:
            return "Type 0 (Unrestricted Grammar)"


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def accepts(self, input_string):
        current_states = {self.start_state}

        current_states = self._epsilon_closure(current_states)

        for symbol in input_string:
            if not current_states:
                return False

            next_states = set()
            for state in current_states:
                if (state, symbol) in self.transitions:
                    next_states.update(self.transitions[(state, symbol)])

            current_states = self._epsilon_closure(next_states)

        return bool(current_states & self.accept_states)

    def _epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            if (state, '') in self.transitions:
                for next_state in self.transitions[(state, '')]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return closure


def grammar_to_fa(grammar):
    states = grammar.VN | {'accept'}
    alphabet = grammar.VT
    transitions = {}
    start_state = grammar.start_symbol
    accept_states = {'accept'}

    for non_terminal, productions in grammar.P.items():
        for production in productions:
            if len(production) == 1:
                if production in grammar.VT:
                    if (non_terminal, production) not in transitions:
                        transitions[(non_terminal, production)] = set()
                    transitions[(non_terminal, production)].add('accept')
            else:
                current = non_terminal
                for i, symbol in enumerate(production):
                    if symbol in grammar.VT:
                        if i == len(production) - 1:
                            if (current, symbol) not in transitions:
                                transitions[(current, symbol)] = set()
                            transitions[(current, symbol)].add('accept')
                        else:
                            new_state = f"{production[i + 1]}"
                            if (current, symbol) not in transitions:
                                transitions[(current, symbol)] = set()
                            transitions[(current, symbol)].add(new_state)
                            current = new_state
                    else:
                        if (current, '') not in transitions:
                            transitions[(current, '')] = set()
                        transitions[(current, '')].add(symbol)
                        current = symbol

    return FiniteAutomaton(states, alphabet, transitions, start_state, accept_states)


if __name__ == "__main__":
    grammar = Grammar()
    valid_strings, derivations = grammar.generate_strings_with_derivation(5)

    print("The generated strings:")
    for string, derivation in zip(valid_strings, derivations):
        print(f"String: {string}, Derivation: {derivation}")

    fa = grammar_to_fa(grammar)

    print("\nTesting strings:")
    test_strings = [
        "ce",
        "dd",
        "abc",
        "cde",
        "fff"
    ]

    for test_string in test_strings:
        is_accepted = fa.accepts(test_string)
        result = "correct" if is_accepted else "wrong"
        print(f"String {test_string} is {result}")

    print("\nGrammar Classification:")
    print(grammar.classify_grammar())