import re
from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, column={self.column})"


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        while self.position < len(self.source):

            # Ignore spaces, tabs and carriage returns
            if self.source[self.position] in " \t\r":
                self.advance()
                continue

            # New line
            if self.source[self.position] == "\n":
                self.advance_line()
                continue

            # Number
            if self.source[self.position].isdigit():
                self.tokenize_number()
                continue

            # Identifier or keyword
            if self.source[self.position].isalpha() or self.source[self.position] == "_":
                self.tokenize_identifier()
                continue

            # Two-character operators
            two_char = self.source[self.position:self.position + 2]

            if two_char in ("==", "!=", "<=", ">="):
                self.tokens.append(
                    Token(two_char, two_char, self.line, self.column)
                )
                self.advance()
                self.advance()
                continue

            # Single-character operators and punctuation
            single_char_tokens = {
                "+": "PLUS",
                "-": "MINUS",
                "*": "MULTIPLY",
                "/": "DIVIDE",
                "=": "ASSIGN",
                "<": "LESS_THAN",
                ">": "GREATER_THAN",
                "(": "LPAREN",
                ")": "RPAREN",
                "{": "LBRACE",
                "}": "RBRACE",
                ";": "SEMICOLON",
                ",": "COMMA"
            }

            current = self.source[self.position]

            if current in single_char_tokens:
                self.tokens.append(
                    Token(
                        single_char_tokens[current],
                        current,
                        self.line,
                        self.column
                    )
                )
                self.advance()
                continue

            # Unknown character
            raise SyntaxError(
                f"Unknown character '{current}' "
                f"at line {self.line}, column {self.column}"
            )

        self.tokens.append(
            Token("EOF", "", self.line, self.column)
        )

        return self.tokens

    def tokenize_number(self):
        start_column = self.column
        number = ""

        while (
            self.position < len(self.source)
            and self.source[self.position].isdigit()
        ):
            number += self.source[self.position]
            self.advance()

        self.tokens.append(
            Token("NUMBER", number, self.line, start_column)
        )

    def tokenize_identifier(self):
        start_column = self.column
        identifier = ""

        while (
            self.position < len(self.source)
            and (
                self.source[self.position].isalnum()
                or self.source[self.position] == "_"
            )
        ):
            identifier += self.source[self.position]
            self.advance()

        keywords = {
            "if": "IF",
            "else": "ELSE",
            "for": "FOR",
            "while": "WHILE",
            "print": "PRINT",
            "read": "READ"
        }

        token_type = keywords.get(identifier, "IDENTIFIER")

        self.tokens.append(
            Token(token_type, identifier, self.line, start_column)
        )

    def advance(self):
        self.position += 1
        self.column += 1

    def advance_line(self):
        self.position += 1
        self.line += 1
        self.column = 1


def tokenize(source):
    lexer = Lexer(source)
    return lexer.tokenize()


if __name__ == "__main__":

    source = """
    x = 10 + 20;
    y = x * 2;
    print(y);
    """

    tokens = tokenize(source)

    for token in tokens:
        print(token)