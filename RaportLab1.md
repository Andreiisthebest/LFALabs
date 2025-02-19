
# Intro to formal languages. Regular grammars. Finite Automata.

### Course: Formal Languages & Finite Automata
### Author: Bobeica Andrei
### Variant: 2

----

## Theory
A formal language consists of an alphabet, a vocabulary, and a grammar.
The grammar defines the rules for constructing valid words in the language, and the automaton defines a mechanism for recognizing strings belonging to the language.
This project explores the relationship between regular grammars and finite automata by converting a given grammar into a finite automaton and checking if a string belongs to the language defined by the grammar.
A finite automaton (FA) is a state machine with a finite number of states that processes input strings one symbol at a time, transitioning between states based on predefined rules.


## Objectives:

* Implement a Grammar class to represent a given grammar.
* Implement a Finite Automaton (FA) class to convert the grammar to an automaton.
* Implement a method to generate valid strings from the grammar.
* Implement functionality to check if a string belongs to the language accepted by the automaton.


## Implementation description

* The "Grammar" class has predefined sets of non-terminals, terminals, rules and the start symbol based on my given variant.

```

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
```

* The " def generate_string_with_derivation " method generates valid strings with the help of recursion and depth to prevent infinite derivations
* It has a "derive" function that tracks the generated string and the derivation steps shown in the output

```    
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
```

* "def generate_string_with_derivation" is used to generate multiple strings and their derivations, and it returns a list containing each string and derivation steps.

```
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
```

* The method "generate_strings_with_derivation has the purpose of converting the grammar to Finite Automaton, and has states and transitions used to recognize the same language as the grammar.


  

```
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

        
``` 
* This function converts a given regular grammar into an equivalent finite automaton (FA). It constructs the FA by defining states, transitions based on the grammar's production rules, and setting the start and accept states accordingly.
```
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
```
## Results
* Here is an example of an output. The program generates strings based on the given rules and it displays the derivations. The finite automaton check also works : "abc" string is correct, because it ends in "c". "abb" is wrong, because it doesn't end with c, which means that it isn't a finite automaton, and "ac" is wrong simply because it doesn't follow the grammar rules.
```
The generated strings:
String: bbdeeefed, Derivation: S→bS S→bS S→dL L→eL L→eL L→eL L→fL L→eL L→d
String: defd, Derivation: S→dL L→eL L→fL L→d
String: bbcdeeeed, Derivation: S→bS S→bS S→cR R→dL L→eL L→eL L→eL L→eL L→d
String: dfffefd, Derivation: S→dL L→fL L→fL L→fL L→eL L→fL L→d
String: ce, Derivation: S→cR R→e

Testing strings:
String ce is correct
String dd is correct
String abc is wrong
String cde is wrong
String fff is wrong
```
## Conclusion

The implementation successfully generates strings based on the defined grammar and converts it into a finite automaton. The Grammar class handles string generation with derivation steps, while the FiniteAutomaton class verifies whether a given string belongs to the language. For instance, the string "aacd" is accepted because it follows valid transitions (S → aS → aS → cR → dL → d). However, the string "abce" is incorrect because "e" is only valid when derived from R, but "cR" cannot transition directly to "e," so it does not reach the final state.
# References

_Formal Languages and Finite Automata, Guide for practical lessons_ by COJUHARI Irina, DUCA Ludmila, FIODOROV Ion.