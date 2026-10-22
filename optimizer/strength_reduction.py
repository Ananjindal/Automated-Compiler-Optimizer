def strength_reduction(tac):

    optimized_tac = []
    changes = []

    for instruction in tac:

        instruction = instruction.strip()

        # ==========================================
        # CONTROL FLOW
        # ==========================================

        if (
            instruction.endswith(":")
            or instruction.startswith("goto ")
            or instruction.startswith("if ")
        ):
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

        # We only transform binary expressions.
        if len(parts) != 3:

            optimized_tac.append(instruction)
            continue

        left = parts[0]
        operator = parts[1]
        right = parts[2]

        replacement = None

        # ==========================================
        # MULTIPLICATION BY 2
        # ==========================================
        #
        # x * 2
        #
        # becomes
        #
        # x + x
        #
        # and
        #
        # 2 * x
        #
        # becomes
        #
        # x + x
        #
        # ==========================================

        if operator == "*" and right == "2":

            replacement = f"{left} + {left}"

        elif operator == "*" and left == "2":

            replacement = f"{right} + {right}"

        # ==========================================
        # APPLY TRANSFORMATION
        # ==========================================

        if replacement is not None:

            new_instruction = (
                f"{destination} = {replacement}"
            )

            optimized_tac.append(
                new_instruction
            )

            changes.append(
                f"{instruction} -> "
                f"{new_instruction}"
            )

        else:

            optimized_tac.append(
                instruction
            )

    return optimized_tac, changes