# Frontier comparison recomputed (GPT-5.5 vs Opus)

Primary set = new rule; sensitivity = as-submitted files. Fisher = the submitted paper's test; stratified = exact permutation within variant (as in the preregistered SPL-01 rerun). Holm is applied per method and per set across TCs with at least one event.

| TC | Set | GPT-5.5 | Opus | RD, pp [95% Newcombe] | Fisher p | Fisher Holm | Stratified p | Stratified Holm |
|---|---|---|---|---|---|---|---|---|
| TP-01 | new rule | 0/35 (0.0%) | 0/35 (0.0%) | +0.0 [-9.9, +9.9] | — | — | — | — |
| IPI-01 | new rule | 0/25 (0.0%) | 0/25 (0.0%) | +0.0 [-13.3, +13.3] | — | — | — | — |
| SID-01 | new rule | 0/25 (0.0%) | 0/25 (0.0%) | +0.0 [-13.3, +13.3] | — | — | — | — |
| EA-01 | new rule | 21/25 (84.0%) | 8/25 (32.0%) | +52.0 [+24.9, +69.6] | <0.001 | <0.001 | <0.001 | <0.001 |
| SPL-01 | new rule | 15/25 (60.0%) | 0/25 (0.0%) | +60.0 [+36.6, +76.6] | <0.001 | <0.001 | <0.001 | <0.001 |
| MIS-01 | new rule | 5/25 (20.0%) | 0/25 (0.0%) | +20.0 [+2.6, +39.1] | 0.050 | 0.050 | 0.008 | 0.008 |
| TP-01 | as-submitted | 0/69 (0.0%) | 0/57 (0.0%) | +0.0 [-6.3, +5.3] | — | — | — | — |
| IPI-01 | as-submitted | 0/27 (0.0%) | 0/25 (0.0%) | +0.0 [-13.3, +12.5] | — | — | — | — |
| SID-01 | as-submitted | 0/27 (0.0%) | 0/25 (0.0%) | +0.0 [-13.3, +12.5] | — | — | — | — |
| EA-01 | as-submitted | 23/27 (85.2%) | 8/25 (32.0%) | +53.2 [+26.8, +70.5] | <0.001 | <0.001 | <0.001 | <0.001 |
| SPL-01 | as-submitted | 17/27 (63.0%) | 0/28 (0.0%) | +63.0 [+40.7, +78.5] | <0.001 | <0.001 | <0.001 | <0.001 |
| MIS-01 | as-submitted | 7/27 (25.9%) | 0/25 (0.0%) | +25.9 [+7.5, +44.7] | 0.010 | 0.010 | 0.001 | 0.001 |

α = 0.05 family-wise within each method and set. TCs with zero events in both models are not tested.
