# Interactive SWE ACI Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a development-only interactive SWE-T2 B/F/S adapter that enacts the SWE-agent ACI instead of generating one-shot patches.

**Architecture:** A path-safe in-memory overlay exposes bounded search, open, edit, test, and submit actions over the locked repository. A loop runner reconstructs each model turn from the common scaffold and recorded observations, invokes the existing hidden scorer without exposing scorer-only assets, and writes pair-traceable development artifacts.

**Tech Stack:** Python 3.12 standard library, existing PaperToSkill endpoint/scorer helpers, JSON/JSONL, SHA-256, unittest/pytest, git-compatible unified diffs.

---

### Task 1: Path-safe overlay workspace

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/src/effectslice/aci_workspace.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_aci_workspace.py`

- [ ] Write failing tests that create a tiny source tree and assert bounded
  `search`, line-window `open`, exact single replacement `edit`, overlay reads,
  deterministic unified diff, unchanged-file omission, traversal rejection,
  absolute-path rejection, missing-text rejection, and binary/oversize rejection.
- [ ] Run `python -m pytest -p no:cacheprovider tests/test_aci_workspace.py -q`
  and verify failures are caused by the missing module.
- [ ] Implement `OverlayWorkspace`, `WorkspaceError`, `SearchHit`, and
  `EditResult` with `resolve_relative`, `search`, `open_lines`, `replace_exact`,
  and `unified_diff` methods. Use `Path.resolve`, `relative_to`, bounded UTF-8
  reads, `difflib.unified_diff`, and no shell commands.
- [ ] Run the focused test file and verify it passes.

### Task 2: Frozen JSON action protocol

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/src/effectslice/aci_protocol.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_aci_protocol.py`

- [ ] Write failing tests for exact JSON and fenced JSON parsing, unknown
  actions, extra fields, missing fields, invalid types, search/open bounds,
  edit payload limits, submit/test shape, and malformed actions consuming one
  action in the loop state.
- [ ] Run the focused tests and verify RED.
- [ ] Implement immutable `ACIAction`, `ACIObservation`, and `ACILoopState`, plus
  `parse_action` and `validate_action`. Allow only `search`, `open`, `edit`,
  `test`, and `submit`; reject ambiguous multiple JSON objects.
- [ ] Run focused tests and verify GREEN.

### Task 3: Hidden scorer bridge

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/src/effectslice/swe_scorer_bridge.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_swe_scorer_bridge.py`

- [ ] Write a tiny repository, hidden test patch, passing candidate patch, and
  failing patch. Assert the bridge materializes only the candidate diff, calls
  `score_patch`, returns a sanitized observation, preserves the complete metric
  separately, truncates command output, and never includes hidden patch text or
  path in model-visible feedback.
- [ ] Run focused tests and verify RED.
- [ ] Implement `SWEScorerBridge.evaluate(diff_text)` using a run-local patch
  file and the existing `scripts/score_real_reuse_swe.py` helper. Return
  `ScorerEvaluation(model_feedback, metric, patch_path)`.
- [ ] Run focused tests and verify GREEN.

### Task 4: Interactive loop and model transport

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/src/effectslice/aci_runner.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_aci_runner.py`

- [ ] Write fake-model tests for search-open-edit-test-submit, malformed action
  recovery, edit failure feedback, provider failure, action exhaustion,
  submit-without-edit, scorer timeout, deterministic transcript order, and
  identical common scaffold hashes across conditions.
- [ ] Run focused tests and verify RED.
- [ ] Implement `InteractiveACIRunner` with a callable model transport, frozen
  action budget, transcript reconstruction, bounded observations, scorer bridge,
  cumulative provider usage, retry lineage, terminal reason codes, and complete
  transcript/result records.
- [ ] Run focused tests and verify GREEN.

### Task 5: SWE source atoms and candidates

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/build_swe_atom_map.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_build_swe_atom_map.py`
- Produce: `stage2/runs/effectslice_attempt_2/artifacts/swe_t2/source_atom_map.json`
- Produce: `stage2/runs/effectslice_attempt_2/artifacts/swe_t2/slice_v0.md`

- [ ] Write failing tests that bind every atom to exact UTF-8 byte and line
  spans in the complete SWE skill, validate the original file digest, validate
  dependency IDs, reject overlapping or missing spans, and reproduce slice text
  and context digests deterministically.
- [ ] Run focused tests and verify RED.
- [ ] Implement the nine atoms in the design, their dependency graph, one
  operational candidate, and every one-atom deletion neighbor. Do not infer
  source spans by fuzzy matching.
- [ ] Run the builder twice, compare digests, and run focused tests.

### Task 6: B/F/S development bundle runner

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/run_swe_effectslice.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_swe_effectslice_runner.py`

- [ ] Write failing tests for B/F/S context construction, common scaffold
  equality, prompt/context/artifact/scorer/source-commit digests, no credential
  persistence, condition-role validation, same action budget, retry lineage,
  output paths, and incomplete bundle failure.
- [ ] Run focused tests and verify RED.
- [ ] Implement the CLI using `InteractiveACIRunner`, the trusted GPT endpoint
  environment variables, maximum five retryable transport attempts, existing
  SWE-T2 task assets, and development-only pair manifests.
- [ ] Run focused tests and the entire attempt-2 suite.

### Task 7: Development aggregation and audit

**Files:**
- Create: `stage2/runs/effectslice_attempt_2/analyze_swe_development.py`
- Create: `stage2/runs/effectslice_attempt_2/tests/test_analyze_swe_development.py`
- Produce: `stage2/runs/effectslice_attempt_2/derived/swe_t2_development_summary.json`
- Produce: `stage2/runs/effectslice_attempt_2/derived/swe_t2_development_summary.md`

- [ ] Write failing tests for inclusion of all `swe_t2_*` manifests, failed or
  missing outcomes retained as failures, B/F/S contrasts, preservation,
  complete deletion-neighbor coverage, no candidate on mixed witnesses, and
  `scientific_claim_ready=false` for all development summaries.
- [ ] Run focused tests and verify RED.
- [ ] Implement deterministic aggregation and reason-coded abstention.
- [ ] Run focused and full tests, then build the empty pre-run summary.

### Task 8: Real development execution

**Files:**
- Produce under: `stage2/runs/effectslice_attempt_2/experiment_results/swe_t2_*`

- [ ] Verify the trusted endpoint variables are present without printing their
  values; verify source commit, scorer digest, task assets, and test command.
- [ ] Run one B/F development bundle with GPT-5.6. Retry only classified network,
  timeout, 429, 502, 503, or 504 failures under the same statistical unit.
- [ ] If F is objectively beneficial, run one F/S bundle and registered deletion
  neighbors; otherwise record `full_artifact_ineligible` and stop SWE discovery.
- [ ] Run at least one independent development repeat before calling the signal
  stable. Repeated calls on the single issue remain development observations,
  not independent held-out task cases.
- [ ] Regenerate the SWE development summary and classify SWE-T2 as candidate or
  abstention. Run the full test suite and preserve raw transcripts and metrics.

### Task 9: Stage routing decision

**Files:**
- Modify only after evidence: `stage2/pac_protocol_design.md`
- Produce when gate is met: `stage_report_2_3.json`

- [ ] Audit whether the interactive task has stable eligibility, preservation,
  deletion witnesses, equal budgets, no hidden leakage, and reproducible scoring.
- [ ] If any item fails, preserve SWE-T2 as an abstention case and route to the
  next objective task family without weakening thresholds post hoc.
- [ ] If all items pass, freeze the candidate and design genuinely new held-out
  paper-task populations before opening confirmation data.
- [ ] Do not mark Stage 2.3 passed until experiment attempts, failures, metrics,
  raw artifacts, and the held-out routing decision are reproducible and complete.

## Self-review

- The plan covers every design component and keeps hidden assets outside prompts.
- It contains no implementation placeholder or unbounded shell tool.
- Software tests and development experiments remain explicitly separate.
- Git commit steps are intentionally omitted because the user prohibited commits
  and pushes for this workflow.

