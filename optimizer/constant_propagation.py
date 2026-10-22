import re


def is_number(value):
    return re.fullmatch(
        r"-?\d+",
        value.strip()
    ) is not None


def get_used_variables(expression):
    """
    Return variables used in a TAC expression.
    """

    parts = expression.split()

    variables = set()

    for part in parts:

        if is_number(part):
            continue

        if part in {"+", "-", "*", "/"}:
            continue

        variables.add(part)

    return variables


def invalidate_variable(
    variable,
    constants
):
    """
    Remove a variable from the constant table when
    its value is changed.
    """

    constants.pop(
        variable,
        None
    )


def constant_propagation(tac):

    optimized_tac = []

    # variable -> known constant
    constants = {}

    changes = []

    for instruction in tac:

        instruction = instruction.strip()

        # ==========================================
        # LABEL
        # ==========================================

        if instruction.endswith(":"):

            # We conservatively clear known constants
            # at control-flow boundaries.

            constants.clear()

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # GOTO
        # ==========================================

        if instruction.startswith("goto "):

            constants.clear()

            optimized_tac.append(instruction)

            continue

        # ==========================================
        # CONDITIONAL GOTO
        # ==========================================

        if instruction.startswith("if "):

            parts = instruction.split()

            if len(parts) == 6:

                left = parts[1]
                right = parts[3]

                if left in constants:
                    left = constants[left]

                if right in constants:
                    right = constants[right]

                new_instruction = (
                    f"if {left} {parts[2]} "
                    f"{right} goto {parts[5]}"
                )

                if new_instruction != instruction:

                    changes.append(
                        f"{instruction} -> "
                        f"{new_instruction}"
                    )

                optimized_tac.append(
                    new_instruction
                )

            else:

                optimized_tac.append(
                    instruction
                )

            # Branching means we cannot safely assume
            # constants after this point.

            constants.clear()

            continue

        # ==========================================
        # PRINT
        # ==========================================

        if instruction.startswith("print "):

            operand = instruction[6:].strip()

            if operand in constants:

                new_instruction = (
                    f"print {constants[operand]}"
                )

                changes.append(
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

                optimized_tac.append(
                    new_instruction
                )

            else:

                optimized_tac.append(
                    instruction
                )

            continue

        # ==========================================
        # READ
        # ==========================================

        if instruction.startswith("read "):

            variable = instruction[5:].strip()

            invalidate_variable(
                variable,
                constants
            )

            optimized_tac.append(
                instruction
            )

            continue

        # ==========================================
        # NON-ASSIGNMENT
        # ==========================================

        if "=" not in instruction:

            optimized_tac.append(
                instruction
            )

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

            value = parts[0]

            # x = 10
            if is_number(value):

                constants[destination] = value

                optimized_tac.append(
                    f"{destination} = {value}"
                )

                continue

            # x = y, where y is known constant
            if value in constants:

                constant_value = constants[value]

                new_instruction = (
                    f"{destination} = "
                    f"{constant_value}"
                )

                constants[destination] = (
                    constant_value
                )

                changes.append(
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

                optimized_tac.append(
                    new_instruction
                )

                continue

            # x = unknown variable
            invalidate_variable(
                destination,
                constants
            )

            optimized_tac.append(
                instruction
            )

            continue

        # ==========================================
        # BINARY EXPRESSION
        # ==========================================

        if len(parts) == 3:

            left = parts[0]
            operator = parts[1]
            right = parts[2]

            if left in constants:
                left = constants[left]

            if right in constants:
                right = constants[right]

            new_instruction = (
                f"{destination} = "
                f"{left} {operator} {right}"
            )

            if new_instruction != instruction:

                changes.append(
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

            optimized_tac.append(
                new_instruction
            )

            # We only know the destination is constant
            # if BOTH operands are constants.

            if (
                is_number(left)
                and is_number(right)
            ):

                # Store the expression as a constant
                # temporarily. Constant folding will
                # calculate it in the next pass.
                constants.pop(
                    destination,
                    None
                )

            else:

                invalidate_variable(
                    destination,
                    constants
                )

            continue

        # ==========================================
        # UNKNOWN ASSIGNMENT FORMAT
        # ==========================================

        invalidate_variable(
            destination,
            constants
        )

        optimized_tac.append(
            instruction
        )

    return optimized_tac, changes