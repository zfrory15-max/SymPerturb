#!/usr/bin/env python3
from __future__ import annotations
import argparse
import pandas as pd


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--modules", required=True)
    args = p.parse_args()
    data = pd.read_csv(args.data)
    modules = pd.read_csv(args.modules)
    problems = []
    if data.empty:
        problems.append("data is empty")
    if data.columns.duplicated().any():
        problems.append("duplicate symptom names")
    if data.isna().any().any():
        problems.append("missing values detected; preprocess explicitly")
    if not {"symptom", "module"}.issubset(modules.columns):
        problems.append("modules CSV must contain symptom,module")
    else:
        missing = sorted(set(data.columns) - set(modules["symptom"].astype(str)))
        if missing:
            problems.append(f"module assignments missing for: {missing}")
    if problems:
        for x in problems:
            print(f"ERROR: {x}")
        return 2
    print(f"OK: n={len(data)}, p={len(data.columns)}; inputs pass structural checks")
    print("Still verify that higher values mean worse symptoms and anchors are clinically meaningful.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
