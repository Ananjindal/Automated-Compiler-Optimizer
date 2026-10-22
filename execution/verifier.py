from execution.tac_executor import execute_tac


class VerificationResult:

    def __init__(
        self,
        passed,
        original_output,
        optimized_output,
        inputs
    ):

        self.passed = passed
        self.original_output = original_output
        self.optimized_output = optimized_output
        self.inputs = inputs

    def to_dict(self):

        return {
            "passed": self.passed,
            "inputs": self.inputs,
            "original_output": self.original_output,
            "optimized_output": self.optimized_output
        }


def verify_tac(
    original_tac,
    optimized_tac,
    inputs=None
):

    if inputs is None:
        inputs = {}

    # Execute original program
    original_output = execute_tac(
        original_tac,
        inputs
    )

    # Execute optimized program
    optimized_output = execute_tac(
        optimized_tac,
        inputs
    )

    # Compare outputs
    passed = (
        original_output == optimized_output
    )

    return VerificationResult(
        passed=passed,
        original_output=original_output,
        optimized_output=optimized_output,
        inputs=inputs
    )


def verify_multiple_inputs(
    original_tac,
    optimized_tac,
    test_inputs
):

    results = []

    for inputs in test_inputs:

        result = verify_tac(
            original_tac,
            optimized_tac,
            inputs
        )

        results.append(result)

    passed_count = sum(
        1
        for result in results
        if result.passed
    )

    total_count = len(results)

    return {
        "results": results,
        "passed": passed_count,
        "failed": (
            total_count - passed_count
        ),
        "total": total_count,
        "all_passed": (
            passed_count == total_count
        )
    }