# EffectSlice Stage 2 Pilot Design

## Goal

Build a deterministic, no-new-dependency pilot that answers two development questions before any expensive campaign:

1. Can the eligibility and admission gates be implemented with explicit, testable abstention behavior?
2. Are the existing eight PaperToSkill real-reuse tasks sufficiently instrumented to enter an EffectSlice certificate run?

The pilot does not estimate EffectSlice effectiveness and does not use synthetic fixtures as scientific evidence.

## Chosen Route

Route A is a local certificate-core and readiness pilot. Existing project artifacts are read-only. New source, tests, logs, summaries, and pilot outputs live only under this Stage 2 run.

No external repository, model, API, package, or dataset is downloaded in this pilot. Python 3.12 standard-library code and `unittest` are sufficient.

## Architecture

- `effectslice.models`: immutable observation, candidate, decision, and manifest records with strict validation.
- `effectslice.statistics`: bounded paired Hoeffding intervals and Holm family rejection.
- `effectslice.admission`: full-artifact eligibility and strict nonempty slice admission with reason-coded abstentions.
- `effectslice.readiness`: read-only audit of the current eight task specs, main-row selections, raw rows, and source maps.
- `run_pilot.py`: produces one evidence-boundary-preserving readiness report plus required baseline/research/ablation summaries.

The scientific data path and the software-validation path remain separate. Real current artifacts may support readiness counts only. Hand-authored test fixtures validate code behavior only.

## Frozen Pilot Decisions

### S1: Score and Statistical Interface

- A task adapter must provide paired case-level net-utility differences and declare finite lower/upper bounds.
- Net utility is primary score improvement minus preregistered normalized compute, API, labor, and guardrail penalties.
- The complete artifact is eligible only when a one-sided Hoeffding lower bound is strictly greater than `delta_min` and every deterministic contract/guardrail predicate passes.
- Slice equivalence uses a two-sided Hoeffding interval and also registers the two one-sided equivalence p-values inside a Holm-corrected family.
- Aggregate task scores, single runs, missing cost conversion, or absent paired case identifiers cause abstention; they are never expanded into pseudo-replicates.

### S10: Candidate Ordering

Surviving candidates are totally ordered by:

1. fewer retained SCC units;
2. larger discovery margin `M_tau`;
3. lower normalized local cost;
4. lexicographically sorted atom identifiers.

This is a pilot choice and does not establish global minimality.

### S11: Baseline Normalization

Any compact-artifact baseline that cannot be deterministically mapped to the same atom/source/executable/contract schema is counted as an abstention and remains in the denominator. It is not silently excluded and is not scored as a false admission.

### S12: Held-Out Boundary

The current eight tasks are development-only. This pilot creates no held-out pair and no confirmatory claim. A future registry must be frozen before execution and include at least four new papers not used to design the extractor, task contracts, scorers, or admission code. Selection requires public source material, an executable task asset, a locked objective scorer, a complete skill/source map, and no overlap with the development paper-task rows.

## Current-Data Readiness Criteria

Each task must have all of the following before a certificate run:

- same-scaffold no-skill baseline `B`;
- at least three paired eligibility seeds for `F` and `B`;
- case-level paired observations with stable pair identifiers;
- explicit score bounds and cost-conversion weights;
- four-way atoms with workflow step, exact source span, executable region, and one contract role;
- a declared dependency graph and complete final-neighbor budget;
- immutable contract and guardrail predicates.

The audit reports every missing criterion per task. A task is ready only when no criterion is missing.

## Error Handling

All expected scientific failures return stable reason codes such as `insufficient_paired_evidence`, `missing_no_skill_baseline`, `ambiguous_atomization`, `no_validated_beneficial_effect`, `empty_slice`, `not_strict_subset`, `insufficient_query_budget`, or `confirmation_family_failed`. Invalid file formats raise a separate execution error and are recorded in the pilot log.

## Testing

TDD covers:

- bounded interval validation and numerical behavior;
- Holm rejection at pass/fail boundaries;
- full-effect eligibility, including minimum pairs and strict lower-bound comparison;
- empty/non-strict slice rejection;
- incomplete deletion-family and query-budget rejection;
- confirmation-family pass/fail behavior;
- current-data readiness without inventing missing observations;
- summary output schemas and evidence-boundary labels.

## Acceptance Boundary

The pilot passes when all tests pass, the current-data audit completes reproducibly, all three required summaries parse, and every summary states that it is development/readiness evidence rather than an EffectSlice effectiveness result.

