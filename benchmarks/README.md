# Compiler Optimizer Benchmark Dataset

This folder is intended to replace the project's existing `benchmarks` folder.

## Contents
- `dataset.json`: dataset consumed by `evaluate_dataset.py`
- `dataset.csv`: spreadsheet-friendly view of the same 100 programs
- `source_programs/`: 100 source program files referenced by dataset.json
- `documentation/`: dataset documentation and summary

## Installation
Extract this archive into the project root (the same folder containing `main.py` and `evaluate_dataset.py`). Ensure the extracted folder is named `benchmarks`, so the final layout is:

```text
Automated-Compiler-Optimiser/
  evaluate_dataset.py
  main.py
  benchmarks/
    dataset.json
    dataset.csv
    README.md
    source_programs/
    documentation/
```

If Windows asks whether to merge/replace files, allow replacement. Do not place this folder inside another `benchmarks` or dataset-named folder.

Dataset source paths are relative to this folder, for example:
`source_programs/category_1_constant_expressions/C001.txt`
