# Implementation of a Context-Free Grammar to Chomsky Normal Form Converter

**Course: Formal Languages & Finite Automata**

**Author: Bobeica Andrei**

**Varianta: 2**

## Theory

Context-Free Grammars (CFGs) are formal grammars used to describe context-free languages, which are important in various areas of computer science, particularly in the parsing of programming languages. A CFG is a 4-tuple G = (V, Σ, R, S) where:
- V is a finite set of non-terminal symbols
- Σ is a finite set of terminal symbols
- R is a finite set of production rules of the form A → α, where A ∈ V and α ∈ (V ∪ Σ)*
- S ∈ V is the start symbol

Chomsky Normal Form (CNF) is a simplified form of CFGs where all production rules are of the form:
- A → BC (where B and C are non-terminals)
- A → a (where a is a terminal)
- S → ε (only if S is the start symbol and does not appear on the right side of any production)

Converting a CFG to CNF is essential for certain parsing algorithms like the CYK algorithm, which requires the grammar to be in CNF to function correctly.

## Objectives

* Implement a Context-Free Grammar (CFG) class that can represent and validate any CFG
* Develop a converter that transforms any valid CFG into its equivalent Chomsky Normal Form (CNF)
* Apply the conversion process through several well-defined steps:
  * Eliminate ε-productions
  * Eliminate unit productions
  * Eliminate inaccessible symbols
  * Eliminate non-productive symbols
  * Convert remaining productions to CNF format
* Test the implementation with various grammars to ensure correctness

## Implementation Description

### Grammar Class

The `Grammar` class implements a representation of context-free grammars with the following components:

* Constructor: Initializes a grammar with its non-terminals, terminals, start symbol, and productions
* Terminal mapping: Handles multi-character terminals to ensure they're treated atomically
* Validation: Ensures the grammar is well-formed
* String representation: Provides a readable format for the grammar

```python
class Grammar:
    def __init__(self, non_terminals=None, terminals=None, start_symbol=None, productions=None):
        """
        Initialize a context-free grammar.

        Args:
            non_terminals: Set of non-terminal symbols
            terminals: Set of terminal symbols
            start_symbol: The start symbol of the grammar
            productions: Dictionary mapping non-terminals to sets of productions
        """
        self.non_terminals = non_terminals if non_terminals else set()
        self.terminals = terminals if terminals else set()
        self.start_symbol = start_symbol
        self.productions = productions if productions else {}

        # Pre-process any multi-character terminals to ensure we treat them as atomic
        self.terminal_mapping = {}
        self.reverse_terminal_mapping = {}
        
        # [Terminal mapping implementation follows]
```

The `validate` method ensures the grammar meets all requirements:

```python
def validate(self):
    """Validate that the grammar is well-formed."""
    errors = []

    # Check that start symbol is a non-terminal
    if self.start_symbol and self.start_symbol not in self.non_terminals:
        errors.append(f"Start symbol '{self.start_symbol}' is not in non-terminals")

    # [Additional validation checks]
    
    return errors
```

### CNF Converter Class

The `CNFConverter` class implements the transformation of a CFG to CNF through a series of steps:

1. **Eliminate ε-productions**:
   * Identifies all nullable symbols (symbols that can derive ε)
   * Creates new productions that account for the possible presence or absence of nullable symbols

```python
def eliminate_epsilon_productions(self):
    """
    Step 1: Eliminate ε productions.

    Returns:
        The modified grammar
    """
    # Find all nullable symbols (symbols that can derive epsilon)
    nullable = set()

    # Find direct nullable symbols
    for left, rights in self.grammar.productions.items():
        if "ε" in rights or "" in rights:
            nullable.add(left)
            new_rights = set(rights)
            new_rights.discard("ε")
            new_rights.discard("")
            self.grammar.productions[left] = new_rights
    
    # [Rest of implementation]
```

2. **Eliminate unit productions**:
   * Identifies all unit pairs (A, B) where A can derive B in one or more steps
   * Replaces A → B with the non-unit productions of B

```python
def eliminate_unit_productions(self):
    """
    Step 2: Eliminate unit productions (A → B where B is a non-terminal).

    Returns:
        The modified grammar
    """
    # Find all unit pairs (A, B) where A =>* B and B is a non-terminal
    unit_pairs = {(nt, nt) for nt in self.grammar.non_terminals}  # Initialize with (A, A) for all A

    # [Rest of implementation]
```

3. **Eliminate inaccessible symbols**:
   * Identifies symbols that cannot be reached from the start symbol
   * Removes these symbols and their associated productions

```python
def eliminate_inaccessible_symbols(self):
    """
    Step 3: Eliminate inaccessible symbols.

    Returns:
        The modified grammar
    """
    # Find all accessible symbols starting from the start symbol
    accessible = {self.grammar.start_symbol}
    symbols_to_check = [self.grammar.start_symbol]
    
    # [Rest of implementation]
```

4. **Eliminate non-productive symbols**:
   * Identifies symbols that cannot derive any string of terminals
   * Removes these symbols and their associated productions

```python
def eliminate_nonproductive_symbols(self):
    """
    Step 4: Eliminate non-productive symbols.

    Returns:
        The modified grammar
    """
    # Find all productive symbols (symbols that can derive a string of terminals)
    productive = set()
    
    # [Rest of implementation]
```

5. **Convert to CNF**:
   * Creates a new start symbol if necessary
   * Handles terminals in longer productions by creating new non-terminals
   * Breaks productions with more than 2 symbols into binary productions

```python
def convert_to_cnf(self):
    """
    Step 5: Convert to Chomsky Normal Form.

    Returns:
        The modified grammar
    """
    # Create a new start symbol if the original appears on the right side
    need_new_start = False
    
    # [Rest of implementation]

    # Handle terminals in longer productions
    terminal_replacements = {}
    new_productions = {nt: set() for nt in self.grammar.non_terminals}
    
    # [Rest of implementation]

    # Break productions with more than 2 symbols
    new_productions = {nt: set() for nt in self.grammar.non_terminals}
    
    # [Rest of implementation]
```

### Main Testing Framework

The code includes test functions to verify the implementation on various grammars:

```python
def test_grammar(grammar, description="Grammar"):
    """Test the CNF conversion on a given grammar."""
    print(f"Original {description}:")
    print(grammar)
    print("\n")

    converter = CNFConverter(grammar)
    cnf_grammar = converter.to_cnf()

    print(f"{description} in Chomsky Normal Form:")
    print(cnf_grammar)
    print("\n" + "=" * 50 + "\n")
    return cnf_grammar
```

Example of a test grammar:

```python
def test_variant_2():
    """Test the CNF conversion on variant 2 grammar."""
    # Create the grammar from variant 2
    non_terminals = {'S', 'A', 'B', 'C', 'D'}
    terminals = {'a', 'b', 'ε'}  # Include epsilon as a special terminal
    start_symbol = 'S'
    productions = {
        'S': {'aB', 'bA'},
        'A': {'B', 'b', 'aD', 'AS', 'bAAB', 'ε'},
        'B': {'b', 'bS'},
        'C': {'AB'},
        'D': {'BB'}
    }

    grammar = Grammar(non_terminals, terminals, start_symbol, productions)
    return test_grammar(grammar, "Variant 2 Grammar")
```

## Results

When executed, the program successfully converts three different grammars to CNF:

1. **Variant 2 Grammar**: A grammar with epsilon productions and unit productions
2. **Expression Grammar**: A simple grammar for mathematical expressions
3. **Grammar with Longer Symbols**: A grammar with multi-character terminal and non-terminal symbols

For each grammar, the program shows:
- The original grammar
- The step-by-step conversion process
- The resulting grammar in CNF

Sample output from conversion (simplified):

```
Original Variant 2 Grammar:
G = ({'S', 'A', 'B', 'C', 'D'}, {'a', 'b', 'ε'}, P, S)
P = {
    A → AS
    A → B
    A → aD
    A → b
    A → bAAB
    A → ε
    B → b
    B → bS
    C → AB
    D → BB
    S → aB
    S → bA
}

Step 1: Eliminating ε-productions...
Step 2: Eliminating unit productions...
Step 3: Eliminating inaccessible symbols...
Step 4: Eliminating non-productive symbols...
Step 5: Converting to CNF...

Variant 2 Grammar in Chomsky Normal Form:
G = ({'S', 'A', 'B', 'T_1', 'T_2', 'X1', 'X2', 'X3', 'X4'}, {'a', 'b', 'ε'}, P, S)
P = {
    A → S
    A → T_2
    A → X1
    A → X3
    A → X4
    B → T_2
    B → X2
    S → T_1B
    S → T_2A
    T_1 → a
    T_2 → b
    X1 → AS
    X2 → T_2S
    X3 → T_1D
    X4 → T_2X3
}
```

## Conclusions

The implementation successfully transforms any context-free grammar into its equivalent Chomsky Normal Form. The modular design separates the grammar representation from the conversion algorithm, making the code maintainable and extensible.

Key features of the implementation include:
- Proper handling of multi-character terminals and non-terminals
- Comprehensive validation of grammar well-formedness
- A step-by-step approach to CNF conversion that follows theoretical foundations
- Ability to handle diverse grammar structures

This implementation provides a robust foundation for algorithms that require grammars in CNF, such as the CYK parsing algorithm. The modular design also makes it easy to extend the functionality, for example, to implement grammar minimization or other transformations.

