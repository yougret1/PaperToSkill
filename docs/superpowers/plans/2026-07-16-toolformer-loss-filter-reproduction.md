# Toolformer Loss-Filter Reproduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run an API-first, objectively scored task that tests whether a source-grounded Toolformer artifact helps reproduce the paper's API-call loss filter.

**Architecture:** Reuse the bounded ACI, provider transport, terminal scorer, and stage gates from SNAP-MFSE. Add an exact Toolformer paper-card builder, independent numerical oracle and frozen cases, isolated patch scorer, locked workspace, task runner, prefix registry, and development-to-confirmation analyzers. Raw bundles remain immutable and all provider-visible feedback excludes oracle values and case vectors.

**Tech Stack:** Python 3.12, NumPy 1.26, SciPy 1.13, pytest 9, existing EffectSlice ACI, DeepSeek Chat Completions, GPT Responses API.

**Git policy:** Do not commit or push. The user's standing instruction overrides generic commit steps.

---

### Task 1: Build Exact Source-Grounded Atoms

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/build_toolformer_filter_artifacts.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_build_toolformer_filter_artifacts.py`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/toolformer_filter/full_artifact.md`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/toolformer_filter/source_atom_map.json`

- [ ] **Step 1: Write a failing artifact contract test**

The test calls `build_artifacts(project_root, output_dir)` and asserts atoms
`T01` through `T05`, dependencies `T02->T01` through `T05->T04`, exact UTF-8
source spans from Toolformer lines 134-171 and 268-272, stable digests, the
weight schedule, `min` counterfactual, inclusive threshold, and absence of
Python reference code.

- [ ] **Step 2: Verify the test fails on the missing module**

```powershell
D:\anaconda3\anaconda\python.exe -m pytest tests\test_build_toolformer_filter_artifacts.py -q -p no:cacheprovider
```

Expected: collection fails with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the deterministic builder**

Define exact atom records and render only these source-grounded procedures:

```python
REQUIRES = {
    "T01": [],
    "T02": ["T01"],
    "T03": ["T02"],
    "T04": ["T03"],
    "T05": ["T04"],
}
```

Compute source byte offsets from `papers/extracted/toolformer.txt`; never copy
case values or implementation code into the card.

- [ ] **Step 4: Pass the focused test and generate byte-identical artifacts**

Run the focused test, run the builder twice in temporary directories, and
assert identical bytes.

### Task 2: Implement the Paper Oracle and Frozen Cases

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/src/effectslice/toolformer_filter_cases.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_toolformer_filter_cases.py`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/toolformer_filter/case_registry.json`

- [ ] **Step 1: Write failing oracle tests**

Test the intended API:

```python
keep, margin = paper_filter_api_calls(
    logp_with_result,
    logp_call_only,
    logp_no_call,
    tau_filter,
)
```

Assert normalized weights `max(0, 1-0.2*t)`, weighted negative log
likelihood, `min(no_call, call_only)`, `margin >= tau_filter`, batch shapes,
zero-weight tails, and invalid input rejection.

- [ ] **Step 2: Verify missing APIs fail**

Expected missing symbols: `paper_weights`, `paper_filter_api_calls`,
`generate_case`, and `build_case_registry`.

- [ ] **Step 3: Implement the minimal oracle**

```python
raw = np.maximum(0.0, 1.0 - 0.2 * np.arange(horizon))
weights = raw / raw.sum()
l_plus = -(logp_with_result * weights).sum(axis=1)
l_empty = -(logp_no_call * weights).sum(axis=1)
l_call_only = -(logp_call_only * weights).sum(axis=1)
margin = np.minimum(l_empty, l_call_only) - l_plus
keep = margin >= tau_filter
```

Reject empty, non-2D, shape-mismatched, nonfinite, positive log-probability
matrices and invalid thresholds.

- [ ] **Step 4: Freeze disjoint cases**

Generate deterministic blocks with counts `4/21/16/59`. Include comparator
reversals, uniform-weight traps, zero-tail perturbations, sign errors,
near-threshold values, exact ties, multiple candidates, and invalid inputs.
Store seeds and case data only in the private registry.

### Task 3: Create the Locked Workspace and Objective Scorer

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/task_workspaces/toolformer_filter_v1/toolformer_filter.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/task_workspaces/toolformer_filter_v1/test_toolformer_filter_public.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/toolformer_filter/task_prompt.md`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/src/effectslice/toolformer_filter_scorer.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_toolformer_filter_workspace.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_toolformer_filter_scorer.py`

- [ ] **Step 1: Write failing workspace and scorer tests**

Assert the starter exposes the exact signature and raises `NotImplementedError`;
the public test checks shape, dtype, and finite margins without numerical oracle
values. Scorer tests apply correct, uniform-weight, wrong-comparator,
strict-threshold, malformed, and exception patches.

- [ ] **Step 2: Implement the starter and public smoke test**

Keep the starter to one incomplete function. The task prompt states interface,
input contract, 16-action horizon, and public command without paper equations.

- [ ] **Step 3: Implement isolated scoring**

Copy the starter to a temporary workspace, apply the unified patch with bounded
paths, import under a unique module name, execute one frozen case block, and
compare Boolean masks exactly and margins with `rtol=1e-10`, `atol=1e-12`.

- [ ] **Step 4: Sanitize feedback**

Model feedback may contain only status, passed/total count, contract status,
failure category, and aggregate score. Assert transcripts cannot contain seeds,
case vectors, registry paths, or expected margins.

### Task 4: Add the Toolformer ACI Runner

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/run_toolformer_filter_effectslice.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_toolformer_filter_runner.py`
- Modify: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/configs/experiment_config.json`

- [ ] **Step 1: Write failing context, manifest, and fake transport tests**

Cover B/F/S context separation, provider/harness v2, block-specific evidence
boundaries, workspace/card/atom/case/scorer digests, credential exclusion,
terminal scoring, and raw `pair_manifest.json`, `run_result.json`, transcript,
and patch paths.

- [ ] **Step 2: Implement by composing existing ACI components**

Use `InteractiveACIRunner`, `OverlayWorkspace`, `ProviderTransport`, and the
Toolformer scorer bridge. Keep 16 actions, 8192 provider tokens, 240-second
timeout, and five same-lineage retries.

- [ ] **Step 3: Add slice and confirmation binding**

Validate candidate ID, artifact digest, prefix registry digest, retained atoms,
confirmation family digest, B/F/S conditions, and case block before calling the
provider.

- [ ] **Step 4: Pass fake transport end to end**

Script a correct edit/test/submit sequence and assert an objective score of 1.0
without secrets or private case data in serialized public artifacts.

### Task 5: Add Prefix, Eligibility, Discovery, and Confirmation Artifacts

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/build_toolformer_filter_slices.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/build_toolformer_filter_confirmation_family.py`
- Create tests with matching `test_*.py` names.
- Generate prefix registry, candidate Markdown files, and confirmation family under `artifacts/toolformer_filter/`.

- [ ] **Step 1: Write failing deterministic prefix tests**

Assert strict prefixes `T01`, `T01:T02`, `T01:T03`, and `T01:T04`, ascending
selection order, dependency closure, digests, and deletion closures to earlier
prefixes or B.

- [ ] **Step 2: Implement prefix generation and freeze before provider runs**

Candidate files contain only retained atom instructions. Registry contains no
model scores, case vectors, or selected candidate field.

- [ ] **Step 3: Write and implement confirmation family tests**

Require a locked discovery candidate and complete deletion audit. Bind B/F/S,
59 cases, alpha, confidence bounds, selected artifact, discovery summary, slice
registry, case registry, and hypothesis IDs before unsealing.

### Task 6: Implement Stage Analyzers

**Files:**
- Create `analyze_toolformer_filter_development.py`
- Create `analyze_toolformer_filter_eligibility.py`
- Create `analyze_toolformer_filter_discovery.py`
- Create `analyze_toolformer_filter_confirmation.py`
- Create one focused test file per analyzer.

- [ ] **Step 1: Test development classification**

Primary DeepSeek positive B/F may authorize eligibility; GPT-only signals are
robustness-only. Provider, harness, unscored-final, identical-patch, and
ineligible bundles remain distinct. `scientific_claim_ready` stays false.

- [ ] **Step 2: Test exact eligibility**

Require valid 21-case B/F vectors, `F-B >= delta_min`, and the configured
one-sided Clopper-Pearson lower bound. Exclude stale or mismatched bundles.

- [ ] **Step 3: Test ordered discovery and deletion audit**

Require paired F/S vectors, equivalence inside `epsilon`, hard constraints,
shortest-prefix selection, and every registered deletion closure to degrade by
`delta_delete` or fail a hard constraint.

- [ ] **Step 4: Test sealed confirmation**

Require exactly one family-matched B/F/S bundle, 59 cases, zero S/F mismatch,
beneficial S/B lower bound, preservation upper bound, and hard constraints.
Set task-local readiness only; keep general readiness false.

### Task 7: Verify and Run Provider Bundles

- [ ] **Step 1: Run the complete attempt-2 suite**

```powershell
$env:PYTHONPATH='D:\a_work\gitee\PaperToSkill\.venv\Lib\site-packages'
D:\anaconda3\anaconda\python.exe -m pytest tests -q -p no:cacheprovider
```

Expected: all tests pass before any provider interpretation.

- [ ] **Step 2: Run DeepSeek and GPT development B/F**

Preserve one immutable bundle per model family. Do not mix conditions across
bundles. DeepSeek is the only primary eligibility route.

- [ ] **Step 3: Apply the stopping rule**

If primary F is not beneficial, write abstention and stop the task. If it is,
run frozen 21-case eligibility.

- [ ] **Step 4: Run ordered discovery only after eligibility**

Run a discovery B/F baseline, then F/S prefixes in registry order. Stop at the
first equivalent candidate only when all deletion closures are already valid or
can be completed without exceeding `Q=24`.

- [ ] **Step 5: Freeze and run one sealed confirmation family**

Run B/F/S once on 59 cases. Do not rerun or alter the family after observing
outcomes except to classify explicit provider or harness failure under a new
protocol version.

### Task 8: Evidence Audit and Stage Integration

- [ ] **Step 1: Inspect all code, manifests, transcripts, and patches**

Check source spans, hidden-data isolation, credential exclusion, final-state
scoring, immutable raw bundles, case counts, digests, and claim boundaries.

- [ ] **Step 2: Run the full suite after every review fix**

No provider result is accepted until the current suite is green.

- [ ] **Step 3: Update Stage 2 summaries and reports**

Add Toolformer outcomes to baseline, research, and ablation summaries alongside
SNAP success and AIDE/SWE abstentions. Preserve task-local versus general claim
boundaries. Do not pass Stage 2.3 or 2.4 until all required artifacts parse and
their evidence is traceable.

## Plan Self-Review

- Every design requirement maps to a task above.
- No placeholder, unspecified error handling, or ambiguous function name remains.
- Oracle, scorer, runner, prefix, and analyzer signatures are consistent.
- The plan produces one testable subsystem and does not include full Toolformer training.
- Git commits are deliberately omitted under the user's standing policy.
