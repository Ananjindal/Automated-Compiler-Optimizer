import re


def is_number(value):
    """Check whether a TAC operand is an integer constant."""
    return re.fullmatch(r"-?\d+", value.strip()) is not None


def calculate(left, operator, right):
    """Perform a constant arithmetic operation."""

    left = int(left)
    right = int(right)

    if operator == "+":
        return left + right

    if operator == "-":
        return left - right

    if operator == "*":
        return left * right

    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("Division by zero")
        return left // right

    raise ValueError(f"Unsupported operator: {operator}")


def constant_folding(tac):

    optimized_tac = []
    changes = []

    for instruction in tac:

        # Only process assignment instructions
        if "=" not in instruction:
            optimized_tac.append(instruction)
            continue

        left_side, right_side = instruction.split("=", 1)

        destination = left_side.strip()
        expression = right_side.strip()

        parts = expression.split()

        # Check for:
        # t1 = 10 + 20
        if len(parts) == 3:

            left = parts[0]
            operator = parts[1]
            right = parts[2]

            if is_number(left) and is_number(right):

                result = calculate(
                    left,
                    operator,
                    right
                )

                new_instruction = (
                    f"{destination} = {result}"
                )

                optimized_tac.append(new_instruction)

                changes.append(
                    f"{instruction} -> {new_instruction}"
                )

                continue

        # No optimization possible
        optimized_tac.append(instruction)

    return optimized_tac, changes