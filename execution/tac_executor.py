class TACExecutor:

    def __init__(self):
        self.variables = {}
        self.output = []
        self.labels = {}

    # ==========================================
    # GET VALUE
    # ==========================================

    def get_value(self, operand):

        operand = operand.strip()

        # Integer constant
        if operand.lstrip("-").isdigit():
            return int(operand)

        # Variable
        if operand in self.variables:
            return self.variables[operand]

        raise RuntimeError(
            f"Undefined variable: {operand}"
        )

    # ==========================================
    # ARITHMETIC
    # ==========================================

    def evaluate_operation(
        self,
        left,
        operator,
        right
    ):

        left_value = self.get_value(left)
        right_value = self.get_value(right)

        if operator == "+":
            return left_value + right_value

        if operator == "-":
            return left_value - right_value

        if operator == "*":
            return left_value * right_value

        if operator == "/":

            if right_value == 0:
                raise ZeroDivisionError(
                    "Division by zero"
                )

            return left_value // right_value

        raise RuntimeError(
            f"Unknown operator: {operator}"
        )

    # ==========================================
    # COMPARISON
    # ==========================================

    def evaluate_condition(
        self,
        left,
        operator,
        right
    ):

        left_value = self.get_value(left)
        right_value = self.get_value(right)

        if operator == "==":
            return left_value == right_value

        if operator == "!=":
            return left_value != right_value

        if operator == "<":
            return left_value < right_value

        if operator == ">":
            return left_value > right_value

        if operator == "<=":
            return left_value <= right_value

        if operator == ">=":
            return left_value >= right_value

        raise RuntimeError(
            f"Unknown comparison operator: {operator}"
        )

    # ==========================================
    # BUILD LABEL TABLE
    # ==========================================

    def build_label_table(self, instructions):

        self.labels = {}

        for index, instruction in enumerate(instructions):

            instruction = instruction.strip()

            if instruction.endswith(":"):

                label = instruction[:-1].strip()

                self.labels[label] = index

    # ==========================================
    # EXECUTE
    # ==========================================

    def execute(
        self,
        instructions,
        inputs=None
    ):

        self.variables = {}
        self.output = []

        if inputs is None:
            inputs = {}

        self.variables.update(inputs)

        self.build_label_table(instructions)

        program_counter = 0

        # Safety limit against accidental infinite loops
        steps = 0
        max_steps = 100000

        while program_counter < len(instructions):

            steps += 1

            if steps > max_steps:

                raise RuntimeError(
                    "Execution exceeded maximum number "
                    "of steps. Possible infinite loop."
                )

            instruction = instructions[
                program_counter
            ].strip()

            # --------------------------------------
            # Empty instruction
            # --------------------------------------

            if not instruction:

                program_counter += 1
                continue

            # --------------------------------------
            # LABEL
            # --------------------------------------

            if instruction.endswith(":"):

                program_counter += 1
                continue

            # --------------------------------------
            # PRINT
            # --------------------------------------

            if instruction.startswith("print "):

                operand = instruction[6:].strip()

                value = self.get_value(operand)

                self.output.append(value)

                program_counter += 1

                continue

            # --------------------------------------
            # READ
            # --------------------------------------

            if instruction.startswith("read "):

                variable = instruction[5:].strip()

                if variable not in inputs:

                    raise RuntimeError(
                        f"No input provided for variable: "
                        f"{variable}"
                    )

                self.variables[variable] = (
                    inputs[variable]
                )

                program_counter += 1

                continue

            # --------------------------------------
            # CONDITIONAL GOTO
            # --------------------------------------

            if instruction.startswith("if "):

                parts = instruction.split()

                # Expected:
                #
                # if x > 10 goto L1
                #
                # [if, x, >, 10, goto, L1]

                if len(parts) != 6:

                    raise RuntimeError(
                        f"Invalid conditional instruction: "
                        f"{instruction}"
                    )

                if_keyword = parts[0]
                left = parts[1]
                operator = parts[2]
                right = parts[3]
                goto_keyword = parts[4]
                label = parts[5]

                if if_keyword != "if":
                    raise RuntimeError(
                        f"Invalid conditional instruction: "
                        f"{instruction}"
                    )

                if goto_keyword != "goto":
                    raise RuntimeError(
                        f"Invalid conditional instruction: "
                        f"{instruction}"
                    )

                condition = self.evaluate_condition(
                    left,
                    operator,
                    right
                )

                if condition:

                    if label not in self.labels:

                        raise RuntimeError(
                            f"Unknown label: {label}"
                        )

                    program_counter = (
                        self.labels[label]
                    )

                else:

                    program_counter += 1

                continue

            # --------------------------------------
            # GOTO
            # --------------------------------------

            if instruction.startswith("goto "):

                label = instruction[5:].strip()

                if label not in self.labels:

                    raise RuntimeError(
                        f"Unknown label: {label}"
                    )

                program_counter = self.labels[label]

                continue

            # --------------------------------------
            # ASSIGNMENT
            # --------------------------------------

            if "=" in instruction:

                left_side, right_side = (
                    instruction.split("=", 1)
                )

                destination = left_side.strip()
                expression = right_side.strip()

                parts = expression.split()

                # Binary expression
                #
                # t1 = x + 10

                if len(parts) == 3:

                    left = parts[0]
                    operator = parts[1]
                    right = parts[2]

                    value = self.evaluate_operation(
                        left,
                        operator,
                        right
                    )

                # Simple assignment
                #
                # x = t1

                elif len(parts) == 1:

                    value = self.get_value(
                        parts[0]
                    )

                else:

                    raise RuntimeError(
                        f"Invalid expression: "
                        f"{expression}"
                    )

                self.variables[destination] = value

                program_counter += 1

                continue

            # --------------------------------------
            # UNKNOWN INSTRUCTION
            # --------------------------------------

            raise RuntimeError(
                f"Invalid TAC instruction: "
                f"{instruction}"
            )

        return self.output


# ==========================================
# PUBLIC FUNCTION
# ==========================================

def execute_tac(
    instructions,
    inputs=None
):

    executor = TACExecutor()

    return executor.execute(
        instructions,
        inputs
    )