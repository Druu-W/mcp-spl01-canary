#!/usr/bin/env python3
"""
Attempted-run accounting for the ORIGINAL experiment (reviewer 2, point 3).

Reads every per-run JSON written by test_runner.py / test_runner_claude.py
(results/raw-logs) and reports, per test case x model:
  - attempted runs (one JSON file = one attempt) and their status
  - runs per variant and repeated run slots (same variant + run number run
    more than once, i.e. re-executions)
  - execution dates and whether variants ran sequentially or interleaved
  - the n reported in the paper next to the counts found in the logs

Nothing is modified. Usage:
  python run_accounting.py --raw-logs ~/skripsi-mcp/results/raw-logs --out-dir accounting
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

PAPER_TCS = ["TP-01", "IPI-01", "SID-01", "EA-01", "SPL-01", "MIS-01"]
PAPER_MODELS = {"nano": "gpt-5-nano-2025-08-07", "gpt55": "gpt-5.5-2026-04-23", "opus": "claude-opus-5-5"}
# n per cell as reported in the submitted paper (Table 3)
REPORTED_N = {
    "TP-01": {"nano": 32, "gpt55": 69, "opus": 57},
    "IPI-01": {"nano": 28, "gpt55": 27, "opus": 25},
    "SID-01": {"nano": 28, "gpt55": 27, "opus": 25},
    "EA-01": {"nano": 30, "gpt55": 27, "opus": 25},
    "SPL-01": {"nano": 28, "gpt55": 27, "opus": 28},
    "MIS-01": {"nano": 28, "gpt55": 27, "opus": 25},
}
NAME_RE = re.compile(r"^(?P<tc>[A-Z]+-\d+)_(?P<variant>V\d+)_run(?P<run>\d+)_(?P<date>\d{8})_(?P<time>\d{6})_(?P<model>.+)\.json$")


def model_key(model: str) -> str | None:
    m = model.lower().replace("_", "-").replace(".", "-")
    if "nano" in m and "gpt-5" in m:
        return "nano"
    if "opus" in m:
        return "opus"
    if "gpt-5-5" in m:
        return "gpt55"
    return None


def natural(s: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-logs", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    files = sorted(Path(args.raw_logs).expanduser().glob("*.json"))
    runs, skipped = [], []
    for f in files:
        m = NAME_RE.match(f.name)
        if not m:
            skipped.append(f.name)
            continue
        status, model, err = "unreadable", m["model"], ""
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            md = d.get("metadata", {})
            status = d.get("status") or "missing_status"
            model = md.get("model_requested") or model
            err = (d.get("error") or "")[:200]
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        runs.append({
            "file": f.name, "tc": m["tc"], "variant": m["variant"], "run": int(m["run"]),
            "date": m["date"], "ts": m["date"] + m["time"], "model": model, "key": model_key(model),
            "status": status, "error": err,
        })

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(out / "all_attempts.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "tc", "variant", "run", "date", "ts", "model", "key", "status", "error"])
        w.writeheader()
        w.writerows(runs)

    groups = defaultdict(list)
    for r in runs:
        groups[(r["tc"], r["model"])].append(r)

    cell_rows = []
    for (tc, model), rs in groups.items():
        by_var = defaultdict(list)
        for r in rs:
            by_var[r["variant"]].append(r)
        for v, vr in by_var.items():
            slots = defaultdict(int)
            for r in vr:
                slots[r["run"]] += 1
            cell_rows.append({
                "tc": tc, "model": model, "variant": v, "attempted": len(vr),
                "success": sum(r["status"] == "success" for r in vr),
                "error": sum(r["status"] == "error" for r in vr),
                "max_iterations": sum(r["status"] == "max_iterations_reached" for r in vr),
                "other": sum(r["status"] not in ("success", "error", "max_iterations_reached") for r in vr),
                "run_numbers": " ".join(str(k) for k in sorted(slots)),
                "repeated_slots": " ".join(f"run{k}x{c}" for k, c in sorted(slots.items()) if c > 1),
                "dates": " ".join(sorted({r["date"] for r in vr})),
            })
    cell_rows.sort(key=lambda r: (natural(r["tc"]), r["model"], natural(r["variant"])))
    with open(out / "by_variant.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cell_rows[0].keys()) if cell_rows else ["tc"])
        w.writeheader()
        w.writerows(cell_rows)

    def order_pattern(rs):
        seq = [r["variant"] for r in sorted(rs, key=lambda r: r["ts"])]
        changes = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
        distinct = len(set(seq))
        kind = "sequential by variant" if changes <= max(0, distinct - 1) * 2 else "interleaved"
        return f"{kind} ({changes + 1} variant blocks)"

    lines = ["# Run accounting — original experiment\n",
             f"Source: `{args.raw_logs}` — {len(runs)} run file(s) parsed, {len(skipped)} file(s) with other names skipped.\n",
             "## Paper scope (6 test cases × 3 models)\n",
             "| Test case | Model | Files (attempts) | success | error | max_iter | other | Repeated slots | "
             "Dates | Execution order | n in paper | Paper n − success |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    totals = defaultdict(int)
    for tc in PAPER_TCS:
        for key, model_name in PAPER_MODELS.items():
            rs = [r for (t, _), g in groups.items() if t == tc for r in g if r["key"] == key]
            succ = sum(r["status"] == "success" for r in rs)
            err = sum(r["status"] == "error" for r in rs)
            mx = sum(r["status"] == "max_iterations_reached" for r in rs)
            oth = len(rs) - succ - err - mx
            slots = defaultdict(int)
            for r in rs:
                slots[(r["variant"], r["run"])] += 1
            rep = sum(1 for c in slots.values() if c > 1)
            dates = ", ".join(sorted({r["date"] for r in rs})) or "—"
            rep_n = REPORTED_N.get(tc, {}).get(key)
            lines.append(f"| {tc} | {model_name} | {len(rs)} | {succ} | {err} | {mx} | {oth} | {rep} | {dates} | "
                         f"{order_pattern(rs) if rs else '—'} | {rep_n} | {rep_n - succ if rep_n is not None else '—'} |")
            totals["files"] += len(rs)
            totals["success"] += succ
            totals["reported"] += rep_n or 0
    lines.append(f"| **Total** | | **{totals['files']}** | **{totals['success']}** | | | | | | | "
                 f"**{totals['reported']}** | **{totals['reported'] - totals['success']}** |\n")

    outside = defaultdict(int)
    for r in runs:
        if r["tc"] not in PAPER_TCS or r["key"] is None:
            outside[(r["tc"], r["model"])] += 1
    if outside:
        lines += ["## Runs outside the paper scope (other test cases or models)\n",
                  "These must either be explained (pilot, discarded design, other model) or stay out of every count.\n",
                  "| Test case | Model | Files |", "|---|---|---|"]
        for (tc, model), n in sorted(outside.items(), key=lambda x: (natural(x[0][0]), x[0][1])):
            lines.append(f"| {tc} | {model} | {n} |")
        lines.append("")

    lines += ["## How to read this\n",
              "- One file = one attempted run; the runner writes a file for every attempt, including errors.",
              "- *Repeated slots* = the same variant and run number executed more than once (a re-execution). "
              "Explain each one in the paper: why it was rerun, and which file was counted.",
              "- *Paper n − success* ≠ 0 means the paper's n is not simply the number of successful files; "
              "write down the actual rule that produced the paper's n.",
              "- *Execution order* is inferred from file timestamps. `test_runner.py` loops variant by variant, "
              "so 'sequential by variant' is expected; the paper must not claim randomised order for these runs.",
              f"- Per-variant detail: `by_variant.csv`. Every file: `all_attempts.csv`."]
    (out / "accounting.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if skipped:
        print(f"\nSkipped (name did not match the runner pattern): {', '.join(skipped[:10])}"
              f"{' ...' if len(skipped) > 10 else ''}")


if __name__ == "__main__":
    main()
