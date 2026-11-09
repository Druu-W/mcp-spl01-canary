# Run accounting — original experiment

Source: `/home/druuu/skripsi-mcp/results/raw-logs` — 901 run file(s) parsed, 41 file(s) with other names skipped.

## Paper scope (6 test cases × 3 models)

| Test case | Model | Files (attempts) | success | error | max_iter | other | Repeated slots | Dates | Execution order | n in paper | Paper n − success |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TP-01 | gpt-5-nano-2025-08-07 | 21 | 21 | 0 | 0 | 0 | 0 | 20260923 | sequential by variant (5 variant blocks) | 32 | 11 |
| TP-01 | gpt-5.5-2026-04-23 | 107 | 106 | 0 | 0 | 1 | 31 | 20260928, 20260929, 20261022 | interleaved (25 variant blocks) | 69 | -37 |
| TP-01 | claude-opus-5-5 | 57 | 56 | 0 | 0 | 1 | 21 | 20260929, 20260930 | interleaved (14 variant blocks) | 57 | 1 |
| IPI-01 | gpt-5-nano-2025-08-07 | 22 | 22 | 0 | 0 | 0 | 0 | 20260928 | sequential by variant (5 variant blocks) | 28 | 6 |
| IPI-01 | gpt-5.5-2026-04-23 | 27 | 27 | 0 | 0 | 0 | 2 | 20260928, 20260929 | sequential by variant (6 variant blocks) | 27 | 0 |
| IPI-01 | claude-opus-5-5 | 25 | 25 | 0 | 0 | 0 | 0 | 20260930 | sequential by variant (5 variant blocks) | 25 | 0 |
| SID-01 | gpt-5-nano-2025-08-07 | 22 | 22 | 0 | 0 | 0 | 0 | 20260928 | sequential by variant (5 variant blocks) | 28 | 6 |
| SID-01 | gpt-5.5-2026-04-23 | 61 | 60 | 0 | 0 | 1 | 25 | 20260928, 20260929, 20261021, 20261022 | interleaved (18 variant blocks) | 27 | -33 |
| SID-01 | claude-opus-5-5 | 25 | 25 | 0 | 0 | 0 | 0 | 20260930 | sequential by variant (5 variant blocks) | 25 | 0 |
| EA-01 | gpt-5-nano-2025-08-07 | 24 | 22 | 0 | 2 | 0 | 2 | 20260928 | sequential by variant (5 variant blocks) | 30 | 8 |
| EA-01 | gpt-5.5-2026-04-23 | 27 | 27 | 0 | 0 | 0 | 2 | 20260928, 20260929 | sequential by variant (6 variant blocks) | 27 | 0 |
| EA-01 | claude-opus-5-5 | 25 | 25 | 0 | 0 | 0 | 0 | 20260930 | sequential by variant (5 variant blocks) | 25 | 0 |
| SPL-01 | gpt-5-nano-2025-08-07 | 22 | 22 | 0 | 0 | 0 | 0 | 20260928 | sequential by variant (5 variant blocks) | 28 | 6 |
| SPL-01 | gpt-5.5-2026-04-23 | 27 | 27 | 0 | 0 | 0 | 2 | 20260928, 20260929 | sequential by variant (6 variant blocks) | 27 | 0 |
| SPL-01 | claude-opus-5-5 | 28 | 28 | 0 | 0 | 0 | 3 | 20260930 | sequential by variant (6 variant blocks) | 28 | 0 |
| MIS-01 | gpt-5-nano-2025-08-07 | 22 | 22 | 0 | 0 | 0 | 0 | 20260928 | sequential by variant (5 variant blocks) | 28 | 6 |
| MIS-01 | gpt-5.5-2026-04-23 | 27 | 27 | 0 | 0 | 0 | 2 | 20260928, 20260929 | sequential by variant (6 variant blocks) | 27 | 0 |
| MIS-01 | claude-opus-5-5 | 25 | 25 | 0 | 0 | 0 | 0 | 20260930 | sequential by variant (5 variant blocks) | 25 | 0 |
| **Total** | | **594** | **589** | | | | | | | **563** | **-26** |

## Runs outside the paper scope (other test cases or models)

These must either be explained (pilot, discarded design, other model) or stay out of every count.

| Test case | Model | Files |
|---|---|---|
| EA-02 | claude-opus-5-5 | 25 |
| EA-02 | gpt-5-nano-2025-08-07 | 25 |
| EA-02 | gpt-5.5-2026-04-23 | 25 |
| MIS-02 | claude-opus-5-5 | 25 |
| MIS-02 | gpt-5-nano-2025-08-07 | 25 |
| MIS-02 | gpt-5.5-2026-04-23 | 25 |
| SID-02 | claude-opus-5-5 | 25 |
| SID-02 | gpt-5-nano-2025-08-07 | 25 |
| SID-02 | gpt-5.5-2026-04-23 | 25 |
| SPL-01 | claude-sonnet-5-5 | 3 |
| SPL-01 | gpt-4.1 | 1 |
| SPL-01 | other-model (pilot) | 2 |
| SPL-02 | claude-opus-5-5 | 25 |
| SPL-02 | gpt-5-nano-2025-08-07 | 25 |
| SPL-02 | gpt-5.5-2026-04-23 | 25 |
| TP-01 | claude-sonnet-5-5 | 1 |

## How to read this

- One file = one attempted run; the runner writes a file for every attempt, including errors.
- *Repeated slots* = the same variant and run number executed more than once (a re-execution). Explain each one in the paper: why it was rerun, and which file was counted.
- *Paper n − success* ≠ 0 means the paper's n is not simply the number of successful files; write down the actual rule that produced the paper's n.
- *Execution order* is inferred from file timestamps. `test_runner.py` loops variant by variant, so 'sequential by variant' is expected; the paper must not claim randomised order for these runs.
- Per-variant detail: `by_variant.csv`. Every file: `all_attempts.csv`.
