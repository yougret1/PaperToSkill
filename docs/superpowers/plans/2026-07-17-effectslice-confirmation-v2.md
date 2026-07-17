# EffectSlice Confirmation V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace contaminated case-adaptive confirmation with write-once,
one-shot hidden scoring and run-level repeated evidence using the DeepSeek API.

**Architecture:** Extend the existing bounded ACI runner with a final-only
private-score policy, strengthen family digest validation, create diverse fresh
hidden suites, and orchestrate 18 randomized B/F/S replicates per task. Preserve
all v1 artifacts and derive v2 summaries only from new bundles.

**Tech Stack:** Python 3.12, pytest, NumPy/SciPy, PowerShell, JSON, SHA-256,
OpenAI-compatible Chat Completions, pdfLaTeX/BibTeX.

---

### Task 1: Final-Only Private Scoring

**Files:**
- Modify: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/src/effectslice/aci_runner.py`
- Modify: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_aci_runner.py`

- [ ] Add a failing test that constructs a runner with
  `private_score_policy="final_only"`, sends a `test` action, and asserts that
  the scorer bridge call count stays zero and the observation contains no
  scorer metric.
- [ ] Run `pytest tests/test_aci_runner.py -q` and verify the new test fails
  because the policy argument does not exist.
- [ ] Add the minimal policy validation and reject `test` without calling
  `_score`; keep `submit` and budget-final scoring terminal.
- [ ] Add a test asserting exactly one scorer call and no later model turn after
  `submit`.
- [ ] Run `pytest tests/test_aci_runner.py -q` and verify all runner tests pass.

### Task 2: Complete Family Binding

**Files:**
- Modify: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/run_snap_mfse_effectslice.py`
- Modify: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/run_toolformer_filter_effectslice.py`
- Modify: matching `tests/test_*_runner.py` files.

- [ ] Add failing tests that mutate a copied case registry, source map, slice
  registry, discovery summary, scorer, and task prompt one at a time and assert
  `load_confirmation_binding` rejects each mismatch.
- [ ] Run the two runner test modules and verify digest-mutation cases fail.
- [ ] Pass actual paths into `load_confirmation_binding`, recompute SHA-256, and
  compare every registered digest.
- [ ] Add `private_score_policy` and binding verification fields to manifests.
- [ ] Re-run the runner tests and verify all mutation cases pass.

### Task 3: Write-Once Run Directories

**Files:**
- Modify: both task runner scripts.
- Modify: matching runner tests.

- [ ] Add a failing test that pre-creates a nonempty output directory and
  expects `RunnerInputError` before transport construction.
- [ ] Verify the test fails because existing output is currently overwritten.
- [ ] Add `require_new_output_dir(path)` and call it before the first manifest
  write; allow a missing path only.
- [ ] Verify both runners reject reuse and their full tests pass.

### Task 4: Fresh Diverse Confirmation Suites

**Files:**
- Modify: `src/effectslice/snap_mfse_cases.py`
- Modify: `src/effectslice/toolformer_filter_cases.py`
- Modify: `tests/test_snap_mfse_cases.py`
- Modify: `tests/test_toolformer_filter_cases.py`
- Create derived v2 case registries under each task artifact directory.

- [ ] Add failing tests for a disjoint `confirmation_v2` block with 64 cases.
- [ ] Add failing Toolformer tests requiring at least six distinct oracle keep
  patterns, variable candidate counts, both boundary ties and strict failures,
  and no overlap with earlier case IDs.
- [ ] Verify the diversity tests fail under the v1 fixed pattern.
- [ ] Implement deterministic v2 generators without changing historical blocks.
- [ ] Generate registries, verify hashes, and run both case test modules.

### Task 5: V2 Family Manifests and Randomized Replicates

**Files:**
- Create: `build_*_confirmation_v2_family.py`
- Create: `run_confirmation_v2.py`
- Create: focused tests for family construction and scheduling.

- [ ] Add failing tests for 18 replicate IDs, balanced/randomized condition
  permutations, fixed thresholds, complete digests, and no historical output
  paths.
- [ ] Verify the tests fail because v2 builders do not exist.
- [ ] Implement builders and a scheduler that invokes one task/condition at a
  time, records the permutation, retries only registered transport failures,
  and resumes solely by absent replicate directories.
- [ ] Run scheduler tests, then commit and push protocol, source, tests, and
  sealed manifests before any provider execution.

### Task 6: Execute DeepSeek Confirmation V2

**Files:**
- Create: write-once raw bundles under `experiment_results/confirmation_v2/`.
- Create: progress and failure ledgers.

- [ ] Check that required endpoint environment variables are present without
  printing values.
- [ ] Run two transport smoke probes that contain no project data.
- [ ] Execute registered replicates with bounded concurrency and five-attempt
  transient retry; preserve every failed run.
- [ ] Verify each completed run has exactly one private scorer metric,
  `private_feedback_exposed=false`, a unique provider conversation lineage, and
  matching manifest digests.
- [ ] Resume only missing registered runs until all are complete or explicitly
  counted as failures.

### Task 7: Run-Level Analysis and Figures

**Files:**
- Create: v2 analyzers and tests.
- Modify: `build_stage2_summaries.py` and `build_stage2_figures.py` or create v2
  replacements if preserving old behavior is clearer.

- [ ] Add fixture tests proving cases are clustered within runs and CP bounds
  use 18 replicate indicators.
- [ ] Add tests that figures read summary JSON and contain no frozen empirical
  arrays.
- [ ] Implement baseline, research, and ablation summaries with explicit old-run
  exclusions and gate outcomes.
- [ ] Generate figures from accepted v2 summaries and verify data hashes.

### Task 8: Manuscript and Independent Review

**Files:**
- Modify: `paper/effectslice_aaai/main.tex`
- Create: `review_text.txt`, `review_img_cap_ref.json`, and revision notes.

- [ ] Rewrite claims around independent agent runs, one-shot hidden scoring,
  dependency-closure deletion, and provider alias transparency.
- [ ] Remove case-level probabilistic claims and all contaminated v1 results
  from confirmatory evidence.
- [ ] Run exactly three cs-paper-read reviewer agents: methodology, empirical
  reproducibility, and novelty/impact.
- [ ] Resolve every critical and major concern or state a narrow non-claim.
- [ ] Compile with pdfLaTeX/BibTeX, run text/format checks, render all pages, and
  inspect figures, tables, references, overlap, clipping, and page limit.

### Task 9: Stage Reports and Backup

**Files:**
- Create/update: `stage_report_2_7.json`, `stage_report_2_8.json`, and
  `stage_report_2.json`.

- [ ] Run the full Stage 2 test suite and artifact validators.
- [ ] Verify no credential, environment, cache, dependency directory, or
  unrelated user change is staged.
- [ ] Commit only the Stage 2 protocol, evidence, manuscript, review, and reports
  using scoped pathspecs.
- [ ] Push the current branch to `origin` and verify the remote revision.
