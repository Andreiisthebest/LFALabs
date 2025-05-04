import re
from enum import Enum, auto

# ---------- Token Type Enum ----------
class TokenType(Enum):
    STATE = auto()
    NUMBER = auto()
    ELEMENT = auto()
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    WHITESPACE = auto()
    UNKNOWN = auto()

# ---------- Token Patterns ----------
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

# ---------- Lexer ----------
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

# ---------- AST Node Classes ----------
class ASTNode: pass

class Molecule(ASTNode):
    def __init__(self, quantity, formula, state=None):
        self.quantity = quantity
        self.formula = formula
        self.state = state

    def __repr__(self):
        return f"Molecule(quantity={self.quantity}, formula='{self.formula}', state={self.state})"

class Reaction(ASTNode):
    def __init__(self, reactants, products):
        self.reactants = reactants
        self.products = products

    def __repr__(self):
        return f"Reaction(\n  Reactants={self.reactants},\n  Products={self.products}\n)"

# ---------- Parser ----------
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

    def peek(self, token_type):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] == token_type

    def match(self, token_type, value=None):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token[0] == token_type and (value is None or token[1] == value):
                self.pos += 1
                return True
        return False

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

# ---------- Main ----------
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
