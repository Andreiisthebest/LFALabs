# Chemical Equation Parser Implementation
# Course: Formal Languages & Finite Automata
 Author: Bobeica Andrei
----

## Theory
In formal language theory, parsing chemical equations involves breaking down chemical notation into a structured representation. Chemical equations are a specific type of formal language with their own syntax and semantics. The implementation uses lexical analysis to tokenize the input followed by syntactic analysis to create an Abstract Syntax Tree (AST), which represents the hierarchical structure of the chemical equation. This approach follows compiler design principles where the first phase identifies tokens through regular expressions, and the second phase applies grammar rules to build a meaningful structure.

## Objectives:
* Implement a lexical analyzer (lexer) for chemical equations using regular expressions
* Create a parser to transform tokens into an Abstract Syntax Tree (AST)
* Design a representation for chemical molecules and reactions
* Demonstrate the parsing process with a sample chemical equation

## Implementation description

### Token Classification
The implementation begins by defining the different types of tokens that can appear in a chemical equation. An enumeration class `TokenType` is created to categorize these tokens:

```
class TokenType(Enum):
    STATE = auto()
    NUMBER = auto()
    ELEMENT = auto()
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    WHITESPACE = auto()
    UNKNOWN = auto()
```

Each token type is associated with a regular expression pattern that helps identify it in the input text:

```
TOKEN_TYPES = [
    (TokenType.STATE, r'\((aq|s|g|l)\)'),
    (TokenType.OPERATOR, r'\+|->'),
    (TokenType.NUMBER, r'\d+'),
    (TokenType.ELEMENT, r'[A-Z][a-z]?\d*'),
    (TokenType.LPAREN, r'\('),
    (TokenType.RPAREN, r'\)'),
    (TokenType.WHITESPACE, r'\s+'),
    (TokenType.UNKNOWN, r'.'),
]
```

### Lexical Analysis
The `ChemicalLexer` class is responsible for tokenizing the input text. It scans the input character by character, matching patterns to identify tokens:

```
class ChemicalLexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0

    def tokenize(self):
        tokens = []
        while self.position < len(self.input_text):
            match = None
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(self.input_text, self.position)
                if match:
                    value = match.group(0)
                    if token_type != TokenType.WHITESPACE:
                        tokens.append((token_type, value))
                    self.position = match.end()
                    break
            if not match:
                raise ValueError(f"Unexpected character '{self.input_text[self.position]}'")
        return tokens
```

The lexer iterates through the token patterns and uses regular expressions to match them at the current position. Whitespace tokens are identified but not added to the token list, effectively ignoring them.

### Abstract Syntax Tree (AST)
The AST is represented by two main classes: `Molecule` and `Reaction`. The `Molecule` class stores information about a chemical molecule, including its quantity, formula, and state. The `Reaction` class represents a chemical reaction with reactants and products:

```
class Molecule(ASTNode):
    def __init__(self, quantity, formula, state=None):
        self.quantity = quantity
        self.formula = formula
        self.state = state

class Reaction(ASTNode):
    def __init__(self, reactants, products):
        self.reactants = reactants
        self.products = products
```

### Syntactic Analysis
The `ChemicalParser` class implements the parser, which constructs the AST from the token stream. It uses recursive descent parsing techniques to handle the grammar of chemical equations:

```
class ChemicalParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        reactants = self.parse_molecules()
        if not self.match(TokenType.OPERATOR, '->'):
            raise SyntaxError("Expected '->'")
        products = self.parse_molecules()
        return Reaction(reactants, products)
```

The parser has helper methods to examine tokens (`peek`, `match`, and `advance`) and specialized methods to parse specific structures (`parse_molecules`):

```
def parse_molecules(self):
    molecules = []
    while self.pos < len(self.tokens):
        quantity = 1
        if self.peek(TokenType.NUMBER):
            quantity = int(self.advance()[1])

        formula_parts = []
        paren_count = 0
        while self.peek(TokenType.ELEMENT) or self.peek(TokenType.LPAREN) or self.peek(TokenType.RPAREN) or self.peek(TokenType.NUMBER):
            token = self.advance()
            if token[0] == TokenType.LPAREN:
                paren_count += 1
            elif token[0] == TokenType.RPAREN:
                paren_count -= 1
            formula_parts.append(token[1])

        formula = ''.join(formula_parts)
        state = None
        if self.peek(TokenType.STATE):
            state = self.advance()[1]

        molecules.append(Molecule(quantity, formula, state))
        if not self.match(TokenType.OPERATOR, '+'):
            break
    return molecules
```

The `parse_molecules` method recognizes the structure of chemical molecules, including their quantities, formulas, and states. It handles multiple molecules separated by '+' symbols.

### Main Execution
The main section demonstrates the usage of the lexer and parser with a sample chemical equation:

```

if __name__ == "__main__":
    input_text = "2 H2SO4(aq) + Ca(OH)2(s) -> CaSO4(s) + 2 H2O(l)"
    lexer = ChemicalLexer(input_text)
    try:
        tokens = lexer.tokenize()
        print("Tokens:")
        for t in tokens:
            print(f"[{t[0].name}, {t[1]}]")

        parser = ChemicalParser(tokens)
        ast = parser.parse()

        print("\nParsed AST:")
        print(ast)

    except Exception as e:
        print(f"Error: {e}")
```

## Conclusions / Results

The implementation successfully parses chemical equations into a structured representation. For the given example "2 H2SO4(aq) + Ca(OH)2(s) -> CaSO4(s) + 2 H2O(l)", the parser correctly identifies:

- Reactants: 
  - 2 molecules of H2SO4 in aqueous state
  - 1 molecule of Ca(OH)2 in solid state
- Products: 
  - 1 molecule of CaSO4 in solid state
  - 2 molecules of H2O in liquid state

The AST output demonstrates the hierarchical structure of the chemical equation:

```
Reaction(
  Reactants=[Molecule(quantity=2, formula='H2SO4', state=(aq)), Molecule(quantity=1, formula='Ca(OH)2', state=(s))],
  Products=[Molecule(quantity=1, formula='CaSO4', state=(s)), Molecule(quantity=2, formula='H2O', state=(l))]
)
```

This implementation demonstrates the application of formal language theory to a practical domain. By using lexical analysis and parsing techniques, we can transform chemical equations from text into structured data that can be manipulated programmatically. This opens up possibilities for various applications such as balancing chemical equations, validating chemical reactions, or integrating with other chemical informatics tools.

The lexer and parser follow the principles of compiler design while adapting to the specific syntax of chemical notation. The modular design makes it easy to extend the implementation to handle more complex chemical equations or to add additional functionality.