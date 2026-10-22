import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# This file is in visualization/plots.py, so parent.parent is the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "plots"
PROGRAM_CSV = RESULTS_DIR / "dataset_results.csv"
TEST_CSV = RESULTS_DIR / "test_results.csv"
SUMMARY_JSON = RESULTS_DIR / "dataset_results.json"


def require_file(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Required results file was not found:\n{path}\n"
            "Run `python evaluate_dataset.py` from the project root first."
        )


def save_chart(fig, filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {OUTPUT_DIR / filename}")


def arithmetic_count_from_tac(tac):
    """
    Count TAC arithmetic instructions shaped like:
        t1 = a + b
        t2 = x * 5

    In a split instruction, the operator is parts[3], not parts[1].
    This helper is included for clarity/testing; the plots use the corrected
    arithmetic counts already written to dataset_results.csv.
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


def main():
    for path in (PROGRAM_CSV, TEST_CSV, SUMMARY_JSON):
        require_file(path)

    programs = pd.read_csv(PROGRAM_CSV)
    tests = pd.read_csv(TEST_CSV)
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    if programs.empty:
        raise ValueError("dataset_results.csv is empty.")
    if tests.empty:
        raise ValueError("test_results.csv is empty.")

    numeric_columns = [
        "original_instructions",
        "optimized_instructions",
        "instruction_reduction_percent",
        "original_arithmetic_operations",
        "optimized_arithmetic_operations",
        "original_temporaries",
        "optimized_temporaries",
        "optimization_time_seconds",
    ]
    for column in numeric_columns:
        if column in programs.columns:
            programs[column] = pd.to_numeric(programs[column], errors="coerce")

    # Validate the columns needed for each graph.
    required_program_columns = [
        "category",
        "instruction_reduction_percent",
        "original_instructions",
        "optimized_instructions",
        "original_arithmetic_operations",
        "optimized_arithmetic_operations",
        "original_temporaries",
        "optimized_temporaries",
        "optimization_time_seconds",
    ]
    missing_program_columns = [
        column for column in required_program_columns
        if column not in programs.columns
    ]
    if missing_program_columns:
        raise ValueError(
            "dataset_results.csv is missing columns: "
            + ", ".join(missing_program_columns)
        )

    if "passed" not in tests.columns:
        raise ValueError("test_results.csv is missing the 'passed' column.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Average instruction reduction by category.
    category_reduction = (
        programs.groupby("category")["instruction_reduction_percent"]
        .mean()
        .sort_values(ascending=False)
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(category_reduction.index, category_reduction.values)
    ax.set_title("Average TAC Instruction Reduction by Category")
    ax.set_xlabel("Benchmark Category")
    ax.set_ylabel("Average Instruction Reduction (%)")
    ax.tick_params(axis="x", labelrotation=22)
    for bar, value in zip(bars, category_reduction.values):
        ax.annotate(
            f"{value:.1f}%",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )
    save_chart(fig, "01_instruction_reduction_by_category.png")

    # 2. Average original vs optimized TAC instructions by category.
    instruction_means = programs.groupby("category")[
        ["original_instructions", "optimized_instructions"]
    ].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    instruction_means.plot(kind="bar", ax=ax, width=0.78)
    ax.set_title("Average TAC Instructions Before and After Optimization")
    ax.set_xlabel("Benchmark Category")
    ax.set_ylabel("Average Instructions per Program")
    ax.tick_params(axis="x", labelrotation=22)
    ax.legend(["Original", "Optimized"])
    save_chart(fig, "02_original_vs_optimized_instructions.png")

    # 3. Total arithmetic operations before and after optimization.
    # These values come from dataset_results.csv. To make them meaningful,
    # evaluate_dataset.py's arithmetic_count() must use parts[3] for the operator
    # in instructions like "t1 = a + b". Rerun evaluate_dataset.py first
    # after correcting that function.
    original_ops = int(
        programs["original_arithmetic_operations"].fillna(0).sum()
    )
    optimized_ops = int(
        programs["optimized_arithmetic_operations"].fillna(0).sum()
    )
    reduction_ops = (
        (original_ops - optimized_ops) / original_ops * 100
        if original_ops else 0.0
    )

    fig, ax = plt.subplots(figsize=(8, 5.5))
    values = [original_ops, optimized_ops]
    labels = ["Original", "Optimized"]
    bars = ax.bar(labels, values, width=0.55)
    ax.set_title("Total Arithmetic Operations Across 100 Programs")
    ax.set_ylabel("Total Arithmetic Operations")
    ax.set_ylim(0, max(values + [1]) * 1.22)
    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value:,}",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            fontsize=11,
        )
    ax.text(
        0.5,
        0.92,
        f"Reduction: {reduction_ops:.1f}%",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=11,
    )
    if original_ops == 0:
        ax.text(
            0.5,
            0.48,
            "No arithmetic operations were counted.\n"
            "Correct arithmetic_count() in evaluate_dataset.py\n"
            "and rerun the evaluator.",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
        )
    save_chart(fig, "03_arithmetic_operations.png")

    # 4. Average temporary variables before and after optimization by category.
    temporary_means = programs.groupby("category")[
        ["original_temporaries", "optimized_temporaries"]
    ].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    temporary_means.plot(kind="bar", ax=ax, width=0.78)
    ax.set_title("Average Temporary Variables Before and After Optimization")
    ax.set_xlabel("Benchmark Category")
    ax.set_ylabel("Average Temporary Variables per Program")
    ax.tick_params(axis="x", labelrotation=22)
    ax.legend(["Original", "Optimized"])
    save_chart(fig, "04_temporary_variables.png")

    # 5. Test results: show pass rate and exact counts clearly.
    passed_values = tests["passed"].astype(str).str.strip().str.lower()
    passed = int(passed_values.isin(["true", "1", "yes"]).sum())
    total = len(tests)
    failed = total - passed
    pass_rate = passed / total * 100 if total else 0.0

    fig, ax = plt.subplots(figsize=(8, 4.8))
    # A single horizontal bar emphasizes the pass rate; zero failures are
    # stated explicitly rather than relying on an invisible zero-height bar.
    ax.barh(["Correctness tests"], [pass_rate], height=0.48)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Pass Rate (%)")
    ax.set_title("Benchmark Correctness Validation")
    ax.set_yticks([0], ["420 unique test cases"])
    ax.text(
        min(pass_rate + 2, 101),
        0,
        f"{pass_rate:.1f}%",
        va="center",
        ha="left",
        fontsize=12,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.22,
        f"Passed: {passed}    Failed: {failed}    Total: {total}",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=11,
    )
    save_chart(fig, "05_test_pass_fail.png")

    # 6. Optimization-time distribution. These measurements are environment-dependent.
    times_ms = programs["optimization_time_seconds"].dropna() * 1000
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(times_ms, bins=15)
    ax.set_title("Distribution of Optimization Time")
    ax.set_xlabel("Optimization Time (milliseconds)")
    ax.set_ylabel("Number of Programs")
    save_chart(fig, "06_optimization_time_distribution.png")

    # Category-wise numerical summary for the report.
    rows = []
    for category, group in programs.groupby("category", dropna=False):
        rows.append(
            {
                "category": category,
                "programs": len(group),
                "average_original_instructions": round(
                    group["original_instructions"].mean(), 3
                ),
                "average_optimized_instructions": round(
                    group["optimized_instructions"].mean(), 3
                ),
                "average_instruction_reduction_percent": round(
                    group["instruction_reduction_percent"].mean(), 3
                ),
                "average_original_arithmetic_operations": round(
                    group["original_arithmetic_operations"].mean(), 3
                ),
                "average_optimized_arithmetic_operations": round(
                    group["optimized_arithmetic_operations"].mean(), 3
                ),
                "average_original_temporaries": round(
                    group["original_temporaries"].mean(), 3
                ),
                "average_optimized_temporaries": round(
                    group["optimized_temporaries"].mean(), 3
                ),
            }
        )

    pd.DataFrame(rows).to_csv(
        OUTPUT_DIR / "category_performance_summary.csv", index=False
    )

    summary_data = summary.get("summary", {})
    overall_reduction = programs["instruction_reduction_percent"].mean()
    overall_original = programs["original_instructions"].mean()
    overall_optimized = programs["optimized_instructions"].mean()

    report = {
        "programs": int(summary_data.get("programs", len(programs))),
        "unique_test_cases": int(summary_data.get("test_cases", len(tests))),
        "passed_tests": int(summary_data.get("passed", passed)),
        "failed_tests": int(summary_data.get("failed", failed)),
        "pass_rate_percent": float(
            summary_data.get("pass_rate_percent", pass_rate)
        ),
        "average_original_instructions_per_program": round(
            float(overall_original), 3
        ),
        "average_optimized_instructions_per_program": round(
            float(overall_optimized), 3
        ),
        "average_instruction_reduction_percent": round(
            float(overall_reduction), 3
        ),
        "total_original_arithmetic_operations": original_ops,
        "total_optimized_arithmetic_operations": optimized_ops,
        "arithmetic_operation_reduction_percent": round(reduction_ops, 3),
        "optimizer_firings": summary.get("optimizer_firings", {}),
        "note": (
            "Arithmetic operation counts depend on the corrected "
            "arithmetic_count() function in evaluate_dataset.py. "
            "Timing measurements depend on the machine and runtime environment."
        ),
    }
    (OUTPUT_DIR / "performance_summary.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    print("\nPERFORMANCE ANALYSIS COMPLETE")
    print(f"Programs analyzed: {len(programs)}")
    print(f"Test rows analyzed: {len(tests)}")
    print(f"Average original instructions/program: {overall_original:.2f}")
    print(f"Average optimized instructions/program: {overall_optimized:.2f}")
    print(f"Average instruction reduction: {overall_reduction:.2f}%")
    print(f"Total arithmetic operations: {original_ops} -> {optimized_ops}")
    if original_ops == 0:
        print(
            "WARNING: arithmetic counts are zero. Correct arithmetic_count() "
            "in evaluate_dataset.py and rerun it before trusting Plot 3."
        )
    print(f"Test pass rate: {passed}/{total} ({pass_rate:.2f}%)")
    print(f"Charts and summaries saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
