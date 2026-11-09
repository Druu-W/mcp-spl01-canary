#!/usr/bin/env python3
"""Final run accounting for the ORIGINAL experiment under one written rule.

Rule (applied identically to every cell):
  1. the six test cases in the paper x the three paper models;
  2. executed 23-30 Sep 2026, the window the submitted paper used;
  3. final harness only: file names that carry a variant (_V<n>_run); the earlier
     23 Sep files without a variant are pilot runs and are excluded;
  4. classifiable status only (success / max_iterations_reached);
  5. first classifiable attempt of each planned variant x run slot (by timestamp);
     later attempts of the same slot are re-executions and are excluded.
Planned design (paper, Section III): V1-V5 x 5 runs; TP-01 adds V6-V7.

Reads  results/accounting/all_attempts.csv (from run_accounting.py) and raw-logs/.
Writes results/accounting/analysis_set.csv and results/accounting/accounting_final.md.
"""
import csv
import re
from collections import Counter
from pathlib import Path

BASE = Path.home() / "skripsi-mcp/results"
ACC, RAW = BASE / "accounting", BASE / "raw-logs"
TCS = ["TP-01", "IPI-01", "SID-01", "EA-01", "SPL-01", "MIS-01"]
MODELS = {"nano": "GPT-5-nano", "gpt55": "GPT-5.5", "opus": "Opus"}
PAPER_N = {"TP-01": {"nano": 32, "gpt55": 69, "opus": 57}, "IPI-01": {"nano": 28, "gpt55": 27, "opus": 25},
           "SID-01": {"nano": 28, "gpt55": 27, "opus": 25}, "EA-01": {"nano": 30, "gpt55": 27, "opus": 25},
           "SPL-01": {"nano": 28, "gpt55": 27, "opus": 28}, "MIS-01": {"nano": 28, "gpt55": 27, "opus": 25}}
WINDOW = ("20260923", "20260930")
CLASSIFIABLE = {"success", "max_iterations_reached"}
RUNS = range(1, 6)


def planned(tc):
    return [(f"V{v}", r) for v in range(1, 8 if tc == "TP-01" else 6) for r in RUNS]


def compact(slots):
    by = {}
    for v, r in sorted(slots, key=lambda s: (int(s[0][1:]), s[1])):
        by.setdefault(v, []).append(str(r))
    return "; ".join(f"{v} r{','.join(rs)}" for v, rs in by.items()) or "—"


rows = list(csv.DictReader(open(ACC / "all_attempts.csv", newline="", encoding="utf-8")))
for r in rows:
    r["run"] = int(r["run"])
pilot = Counter(p.name.split("_")[0] for p in RAW.glob("*.json") if not re.search(r"_V\d+_run", p.name))

chosen_all, lines, tot = [], [], Counter()
lines += ["# Run accounting under one rule — original experiment\n",
          "Rule: six paper TCs × three models; executed 23–30 Sep 2026; final harness only (pilot files without a "
          "variant excluded); classifiable status only; first classifiable attempt per planned variant × run slot.\n",
          "## Paper scope\n",
          "| TC | Model | n in paper | Pilot (excluded) | Incomplete (excluded) | Re-executions (excluded) | "
          "Unplanned slots | **Analysed n** | Planned | Missing planned slots | Check |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
for tc in TCS:
    for key, name in MODELS.items():
        win = sorted((r for r in rows if r["tc"] == tc and r["key"] == key and WINDOW[0] <= r["date"] <= WINDOW[1]),
                     key=lambda r: r["ts"])
        incomplete = [r for r in win if r["status"] not in CLASSIFIABLE]
        first = {}
        for r in win:
            if r["status"] in CLASSIFIABLE:
                first.setdefault((r["variant"], r["run"]), r)
        reexec = sum(r["status"] in CLASSIFIABLE for r in win) - len(first)
        plan = planned(tc)
        analysed = [first[s] for s in plan if s in first]
        unplanned = [s for s in first if s not in plan]
        missing = [s for s in plan if s not in first]
        p = pilot[tc] if key == "nano" else 0
        paper = PAPER_N[tc][key]
        check = "ok" if p + len(win) == paper else f"paper − (pilot+window) = {paper - p - len(win)}"
        lines.append(f"| {tc} | {name} | {paper} | {p} | {len(incomplete)} | {reexec} | {len(unplanned)} | "
                     f"**{len(analysed)}** | {len(plan)} | {compact(missing)} | {check} |")
        for k, v in (("paper", paper), ("pilot", p), ("incomplete", len(incomplete)), ("reexec", reexec),
                     ("unplanned", len(unplanned)), ("analysed", len(analysed)), ("planned", len(plan)),
                     ("missing", len(missing))):
            tot[k] += v
        chosen_all += [{"tc": tc, "model": key, "variant": r["variant"], "run": r["run"], "file": r["file"],
                        "status": r["status"]} for r in analysed]
lines.append(f"| **Total** | | **{tot['paper']}** | {tot['pilot']} | {tot['incomplete']} | {tot['reexec']} | "
             f"{tot['unplanned']} | **{tot['analysed']}** | {tot['planned']} | {tot['missing']} slots | |\n")

late = Counter((r["tc"], r["key"], r["date"]) for r in rows
               if r["tc"] in TCS and r["key"] in MODELS and r["date"] > WINDOW[1])
other = Counter((r["tc"], r["model"], r["date"]) for r in rows if r["tc"] not in TCS or r["key"] not in MODELS)
lines += ["## Runs not in the paper's window or scope\n", "| Group | TC | Model | Date | Files |", "|---|---|---|---|---|"]
lines += [f"| After window | {tc} | {MODELS[k]} | {d} | {n} |" for (tc, k, d), n in sorted(late.items())]
lines += [f"| Other TC / model | {tc} | {m} | {d} | {n} |" for (tc, m, d), n in sorted(other.items())]
n_files = len(rows) + sum(pilot.values())
lines.append(f"\nAll files in raw-logs: {n_files} = paper scope and window {tot['paper']} + after window "
             f"{sum(late.values())} + other TC/model {sum(other.values())}.")

with open(ACC / "analysis_set.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["tc", "model", "variant", "run", "file", "status"])
    w.writeheader()
    w.writerows(chosen_all)
(ACC / "accounting_final.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"\nWritten: {ACC/'accounting_final.md'} and {ACC/'analysis_set.csv'} ({len(chosen_all)} runs)")
