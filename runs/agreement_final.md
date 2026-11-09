# Annotation agreement and detector validation

## Inter-annotator agreement

| Label | Rows labelled by both | Observed agreement | Cohen's κ |
|---|---|---|---|
| secret_disclosed | 150 | 97.3% | 0.00 |
| sysprompt_disclosed | 150 | 94.0% | 0.88 |
| task_completed | 150 | 100.0% | 1.00 |
| refused | 150 | 88.0% | 0.70 |

## Detector validation

Reference standard: adjudicated labels from runs/annotation/adjudicated.csv.

| Detector | Human positive | n | TP | FP | FN | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|---|
| secret_any (exact/normalised) | secret_disclosed ∈ {yes} | 150 | 0 | 0 | 0 | 150 | n/a | n/a |
| secret_any (exact/normalised) | secret_disclosed ∈ {partial, yes} | 150 | 0 | 0 | 0 | 150 | n/a | n/a |
| style_any | sysprompt_disclosed ∈ {yes} | 150 | 23 | 0 | 55 | 72 | 100.0% | 29.5% |
| task_completed | task_completed ∈ {yes} | 150 | 87 | 0 | 0 | 63 | 100.0% | 100.0% |

31 disagreement(s) written to to_adjudicate.csv. Resolve them by discussion, fill the 'resolved' column, build an adjudicated sheet, and rerun.
