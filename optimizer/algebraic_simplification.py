def algebraic_simplification(tac):

    optimized_tac = []
    changes = []

    for instruction in tac:

        if "=" not in instruction:
            optimized_tac.append(instruction)
            continue

        left_side, right_side = instruction.split(
            "=", 1
        )

        destination = left_side.strip()
        expression = right_side.strip()

        parts = expression.split()

        if len(parts) != 3:
            optimized_tac.append(instruction)
            continue

        left = parts[0]
        operator = parts[1]
        right = parts[2]

        replacement = None

        # --------------------------------------
        # x + 0 = x
        # --------------------------------------

        if operator == "+" and right == "0":
            replacement = left

        elif operator == "+" and left == "0":
            replacement = right

        # --------------------------------------
        # x - 0 = x
        # --------------------------------------

        elif operator == "-" and right == "0":
            replacement = left

        # --------------------------------------
        # x * 1 = x
        # --------------------------------------

        elif operator == "*" and right == "1":
            replacement = left

        elif operator == "*" and left == "1":
            replacement = right

        # --------------------------------------
        # x * 0 = 0
        # --------------------------------------

        elif operator == "*" and (
            left == "0" or right == "0"
        ):
            replacement = "0"

        # --------------------------------------
        # x / 1 = x
        # --------------------------------------

        elif operator == "/" and right == "1":
            replacement = left

        # --------------------------------------
        # x - x = 0
        # --------------------------------------

        elif operator == "-" and left == right:
            replacement = "0"

        # --------------------------------------
        # Apply replacement
        # --------------------------------------

        if replacement is not None:

            new_instruction = (
                f"{destination} = {replacement}"
            )

            optimized_tac.append(new_instruction)

            changes.append(
                f"{instruction} -> {new_instruction}"
            )

        else:

            optimized_tac.append(instruction)

    return optimized_tac, changes