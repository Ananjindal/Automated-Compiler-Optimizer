def get_variables(expression):
    """
    Return variables used by a TAC expression.

    Numbers and arithmetic operators are ignored.
    """

    parts = expression.split()

    variables = set()

    for part in parts:

        if part.lstrip("-").isdigit():
            continue

        if part in {"+", "-", "*", "/"}:
            continue

        variables.add(part)

    return variables


def make_expression_key(left, operator, right):
    """
    Create a normalized key for an expression.

    Addition and multiplication are commutative:

        a + b == b + a
        a * b == b * a

    Subtraction and division are not.
    """

    if operator in {"+", "*"}:

        operands = sorted([left, right])

        return (
            operands[0],
            operator,
            operands[1]
        )

    return (
        left,
        operator,
        right
    )


def common_subexpression_elimination(tac):

    optimized_tac = []

    # expression_key -> variable containing result
    expression_table = {}

    # expression_key -> variables used by expression
    expression_variables = {}

    changes = []

    for instruction in tac:

        instruction = instruction.strip()

        # ==========================================
        # CONTROL-FLOW INSTRUCTIONS
        # ==========================================

        if (
            instruction.endswith(":")
            or instruction.startswith("goto ")
            or instruction.startswith("if ")
        ):

            # A branch can change which execution path
            # reaches the next instruction.
            #
            # To stay conservative, discard available
            # expressions at control-flow boundaries.

            expression_table.clear()
            expression_variables.clear()

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # PRINT
        # ==========================================

        if instruction.startswith("print "):

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # READ
        # ==========================================

        if instruction.startswith("read "):

            variable = instruction[5:].strip()

            # The value of this variable has changed.
            invalidate_variable(
                variable,
                expression_table,
                expression_variables
            )

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # NON-ASSIGNMENT
        # ==========================================

        if "=" not in instruction:

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # ASSIGNMENT
        # ==========================================

        left_side, right_side = instruction.split(
            "=",
            1
        )

        destination = left_side.strip()
        expression = right_side.strip()

        parts = expression.split()

        # ==========================================
        # SIMPLE ASSIGNMENT
        # ==========================================

        if len(parts) == 1:

            # Destination is being overwritten.
            invalidate_variable(
                destination,
                expression_table,
                expression_variables
            )

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # BINARY EXPRESSION
        # ==========================================

        if len(parts) == 3:

            left = parts[0]
            operator = parts[1]
            right = parts[2]

            # Destination is being overwritten.
            #
            # Example:
            #
            # a = a + b
            #
            # We cannot use an old expression involving a.
            invalidate_variable(
                destination,
                expression_table,
                expression_variables
            )

            key = make_expression_key(
                left,
                operator,
                right
            )

            # ======================================
            # EXPRESSION ALREADY AVAILABLE
            # ======================================

            if key in expression_table:

                previous_result = expression_table[key]

                new_instruction = (
                    f"{destination} = "
                    f"{previous_result}"
                )

                optimized_tac.append(
                    new_instruction
                )

                changes.append(
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

            # ======================================
            # NEW EXPRESSION
            # ======================================

            else:

                optimized_tac.append(
                    instruction
                )

                expression_table[key] = destination

                expression_variables[key] = (
                    get_variables(expression)
                )

            continue

        optimized_tac.append(instruction)

    return optimized_tac, changes


def invalidate_variable(
    variable,
    expression_table,
    expression_variables
):
    """
    Remove every available expression that depends
    on a variable whose value has changed.
    """

    expressions_to_remove = []

    for key, variables in expression_variables.items():

        if variable in variables:

            expressions_to_remove.append(key)

    for key in expressions_to_remove:

        expression_table.pop(
            key,
            None
        )

        expression_variables.pop(
            key,
            None
        )