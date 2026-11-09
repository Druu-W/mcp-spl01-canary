#!/usr/bin/env python3
"""Frontier comparison (GPT-5.5 vs Opus) per test case, original experiment.

Input : results/accounting/asr_per_run.csv (recompute_asr.py)
Sets  : new rule (in_new_rule == 1) = primary; as-submitted (all rows) = sensitivity
Per TC: k/n per model, risk difference with Newcombe hybrid-score 95% CI,
        Fisher exact two-sided p (the submitted paper's test),
        variant-stratified exact permutation p (model labels permuted within
        variant, conditional on per-variant margins; the preregistered SPL-01
        rerun uses the same test).
Holm across the TCs where a test is possible (at least one event), per method.
Both methods are reported for every TC; neither is chosen after seeing results.

Writes results/accounting/stats_recomputed.md
"""
import csv
import math
import re
from collections import defaultdict
from pathlib import Path

from scipy.stats import fisher_exact

ACC = Path.home() / "skripsi-mcp/results/accounting"
TCS = ["TP-01", "IPI-01", "SID-01", "EA-01", "SPL-01", "MIS-01"]
A, B = "gpt55", "opus"
Z = 1.959964


def wilson(k, n):
    p, d = k / n, 1 + Z * Z / n
    c, h = (p + Z * Z / (2 * n)) / d, Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    (l1, u1), (l2, u2) = wilson(k1, n1), wilson(k2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def hyper_pmf(N, K, n):
    return {x: math.comb(K, x) * math.comb(N - K, n - x) / math.comb(N, n) for x in range(max(0, n - (N - K)), min(K, n) + 1)}


def stratified_exact(strata):
    """strata: list of (k_a, n_a, k_b, n_b). Returns two-sided p for difference in overall proportions."""
    dist = {0: 1.0}
    for ka, na, kb, nb in strata:
        pmf = hyper_pmf(na + nb, ka + kb, na)
        new = defaultdict(float)
        for x, px in dist.items():
            for y, py in pmf.items():
                new[x + y] += px * py
        dist = new
    NA = sum(s[1] for s in strata)
    NB = sum(s[3] for s in strata)
    M = sum(s[0] + s[2] for s in strata)
    stat = lambda x: x / NA - (M - x) / NB
    obs = abs(stat(sum(s[0] for s in strata)))
    return min(1.0, sum(p for x, p in dist.items() if abs(stat(x)) >= obs - 1e-12))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [None] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


def fp(p):
    return "—" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")


rows = list(csv.DictReader(open(ACC / "asr_per_run.csv", newline="", encoding="utf-8")))
out = ["# Frontier comparison recomputed (GPT-5.5 vs Opus)\n",
       "Primary set = new rule; sensitivity = as-submitted files. Fisher = the submitted paper's test; "
       "stratified = exact permutation within variant (as in the preregistered SPL-01 rerun). "
       "Holm is applied per method and per set across TCs with at least one event.\n",
       "| TC | Set | GPT-5.5 | Opus | RD, pp [95% Newcombe] | Fisher p | Fisher Holm | Stratified p | Stratified Holm |",
       "|---|---|---|---|---|---|---|---|---|"]
for label, keep in (("new rule", lambda r: r["in_new_rule"] == "1"), ("as-submitted", lambda r: True)):
    res = []
    for tc in TCS:
        cell = defaultdict(lambda: [0, 0])
        for r in rows:
            if r["tc"] == tc and r["model"] in (A, B) and keep(r):
                m = re.search(r"_(V\d+)_run", r["file"])
                v = m[1] if m else "pilot"
                cell[(r["model"], v)][0] += int(r["hit"])
                cell[(r["model"], v)][1] += 1
        ka = sum(c[0] for (m, _), c in cell.items() if m == A)
        na = sum(c[1] for (m, _), c in cell.items() if m == A)
        kb = sum(c[0] for (m, _), c in cell.items() if m == B)
        nb = sum(c[1] for (m, _), c in cell.items() if m == B)
        testable = ka + kb > 0
        pf = fisher_exact([[ka, na - ka], [kb, nb - kb]])[1] if testable else None
        variants = sorted({v for (_, v) in cell})
        strata = [(cell[(A, v)][0], cell[(A, v)][1], cell[(B, v)][0], cell[(B, v)][1]) for v in variants
                  if cell[(A, v)][1] and cell[(B, v)][1]]
        dropped = [v for v in variants if not (cell[(A, v)][1] and cell[(B, v)][1])]
        ps = stratified_exact(strata) if testable else None
        res.append([tc, ka, na, kb, nb, pf, ps, dropped])
    idx = [i for i, r in enumerate(res) if r[5] is not None]
    hf = dict(zip(idx, holm([res[i][5] for i in idx])))
    hs = dict(zip(idx, holm([res[i][6] for i in idx])))
    for i, (tc, ka, na, kb, nb, pf, ps, dropped) in enumerate(res):
        d, lo, hi = newcombe(ka, na, kb, nb)
        note = f" (strata without both models dropped: {', '.join(dropped)})" if dropped else ""
        out.append(f"| {tc} | {label} | {ka}/{na} ({100*ka/na:.1f}%) | {kb}/{nb} ({100*kb/nb:.1f}%) | "
                   f"{100*d:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}] | {fp(pf)} | {fp(hf.get(i))} | {fp(ps)} | "
                   f"{fp(hs.get(i))}{note} |")
out.append("\nα = 0.05 family-wise within each method and set. TCs with zero events in both models are not tested.")
(ACC / "stats_recomputed.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out) + f"\n\nWritten: {ACC/'stats_recomputed.md'}")
