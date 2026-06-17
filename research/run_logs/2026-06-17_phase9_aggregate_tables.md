# Phase 9 Run Log: Aggregate Paper-Ready Tables

- Run ID: phase9_aggregate_tables
- Date: 2026-06-17
- Objective: aggregate existing deterministic/offline PaperToSkill evaluation
  JSON into paper-ready result tables.
- Command: `python scripts\aggregate_results_tables.py --output-dir results\tables`
- Expected output: Markdown and CSV tables for main results, transfer ablation,
  compactness/source grounding, plus a combined summary.
- Actual output:
  - `results/tables/main_results.md`
  - `results/tables/main_results.csv`
  - `results/tables/transfer_ablation.md`
  - `results/tables/transfer_ablation.csv`
  - `results/tables/compactness_source_grounding.md`
  - `results/tables/compactness_source_grounding.csv`
  - `results/tables/paper_ready_summary.md`
- Verification:
  - `python -m unittest tests.test_aggregate_results_tables -v`
- Result: aggregation succeeded and the smoke test passed.
- Evidence boundary: tables are generated from existing deterministic/offline
  result files and are not live agent-task evidence.
- Retain as case: yes.
