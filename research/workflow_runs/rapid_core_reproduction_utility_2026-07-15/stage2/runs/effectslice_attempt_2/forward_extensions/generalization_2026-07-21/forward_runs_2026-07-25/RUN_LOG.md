# Chronological Run Log

## 2026-07-25: Scope and audit start

- Scope frozen to four experiments only: Controls-v2, FG6, FG7, and FG8.
- `researchstudio-full-research-workflow` is explicitly excluded.
- `task-execution-principles` is used only for execution, logging,
  verification, filesystem, and Git discipline.
- Existing FG3-FG5 artifacts and completed analyses are read-only.
- The unrelated untracked `forward_analysis_2026-07-25/s08/` directory is
  excluded and left untouched.
- Git branch was synchronized with its remote at audit start except for the
  excluded `s08/` directory.
- No provider call has been made for this phase.
- Old controls audit found that the prior positive was byte-identical to F and
  the destructive negative lacked contract/case-level machine binding. The
  successor therefore requires a deterministic label layer before calls.
- The user corrected the repetition size: FG6, FG7, and FG8 each contain the
  complete 1,296-row grid, for 3,888 repetition calls and 3,984 total calls
  including the 96 model-mediated Controls-v2 rows.

## 2026-07-25: Formal no-call registration and freeze

- Independently audited all 1,296 FG5 source requests: no missing request, no
  request SHA mismatch, and no model alias or frozen decoding mismatch.
- Registered FG6, FG7, and FG8 as three independent exact-protocol
  repetitions. Each repeat has 1,296 rows and its own execution/transport
  namespace; the three repeats have 3,888 globally unique execution IDs.
- Replaced the draft per-row offset schedule with an 18-wave block-balanced
  schedule. Each of the six 216-row blocks uses a different FG6/FG7/FG8 order,
  balancing registry-local first, second, and third positions.
- Registered Controls-v2 with 96 model-mediated rows:
  4 tasks x 2 registries x 4 arms x 3 repetitions. Its deterministic layer has
  40 cells and computes Admit/Reject/Invalid from digest and case-level results
  rather than copying an expected label.
- Bound 16 control mutations through atom IDs, contract IDs, all 64 private
  case IDs, and scorer keys. Model-mediated behavior is explicitly separate
  from deterministic ground-truth labels.
- Added and passed seven no-call tests for exact call accounting, repeat and
  transport namespace uniqueness, noncontiguous block scheduling, deterministic
  control classification, factorial balance, and Windows long-path writes.
- Two pre-freeze construction attempts failed before any provider call. The
  first exposed an invalid assumption that block rows were contiguous; the
  second exposed Win32 path-length handling. Both causes were fixed and the
  incomplete, unfrozen registration directories were removed before rebuilding.
- `compileall` could not write two long-path `__pycache__` targets through its
  normal path API. This was recorded as a tooling/path failure, not a source
  syntax failure: the same modules imported and executed in all seven tests,
  and both formal registration builders and verifiers completed successfully.
- Formal registration bundles:
  - Full grid: `0ce5a41ab83289e23b2c3002911cfdb8fb635722cb26edcf7b1142e1863bc94dd`
  - Controls-v2: `7b7f3ba6f68f66f748188dd540e5fe8bb7e7c8b33ee67ee0b60ac75de587b1eb`
- Joint freeze SHA:
  `da5148475835251551e9ad5075d24c4c97bde2282b08bf3dfe074fbe92174ee1`
- The recorded no-call verifier passed with provider calls started `false`,
  1,296 rows per full-grid repeat, 3,888 full-grid rows, 96 Controls-v2 rows,
  and 3,984 total registered rows. Operational preflights are excluded.
- Pre-call freeze commit `cb5a758e` was pushed successfully to the private
  `origin/codex/effectslice-v3` branch. The commit excludes credentials,
  `.venv-forward/`, caches, temporary directories, the unrelated `s08/`, and
  all other unrelated changes.
