# Legacy V1 Migration Map

The v1 project history is preserved as raw evidence. This map defines its
workflow ownership without pretending that retrospective stage reports existed.

| Existing path | Workflow ownership | Planned canonical location | Current action |
| --- | --- | --- | --- |
| `memory/long_term_memory.md` | Legacy cross-stage summary | `legacy_papertoskill_v1/memory/long_term_memory.md` | Keep in place for compatibility |
| `memory/short_term_memory.md` | Legacy active-state snapshot | `legacy_papertoskill_v1/memory/short_term_memory.md` | Keep in place for compatibility |
| `research/idea_cards.md`, `literature_matrix.md`, `related_work_gap_map.md` | Legacy Stage 1 inputs | `legacy_papertoskill_v1/stage1/docs/` | Keep in place; read-only input |
| `research/experiment_design.md`, `experiment_queue.md`, task contracts | Legacy Stage 2 planning | `legacy_papertoskill_v1/stage2/planning/` | Keep in place; read-only input |
| `research/run_logs/` and `research/stage_log.md` | Legacy Stage 2 raw logs | `legacy_papertoskill_v1/stage2/logs/` | Keep in place; no new writes |
| `research/claim_evidence_matrix.md`, `claim_source_map.md` | Legacy Stage 2 evidence maps | `legacy_papertoskill_v1/stage2/evidence/` | Keep in place; re-audit before reuse |
| `research/review_report.md`, `rebuttal_bank.md`, `submission_checklist.md` | Legacy Stage 2 review | `legacy_papertoskill_v1/stage2/review/` | Keep in place; historical only |
| `paper/aaai/` | Legacy Stage 2 manuscript | `legacy_papertoskill_v1/stage2/manuscript/` | Keep in place; not the active claim source |
| `results/` | Legacy Stage 2 raw and derived evidence | `legacy_papertoskill_v1/stage2/results/` | Keep in place; inherit only through explicit audit |

Physical moves are deferred because current scripts and generated manifests
reference these paths directly. Each later migration batch must update all
consumers and pass focused tests plus the repository verification suite.

