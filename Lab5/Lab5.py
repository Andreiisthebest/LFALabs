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

        for terminal in self.terminals:
            if len(terminal) > 1 and terminal != "ε":
                # Create a unique single-character representation
                unique_id = f"§{len(self.terminal_mapping)}"
                self.terminal_mapping[terminal] = unique_id
                self.reverse_terminal_mapping[unique_id] = terminal

        # Update productions to use the terminal mappings
        for left, rights in self.productions.items():
            if not isinstance(rights, set):
                self.productions[left] = set(rights)

            new_rights = set()
            for right in rights:
                # Skip epsilon
                if right == "ε" or right == "":
                    new_rights.add(right)
                    continue

                # Replace multi-character terminals with their unique IDs
                new_right = right
                for terminal, unique_id in self.terminal_mapping.items():
                    new_right = new_right.replace(terminal, unique_id)
                new_rights.add(new_right)

            self.productions[left] = new_rights

    def __str__(self):
        """String representation of the grammar."""
        result = f"G = ({self.non_terminals}, {self.terminals}, P, {self.start_symbol})\n"
        result += "P = {\n"
        for left, rights in sorted(self.productions.items()):
            for right in sorted(rights):
                # Restore original terminals for display
                display_right = right
                if right and right != "ε":
                    for unique_id, terminal in self.reverse_terminal_mapping.items():
                        display_right = display_right.replace(unique_id, terminal)
                result += f"    {left} → {display_right or 'ε'}\n"
        result += "}"
        return result

    def copy(self):
        """Create a deep copy of the grammar."""
        new_grammar = Grammar(
            non_terminals=set(self.non_terminals),
            terminals=set(self.terminals),
            start_symbol=self.start_symbol
        )

        # Copy productions
        new_productions = {}
        for left, rights in self.productions.items():
            new_productions[left] = set(rights)
        new_grammar.productions = new_productions

        # Copy terminal mappings
        new_grammar.terminal_mapping = dict(self.terminal_mapping)
        new_grammar.reverse_terminal_mapping = dict(self.reverse_terminal_mapping)

        return new_grammar

    def validate(self):
        """Validate that the grammar is well-formed."""
        errors = []

        # Check that start symbol is a non-terminal
        if self.start_symbol and self.start_symbol not in self.non_terminals:
            errors.append(f"Start symbol '{self.start_symbol}' is not in non-terminals")

        # Check that all production left-hand sides are non-terminals
        for left in self.productions:
            if left not in self.non_terminals:
                errors.append(f"Production left-hand side '{left}' is not in non-terminals")

        # Check that all symbols in productions are either non-terminals or terminals
        for left, rights in self.productions.items():
            for right in rights:
                # Skip validation for epsilon (empty string)
                if right == "ε" or right == "":
                    continue

                # Create a list to track positions as we check symbols
                pos = 0
                while pos < len(right):
                    # Check if this position starts a non-terminal
                    found_symbol = False
                    for nt in self.non_terminals:
                        if right[pos:].startswith(nt):
                            pos += len(nt)
                            found_symbol = True
                            break

                    # Check if this position starts a mapped terminal
                    if not found_symbol:
                        if right[pos] == '§':
                            # This is a mapped multi-character terminal
                            unique_id = right[pos:pos + 2]  # Assuming the format §N
                            if unique_id in self.reverse_terminal_mapping:
                                pos += 2
                                found_symbol = True

                    # Check if this position starts a regular terminal
                    if not found_symbol:
                        terminal_found = False
                        for term in self.terminals:
                            if right[pos:].startswith(term):
                                pos += len(term)
                                terminal_found = True
                                found_symbol = True
                                break

                    # If no valid symbol was found, report an error
                    if not found_symbol:
                        errors.append(f"Symbol starting at position {pos} in production {left} → {right} "
                                      "is neither a terminal nor a non-terminal")
                        pos += 1  # Move past this problematic character

        return errors


class CNFConverter:
    def __init__(self, grammar):
        """
        Initialize the converter with a grammar.

        Args:
            grammar: A Grammar object to convert to CNF
        """
        self.grammar = grammar.copy()
        self.new_symbol_counter = 0

        # Validate the grammar
        errors = self.grammar.validate()
        if errors:
            raise ValueError(f"Invalid grammar: {'; '.join(errors)}")

    def _generate_new_symbol(self, prefix="X"):
        """
        Generate a new non-terminal symbol that doesn't exist in the grammar.

        Args:
            prefix: Prefix for the new symbol

        Returns:
            A new unique non-terminal symbol
        """
        while True:
            self.new_symbol_counter += 1
            new_symbol = f"{prefix}{self.new_symbol_counter}"
            if new_symbol not in self.grammar.non_terminals:
                return new_symbol

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

        # Find indirect nullable symbols using fixed-point iteration
        changed = True
        while changed:
            changed = False
            for left, rights in self.grammar.productions.items():
                if left in nullable:
                    continue

                for right in rights:
                    # Check if all symbols in this production are nullable
                    if right and all(symbol in nullable for symbol in right):
                        nullable.add(left)
                        changed = True
                        break

        # Replace productions with nullable symbols
        new_productions = {}
        for left, rights in self.grammar.productions.items():
            new_productions[left] = set(rights)

            for right in list(rights):  # Use list to avoid modifying during iteration
                # Skip empty productions
                if not right:
                    continue

                # Find positions of nullable symbols
                nullable_positions = []
                for i, symbol in enumerate(right):
                    if symbol in nullable:
                        nullable_positions.append(i)

                if not nullable_positions:
                    continue

                # Generate all possible combinations without nullable symbols
                # We use binary counting to generate all subsets
                for mask in range(1, 1 << len(nullable_positions)):
                    new_right = list(right)

                    # Mark positions to be removed (in reverse to maintain indices)
                    positions_to_remove = []
                    for i, pos in enumerate(nullable_positions):
                        if mask & (1 << i):
                            positions_to_remove.append(pos)

                    # Remove positions in reverse order
                    for pos in sorted(positions_to_remove, reverse=True):
                        new_right = new_right[:pos] + new_right[pos + 1:]

                    new_right_str = ''.join(new_right)
                    if new_right_str:  # Don't add empty string as a production
                        new_productions[left].add(new_right_str)

        self.grammar.productions = new_productions
        return self.grammar

    def eliminate_unit_productions(self):
        """
        Step 2: Eliminate unit productions (A → B where B is a non-terminal).

        Returns:
            The modified grammar
        """
        # Find all unit pairs (A, B) where A =>* B and B is a non-terminal
        unit_pairs = {(nt, nt) for nt in self.grammar.non_terminals}  # Initialize with (A, A) for all A

        # Find direct unit pairs
        for left, rights in self.grammar.productions.items():
            for right in rights:
                if len(right) == 1 and right in self.grammar.non_terminals:
                    unit_pairs.add((left, right))

        # Find all unit pairs using transitive closure
        changed = True
        while changed:
            changed = False
            new_pairs = set(unit_pairs)

            for a, b in unit_pairs:
                for b2, c in unit_pairs:
                    if b == b2 and (a, c) not in new_pairs:
                        new_pairs.add((a, c))
                        changed = True

            unit_pairs = new_pairs

        # Replace unit productions
        new_productions = {nt: set() for nt in self.grammar.non_terminals}

        # First, add all non-unit productions
        for left, rights in self.grammar.productions.items():
            for right in rights:
                if not (len(right) == 1 and right in self.grammar.non_terminals):
                    new_productions[left].add(right)

        # Then add productions based on unit pairs
        for a, b in unit_pairs:
            if a != b:  # Skip the reflexive pairs
                if b in self.grammar.productions:
                    for right in self.grammar.productions[b]:
                        if not (len(right) == 1 and right in self.grammar.non_terminals):
                            new_productions[a].add(right)

        self.grammar.productions = new_productions
        return self.grammar

    def eliminate_inaccessible_symbols(self):
        """
        Step 3: Eliminate inaccessible symbols.

        Returns:
            The modified grammar
        """
        # Find all accessible symbols starting from the start symbol
        accessible = {self.grammar.start_symbol}
        symbols_to_check = [self.grammar.start_symbol]

        while symbols_to_check:
            symbol = symbols_to_check.pop(0)
            if symbol in self.grammar.productions:
                for right in self.grammar.productions[symbol]:
                    for s in right:
                        if s in self.grammar.non_terminals and s not in accessible:
                            accessible.add(s)
                            symbols_to_check.append(s)

        # Create new grammar with only accessible symbols
        new_productions = {}
        for left in accessible:
            if left in self.grammar.productions:
                new_productions[left] = self.grammar.productions[left]

        # Update non-terminals
        new_non_terminals = self.grammar.non_terminals.intersection(accessible)

        self.grammar.non_terminals = new_non_terminals
        self.grammar.productions = new_productions
        return self.grammar

    def eliminate_nonproductive_symbols(self):
        """
        Step 4: Eliminate non-productive symbols.

        Returns:
            The modified grammar
        """
        # Find all productive symbols (symbols that can derive a string of terminals)
        productive = set()

        # Initially, identify symbols that produce terminals directly
        for left, rights in self.grammar.productions.items():
            for right in rights:
                if all(symbol in self.grammar.terminals for symbol in right):
                    productive.add(left)
                    break

        # Fixed-point iteration to find all productive symbols
        changed = True
        while changed:
            changed = False
            for left, rights in self.grammar.productions.items():
                if left in productive:
                    continue

                for right in rights:
                    if all(symbol in productive or symbol in self.grammar.terminals for symbol in right):
                        productive.add(left)
                        changed = True
                        break

        # Create new grammar with only productive symbols
        new_productions = {}
        for left in productive:
            if left in self.grammar.productions:
                new_rights = set()
                for right in self.grammar.productions[left]:
                    # Only keep productions with productive symbols
                    if all(symbol in productive or symbol in self.grammar.terminals for symbol in right):
                        new_rights.add(right)
                if new_rights:  # Only add if there are valid productions
                    new_productions[left] = new_rights

        # Update non-terminals
        new_non_terminals = self.grammar.non_terminals.intersection(productive)

        self.grammar.non_terminals = new_non_terminals
        self.grammar.productions = new_productions
        return self.grammar

    def convert_to_cnf(self):
        """
        Step 5: Convert to Chomsky Normal Form.

        Returns:
            The modified grammar
        """
        # Create a new start symbol if the original appears on the right side
        need_new_start = False
        for left, rights in self.grammar.productions.items():
            if left != self.grammar.start_symbol:
                for right in rights:
                    if self.grammar.start_symbol in right:
                        need_new_start = True
                        break
            if need_new_start:
                break

        if need_new_start:
            new_start = self._generate_new_symbol("S'")
            self.grammar.non_terminals.add(new_start)
            self.grammar.productions[new_start] = {self.grammar.start_symbol}
            self.grammar.start_symbol = new_start

        # Handle terminals in longer productions
        terminal_replacements = {}
        new_productions = {nt: set() for nt in self.grammar.non_terminals}

        for left, rights in self.grammar.productions.items():
            for right in rights:
                if len(right) <= 1:  # Keep A → a and A → B as is
                    new_productions[left].add(right)
                else:
                    new_right_symbols = []
                    for symbol in right:
                        if symbol in self.grammar.terminals:
                            if symbol not in terminal_replacements:
                                new_nt = self._generate_new_symbol("T_")
                                terminal_replacements[symbol] = new_nt
                                self.grammar.non_terminals.add(new_nt)
                                new_productions[new_nt] = {symbol}
                            new_right_symbols.append(terminal_replacements[symbol])
                        else:
                            new_right_symbols.append(symbol)

                    new_right = ''.join(new_right_symbols)
                    new_productions[left].add(new_right)

        self.grammar.productions = new_productions

        # Break productions with more than 2 symbols
        new_productions = {nt: set() for nt in self.grammar.non_terminals}

        for left, rights in self.grammar.productions.items():
            for right in rights:
                if len(right) <= 2:  # Keep A → a, A → B, and A → BC as is
                    new_productions[left].add(right)
                else:
                    # Break down right-hand side with more than 2 symbols
                    current_symbols = list(right)
                    current_left = left

                    while len(current_symbols) > 2:
                        # Create a new non-terminal for the last two symbols
                        last_two = current_symbols[-2:]
                        current_symbols = current_symbols[:-2]

                        new_nt = self._generate_new_symbol()
                        self.grammar.non_terminals.add(new_nt)

                        # Add production for the new non-terminal
                        if new_nt not in new_productions:
                            new_productions[new_nt] = set()
                        new_productions[new_nt].add(''.join(last_two))

                        # Update current symbols
                        current_symbols.append(new_nt)

                    # Add the final production
                    new_productions[current_left].add(''.join(current_symbols))

        self.grammar.productions = new_productions
        return self.grammar

    def to_cnf(self):
        """
        Convert grammar to Chomsky Normal Form by applying all steps in sequence.

        Returns:
            The grammar in Chomsky Normal Form
        """
        print("Step 1: Eliminating ε-productions...")
        self.eliminate_epsilon_productions()
        print("Step 2: Eliminating unit productions...")
        self.eliminate_unit_productions()
        print("Step 3: Eliminating inaccessible symbols...")
        self.eliminate_inaccessible_symbols()
        print("Step 4: Eliminating non-productive symbols...")
        self.eliminate_nonproductive_symbols()
        print("Step 5: Converting to CNF...")
        self.convert_to_cnf()
        return self.grammar


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


def test_additional_grammar():
    """Test the CNF conversion on an additional grammar."""
    # Create a more complex grammar with multi-character terminals properly defined
    non_terminals = {'E', 'T', 'F'}
    terminals = {'+', '*', '(', ')', 'id'}  # 'id' is treated as a single terminal
    start_symbol = 'E'
    productions = {
        'E': {'E+T', 'T'},
        'T': {'T*F', 'F'},
        'F': {'(E)', 'id'}
    }

    grammar = Grammar(non_terminals, terminals, start_symbol, productions)
    return test_grammar(grammar, "Expression Grammar")


def test_with_longer_symbols():
    """Test the CNF conversion on a grammar with multi-character symbols."""
    non_terminals = {'START', 'EXPR', 'TERM', 'FACTOR'}
    terminals = {'plus', 'times', 'open', 'close', 'id'}
    start_symbol = 'START'
    productions = {
        'START': {'EXPR'},
        'EXPR': {'EXPRplusTERM', 'TERM'},
        'TERM': {'TERMtimesFACTOR', 'FACTOR'},
        'FACTOR': {'openEXPRclose', 'id', 'ε'}
    }

    grammar = Grammar(non_terminals, terminals, start_symbol, productions)
    return test_grammar(grammar, "Grammar with Longer Symbols")


if __name__ == "__main__":
    # Test the implementation with multiple grammars
    print("Testing the CNF converter with multiple grammars...")
    print("=" * 50 + "\n")

    # Test the original variant
    test_variant_2()

    # Test with an expression grammar
    test_additional_grammar()

    # Test with a grammar that has multi-character symbols
    test_with_longer_symbols()