from lexer.lexer import tokenize

from parser.ast import (
    Number,
    Variable,
    BinaryOperation,
    Comparison,
    Assignment,
    PrintStatement,
    ReadStatement,
    IfStatement,
    WhileStatement,
    ForStatement,
    Program
)


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    # ==========================================
    # TOKEN HELPERS
    # ==========================================

    def current_token(self):
        return self.tokens[self.position]

    def advance(self):
        self.position += 1

    def expect(self, token_type):
        token = self.current_token()

        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, but found {token.type} "
                f"at line {token.line}, column {token.column}"
            )

        self.advance()
        return token

    # ==========================================
    # PROGRAM
    # ==========================================

    def parse(self):

        statements = []

        while self.current_token().type != "EOF":
            statements.append(self.parse_statement())

        return Program(statements)

    # ==========================================
    # STATEMENTS
    # ==========================================

    def parse_statement(self):

        token = self.current_token()

        # --------------------------------------
        # Assignment
        # --------------------------------------

        if token.type == "IDENTIFIER":

            variable = token.value
            self.advance()

            self.expect("ASSIGN")

            expression = self.parse_expression()

            self.expect("SEMICOLON")

            return Assignment(
                variable,
                expression
            )

        # --------------------------------------
        # Print
        # --------------------------------------

        if token.type == "PRINT":

            self.advance()

            self.expect("LPAREN")

            expression = self.parse_expression()

            self.expect("RPAREN")
            self.expect("SEMICOLON")

            return PrintStatement(expression)

        # --------------------------------------
        # Read
        # --------------------------------------

        if token.type == "READ":

            self.advance()

            self.expect("LPAREN")

            variable = self.expect(
                "IDENTIFIER"
            ).value

            self.expect("RPAREN")
            self.expect("SEMICOLON")

            return ReadStatement(variable)

        # --------------------------------------
        # If / Else
        # --------------------------------------

        if token.type == "IF":

            return self.parse_if()

        # --------------------------------------
        # While
        # --------------------------------------

        if token.type == "WHILE":

            return self.parse_while()

        # --------------------------------------
        # For
        # --------------------------------------

        if token.type == "FOR":

            return self.parse_for()

        raise SyntaxError(
            f"Unexpected token {token.type} "
            f"at line {token.line}, column {token.column}"
        )

    # ==========================================
    # IF / ELSE
    # ==========================================

    def parse_if(self):

        self.expect("IF")

        self.expect("LPAREN")

        condition = self.parse_condition()

        self.expect("RPAREN")

        then_body = self.parse_block()

        else_body = []

        if self.current_token().type == "ELSE":

            self.advance()

            else_body = self.parse_block()

        return IfStatement(
            condition,
            then_body,
            else_body
        )

    # ==========================================
    # WHILE
    # ==========================================

    def parse_while(self):

        self.expect("WHILE")

        self.expect("LPAREN")

        condition = self.parse_condition()

        self.expect("RPAREN")

        body = self.parse_block()

        return WhileStatement(
            condition,
            body
        )

    # ==========================================
    # FOR
    # ==========================================

    def parse_for(self):

        self.expect("FOR")

        self.expect("LPAREN")

        # Initialization
        variable = self.expect(
            "IDENTIFIER"
        ).value

        self.expect("ASSIGN")

        initialization_expression = (
            self.parse_expression()
        )

        initialization = Assignment(
            variable,
            initialization_expression
        )

        self.expect("SEMICOLON")

        # Condition
        condition = self.parse_condition()

        self.expect("SEMICOLON")

        # Update
        update_variable = self.expect(
            "IDENTIFIER"
        ).value

        self.expect("ASSIGN")

        update_expression = (
            self.parse_expression()
        )

        update = Assignment(
            update_variable,
            update_expression
        )

        self.expect("RPAREN")

        body = self.parse_block()

        return ForStatement(
            initialization,
            condition,
            update,
            body
        )

    # ==========================================
    # BLOCK
    # ==========================================

    def parse_block(self):

        self.expect("LBRACE")

        statements = []

        while self.current_token().type != "RBRACE":

            if self.current_token().type == "EOF":
                raise SyntaxError(
                    "Expected '}', but reached end of input"
                )

            statements.append(
                self.parse_statement()
            )

        self.expect("RBRACE")

        return statements

    # ==========================================
    # CONDITIONS
    # ==========================================

    def parse_condition(self):

        left = self.parse_expression()

        token = self.current_token()

        comparison_operators = {
            "==",
            "!=",
            "LESS_THAN",
            "GREATER_THAN",
            "<=",
            ">="
        }

        if token.type not in comparison_operators:
            raise SyntaxError(
                f"Expected comparison operator, "
                f"but found {token.type}"
            )

        operator = token.value

        self.advance()

        right = self.parse_expression()

        return Comparison(
            left,
            operator,
            right
        )

    # ==========================================
    # EXPRESSIONS
    # ==========================================

    def parse_expression(self):

        return self.parse_addition()

    # ==========================================
    # ADDITION / SUBTRACTION
    # ==========================================

    def parse_addition(self):

        node = self.parse_multiplication()

        while self.current_token().type in (
            "PLUS",
            "MINUS"
        ):

            operator = self.current_token().value

            self.advance()

            right = self.parse_multiplication()

            node = BinaryOperation(
                node,
                operator,
                right
            )

        return node

    # ==========================================
    # MULTIPLICATION / DIVISION
    # ==========================================

    def parse_multiplication(self):

        node = self.parse_primary()

        while self.current_token().type in (
            "MULTIPLY",
            "DIVIDE"
        ):

            operator = self.current_token().value

            self.advance()

            right = self.parse_primary()

            node = BinaryOperation(
                node,
                operator,
                right
            )

        return node

    # ==========================================
    # PRIMARY
    # ==========================================

    def parse_primary(self):

        token = self.current_token()

        # Number
        if token.type == "NUMBER":

            self.advance()

            return Number(
                int(token.value)
            )

        # Variable
        if token.type == "IDENTIFIER":

            self.advance()

            return Variable(
                token.value
            )

        # Parenthesized expression
        if token.type == "LPAREN":

            self.advance()

            expression = (
                self.parse_expression()
            )

            self.expect("RPAREN")

            return expression

        raise SyntaxError(
            f"Unexpected token {token.type} "
            f"at line {token.line}, "
            f"column {token.column}"
        )


# ==========================================
# PUBLIC PARSE FUNCTION
# ==========================================

def parse(source):

    tokens = tokenize(source)

    parser = Parser(tokens)

    return parser.parse()


# ==========================================
# TEMPORARY TEST
# ==========================================

if __name__ == "__main__":

    source = """
    read(x);

    if (x > 10) {
        y = x * 2;
        print(y);
    } else {
        y = x + 5;
        print(y);
    }

    """

    program = parse(source)

    print(program)