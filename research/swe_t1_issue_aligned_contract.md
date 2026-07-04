# SWE-T1 Issue-Aligned Contract

Date: 2026-07-05

Evidence boundary: this pre-registers a future SWE-T1 revised scorer/test
path. It does not add task-success evidence, does not replace the current
paper-facing SWE-T1 row, and does not authorize promotion by itself.

Machine-readable source:
`benchmarks/real_reuse/swe_t1_issue_aligned_contract_v0.json`

## Why This Exists

The current SWE-T1 main row is frozen as boundary evidence. The first pass
failed because candidate patches did not apply. Phase107 fixed the patch-apply
boundary by giving both Summary and PaperToSkill the same locked source
context, but both candidates still failed the hidden test.

The task-contract diagnosis found that the scorer-only hidden test primarily
checks a specific L031 warning-message text change, while the model-visible
issue asks for a no-join TSQL alias false-positive fix. A future rerun should
therefore use an issue-aligned hidden check before spending model calls.

## Pre-Registered Check

The hidden check is:

`benchmarks/real_reuse/assets/SWE-T1/scorer_only/issue_aligned_check.py`

It runs after a candidate patch is applied to the locked SQLFluff workspace and
requires:

| Criterion | Expected Outcome |
| --- | --- |
| TSQL single-table query without alias | no L031 |
| TSQL single-table query with alias | no L031 |
| TSQL join query with aliases | L031 still appears |

The join query is a regression guard so a candidate cannot pass by disabling
L031 entirely.

## Future Rerun Rule

A future SWE-T1 issue-aligned rerun may be executed only if:

- Summary and PaperToSkill remain paired.
- Both conditions use GPT-family `gpt-5.5` unless this is an explicit LLM
  ablation.
- Both conditions use the same locked SQLFluff fixture, source context,
  scorer, resource budget, and no-mid-run-human rule.
- Scorer-only assets remain hidden from model prompts.
- Any paper-facing replacement requires explicit promotion through
  `results/real_reuse/main_run_selection.json`.
