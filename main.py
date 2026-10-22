from lexer.lexer import tokenize
from parser.parser import Parser
from tac.tac_generator import generate_tac
from optimizer.optimizer import optimize_tac
from execution.tac_executor import execute_tac


def print_section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_tac(title, tac):
    print_section(title)

    if not tac:
        print("(empty)")
        return

    for index, instruction in enumerate(tac, start=1):
        print(f"{index:03}: {instruction}")


def main():

    print_section("AUTOMATED RULE-BASED COMPILER CODE OPTIMIZER")

    print("Enter your source program.")
    print("Type END on a separate line when finished.")
    print()

    source_lines = []

    while True:

        line = input()

        if line.strip() == "END":
            break

        source_lines.append(line)

    source = "\n".join(source_lines)

    if not source.strip():

        print("No source code provided.")
        return

    # ==========================================
    # 1. LEXICAL ANALYSIS
    # ==========================================

    print_section("LEXICAL ANALYSIS")

    tokens = tokenize(source)

    for token in tokens:

        if token.type != "EOF":
            print(token)

    # ==========================================
    # 2. PARSING
    # ==========================================

    parser = Parser(tokens)

    program = parser.parse()

    print_section("PARSING")

    print("Source successfully parsed into AST.")

    # ==========================================
    # 3. TAC GENERATION
    # ==========================================

    original_tac = generate_tac(program)

    print_tac(
        "ORIGINAL THREE ADDRESS CODE",
        original_tac
    )

    # ==========================================
    # 4. OPTIMIZATION
    # ==========================================

    optimized_tac, optimization_log, pass_history = (
        optimize_tac(original_tac)
    )

    print_tac(
        "OPTIMIZED THREE ADDRESS CODE",
        optimized_tac
    )

    # ==========================================
    # 5. OPTIMIZATIONS APPLIED
    # ==========================================

    print_section("OPTIMIZATIONS APPLIED")

    if not optimization_log:

        print("No optimizations were applied.")

    else:

        for entry in optimization_log:

            print(
                f"Pass {entry['pass']} | "
                f"{entry['optimizer']}"
            )

            print(
                f"    {entry['change']}"
            )

    # ==========================================
    # 6. OPTIMIZATION SUMMARY
    # ==========================================

    print_section("OPTIMIZATION SUMMARY")

    original_count = len(original_tac)
    optimized_count = len(optimized_tac)

    instructions_removed = (
        original_count - optimized_count
    )

    if original_count > 0:

        reduction = (
            instructions_removed
            / original_count
        ) * 100

    else:

        reduction = 0

    print(
        f"Original instructions : "
        f"{original_count}"
    )

    print(
        f"Optimized instructions: "
        f"{optimized_count}"
    )

    print(
        f"Instructions removed  : "
        f"{instructions_removed}"
    )

    print(
        f"Instruction reduction : "
        f"{reduction:.2f}%"
    )

    # ==========================================
    # 7. FIXED-POINT HISTORY
    # ==========================================

    print_section("OPTIMIZATION PASS HISTORY")

    for entry in pass_history:

        status = (
            "CHANGED"
            if entry["changed"]
            else "NO CHANGE"
        )

        print(
            f"Pass {entry['pass']}: "
            f"{entry['instruction_count']} "
            f"instructions - {status}"
        )

    # ==========================================
    # 8. EXECUTE ORIGINAL PROGRAM
    # ==========================================

    print_section("PROGRAM EXECUTION")

    # Find variables that require input.
    input_variables = []

    for instruction in original_tac:

        if instruction.startswith("read "):

            variable = instruction[
                5:
            ].strip()

            if variable not in input_variables:

                input_variables.append(
                    variable
                )

    inputs = {}

    # Ask user for required inputs.
    for variable in input_variables:

        while True:

            try:

                value = int(
                    input(
                        f"Enter value for {variable}: "
                    )
                )

                inputs[variable] = value

                break

            except ValueError:

                print(
                    "Please enter an integer."
                )

    original_output = execute_tac(
        original_tac,
        inputs
    )

    print(
        "Original program output:",
        original_output
    )

    # ==========================================
    # 9. EXECUTE OPTIMIZED PROGRAM
    # ==========================================

    optimized_output = execute_tac(
        optimized_tac,
        inputs
    )

    print(
        "Optimized program output:",
        optimized_output
    )

    # ==========================================
    # 10. CORRECTNESS CHECK
    # ==========================================

    print_section("CORRECTNESS CHECK")

    if original_output == optimized_output:

        print(
            "PASS: Optimized program produces "
            "the same output as the original."
        )

    else:

        print(
            "FAIL: Optimized program produces "
            "different output."
        )

    print_section("COMPILATION COMPLETE")


if __name__ == "__main__":
    main()