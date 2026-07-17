# SNAP-MFSE Reproduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run an API-first, objectively scored task that tests whether a source-grounded SnapATAC2 artifact helps reproduce the paper's matrix-free spectral embedding core.

**Architecture:** Reuse the bounded ACI and provider transport from EffectSlice attempt 2. Add a deterministic paper-card builder, a locked starter workspace, a numerical reference/case registry, a sanitized patch scorer, a SNAP-specific runner, and a development analyzer. Raw model bundles remain immutable; derived reports normalize only protocol-defined boundary cases.

**Tech Stack:** Python 3.12, NumPy 1.26, SciPy 1.13, pytest 9, existing EffectSlice ACI, DeepSeek Chat Completions, GPT Responses API.

**Git policy:** Do not commit or push. The user's standing instruction overrides the generic commit steps in the planning skill.

---

### Task 1: Build the source-grounded execution card

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/build_snap_mfse_artifacts.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_build_snap_mfse_artifacts.py`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/snap_mfse/full_artifact.md`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/snap_mfse/source_atom_map.json`

- [ ] **Step 1: Write the failing artifact-contract test**

The test imports `build_artifacts`, builds into a temporary directory, and asserts five atoms (`A01` through `A05`), exact source byte/line spans, dependency closure, a nonempty full artifact, stable SHA-256 digests, the paper IDF equation `log(n / (1 + df))`, the matrix-vector equation, and absence of Python/Rust reference code.

- [ ] **Step 2: Run the test and verify import failure**

Run:

```powershell
D:\anaconda3\anaconda\python.exe -m pytest tests\test_build_snap_mfse_artifacts.py -q -p no:cacheprovider
```

Expected: collection fails because `build_snap_mfse_artifacts` does not exist.

- [ ] **Step 3: Implement the deterministic builder**

Use fixed atom records derived from paper lines 74-79. Compute source spans from UTF-8 bytes, store the full paper digest, and render only source-grounded procedural statements. Define dependencies `A02 -> A01`, `A03 -> A02`, `A04 -> A03`, and `A05 -> A04`.

- [ ] **Step 4: Run the focused test and generate artifacts**

Expected: test passes and rerunning the builder produces byte-identical outputs.

### Task 2: Freeze numerical cases and the paper-equation oracle

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/src/effectslice/snap_mfse_cases.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_snap_mfse_cases.py`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/snap_mfse/case_registry.json`

- [ ] **Step 1: Write failing tests for the oracle and registry**

Tests cover the exact IDF formula, row normalization, zero-diagonal degree, descending dense eigenpairs, projection-invariant comparison, invalid inputs, deterministic case generation, disjoint block seeds, counts of 4/21/16/59, and stable registry digests.

- [ ] **Step 2: Verify the tests fail on missing APIs**

Expected missing functions: `paper_reference_embedding`, `generate_case`, `compare_embedding`, and `build_case_registry`.

- [ ] **Step 3: Implement minimal numerical APIs**

The dense oracle computes:

```python
idf = numpy.log(n_cells / (1.0 + numpy.count_nonzero(counts, axis=0)))
x = counts * idf
x = x / numpy.linalg.norm(x, axis=1, keepdims=True)
degree = x @ (x.T @ numpy.ones(n_cells)) - numpy.ones(n_cells)
x_tilde = x / numpy.sqrt(degree)[:, None]
w_tilde = x_tilde @ x_tilde.T - numpy.diag(1.0 / degree)
```

It then uses `numpy.linalg.eigh`, selects top eigenpairs in descending order, and returns the result. Case generation rejects matrices with zero rows, nonpositive degrees, or an insufficient eigengap.

- [ ] **Step 4: Generate and hash the case registry**

No raw model result enters the registry. Block membership and seeds are fixed before provider calls.

### Task 3: Create the locked starter workspace

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/task_workspaces/snap_mfse_v1/snap_core.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/task_workspaces/snap_mfse_v1/test_snap_core_public.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/snap_mfse/task_prompt.md`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_snap_mfse_workspace.py`

- [ ] **Step 1: Write failing workspace-contract tests**

Assert that the starter is incomplete, imports without side effects, exposes the required signature, contains no oracle values, and has a stable tree digest. Assert that the prompt names the API, input/resource contracts, 16-action horizon, and public verification command without including the MFSE equations.

- [ ] **Step 2: Create the minimal starter and public smoke test**

The starter validates the function signature but raises `NotImplementedError`. The public test checks only output shape and finite values on one tiny matrix; it does not disclose numerical expected values.

- [ ] **Step 3: Run the workspace tests**

Expected: workspace contract passes while the public task test fails with `NotImplementedError`.

### Task 4: Implement the objective patch scorer

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/src/effectslice/snap_mfse_scorer.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_snap_mfse_scorer.py`

- [ ] **Step 1: Write failing scorer tests**

Use known patches for a correct LinearOperator/eigsh implementation, a dense `x @ x.T` implementation, a wrong-IDF implementation, malformed patches, and exceptions. Assert per-case binary vectors, aggregate score, sanitized feedback, preserved private metrics, and no hidden source paths in model feedback.

- [ ] **Step 2: Implement patch application and isolated import**

Copy the starter workspace to a temporary directory, apply the unified diff with `git apply --unsafe-paths` disabled, import `snap_core.py` under a unique module name, run the selected case block, and discard the copy.

- [ ] **Step 3: Add matrix-free guards**

Parse the candidate with `ast` and reject direct construction patterns equivalent to `x @ x.T`, `numpy.dot(x, x.T)`, and explicit `(n_cells, n_cells)` dense allocation. Numerical scoring remains the primary endpoint; guard failures are separate hard constraints.

- [ ] **Step 4: Run focused integration tests**

Expected: correct patch passes all development cases; dense and wrong-equation patches fail deterministically.

### Task 5: Add the SNAP-MFSE ACI runner

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/run_snap_mfse_effectslice.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_snap_mfse_runner.py`

- [ ] **Step 1: Write failing manifest and fake-transport tests**

Assert B/F context separation, same common scaffold, visible 16-action horizon, provider metadata without credentials, source/card/case/scorer/workspace digests, block ID, retry lineage, and immutable raw output paths.

- [ ] **Step 2: Implement the runner by composing existing components**

Reuse `ProviderTransport`, `InteractiveACIRunner`, `OverlayWorkspace`, and the fixed action limits. Inject the SNAP scorer bridge and save `pair_manifest.json`, condition `run_result.json`, `transcript.json`, `candidate.patch`, and `run_report.json`.

- [ ] **Step 3: Run fake-transport end-to-end tests**

Expected: a scripted correct edit/test/submit path scores, credentials never serialize, and model feedback excludes case seeds and oracle values.

### Task 6: Analyze development eligibility without overclaiming

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/analyze_snap_mfse_development.py`
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_analyze_snap_mfse_development.py`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/derived/snap_mfse_development_summary.json`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/derived/snap_mfse_development_summary.md`

- [ ] **Step 1: Write failing classification tests**

Classify harness failures, provider failures, full-artifact ineligibility, a positive development signal, final-step scored-test normalization, identical patches, and the mandatory `scientific_claim_ready=false` boundary.

- [ ] **Step 2: Implement loading, classification, and report rendering**

Development can select whether to proceed to frozen eligibility but cannot certify EffectSlice.

### Task 7: Verify and run provider development bundles

**Files:**
- Update: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/configs/experiment_config.json`
- Preserve new raw bundles under: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/experiment_results/`

- [ ] **Step 1: Run the complete attempt-2 suite**

Run with the locked system NumPy plus project pytest environment. Expected: all tests pass; skips are documented.

- [ ] **Step 2: Run DeepSeek B/F on the development block**

The preserved provider-v1 bundles used `deepseek-v4-flash`, Chat Completions,
16 visible actions, a 4096 output-token cap, 240-second timeout, five
same-lineage retries, and no persisted credential. Both primary B bundles were
provider-inconclusive after repeated token-cap exhaustion. Run one v2 bundle
with only `max_tokens` raised to 8192 and record
`effectslice-deepseek-output-budget.v2`; do not change the task, artifact,
cases, scorer, action budget, thresholds, or retry policy.

- [ ] **Step 3: Run GPT B/F as robustness development evidence**

Use `gpt-5.6`, Responses API, the same task/card/scorer/action block, and matched retry policy.

- [ ] **Step 4: Generate the development audit and apply the stopping rule**

If neither model has a positive F-B signal, stop SNAP-MFSE and record abstention. If the primary model has a positive signal, freeze all digests and run the already registered 21-case eligibility block without changing task, thresholds, or action budget.

The first eligibility bundle is excluded because harness v1 left a final B
edit unscored and retained a stale intermediate score. Before rerunning, freeze
harness v2: keep 16 model-visible actions, then score a nonempty terminal diff
once after exhaustion without returning feedback to the model. Record the new
bundle separately and retain the v1 exclusion in the eligibility summary.

### Task 8: Self-review and evidence audit

**Files:**
- Update only derived documentation or tests required by findings.

- [ ] **Step 1: Inspect all new code and artifact diffs**

Check source attribution, secret hygiene, hidden-data isolation, scoring semantics, and preservation of raw bundles.

- [ ] **Step 2: Run the full suite again after any review fix**

Do not interpret provider results until this verification is green.

- [ ] **Step 3: Update the Stage 2 evidence ledger**

Record the task disposition, accepted raw artifacts, exclusions, and remaining requirements for Stage 2.3. Do not write `stage_report_2_3.json` as passed until the broader experiment gate is genuinely met.
