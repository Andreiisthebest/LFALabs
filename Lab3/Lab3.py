import re

# Define token types
TOKEN_TYPES = [
    ('NUMBER', r'\d+'),                  # Match stoichiometric coefficients
    ('ELEMENT', r'[A-Z][a-z]?\d*'),      # Match element symbols (e.g., H2, O2, H2O)
    ('OPERATOR', r'\+|->'),              # Match + and ->
    ('STATE', r'\([sglaq]\)'),           # Match state symbols (e.g., (s), (g), (l))
    ('WHITESPACE', r'\s+'),              # Match whitespace
    ('UNKNOWN', r'.'),                   # Match any other character
]

# Lexer class
class ChemicalLexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.line_num = 1
        self.line_start = 0

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

# Example usage
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