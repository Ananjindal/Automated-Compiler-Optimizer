def is_number(value):
    return value.lstrip("-").isdigit()


def get_used_variables(expression):
    parts = expression.split()
    variables = set()

    for part in parts:
        if is_number(part):
            continue

        if part in {"+", "-", "*", "/"}:
            continue

        variables.add(part)

    return variables


def get_condition_variables(instruction):
    parts = instruction.split()

    if len(parts) != 6:
        return set()

    variables = set()

    left = parts[1]
    right = parts[3]

    if not is_number(left):
        variables.add(left)

    if not is_number(right):
        variables.add(right)

    return variables


def get_control_flow_variables(tac):
    """
    Find variables that participate in branch/loop conditions.

    These variables must be treated conservatively by DCE because
    assignments to them may control program flow.
    """

    control_variables = set()

    for instruction in tac:
        instruction = instruction.strip()

        if instruction.startswith("if "):
            control_variables.update(
                get_condition_variables(instruction)
            )

    return control_variables


def dead_code_elimination(tac):
    optimized_reversed = []
    changes = []

    live_variables = set()

    # Variables used in conditions must be protected.
    control_flow_variables = get_control_flow_variables(tac)

    for instruction in reversed(tac):
        instruction = instruction.strip()

        if not instruction:
            continue

        # Labels are always preserved.
        if instruction.endswith(":"):
            optimized_reversed.append(instruction)
            continue

        # Gotos are always preserved.
        if instruction.startswith("goto "):
            optimized_reversed.append(instruction)
            continue

        # Conditional branches are always preserved.
        if instruction.startswith("if "):
            variables = get_condition_variables(instruction)

            live_variables.update(variables)

            optimized_reversed.append(instruction)
            continue

        # Print statements are always preserved.
        if instruction.startswith("print "):
            operand = instruction[6:].strip()

            if not is_number(operand):
                live_variables.add(operand)

            optimized_reversed.append(instruction)
            continue

        # Read statements are always preserved.
        if instruction.startswith("read "):
            variable = instruction[5:].strip()

            optimized_reversed.append(instruction)

            live_variables.discard(variable)

            continue

        # Assignment.
        if "=" in instruction:
            left_side, right_side = instruction.split("=", 1)

            destination = left_side.strip()
            expression = right_side.strip()

            used_variables = get_used_variables(expression)

            # Variables controlling conditions must never have their
            # assignments removed.
            if destination in control_flow_variables:
                optimized_reversed.append(instruction)

                live_variables.discard(destination)
                live_variables.update(used_variables)

                continue

            # Normal liveness-based elimination.
            if destination in live_variables:
                optimized_reversed.append(instruction)

                live_variables.discard(destination)
                live_variables.update(used_variables)

            else:
                changes.append(
                    f"Removed dead instruction: {instruction}"
                )

            continue

        optimized_reversed.append(instruction)

    optimized_tac = list(reversed(optimized_reversed))

    return optimized_tac, changes