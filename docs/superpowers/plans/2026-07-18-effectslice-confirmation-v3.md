# EffectSlice Confirmation V3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, preregister, execute, and audit a Toolformer-based v3 calibration that uses one joint substitution event, admits a planted-redundancy strict subset, rejects the existing unstable prefix-01 subset, and hashes the full evidence chain.

**Architecture:** V3 is additive: it introduces pure decision/schedule helpers, a write-once family builder, a configurable Toolformer runner, a resumable scheduler, a final-only analyzer, and a hash-ledger validator. Existing confirmation v2 families and raw bundles remain immutable and are consumed only as the negative-control input. Provider inference uses the user-supplied endpoint labeled DeepSeek V3.2 through request alias `deepseek-v4-flash`; all local work stays on the commodity PC.

**Tech Stack:** Python 3.12, standard library, existing EffectSlice ACI runner/scorer modules, SciPy for iid-conditional reference bounds, pytest, JSON/SHA-256, PowerShell, DeepSeek-compatible chat-completions API.

---

## File Map

- Create `src/effectslice/confirmation_v3.py`: pure schedules, joint event, family validation, and file/canonical-text hashing.
- Create `build_confirmation_v3.py`: write-once identity/planted artifacts, v3 case registry, and bound family manifests.
- Create `run_toolformer_filter_confirmation_v3.py`: configurable B/F/S execution and confirmation-specific pair metadata.
- Create `run_confirmation_v3.py`: registered scheduler, resume semantics, and preserved failures.
- Create `analyze_confirmation_v3.py`: negative-control reanalysis, identity calibration, planted-control decision, and iid-conditional reference bound.
- Create `build_confirmation_v3_ledger.py`: raw-to-derived SHA-256 ledger and verifier.
- Create `tests/test_confirmation_v3.py`: pure decision and schedule tests.
- Create `tests/test_build_confirmation_v3.py`: artifact/family binding tests.
- Create `tests/test_toolformer_confirmation_v3_runner.py`: runner metadata and write-once tests.
- Create `tests/test_run_confirmation_v3.py`: scheduler and failure-preservation tests.
- Create `tests/test_analyze_confirmation_v3.py`: analyzer and negative-control tests.
- Create `tests/test_confirmation_v3_ledger.py`: ledger coverage and tamper-detection tests.
- Generate `artifacts/toolformer_filter/confirmation_v3/**`: registered inputs only.
- Generate `experiment_results/confirmation_v3/**`: write-once provider outputs only.
- Generate `derived/confirmation_v3/**`: reproducible summaries and ledgers.

### Task 1: Pure Joint Event and Schedule Semantics

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/src/effectslice/confirmation_v3.py`
- Test: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_confirmation_v3.py`

- [ ] **Step 1: Write failing truth-table and schedule tests**

```python
from effectslice.confirmation_v3 import balanced_schedule, joint_substitution_event


def condition(success: bool, score: float, hard: bool = True) -> dict:
    return {
        "success": success,
        "task_score": score,
        "hard_constraints_passed": hard,
        "private_score_count": 1,
        "private_feedback_exposed": False,
        "integrity_violations": [],
    }


def test_joint_event_requires_b_failure_and_successful_noninferior_f_and_s():
    assert joint_substitution_event(
        condition(False, 0.0), condition(True, 0.98), condition(True, 0.96)
    )
    assert joint_substitution_event(
        condition(False, 0.0), condition(True, 0.95), condition(True, 1.0)
    )
    assert not joint_substitution_event(
        condition(False, 0.0), condition(False, 0.1), condition(False, 0.1)
    )
    assert not joint_substitution_event(
        condition(False, 0.0), condition(True, 1.0), condition(True, 0.94)
    )
    assert not joint_substitution_event(
        condition(False, 0.0), condition(True, 1.0), condition(True, 1.0, hard=False)
    )


def test_schedules_balance_all_six_orders():
    identity = balanced_schedule(seed=2026071801, replicate_count=6)
    planted = balanced_schedule(seed=2026071802, replicate_count=18)
    assert len({tuple(row["condition_order"]) for row in identity}) == 6
    counts = {}
    for row in planted:
        key = tuple(row["condition_order"])
        counts[key] = counts.get(key, 0) + 1
    assert set(counts.values()) == {3}
```

- [ ] **Step 2: Run the tests and verify import failure**

Run:

```powershell
D:\anaconda3\anaconda\python.exe -m pytest tests/test_confirmation_v3.py -q
```

Expected: FAIL because `effectslice.confirmation_v3` does not exist.

- [ ] **Step 3: Implement the pure helpers**

```python
from __future__ import annotations

import hashlib
import itertools
import random
from pathlib import Path
from typing import Any


CONDITIONS = ("B", "F", "S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_canonical_text(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8").strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def balanced_schedule(seed: int, replicate_count: int) -> list[dict[str, Any]]:
    orders = list(itertools.permutations(CONDITIONS))
    if replicate_count <= 0 or replicate_count % len(orders):
        raise ValueError("replicate_count must be a positive multiple of six")
    rows = orders * (replicate_count // len(orders))
    random.Random(seed).shuffle(rows)
    return [
        {"replicate_id": f"r{index:03d}", "condition_order": list(order)}
        for index, order in enumerate(rows, start=1)
    ]


def _condition_valid(row: dict[str, Any]) -> bool:
    return (
        row.get("private_score_count") == 1
        and row.get("private_feedback_exposed") is False
        and row.get("hard_constraints_passed") is True
        and not row.get("integrity_violations")
    )


def joint_substitution_event(
    baseline: dict[str, Any],
    full: dict[str, Any],
    sliced: dict[str, Any],
    maximum_shortfall: float = 0.05,
) -> bool:
    if not all(_condition_valid(row) for row in (baseline, full, sliced)):
        return False
    return bool(
        not baseline.get("success")
        and full.get("success")
        and sliced.get("success")
        and float(sliced["task_score"]) >= float(full["task_score"]) - maximum_shortfall
    )
```

- [ ] **Step 4: Run tests and commit**

Expected: `2 passed`.

Commit only these two files with:

```powershell
git commit -m "feat: define EffectSlice v3 joint admission event"
```

### Task 2: Write-Once V3 Artifacts and Family Builder

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/build_confirmation_v3.py`
- Test: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_build_confirmation_v3.py`

- [ ] **Step 1: Write failing builder tests**

Test `build_family(control="identity")` produces six blocks and byte-identical
F/S digests. Test `build_family(control="planted")` produces 18 blocks, an F
artifact with `T06`, an S artifact equal to the original five-unit artifact, a
new 64-case registry, distinct `task_prompt_file_sha256` and
`task_prompt_canonical_text_sha256` fields, and `comparison_role` equal to
`registered_final_only_confirmation_v3`. Call the builder twice and assert the
second call raises `FileExistsError`.

- [ ] **Step 2: Run the tests and verify failure**

Run `D:\anaconda3\anaconda\python.exe -m pytest tests/test_build_confirmation_v3.py -q`.

Expected: FAIL because `build_confirmation_v3.py` does not exist.

- [ ] **Step 3: Implement builder inputs and outputs**

Use `Path.open("x")` for every registered file. Build the planted F artifact by
copying the five-unit artifact and adding this registered redundant unit:

```markdown
6. **Restate the shared selection invariant** (`T06`)
   Apply the same inclusive `margin >= tau_filter` rule independently to every
   proposed call and preserve the proposals' original order in the returned
   decisions. This restates the registered T04/T05 invariant and introduces no
   new computation.
```

Generate cases with the existing `toolformer_filter_cases` structured API and a
new seed/config identifier. Do not edit v2 case files. Bind the exact runner,
scorer, workspace tree, source map, cases, task prompt file bytes, canonical
task prompt text, F/S artifacts, schedule, thresholds, provider label, and
request alias.

- [ ] **Step 4: Run builder tests and commit**

Expected: all builder tests pass and no file outside a pytest temp directory is
created.

Commit with `feat: build write-once EffectSlice v3 families`.

### Task 3: Configurable Confirmation Runner

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/run_toolformer_filter_confirmation_v3.py`
- Test: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_toolformer_confirmation_v3_runner.py`

- [ ] **Step 1: Write failing runner tests**

Use a fake provider transport and the existing temporary Toolformer workspace.
Assert that the runner:

```python
assert manifest["schema_version"] == "effectslice-confirmation-v3-pair.v1"
assert manifest["comparison_role"] == "registered_final_only_confirmation_v3"
assert manifest["evidence_boundary"] == "registered_final_only_confirmation_v3"
assert manifest["task_prompt_file_sha256"] == sha256_file(task_prompt_path)
assert manifest["task_prompt_canonical_text_sha256"] == sha256_canonical_text(task_prompt_path)
assert manifest["private_score_policy"] == "final_only"
assert manifest["condition_execution_order"] == ["S", "F", "B"]
```

Also assert F and S are loaded from family-bound paths rather than hard-coded
artifact names, and that rerunning into an existing condition directory raises
`FileExistsError`.

- [ ] **Step 2: Run tests and verify failure**

Run `D:\anaconda3\anaconda\python.exe -m pytest tests/test_toolformer_confirmation_v3_runner.py -q`.

- [ ] **Step 3: Implement the runner**

Reuse `ProviderTransport`, `run_condition`, workspace digest helpers, and
Toolformer scorer plumbing from the existing runner. Do not alter the frozen v2
runner. Validate every family-bound file digest before the first provider call.
Build contexts as:

```python
contexts = {
    "B": NO_ARTIFACT_CONTEXT,
    "F": family_path(family, "full_artifact").read_text(encoding="utf-8"),
    "S": family_path(family, "selected_artifact").read_text(encoding="utf-8"),
}
```

Write pair manifest, transcript, candidate patch, run result, and scorer-call
artifacts with exclusive creation. Store response IDs, model fields, created
times, token usage, and retry lineage. Scoring remains terminal.

- [ ] **Step 4: Run runner tests and commit**

Expected: runner tests pass without network access.

Commit with `feat: add bound Toolformer v3 confirmation runner`.

### Task 4: Registered Scheduler and Failure Preservation

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/run_confirmation_v3.py`
- Test: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_run_confirmation_v3.py`

- [ ] **Step 1: Write failing scheduler tests**

Cover namespace construction, exact registered order, `max_workers <= 2`, resume
that preserves completed bundles, explicit failed records, and no replacement
replicate IDs. Assert progress counts equal registered schedule length.

- [ ] **Step 2: Run tests and verify failure**

Run `D:\anaconda3\anaconda\python.exe -m pytest tests/test_run_confirmation_v3.py -q`.

- [ ] **Step 3: Implement scheduler**

Follow v2's bounded worker pattern, but write
`effectslice-confirmation-v3-progress.v1`. A registered replicate may have only
`completed`, `failed`, or `preserved` status. Never generate a replacement ID.
Use separate output roots for `identity` and `planted` controls.

- [ ] **Step 4: Run scheduler tests and commit**

Commit with `feat: schedule write-once EffectSlice v3 controls`.

### Task 5: V3 Analyzer and V2 Negative-Control Reanalysis

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/analyze_confirmation_v3.py`
- Test: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_analyze_confirmation_v3.py`

- [ ] **Step 1: Write failing analyzer tests**

Create synthetic complete, failed, duplicate, and missing schedules. Assert:

```python
assert summary["primary_event"] == "joint_substitution_event"
assert summary["decision_basis"] == "finite_registered_schedule"
assert summary["independence_verified"] is False
assert summary["iid_conditional_reference"]["label"] == "iid_conditional_only"
assert summary["strict_subset_admitted"] is True
```

Test common F/S failure does not count as preservation, S better than F remains
eligible, any missing/duplicate/replaced block rejects integrity, and the real
v2 prefix-01 final summaries produce a negative-control rejection.

- [ ] **Step 2: Run tests and verify failure**

Run `D:\anaconda3\anaconda\python.exe -m pytest tests/test_analyze_confirmation_v3.py -q`.

- [ ] **Step 3: Implement analyzer**

Load only progress-registered bundles. For each condition require one score,
zero later model turns, no exposed pre-turn feedback, matching family/workspace
digests, expected response identity, and 64 cases. The planted decision is
`admit` only for 18/18 joint events plus integrity. Compute
`scipy.stats.beta.ppf(0.02, k, n-k+1)` under the explicit
`iid_conditional_only` label. Identity results are descriptive and cannot set
`strict_subset_admitted`.

- [ ] **Step 4: Run analyzer tests and commit**

Commit with `feat: analyze finite-schedule EffectSlice v3 admission`.

### Task 6: Full Evidence Hash Ledger

**Files:**
- Create: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/build_confirmation_v3_ledger.py`
- Test: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/tests/test_confirmation_v3_ledger.py`

- [ ] **Step 1: Write failing ledger tests**

Create a synthetic bundle with pair manifest, three transcripts, three patches,
three run results, scorer artifacts, summary, table JSON, and figure bytes.
Assert the ledger includes every relative path and SHA-256. Mutate one byte and
assert verification returns the exact mismatched path.

- [ ] **Step 2: Run tests and verify failure**

Run `D:\anaconda3\anaconda\python.exe -m pytest tests/test_confirmation_v3_ledger.py -q`.

- [ ] **Step 3: Implement ledger builder and verifier**

Use stable relative paths, sorted entries, file sizes, and SHA-256. Exclude API
keys, environment-variable values, caches, and LaTeX temporary files. Store the
ledger under `derived/confirmation_v3/evidence_hash_ledger.json` and a separate
verification report.

- [ ] **Step 4: Run ledger tests and commit**

Commit with `feat: verify EffectSlice v3 evidence hashes`.

### Task 7: Freeze and Validate V3 Registration

**Files:**
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/artifacts/toolformer_filter/confirmation_v3/**`
- Generate: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/confirmation_v3_public_preregistration.json`

- [ ] **Step 1: Run all v3 and inherited runner/scorer tests**

Run the six v3 test files plus Toolformer scorer, cases, workspace, ACI runner,
and v2 regression tests. Expected: all pass.

- [ ] **Step 2: Build identity and planted families with write-once outputs**

Run `build_confirmation_v3.py` once for each control. Record family, case,
artifact, runner, scorer, workspace, and schedule hashes in a public manifest
that contains no task prompt, hidden cases, endpoint, or credential.

- [ ] **Step 3: Independently validate registration**

Recompute all bound hashes, verify 6/18 schedules, confirm zero raw v3 bundles,
scan for credentials, and save `derived/confirmation_v3/preregistration_audit.json`.

- [ ] **Step 4: Commit the implementation and registration**

Stage only v3 code, tests, registered non-secret manifests/artifacts, and the
audit. Commit with `feat: preregister EffectSlice confirmation v3 calibration`.
Do not push hidden cases or private task content to a public remote.

### Task 8: Execute the Registered DeepSeek API Runs

**Files:**
- Generate: `experiment_results/confirmation_v3/identity/**`
- Generate: `experiment_results/confirmation_v3/planted/**`

- [ ] **Step 1: Load endpoint credentials without printing them**

Read the already user-approved local API documentation under
`C:\Users\Z\Desktop\论文\SelfPaper\LLMAPIDocument`; set only
`EFFECTSLICE_DEEPSEEK_BASE_URL` and `EFFECTSLICE_DEEPSEEK_API_KEY` in the child
process environment. Do not write credentials to disk or command output.

- [ ] **Step 2: Run the six-block identity schedule**

Invoke `run_confirmation_v3.py` with the frozen identity family, its dedicated
output root, and `--max-workers 2`. Poll progress until all six bundles are
completed or explicitly failed.

- [ ] **Step 3: Run the 18-block planted schedule**

Invoke the same scheduler with the frozen planted family and `--max-workers 2`.
Poll until all 18 bundles are completed or explicitly failed. Retry transport
only inside the registered five-attempt policy; never replace a replicate.

- [ ] **Step 4: Verify raw immutability**

Record counts, failed IDs, response-ID uniqueness, model fields, scorer counts,
feedback exposure, and file timestamps. Do not rerun a completed bundle.

### Task 9: Analyze, Gate, and Build the Calibration Evidence

**Files:**
- Generate: `derived/confirmation_v3/*_summary.json`
- Generate: `derived/confirmation_v3/*_summary.md`
- Generate: `derived/confirmation_v3/rule_comparison.json`
- Generate: `derived/confirmation_v3/evidence_hash_ledger.json`
- Generate: `figures/confirmation_v3/effectslice_v3_calibration.png`

- [ ] **Step 1: Run the v3 analyzer**

Require exact registered denominators, final-only scoring, zero integrity
violations, and explicit failure records. Never hand-edit results.

- [ ] **Step 2: Apply the frozen decision gate**

Pass only when the v2 prefix-01 negative control rejects and the planted strict
subset admits. Report identity separately. If the planted control fails, stop
before broad task expansion and preserve the failure.

- [ ] **Step 3: Build and verify the hash ledger**

Hash all raw and derived evidence, then run the verifier. Expected: zero missing
or mismatched paths.

- [ ] **Step 4: Generate one calibration figure from JSON**

Plot the negative control, identity calibration, and planted control with joint
event counts. Label CP values `iid-conditional reference`; do not label sessions
independent.

- [ ] **Step 5: Commit derived non-secret evidence**

Commit code, summaries, ledger, and figure separately from raw provider
transcripts. Use `data: record EffectSlice v3 calibration evidence`.

### Task 10: Manuscript and Stage-Report Revision

**Files:**
- Modify: `paper/effectslice_aaai/main_v2.tex`
- Regenerate: `paper/effectslice_aaai/generated_results.tex`
- Regenerate: `paper/effectslice_aaai/images/effectslice_v3_calibration.png`
- Create/update: `stage_report_2_1.json` through `stage_report_2_8.json`
- Create/update: `stage_report_2.json`
- Create/update: `review_text.txt`
- Create/update: `review_img_cap_ref.json`

- [ ] **Step 1: Rewrite the statistical claim**

Describe a finite registered schedule, one joint admission event, fresh provider
conversations, and an iid-conditional reference bound. Remove every claim that
provider independence was established.

- [ ] **Step 2: Add positive and negative calibration results**

State that identity is instrumentation calibration, planted redundancy is the
only positive strict-subset control, and v2 prefix-01 is the real unstable
negative control. Do not convert calibration into cross-paper effectiveness.

- [ ] **Step 3: Disclose v2 metadata and hard-contract facts**

Report the SNAP hard-contract failure, v2 prompt-hash naming ambiguity, and
legacy `development_triage` role as preserved metadata defects that do not alter
the registered v2 counts.

- [ ] **Step 4: Compile and verify**

Run pdflatex, bibtex, pdflatex twice, ChkTeX, PDF text checks, and visual
rendering within the AAAI page limit. Reject unresolved references, overfull boxes, clipped
figures, model-identity overclaims, or hand-written empirical values.

- [ ] **Step 5: Repeat cs-paper-read review**

Use structure and evidence analysts, then exactly three reviewers for technical
correctness, empirical reproducibility, and novelty/impact. Address factual and
traceability findings before style findings.

- [ ] **Step 6: Validate stage reports and commit**

Run the local pipeline artifact validator, full relevant pytest suite, hash
ledger verifier, and credential scan. Mark Stage 2 passed only if the rendered
manuscript and review gate pass; otherwise record the concrete blocker. Commit
with `docs: revise EffectSlice after v3 calibration`.
