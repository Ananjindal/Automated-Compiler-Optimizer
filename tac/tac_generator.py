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


class TACGenerator:

    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    # ==========================================
    # TEMPORARIES
    # ==========================================

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    # ==========================================
    # LABELS
    # ==========================================

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    # ==========================================
    # GENERATE PROGRAM
    # ==========================================

    def generate(self, program):

        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

        for statement in program.statements:
            self.generate_statement(statement)

        return self.instructions

    # ==========================================
    # GENERATE STATEMENT
    # ==========================================

    def generate_statement(self, statement):

        # Assignment
        if isinstance(statement, Assignment):

            value = self.generate_expression(
                statement.expression
            )

            self.instructions.append(
                f"{statement.variable} = {value}"
            )

        # Print
        elif isinstance(statement, PrintStatement):

            value = self.generate_expression(
                statement.expression
            )

            self.instructions.append(
                f"print {value}"
            )

        # Read
        elif isinstance(statement, ReadStatement):

            self.instructions.append(
                f"read {statement.variable}"
            )

        # If / Else
        elif isinstance(statement, IfStatement):

            self.generate_if(statement)

        # While
        elif isinstance(statement, WhileStatement):

            self.generate_while(statement)

        # For
        elif isinstance(statement, ForStatement):

            self.generate_for(statement)

        else:

            raise ValueError(
                f"Unsupported statement: {statement}"
            )

    # ==========================================
    # IF / ELSE
    # ==========================================

    def generate_if(self, statement):

        true_label = self.new_label()
        false_label = self.new_label()
        end_label = self.new_label()

        # Condition

        self.generate_condition(
            statement.condition,
            true_label,
            false_label
        )

        # TRUE branch

        self.instructions.append(
            f"{true_label}:"
        )

        for body_statement in statement.then_body:

            self.generate_statement(body_statement)

        self.instructions.append(
            f"goto {end_label}"
        )

        # FALSE branch

        self.instructions.append(
            f"{false_label}:"
        )

        for body_statement in statement.else_body:

            self.generate_statement(body_statement)

        # END

        self.instructions.append(
            f"{end_label}:"
        )

    # ==========================================
    # WHILE
    # ==========================================

    def generate_while(self, statement):

        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()

        # Loop start

        self.instructions.append(
            f"{start_label}:"
        )

        # Condition

        self.generate_condition(
            statement.condition,
            body_label,
            end_label
        )

        # Loop body

        self.instructions.append(
            f"{body_label}:"
        )

        for body_statement in statement.body:

            self.generate_statement(body_statement)

        # Repeat

        self.instructions.append(
            f"goto {start_label}"
        )

        # Loop end

        self.instructions.append(
            f"{end_label}:"
        )

    # ==========================================
    # FOR
    # ==========================================

    def generate_for(self, statement):

        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()

        # Initialization

        self.generate_statement(
            statement.initialization
        )

        # Start of loop

        self.instructions.append(
            f"{start_label}:"
        )

        # Condition

        self.generate_condition(
            statement.condition,
            body_label,
            end_label
        )

        # Body

        self.instructions.append(
            f"{body_label}:"
        )

        for body_statement in statement.body:

            self.generate_statement(body_statement)

        # Update

        self.generate_statement(
            statement.update
        )

        # Repeat

        self.instructions.append(
            f"goto {start_label}"
        )

        # End

        self.instructions.append(
            f"{end_label}:"
        )

    # ==========================================
    # CONDITION
    # ==========================================

    def generate_condition(
        self,
        condition,
        true_label,
        false_label
    ):

        left = self.generate_expression(
            condition.left
        )

        right = self.generate_expression(
            condition.right
        )

        self.instructions.append(
            f"if {left} {condition.operator} "
            f"{right} goto {true_label}"
        )

        self.instructions.append(
            f"goto {false_label}"
        )

    # ==========================================
    # EXPRESSIONS
    # ==========================================

    def generate_expression(self, expression):

        # Number

        if isinstance(expression, Number):

            return str(expression.value)

        # Variable

        if isinstance(expression, Variable):

            return expression.name

        # Binary operation

        if isinstance(expression, BinaryOperation):

            left = self.generate_expression(
                expression.left
            )

            right = self.generate_expression(
                expression.right
            )

            temp = self.new_temp()

            self.instructions.append(
                f"{temp} = {left} "
                f"{expression.operator} {right}"
            )

            return temp

        raise ValueError(
            f"Unsupported expression: {expression}"
        )


# ==========================================
# PUBLIC FUNCTION
# ==========================================

def generate_tac(program):

    generator = TACGenerator()

    return generator.generate(program)