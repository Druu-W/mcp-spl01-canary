# SPL-01 canary rerun and run audit (ICIMCIS 2026, paper #1571372503, revision)

Materials for the major revision of "Comparative Evaluation of LLM Host Resilience Against
Model Context Protocol (MCP)-Based Attacks Using OWASP Top 10 for LLM Applications".

## 1. Preregistered SPL-01 canary rerun
- `PREREGISTRATION.md`: protocol, registered in commit 7f35d3a before the first API call
- `spl_canary_runner.py`, `analyze_canary.py`, `spl01_case.py`: unchanged since registration
- `runs/schedule.json`: 150 cells, seed 619451323 (SHA-256 in the protocol)
- `runs/pilot/`: connectivity pilot, excluded from analysis
- `runs/logs/`: all 150 attempts with full transcripts
- `runs/scored.csv`, `runs/stats.md`, `runs/stats.json`: preregistered analysis
- `runs/annotation/`: blinded sheets, codebook, both annotators' labels, adjudication log, adjudicated labels, key
- `runs/agreement_final.md`: inter-annotator agreement and detector validation
- `explore_adjudicated.py`, `runs/exploratory_adjudicated.md`: exploratory analysis (DEVIATIONS D8)
- `DEVIATIONS.md`: every departure from the protocol

## 2. Audit of the original experiment
- `run_accounting.py`, `original_audit/accounting_final.py`: attempted-run accounting
- `original_audit/recompute_asr.py`: ASR recomputed with the original detector functions, loaded verbatim
- `original_audit/recompute_stats.py`: GPT-5.5 vs Opus (Fisher and variant-stratified exact tests, Holm)
- `original_audit/*.md`, `*.csv`: outputs; `asr_per_run.csv` lists the score of every run
- `original_audit/posthoc_opus_full_context.txt`: post-hoc inspection of Opus SPL-01 outputs

The audit scripts expect the original logs at `~/skripsi-mcp/results/raw-logs`. Those raw logs are not
included yet because they contain provider-injected system content verbatim (protocol section 11);
they are available from the author on request.

All tokens in the canary system prompt are synthetic. No real credential appears anywhere.

Note: in `original_audit/accounting.md` and `accounting_final.md`, the name of one model used only in two
pilot runs outside the paper's scope was replaced with "other-model (pilot)". No counts were changed.
