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

## 2026-07-25: First live-run stop and terminal-row successor freeze

- All live preflights passed: 1/1 Controls-v2 route and all 18 full-grid
  repeat/model slots were available. No credential value was recorded.
- The first parallel invocation was stopped after detecting 12 Controls-v2 and
  18 FG6 started markers with zero terminal rows. FG7 and FG8 had not started.
- Root cause was deterministic and local: the live model calls and scoring
  completed, but the new runners appended repeat/control metadata to the
  frozen strict result row before calling its schema validator. The validator
  correctly rejected those extra fields before terminal-row persistence.
- Audit classified the 30 affected semantic rows as follows:
  26 have complete attempts, raw response, canonical output, and scoring
  evidence; 4 have only a started marker because they were in flight when the
  faulty launchers were stopped.
- Added a forward-only terminal-row successor. It leaves the original frozen
  runners unchanged, writes only the original 25-field strict result schema,
  and stores repeat/control ownership in a separately hash-bound metadata
  sidecar used by progress verification and later analysis.
- The 26 complete responses are reconstructed locally from persisted transport
  bodies. The successor verifies regenerated attempts/raw/canonical/scoring
  hashes byte-for-byte before writing a result row and makes no HTTP call for
  those rows.
- The 4 started-marker-only rows are continued with their original execution ID
  and idempotency key. Transient network and retryable HTTP states are not
  accepted as final experiment rows; each invocation permits three transport
  cycles (up to nine underlying attempts) and leaves the row pending if all
  remain retryable.
- Added six successor tests. Together with the seven original protocol tests,
  all 13 tests passed. One test performs a real persisted-response local
  reprojection and verifies that all source evidence hashes remain unchanged.
- Terminal-row successor freeze:
  `a6b4d581968e098693ba3ef94fd3d359f2e283477c239fe85670ce44ce7809bd6`
- The freeze binds 96 Controls-v2 rows and exactly 1,296 rows in each of FG6,
  FG7, and FG8. It binds all 30 affected execution IDs, 26 complete evidence
  manifests, 4 started markers, the successor source, its tests, and the
  original joint freeze.

## 2026-07-25: Terminal-row recovery completion

- Confirmed the stale lock owners (PIDs 40944 and 39276) no longer existed,
  then removed only those two assistant-created lock files.
- Recovered all 30 affected rows. The 26 persisted responses were locally
  reprojected with byte-identical source evidence; the 4 started-marker-only
  rows completed by continuing transport with their original execution IDs.
- No row remained deferred due to transport. Network or retryable HTTP states
  were not accepted as final experiment outcomes.
- Recovery-subset outcomes were 4 operational successes, 25 hard-contract
  failures, and 1 malformed/no-submission. These are only the 30 recovered
  rows and are not an estimate for any complete experiment.
- A full registration and result-binding verification passed in the project
  environment. Exact progress after recovery:
  Controls-v2 12/96, FG6 18/1,296, FG7 0/1,296, and FG8 0/1,296.
- Artifact safety audit passed over all 373 current run files: zero credential
  reflections, zero generic credential-pattern matches, and zero forbidden
  local model-design files.

## 2026-07-25: Recursive-writer stop and terminal-row successor v2 freeze

- The next parallel launch was stopped after progress reached 22 started
  Controls-v2 rows and 28 started FG6 rows while terminal progress remained
  12 and 18 respectively. FG7 and FG8 remained untouched.
- Root cause was deterministic and local. Successor v1 replaced
  `fg1.write_row`, but its helper reached that same patched symbol again instead
  of a captured base writer, causing recursion before result-row persistence.
- Both assistant-created launchers were stopped and confirmed exited before
  repair. No previously terminal row or frozen FG3-FG5 artifact was changed.
- The 20 newly affected rows comprise 10 Controls-v2 and 10 FG6 semantic rows:
  16 have persisted response/scoring evidence and 4 have only a started marker.
- Terminal-row successor v2 captures the unpatched base writer before installing
  the live patch, calls it exactly once, and keeps repeat/control ownership in
  hash-bound metadata sidecars. Retryable transport states remain pending and
  cannot be written as terminal experimental outcomes.
- Three v2 root-cause tests passed: nonrecursive single base-writer invocation,
  rejection of retryable transport as a terminal row, and frozen registration
  counts of 96 Controls-v2 plus exactly 1,296 rows in each full-grid repeat.
- The combined test directory produced 15 passes and one expected stale-state
  assertion from the immutable v1 test, which still encodes its earlier 12/18
  started-row boundary. The v1 freeze verifier itself passed unchanged.
- Terminal-row successor v2 freeze:
  `6f9cfaa00304176190681df71b59a01d704b67aff892b3c61dcf80a64b3e17aef`
- The v2 freeze binds the 20 new affected execution IDs, their evidence
  manifests or started-marker hashes, the v1 freeze, the v2 source, and the v2
  tests. Formal v2 freeze verification passed before recovery.

## 2026-07-25: Nonterminal-row recovery and detached continuation

- A later launcher exit left eight additional registered executions without
  terminal rows: two Controls-v2 rows and six FG6 rows. All eight had only their
  original started markers; no conflicting terminal row existed.
- Terminal-row successor v2 continued those eight executions under their
  original execution IDs and idempotency keys. The recovery produced exactly
  eight terminal rows and no deferred transport row.
- Exact progress after this recovery was Controls-v2 85/96, FG6 127/1,296,
  FG7 0/1,296, and FG8 0/1,296.
- The continuation launchers were detached from the interactive session so a
  later session transition could not terminate registered work in flight.
- Controls-v2 and the full grid remained logically independent. Controls-v2
  completed while the full-grid launcher continued the frozen 18-wave,
  block-balanced schedule. Full-grid blocks are interleaved across repetitions;
  a later repeat can begin a 216-row block before an earlier repeat reaches its
  complete 1,296-row denominator.

## 2026-07-25: Controls-v2 completion, analysis, and verification

- Controls-v2 completed with exactly 96 unique terminal result rows. The strict
  result-row set, hash-bound metadata-sidecar set, and terminal-marker set each
  exactly equal the 96-row frozen registration; all 96 rows are valid.
- Terminal outcomes are 23 operational successes, 71 hard-contract failures,
  and 2 malformed/no-submission results. Retryable transport states are absent
  from the terminal-result set.
- The deterministic layer passed all 40 registered cells. Its confusion matrix
  contains only matching cells: 24 Admit/Admit, 8 Reject/Reject, and
  8 Invalid/Invalid.
- Model-mediated arm results over 24 registered rows per arm are:
  `F_reference` 8 successes and 8 direction matches; `F_identity` 8 and 8;
  `P_redundancy_removed` 7 and 7; and `N_exact_contract_removed` 0 successes
  with 24/24 direction matches.
- `F_reference` and `F_identity` have identical valid-row mean private score
  (0.532552) and success rate (8/24). The nonidentical redundancy-removal arm is
  slightly lower at 7/24 and mean private score 0.490885. These descriptive
  differences are retained without favorable-case deletion.
- The destructive exact-contract-removal negative behaves as preregistered:
  all 24 rows fail operationally and all 24 match the negative direction.
- The post-hoc completion verifier passed. It checks the exact denominator,
  execution-ID uniqueness, strict schema, registration/result/metadata/marker
  bindings, and absence of retryable transport terminal states.
- Primary artifacts:
  `runs/controls_v2/`, `analysis/controls_v2/analysis.json`, and
  `verification/controls_v2.json`.
- Analysis SHA-256:
  `f11f01f5ed4fedbdf08e3574faa75ec1491e735b40a82a3bcdaded60c9a039b52`.
- A scoped artifact-safety audit passed over all 877 Controls-v2 evidence,
  analysis, verification, source, and log files selected for backup: zero exact
  credential reflections, zero generic credential-pattern matches, and zero
  forbidden local-model-design markers.
- Controls-v2 evidence commit `912edd61` was pushed to the private
  `origin/codex/effectslice-v3` branch. The push also synchronized the preceding
  terminal-row successor v2 freeze commit `b874ac08`.

## 2026-07-26: FG6 completion, analysis, and verification

- FG6 completed with exactly 1,296 unique terminal result rows. The registered
  execution-ID set, strict result-row set, hash-bound metadata-sidecar set, and
  terminal-marker set are identical and contain no extra or missing IDs.
- All 1,296 strict result schemas and schedule/metadata/result-hash bindings
  passed. No retryable transport state is present in the terminal denominator.
- Terminal outcomes are 388 operational successes, 668 hard-contract failures,
  160 integrity/digest failures, and 80 malformed/no-submission results. There
  are 1,136 valid rows and 160 technical-invalid rows; all remain in the frozen
  denominator.
- The post-hoc single-repeat analysis reuses the frozen score and decision
  functions. It materializes schedule bindings from verified metadata sidecars
  in memory and does not rewrite strict result rows or persist a global overlay.
- The 24 primary paper-task units yield 3 Admit and 21 Reject decisions.
  Mean paper-task effects are F-B 0.263346 (approximate 95% CI
  [0.140534, 0.386159]), S-B 0.311198 ([0.174108, 0.448288]), and
  S-F 0.047852 ([-0.023870, 0.119573]).
- Primary artifacts are `runs/full_grid/FG6/`, `verification/fg6.json`, and
  `analysis/full_grid/fg6.json`.
- Verification SHA-256:
  `3e13c2f053d3caf7701b482a00338b7949e0cfe6d6ff8805764581264604a831`.
- Analysis SHA-256:
  `5cfea836f66bee17f14e14ef44c3ceccd6377eb040a24d46cd1f435ece521bdd`.
- The heuristic credential scanner now excludes only opaque
  `encrypted_content` ciphertext from generic-pattern matching; exact configured
  credential matching still scans every original byte. Seven focused safety
  tests pass, including an exact-credential-in-ciphertext fail-closed case.
- A scoped artifact-safety audit passed over 11,383 FG6 evidence, analysis,
  verification, source, and log files: zero exact credential reflections, zero
  generic credential-pattern matches outside opaque ciphertext, and zero
  forbidden local-model-design markers.
