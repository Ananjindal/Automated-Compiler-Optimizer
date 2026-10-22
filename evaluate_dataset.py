import csv
import json
import time
from pathlib import Path

from lexer.lexer import tokenize
from parser.parser import Parser
from tac.tac_generator import generate_tac
from optimizer.optimizer import optimize_tac
from execution.tac_executor import execute_tac


PROJECT_ROOT = Path(__file__).resolve().parent
BENCHMARKS_DIR = PROJECT_ROOT / "benchmarks"
DATASET_PATH = BENCHMARKS_DIR / "dataset.json"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def arithmetic_count(tac):
    """
    Count arithmetic TAC instructions.

    Supported generated TAC format:
        t1 = a + b
        t2 = x * 5

    Splitting 't1 = a + b' produces:
        ['t1', '=', 'a', '+', 'b']
    Therefore, the operator is parts[3].
    """
    operators = {"+", "-", "*", "/"}
    count = 0

    for instruction in tac:
        parts = instruction.split()
        if (
            len(parts) == 5
            and parts[1] == "="
            and parts[3] in operators
        ):
            count += 1

    return count


def temporary_count(tac):
    count = 0

    for instruction in tac:
        if "=" not in instruction:
            continue

        left_side = instruction.split("=", 1)[0].strip()
        if left_side.startswith("t") and left_side[1:].isdigit():
            count += 1

    return count


def resolve_source_path(source_file, program_id):
    """Resolve source paths relative to the project or benchmarks directory."""
    raw = str(source_file).replace("\\", "/")
    raw_path = Path(raw)
    source_dir = BENCHMARKS_DIR / "source_programs"

    candidates = []
    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.extend([
            PROJECT_ROOT / raw_path,
            BENCHMARKS_DIR / raw_path,
            source_dir / raw_path.name,
        ])

        if "source_programs/" in raw:
            relative = raw.split("source_programs/", 1)[1]
            candidates.append(source_dir / relative)

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    # Fallback: locate by program ID stem, regardless of extension or category folder.
    if source_dir.exists():
        matches = [
            path for path in source_dir.rglob("*")
            if path.is_file() and path.stem.lower() == Path(str(program_id)).stem.lower()
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise FileNotFoundError(
                f"Multiple source files found for {program_id}: "
                + ", ".join(str(path) for path in matches)
            )

    raise FileNotFoundError(
        f"Source file for {program_id!r} was not found.\n"
        f"Dataset source_file: {source_file!r}\n"
        f"Expected source folder: {source_dir}"
    )


def normalize_expected_output(value):
    """Unwrap accidental nested singleton lists in dataset outputs."""
    while (
        isinstance(value, list)
        and len(value) == 1
        and isinstance(value[0], list)
    ):
        value = value[0]
    return value


def unique_test_cases(program):
    inputs_list = program.get("test_inputs", [])
    expected_list = program.get("expected_output", [])

    if len(inputs_list) != len(expected_list):
        raise ValueError(
            f"{program.get('id', 'Unknown')}: test_inputs has "
            f"{len(inputs_list)} entries but expected_output has "
            f"{len(expected_list)} entries."
        )

    unique_cases = []
    seen = {}

    for original_index, (inputs, expected) in enumerate(
        zip(inputs_list, expected_list), start=1
    ):
        key = json.dumps(inputs, sort_keys=True)
        expected = normalize_expected_output(expected)

        if key in seen:
            if seen[key]["expected"] != expected:
                raise ValueError(
                    f"{program.get('id')}: duplicate inputs have conflicting "
                    "expected outputs."
                )
            continue

        case = {
            "test_case": len(unique_cases) + 1,
            "original_dataset_entry": original_index,
            "inputs": inputs,
            "expected": expected,
        }
        seen[key] = case
        unique_cases.append(case)

    return unique_cases, len(inputs_list) - len(unique_cases)


def prepare_program(source):
    tokens = tokenize(source)
    ast = Parser(tokens).parse()
    original_tac = generate_tac(ast)

    start = time.perf_counter()
    optimized_tac, optimization_log, pass_history = optimize_tac(original_tac)
    optimization_time = time.perf_counter() - start

    return {
        "original_tac": original_tac,
        "optimized_tac": optimized_tac,
        "optimization_log": optimization_log,
        "pass_history": pass_history,
        "optimization_time_seconds": optimization_time,
    }


def main():
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}\n"
            "Make sure dataset.json is inside benchmarks."
        )

    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    programs = dataset.get("programs", [])

    if not programs:
        raise ValueError(f"No programs found in {DATASET_PATH}")

    program_results = []
    test_results = []
    optimizer_counts = {}
    category_stats = {}

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    duplicate_entries_skipped = 0

    for program in programs:
        program_id = program.get("id", "UNKNOWN")
        category = program.get("category", "Uncategorized")

        category_stats.setdefault(category, {
            "programs": 0,
            "tests": 0,
            "passed": 0,
            "failed": 0,
            "instruction_reduction_sum": 0.0,
        })
        category_stats[category]["programs"] += 1

        base = {
            "id": program_id,
            "category": category,
            "description": program.get("description", ""),
            "target_optimization": program.get("target_optimization", ""),
            "status": "ERROR",
            "error": "",
        }

        try:
            source_path = resolve_source_path(program["source_file"], program_id)
            source = source_path.read_text(encoding="utf-8")
            cases, duplicates = unique_test_cases(program)
            duplicate_entries_skipped += duplicates

            if not cases:
                raise ValueError(f"{program_id} has no test cases.")

            run_data = prepare_program(source)
            original_tac = run_data["original_tac"]
            optimized_tac = run_data["optimized_tac"]

            original_count = len(original_tac)
            optimized_count = len(optimized_tac)
            reduction = (
                (original_count - optimized_count) / original_count * 100
                if original_count else 0.0
            )

            fired = {}
            for entry in run_data["optimization_log"]:
                name = entry.get("optimizer", "Unknown optimizer")
                fired[name] = fired.get(name, 0) + 1
                optimizer_counts[name] = optimizer_counts.get(name, 0) + 1

            program_test_rows = []

            for case in cases:
                inputs = case["inputs"]
                expected = case["expected"]

                original_start = time.perf_counter()
                original_output = execute_tac(original_tac, inputs)
                original_time = time.perf_counter() - original_start

                optimized_start = time.perf_counter()
                optimized_output = execute_tac(optimized_tac, inputs)
                optimized_time = time.perf_counter() - optimized_start

                original_matches_expected = (
                    normalize_expected_output(original_output) == expected
                )
                outputs_match = (
                    normalize_expected_output(original_output)
                    == normalize_expected_output(optimized_output)
                )
                passed = original_matches_expected and outputs_match

                total_tests += 1
                if passed:
                    passed_tests += 1
                    category_stats[category]["passed"] += 1
                else:
                    failed_tests += 1
                    category_stats[category]["failed"] += 1
                category_stats[category]["tests"] += 1

                row = {
                    "program_id": program_id,
                    "category": category,
                    "test_case": case["test_case"],
                    "original_dataset_entry": case["original_dataset_entry"],
                    "inputs": json.dumps(inputs, sort_keys=True),
                    "expected_output": json.dumps(expected),
                    "original_output": json.dumps(original_output),
                    "optimized_output": json.dumps(optimized_output),
                    "original_matches_expected": original_matches_expected,
                    "original_matches_optimized": outputs_match,
                    "passed": passed,
                    "original_execution_time_seconds": original_time,
                    "optimized_execution_time_seconds": optimized_time,
                }
                test_results.append(row)
                program_test_rows.append(row)

            program_passed = sum(1 for row in program_test_rows if row["passed"])
            program_total = len(program_test_rows)
            category_stats[category]["instruction_reduction_sum"] += reduction

            base.update({
                "source_path_used": str(source_path),
                "original_instructions": original_count,
                "optimized_instructions": optimized_count,
                "instruction_reduction_percent": round(reduction, 2),
                "original_arithmetic_operations": arithmetic_count(original_tac),
                "optimized_arithmetic_operations": arithmetic_count(optimized_tac),
                "original_temporaries": temporary_count(original_tac),
                "optimized_temporaries": temporary_count(optimized_tac),
                "test_cases_passed": program_passed,
                "test_cases_total": program_total,
                "passes": len(run_data["pass_history"]),
                "optimization_time_seconds": run_data["optimization_time_seconds"],
                "optimizers_fired": fired,
                "status": (
                    "PASS"
                    if program_total > 0 and program_passed == program_total
                    else "FAIL"
                ),
                "error": "",
            })

        except Exception as exc:
            base["error"] = f"{type(exc).__name__}: {exc}"

        program_results.append(base)

    for stats in category_stats.values():
        stats["average_instruction_reduction_percent"] = round(
            stats["instruction_reduction_sum"] / stats["programs"], 2
        ) if stats["programs"] else 0.0
        del stats["instruction_reduction_sum"]

    summary = {
        "programs": len(programs),
        "test_cases": total_tests,
        "duplicate_test_entries_skipped": duplicate_entries_skipped,
        "passed": passed_tests,
        "failed": failed_tests,
        "pass_rate_percent": round(
            passed_tests / total_tests * 100, 2
        ) if total_tests else 0.0,
        "program_errors": sum(
            1 for row in program_results if row["status"] == "ERROR"
        ),
    }

    results = {
        "dataset": dataset.get("dataset_name", "Custom Compiler Benchmark"),
        "dataset_version": dataset.get("version", ""),
        "summary": summary,
        "optimizer_firings": optimizer_counts,
        "category_statistics": category_stats,
        "program_results": program_results,
        "test_results": test_results,
    }

    (RESULTS_DIR / "dataset_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    program_fields = [
        "id", "category", "description", "target_optimization",
        "original_instructions", "optimized_instructions",
        "instruction_reduction_percent", "original_arithmetic_operations",
        "optimized_arithmetic_operations", "original_temporaries",
        "optimized_temporaries", "test_cases_passed", "test_cases_total",
        "passes", "optimization_time_seconds", "status", "error",
    ]

    with (RESULTS_DIR / "dataset_results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=program_fields)
        writer.writeheader()
        for row in program_results:
            writer.writerow({key: row.get(key, "") for key in program_fields})

    test_fields = [
        "program_id", "category", "test_case", "original_dataset_entry",
        "inputs", "expected_output", "original_output", "optimized_output",
        "original_matches_expected", "original_matches_optimized", "passed",
        "original_execution_time_seconds", "optimized_execution_time_seconds",
    ]

    with (RESULTS_DIR / "test_results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=test_fields)
        writer.writeheader()
        writer.writerows(test_results)

    print("=" * 65)
    print("AUTOMATED COMPILER OPTIMIZER - DATASET EVALUATION")
    print("=" * 65)
    print(f"Programs in dataset        : {summary['programs']}")
    print(f"Unique test cases          : {summary['test_cases']}")
    print(f"Duplicate entries skipped : {summary['duplicate_test_entries_skipped']}")
    print(f"Passed                     : {summary['passed']}")
    print(f"Failed                     : {summary['failed']}")
    print(f"Program errors             : {summary['program_errors']}")
    print(f"Pass rate                  : {summary['pass_rate_percent']:.2f}%")
    print()
    print("Optimizer firings:")
    for name, count in sorted(optimizer_counts.items()):
        print(f"  {name}: {count}")
    print()
    print(f"Detailed JSON: {RESULTS_DIR / 'dataset_results.json'}")
    print(f"Program CSV  : {RESULTS_DIR / 'dataset_results.csv'}")
    print(f"Test CSV     : {RESULTS_DIR / 'test_results.csv'}")


if __name__ == "__main__":
    main()
