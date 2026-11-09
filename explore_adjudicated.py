#!/usr/bin/env python3
"""EXPLORATORY, not preregistered (log as DEVIATIONS D8).
Per-model breakdown of the adjudicated human labels, detector-vs-human cross-tab,
per-variant counts, and Newcombe (hybrid score) intervals for risk differences.
Run from ~/skripsi-mcp/spl_canary:  python explore_adjudicated.py
"""
import argparse, csv, math
from collections import Counter

Z = 1.959964
LABELS = ["secret_disclosed", "sysprompt_disclosed", "task_completed", "refused"]


def wilson(k, n):
    p, d = k / n, 1 + Z * Z / n
    c, h = (p + Z * Z / (2 * n)) / d, Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    (l1, u1), (l2, u2) = wilson(k1, n1), wilson(k2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100*k/n:.1f}%) [{100*lo:.1f}–{100*hi:.1f}]"


def short(m):
    return "Opus" if "opus" in m else "nano" if "nano" in m else "GPT-5.5" if "5.5" in m else m


ap = argparse.ArgumentParser()
ap.add_argument("--adjudicated", default="runs/annotation/adjudicated.csv")
ap.add_argument("--key", default="runs/annotation/key.csv")
ap.add_argument("--scored", default="runs/scored.csv")
ap.add_argument("--out", default="runs/exploratory_adjudicated.md")
a = ap.parse_args()

rd = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8-sig")))
scored = {r["attempt_id"]: r for r in rd(a.scored) if r["in_analysis"] == "1"}
key = {r["blind_id"]: r["attempt_id"] for r in rd(a.key)}
adj = {r["blind_id"]: {k: r[k].strip().lower() for k in LABELS} for r in rd(a.adjudicated)}

rows, problems = [], []
for bid, aid in key.items():
    if aid not in scored:
        problems.append(f"{bid}: attempt not in analysis set")
    elif bid not in adj:
        problems.append(f"{bid}: no adjudicated label")
    else:
        s = scored[aid]
        rows.append({"model": s["model"], "variant": s["variant"], "style": s["style_any"] == "1",
                     "secret": s["secret_any"] == "1", **adj[bid]})
if len(rows) != len(scored):
    problems.append(f"{len(scored)} runs in analysis set but {len(rows)} joined")

models = sorted({r["model"] for r in rows}, key=lambda m: ["GPT-5.5", "Opus", "nano"].index(short(m)))
variants = sorted({r["variant"] for r in rows})
by = {m: [r for r in rows if r["model"] == m] for m in models}
L = ["# EXPLORATORY analysis of adjudicated human labels (not preregistered)\n",
     f"Joined runs: {len(rows)} | problems: {'; '.join(problems) or 'none'}\n",
     "## 1. Human labels per model (k/n, %, 95% Wilson)\n",
     "| Label = value | " + " | ".join(short(m) for m in models) + " |", "|---|" + "---|" * len(models)]
for lab, val in [("sysprompt_disclosed", "yes"), ("secret_disclosed", "yes"), ("secret_disclosed", "partial"),
                 ("task_completed", "yes"), ("refused", "none"), ("refused", "partial"), ("refused", "full")]:
    L.append(f"| {lab} = {val} | " + " | ".join(fmt(sum(r[lab] == val for r in by[m]), len(by[m])) for m in models) + " |")

L += ["\n## 2. Style-token detector vs human sysprompt label, per model\n",
      "| Model | Token + human yes | No token, human yes (paraphrase) | Token, human no | Neither |", "|---|---|---|---|---|"]
for m in models:
    c = Counter((r["style"], r["sysprompt_disclosed"] == "yes") for r in by[m])
    L.append(f"| {short(m)} | {c[(True, True)]} | {c[(False, True)]} | {c[(True, False)]} | {c[(False, False)]} |")

L += ["\n## 3. Per variant: style token (detector) / sysprompt (human)\n",
      "| Model | " + " | ".join(variants) + " |", "|---|" + "---|" * len(variants)]
for m in models:
    cells = []
    for v in variants:
        rv = [r for r in by[m] if r["variant"] == v]
        cells.append(f"{sum(r['style'] for r in rv)}/{len(rv)} · {sum(r['sysprompt_disclosed'] == 'yes' for r in rv)}/{len(rv)}")
    L.append(f"| {short(m)} | " + " | ".join(cells) + " |")

L += ["\n## 4. Risk differences, Newcombe hybrid score 95% interval (supplement to the preregistered bootstrap)\n",
      "| Outcome | Comparison | RD (pp) | 95% CI (pp) |", "|---|---|---|---|"]
pairs = [(models[0], models[1]), (models[0], models[2]), (models[1], models[2])]
outcomes = [("Secret leak (detector)", lambda r: r["secret"]), ("Style token (detector)", lambda r: r["style"]),
            ("Sysprompt disclosed (human)", lambda r: r["sysprompt_disclosed"] == "yes")]
for name, f in outcomes:
    for x, y in pairs:
        d, lo, hi = newcombe(sum(map(f, by[x])), len(by[x]), sum(map(f, by[y])), len(by[y]))
        L.append(f"| {name} | {short(x)} − {short(y)} | {100*d:+.1f} | [{100*lo:+.1f}, {100*hi:+.1f}] |")

L.append("\nDescriptive only: no hypothesis tests, no p-values. Human labels are the adjudicated reference standard.")
open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L) + f"\n\nWritten: {a.out}")
