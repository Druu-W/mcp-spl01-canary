# API parameters, original experiment (23-30 Sep 2026)

- Harness: `original_scripts/test_runner.py` (OpenAI models) and `original_scripts/test_runner_claude.py` (Anthropic).
- OpenAI: `chat.completions.create`, models `gpt-5.5-2026-04-23` and `gpt-5-nano-2025-08-07`. No system message; no temperature, top_p, max tokens or reasoning parameters (provider defaults).
- Anthropic: `messages.create`, model `claude-opus-5-5`, `max_tokens = 4096`. No system prompt; no temperature or top_p.
- Tool loop: at most 20 iterations (`MAX_ITERATIONS = 20`); a run that hits the cap is logged as `max_iterations_reached`.
- Execution date and time of every run: in the log file names (see `accounting.md`, `analysis_set.csv`).

SPL-01 canary rerun (Nov 2026): see `PREREGISTRATION.md`, section 2.
