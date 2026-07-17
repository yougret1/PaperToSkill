# Interactive SWE ACI Development Adapter

## Decision

Use a real, bounded agent-computer-interface loop for SWE-T2 development. The
existing one-shot Summary/PaperToSkill patch comparison remains a diagnostic
signal only because the model could not actually inspect, edit, or test the
repository. It cannot establish that the SWE-agent ACI mechanism caused the
observed score difference.

## Scope

This adapter is development-only. It may select or reject EffectSlice
candidates, but it cannot support a sealed confirmation claim. It uses the
existing locked Astropy SWE-bench Verified instance, scorer, hidden test patch,
base commit, and task prompt.

## Conditions

- `B`: the common ACI action contract with no paper-derived procedural context.
- `F`: the same action contract plus the complete SWE-agent paper skill.
- `S`: the same action contract plus one source-grounded candidate slice.

All conditions receive identical task text, action names, budgets, scorer,
failure handling, model settings, retry policy, and observation limits.

## Architecture

### Read-only source with an overlay

The model never writes the locked repository. `OverlayWorkspace` reads files
from the source snapshot and stores exact-replacement edits in memory. It
validates normalized relative paths, rejects traversal and symlink escapes,
limits file and observation sizes, and generates a unified diff from the
overlay.

### Bounded ACI protocol

Every model turn returns one JSON action:

- `search`: literal repository text search with a bounded result count.
- `open`: bounded line-window inspection.
- `edit`: exact old-text replacement in one source file.
- `test`: score the current overlay through the hidden scorer.
- `submit`: finish and score the final patch.

Malformed actions consume an action and return concise corrective feedback.
The loop has a frozen maximum action count. A missing submit, invalid patch,
provider failure, timeout, or exhausted retry is retained as a failed outcome.

### Hidden scorer boundary

The hidden test patch and gold patch never enter a model prompt, transcript, or
tool observation. `test` materializes only the candidate diff and invokes the
existing `score_real_reuse_swe.score_patch` function against the clean source.
The model receives a sanitized result containing pass/fail, failure class, and
bounded public command output. The full metric is preserved outside the prompt.

### Pair traceability

Each B/F/S development bundle records pair ID, case ID, seed block, model alias,
source commit, scorer/test/artifact/context/prompt digests, retry lineage, action
transcript, candidate patch, scorer output, timing, token use, and failure class.
Credentials and authorization headers are never persisted.

## Initial SWE Atoms

The complete source skill is compiled into source-span-bound procedure atoms:

1. ACI framing and state/feedback discipline.
2. Simple actions with concise observations.
3. ReAct search, inspect, edit, execute loop.
4. Repository localization by bounded search.
5. Bounded line-window inspection.
6. Focused edits followed by immediate inspection.
7. Invalid-edit and lint/test guardrails.
8. Context, error, and history management.
9. Objective test, resolved-rate, and budget validation.

Candidate slices must be strict, nonempty, source-grounded, and dependency
closed. Development starts with a compact operational candidate containing
localization, inspection, focused edit, guardrail, and objective validation.
Every retained atom must have a registered deletion neighbor before a candidate
can advance.

## Acceptance and Falsification

Development may advance only if repeated B/F/S bundles show:

- `F` is beneficial over `B` on the objective scorer;
- `S` preserves `F` within the frozen development margin;
- every registered deletion neighbor loses the required effect or violates a
  frozen contract;
- the result is not explained by prompt leakage, hidden-test exposure, unequal
  action budgets, patch-format differences, or scorer instability.

Otherwise SWE-T2 becomes an explicit abstention/failure case and the workflow
moves to another objective task family. No repeated call on this single issue is
treated as an independent held-out task instance or population-level evidence.

## Model and Compute Boundary

GPT-5.6 is the main development model. Qwen2.5-Coder-7B-Instruct Q4_K_M is the
reproducible low-resource model when its verified GGUF is available, using an
8-12K context and the existing 8GB GPU. No 80GB GPU is required. A second local
model is not required for this adapter.

## Testing

Unit tests use tiny local repositories and fake model responses. They must cover
path escape rejection, exact edit behavior, deterministic diff generation,
bounded search/open observations, action parsing, malformed-action budget use,
hidden scorer isolation, transcript persistence, identical B/F/S scaffold, and
reason-coded failure. Live endpoint and Astropy runs are separate development
experiments, never software tests.

