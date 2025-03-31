# Lexer & Scanner
### Course: Formal Languages & Finite Automata
### Author: Bobeica Andrei

----

## Theory

### Lexical Analysis and Lexers

A lexer is a crucial part of many language processing tools, such as compilers and interpreters. Its main job is to scan an input string and divide it into smaller, meaningful components called tokens. Tokens represent the fundamental elements of a language, such as keywords, identifiers, operators, and literals.

In this case, the lexer is designed to process chemical equations by identifying elements, numbers, operators, and state symbols. The tokenization process relies on regular expressions to match predefined patterns in the input text.
### Domain-Specific Languages (DSLs)
A domain-specific language (DSL) is a specialized programming or notation language designed for a particular application domain. Unlike general-purpose languages like Python or Java, which are meant for a wide range of tasks, DSLs focus on solving problems within a narrow context. This makes them more expressive and easier to use for their specific purpose. Examples of DSLs include SQL for database queries, regular expressions for pattern matching, and LaTeX for document formatting.

In this case, chemical equations can be considered a form of DSL. They follow a structured syntax and semantics that represent chemical reactions. For example:

+ 2 H2(g) + O2(g) -> 2 H2O(l) describes the reaction of hydrogen and oxygen forming water.

+ (s), (g), (l), and (aq) specify the physical states of substances.

+ separates reactants and products, while -> indicates the direction of the reaction.

The lexer in this program is designed to recognize and tokenize these domain-specific notations, enabling further processing, such as validation, analysis, or translation into computational models.

### How Lexers and DSLs Relate

In this program, the lexer processes a domain-specific language (DSL) designed for chemical equation notation. The TOKEN_TYPES list defines the syntax of this DSL using regular expressions, specifying patterns for stoichiometric numbers, chemical elements, operators, and state symbols. The lexer scans the input string, matches these patterns, and produces a structured stream of tokens representing the chemical reaction.

For example, the input string `2 H2(g) + O2(g) -> 2 H2O(l)` is broken down into tokens like `[('NUMBER', '2'), ('ELEMENT', 'H2'), ('STATE', '(g)'),  
 ('OPERATOR', '+'), ('ELEMENT', 'O2'), ('STATE', '(g)'),  
 ('OPERATOR', '->'), ('NUMBER', '2'), ('ELEMENT', 'H2O'), ('STATE', '(l)')]`. This tokenized representation can then be used for further processing, such as validating the moves, generating a chessboard visualization, or analyzing the game.


## Objectives

The primary objectives of this lab are to:

1. **Understand Lexical Analysis in the Context of a DSL:**
   - Gain a deep understanding of how lexical analysis converts raw text into a structured sequence of tokens.
   - Recognize the importance of lexers in the process of compiling or interpreting domain-specific languages, such as the Chess notations language.

2. **Design and Implement a Lexer for the Chemistry DSL:**
   - Develop a lexer that can process input scripts.
   - Define token types for keywords, identifiers, string literals, numeric values, and operators.

## Implementation description

In this section, i will talk about the implementation of the Chemistry Notation DSL lexer and explain each part of the code separately.


### token_specs list

This list defines the different types of tokens (patterns) that the lexer will recognize in the input string. Each token is represented as a tuple with two elements:

```
token_specs = [
    # move numbers
    ('MOVE_NUM', r'\d+\.'),
    # queen/king castling
    ('CASTLE', r'O-O(?:-O)TOKEN_TYPES = [
    ('NUMBER', r'\d+'),                  # Match stoichiometric coefficients
    ('ELEMENT', r'[A-Z][a-z]?\d*'),      # Match element symbols (e.g., H2, O2, H2O)
    ('OPERATOR', r'\+|->'),              # Match + and ->
    ('STATE', r'\([sglaq]\)'),           # Match state symbols (e.g., (s), (g), (l))
    ('WHITESPACE', r'\s+'),              # Match whitespace
    ('UNKNOWN', r'.'),                   # Match any other character
]
```

The way it works is that it has a structure, where each token is represented as a tuple that consists of a name and pattern(name, pattern)
* **name** is a descriptive name for the token
* **pattern** is the regex pattern that matches the token

For example:

+ NUMBER is used to match stoichiometric coefficients like "2", "3", or "10", which indicate the quantity of molecules in a reaction (e.g., "2 H2" or "3 O2").

+ ELEMENT is used to match chemical element symbols such as "H2", "O2", or "NaCl", which represent molecules and compounds in the equation.

+ OPERATOR is used to match "+" and "->", where "+" separates reactants and products, and "->" represents the reaction arrow indicating the direction of the reaction.

+ STATE is used to match state symbols like "(s)", "(g)", "(l)", and "(aq)", which indicate whether a substance is a solid, gas, liquid, or aqueous solution.

+ WHITESPACE is used to match spaces, tabs, and newlines in the input. These are ignored during tokenization.

+ UNKNOWN is used for error handling, catching any unexpected characters that don’t fit the defined patterns.
### ChemicalLexer class
This part of the ChemicalLexer class defines the initializer (__init__ method), which sets up the necessary attributes for the lexer to process the input text.
```
class ChemicalLexer:
    def __init__(self, input_text):
```
**This is the constructor of the ChemicalLexer class.**

+ It takes **input_text** as an argument, which is the chemical equation or reaction string that the lexer will analyze.
```
self.input_text = input_text
```
+ Stores the input text in self.input_text, making it accessible throughout the class.

+ This is the string that will be tokenized

```
self.position = 0
```
+ Tracks the current position (index) in the input string while scanning.

+ Starts at 0 because no characters have been processed yet.
```
self.line_num = 1
```
+ Tracks the current line number in the input.

+ Initialized to 1 because scanning starts at the first line.

+ Useful for error reporting if the lexer encounters an unexpected character.

```
self.line_start = 0
```
+ Stores the starting position of the current line.

+ Helps calculate the column number of tokens for precise error messages.

+ Updates when a newline (\n) is encountered.
### The tokenize method

This method has the role of tokenizing the input string into a list of tokens
```
    def tokenize(self):
        tokens = []
        while self.position < len(self.input_text):
            match = None
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(self.input_text, self.position)
                if match:
                    value = match.group(0)
                    # Track line and column for error reporting
                    self.line_num += self.input_text[self.position:match.start()].count('\n')
                    if '\n' in self.input_text[self.position:match.start()]:
                        self.line_start = self.input_text.rfind('\n', self.position, match.start()) + 1
                    column = match.start() - self.line_start + 1

                    if token_type != 'WHITESPACE':  # Skip whitespace
                        tokens.append((token_type, value, self.line_num, column))
                    self.position = match.end()
                    break
            if not match:
                raise ValueError(f"Unexpected character '{self.input_text[self.position]}' at line {self.line_num}, column {column}")
        return tokens
```

In order to do that, it goes through multiple steps as follows:
1. Loops through the input string character by character.

2. Tries to match each character sequence against the token patterns.

3. Tracks line and column numbers for error reporting.

4. Ignores whitespace tokens.

5. Returns a structured list of tokens for further processing.

6. Raises an error if an unexpected character is found.


### Test cases list
This is the main execution block of the program. It initializes the lexer, tokenizes the input, and prints the results while handling errors.

```
if __name__ == "__main__":
    input_text = "2 H2(g) + O2(g) -> 2 H2O(l)"
    lexer = ChemicalLexer(input_text)
    try:
        tokens = lexer.tokenize()
        print("Tokens:")
        for token in tokens:
            print(f"[{token[0]}, {token[1]}] (Line {token[2]}, Column {token[3]})")
    except ValueError as e:
        print(f"Error: {e}")
```




+ Initializes a ChemicalLexer object.

+ Tokenizes the input string.

+ Prints tokens in a structured format.

+ Handles errors gracefully, reporting unexpected character
## Results
```
Tokens:
[NUMBER, 2] (Line 1, Column 1)
[ELEMENT, H2] (Line 1, Column 3)
[STATE, (g)] (Line 1, Column 5)
[OPERATOR, +] (Line 1, Column 9)
[ELEMENT, O2] (Line 1, Column 11)
[STATE, (g)] (Line 1, Column 13)
[OPERATOR, ->] (Line 1, Column 17)
[NUMBER, 2] (Line 1, Column 20)
[ELEMENT, H2] (Line 1, Column 22)
[ELEMENT, O] (Line 1, Column 24)
[STATE, (l)] (Line 1, Column 25)
```


# Conclusion

In this laboratory work, I've successfully designed and implemented a lexical analyzer (lexer) for chemical equations. This lexer serves as a fundamental component for processing and understanding chemical notation as a domain-specific language (DSL). The implementation effectively converts raw textual representations of chemical equations into a structured sequence of tokens that can be further processed for validation, analysis, or computational modeling.

The lexer is built around a set of carefully defined regular expressions that recognize the various components of chemical equations, including:
- Stoichiometric coefficients (numbers)
- Chemical elements and compounds
- Operators (+ and ->)
- State symbols ((s), (g), (l), (aq))

The ChemicalLexer class provides a robust framework for tokenization while maintaining detailed position tracking for error reporting. This positional information is crucial for providing meaningful feedback when invalid characters or syntax are encountered in the input.

The program successfully handles the example equation "2 H2(g) + O2(g) -> 2 H2O(l)", breaking it down into its constituent tokens with precise line and column information. This demonstrates the lexer's ability to process standard chemical notation accurately.

While the current implementation is functional and effective for basic chemical equations, there are several potential extensions that could enhance its capabilities:
1. Support for more complex chemical notation, such as ionic charges and structural formulas
2. Integration with a parser to validate the grammatical structure of the equations
3. Implementation of semantic analysis to check for conservation of mass and charge
4. Development of visualization tools based on the tokenized representation

This lexer represents a solid foundation for building more advanced chemical equation processing systems. By establishing a clear lexical structure for chemical notation, it opens up possibilities for more sophisticated computational chemistry applications, educational tools, and chemical reaction simulators.

Through this implementation, I've gained valuable insights into lexical analysis techniques, regular expression pattern matching, and the principles of domain-specific language design. These skills are transferable to a wide range of language processing applications beyond chemistry notation.

## References

[1] [A sample of a lexer implementation](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)

[2] [Lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis)

[3] [Formal Languages and Finite Automata, Guide for practical lessons](https://else.fcim.utm.md/pluginfile.php/110458/mod_resource/content/0/LFPC_Guide.pdf)