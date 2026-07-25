# Section 07 Run Log

## 2026-07-25: Pre-Call Design

- Scope: four tasks (`NLP-LLM-01`, `SE-PE-01`, `DATA-HDB-01`, and
  `AGENT-TF-01`), two registries, six arms, 48 registered DeepSeek calls.
- Critical atom: index 10, covering no input mutation and deterministic
  ranking/traversal ties; direct hard-contract mappings are task-specific and
  frozen in the registry.
- Noncritical comparator: index 8, covering external-resource exclusion with no
  direct scorer hard-contract identifier.
- Protocol: corrected FG5 explicit case interface, exact output contract, and
  strict JSON submission envelope; `deepseek-v4-flash`, temperature 0, top-p 1,
  8,192 output-token cap, no API seed.
- Order: deterministic SHA-256 ordering over task, registry, and arm.
- Retry policy: at most five transport attempts; completed semantic responses
  are never replayed.
- Frozen predecessors: FG3, FG4, FG5, and Sections 01-06 are read-only inputs.

## Deferred By Time Constraint And Not Executed In This Goal

These items remain at the bottom of `CHECKLIST.md`, in priority order, with the
note "准备时间多的话再去做":

1. Additional compression points and Pareto analysis.
2. Additional publication-figure implementation and visual polishing.
3. FG6 comprehensive multi-seed experiment.
