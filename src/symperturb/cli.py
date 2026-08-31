from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import yaml

from .analysis import SymPerturbAnalyzer, load_config, save_result


def _mapping_csv(path: str, key: str, value: str) -> dict[str, object]:
    df = pd.read_csv(path)
    if key not in df.columns or value not in df.columns:
        raise ValueError(f"{path} must contain columns {key!r} and {value!r}")
    return dict(zip(df[key].astype(str), df[value]))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="symperturb",
        description="Run the SymPerturb reference virtual-perturbation workflow.",
    )
    p.add_argument("--data", required=True, help="CSV with rows=participants, columns=symptoms")
    p.add_argument("--modules", required=True, help="CSV columns: symptom,module")
    p.add_argument("--config", help="YAML analysis config")
    p.add_argument("--anchors", help="Optional CSV columns: symptom,anchor")
    p.add_argument("--weights", help="Optional CSV columns: symptom,weight")
    p.add_argument("--candidates", help="Optional text file with one candidate symptom per line")
    p.add_argument("--costs", help="Optional CSV columns: symptom,cost")
    p.add_argument("--out", required=True, help="Output directory")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    data = pd.read_csv(args.data)
    modules = _mapping_csv(args.modules, "symptom", "module")
    anchors = _mapping_csv(args.anchors, "symptom", "anchor") if args.anchors else None
    weights = _mapping_csv(args.weights, "symptom", "weight") if args.weights else None
    costs = _mapping_csv(args.costs, "symptom", "cost") if args.costs else None
    candidates = None
    if args.candidates:
        candidates = [x.strip() for x in Path(args.candidates).read_text(encoding="utf-8").splitlines() if x.strip()]
    config = load_config(args.config) if args.config else load_config(None)
    analyzer = SymPerturbAnalyzer(
        data,
        modules,
        anchors=anchors,
        symptom_weights=weights,
        candidate_targets=candidates,
        config=config,
        costs=costs,
    )
    result = analyzer.run()
    save_result(result, args.out)
    print(f"SymPerturb outputs written to: {args.out}")
    print("Interpret as model-derived target hypotheses, not causal treatment effects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
