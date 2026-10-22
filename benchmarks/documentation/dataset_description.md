# Dataset Description

## 1. Objective
The benchmark dataset is designed to systematically evaluate the Automated Rule-Based Compiler Code Optimizer.

## 2. Dataset size
- Total programs: 100
- Categories: 5
- Programs per category: 20
- Test inputs per program: 5
- Planned correctness checks: 500

## 3. Categories
### Category 1 — Constant Expressions
Programs contain arithmetic expressions whose operands are compile-time constants, allowing constant folding and propagation to be evaluated.

### Category 2 — Algebraic Redundancy
Programs contain identities such as `x + 0`, `x * 1`, `x - 0`, and `x * 0` to evaluate algebraic simplification.

### Category 3 — Dead Code
Programs contain assignments or computations whose results are not required by the final output, allowing dead-code elimination to be evaluated.

### Category 4 — Common Subexpressions
Programs intentionally repeat equivalent arithmetic expressions so that common-subexpression elimination can be measured.

### Category 5 — Loop-Based Programs
Programs contain `for` and `while` loops and arithmetic inside loops, providing cases for strength reduction and other optimization passes.

## 4. Data construction
The programs were custom-constructed for this compiler project. Each program is constrained to the syntax supported by the project's lexer and recursive-descent parser.

## 5. Reproducibility
Every benchmark has a unique identifier, source file, five test inputs, and expected output values. This makes the evaluation repeatable and allows the same benchmark set to be used for future experiments.

## 6. Review-1 status
The benchmark dataset constitutes the Phase-1 program-generation component of the proposed methodology. Automated evaluation and metric generation will use this dataset in the subsequent evaluation stage.
