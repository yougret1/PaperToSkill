# SnapATAC2 Executable-Candidate Contract

Date: 2026-07-04

Evidence boundary: this is a pre-registered contract for future SNAP
executable-candidate reruns. It does not add new task-success evidence, does
not replace current paper-facing SNAP rows, and does not change
`results/real_reuse/main_run_selection.json`.

Machine-readable source:
`benchmarks/real_reuse/snapatac2_executable_candidate_contract_v0.json`

## Why This Exists

The current SNAP main rows are failure-boundary rows because the first-pass
runner collected model-authored plan/JSON outputs, while the scorer requires
completed artifacts plus runtime and memory records.

The phase108 controlled scaffold shows the existing scorer can be satisfied
when artifacts and resource records are actually materialized. The missing
piece before future LLM reruns is a contract that makes execution, artifact
materialization, and resource recording the runner's responsibility rather
than trusting model-authored `completed=true`.

## Contract Summary

| Item | Rule |
| --- | --- |
| Tasks | SNAP-T1 and SNAP-T2 |
| Conditions | Summary and PaperToSkill, always paired |
| Base model | GPT-family `gpt-5.5`, except explicit LLM ablations |
| Main-row policy | Main rows stay unchanged unless a paired rerun is pre-registered and explicitly promoted |
| Candidate form | Executable Python script, checked-in script command, or structured JSON pointing to executable script and arguments |
| Runner duty | Execute candidate, measure runtime, measure peak memory, write candidate output, write artifact manifest, call existing scorer |
| Human intervention | None mid-run |
| Provider failures | Availability metadata, not task-quality failure |

## Required Candidate Outputs

| Output | Owner | Purpose |
| --- | --- | --- |
| `candidate_output.json` | Runner after execution | Scorer-readable summary with `completed`, method steps, artifact paths, runtime, memory, and task-specific quality fields |
| `artifact_manifest.json` | Runner after execution | Auditable list of concrete files created by the candidate |
| `resource_record.json` | Runner after execution | Runtime and peak memory measurement source |

The runner must ignore model-authored `completed=true` until the candidate has
actually executed and required artifacts plus resource records exist.

## Task Requirements

| Task | Required Artifacts | Scorer Components |
| --- | --- | --- |
| SNAP-T1 | `embedding.csv`, `cell_features.csv`, `fragment_summary.json` | completed, artifacts, resource, method alignment |
| SNAP-T2 | `clusters.csv`, `marker_summary.json`, `embedding.csv` | completed, artifacts, resource, method alignment, quality |

SNAP-T2 quality must use hidden reference labels when they exist; otherwise it
must use a pre-registered proxy quality metric declared before execution.

## Failure Handling

| Failure | Treatment |
| --- | --- |
| Provider/model unavailable | Availability metadata; no scored raw row |
| Candidate cannot be executed | Scored task failure after provider output exists |
| Required artifacts missing | Scored task failure with `completed=false` |
| Resource budget exceeded | Scored task failure through the resource component |
| Invalid scorer JSON | Scored task failure through the existing scorer |

## Promotion Rule

Future SNAP reruns may only replace paper-facing main SNAP rows if all of the
following are true:

- the rerun is pre-registered before execution;
- Summary and PaperToSkill are run as a paired comparison;
- both conditions use the same fixture, scorer, resource budget, hidden/proxy
  label policy, and no-mid-run-human rule;
- the replacement is explicitly promoted by updating
  `results/real_reuse/main_run_selection.json`.

