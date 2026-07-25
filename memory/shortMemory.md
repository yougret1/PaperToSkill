# Short-Term Memory

## Authoritative Current Checkpoint

- Active boundary: commit and privately push the frozen FG5
  exact-output-contract class, then move forward to response-format handling.
- Branch: `codex/effectslice-v3`; latest pushed commit before this checkpoint is
  `3879b79e`.
- The editable SkillAudit main figure V3.3 is backed up at
  `paper/effectslice_aaai/images/SkillAudit_Main_Figure_v3_3.pptx` and was
  privately pushed in commit `640ad272`; slide 2 now presents the full
  `F=R(A)` path above the upstream-produced `S=R(A_S)` path with manuscript
  notation aligned through the frozen boundary.
- FG3 remains frozen with 1,296 terminal rows. Its exclusive classification is
  268 payload-interface, 684 exact-output contract, 77 response-format, 120
  integrity/digest, one provider availability, 141 experimental outcomes, and
  five operational successes.
- All 684 exact-output-contract rows have terminal FG5 successors across 24
  tasks. Independent validation checked 40,896 returned values from 639 rows;
  every value conforms to its frozen public structural contract.
- The 684-row outcomes are 224 operational successes, 424 experimental
  hard-contract failures, 27 response-format deferrals, and nine
  integrity/digest deferrals.
- Nine experimental rows produced no shape-evaluable output: six scorer safety
  policy violations, one worker timeout, and two completed candidates with 64
  case errors. They were not semantically rerun.
- The output-contract registry SHA is
  `9d1d21600a0a99c1c00928b0da592d790dd63a531db65dd2c76e4b35cbdc9350`.
- The exact-output final report passes and the successor is frozen under bundle
  SHA `8ec345c120d8aa4ae432ba77e5a120f81c3ce727bca8a7a94800cade9344779a6`.
- FG5 currently contains 691/1,296 terminal rows and 226 operational successes;
  the forward-extension suite passes `191` tests.
- Next worklist: 77 original response-format rows plus 27 routed FG5 malformed
  rows, followed by 120 original plus nine routed integrity/digest rows, then one
  provider-availability row.
- FG3, FG4, and the frozen FG5 successor are immutable. Do not replay completed
  semantic responses, and keep credentials, caches, and temporary outputs out of
  Git.

Everything below this notice is retained historical context and is not the active
execution boundary.

## Active Iteration

Complete and privately back up the final FG3 registered batch 018. The accepted
V4/V5 evidence, frozen parent Stage `2.2` bundle, remote-only successor,
materialization anchor, FG1, FG2, and FG3 pilot are immutable; no parent stage is
reopened.

## Completed This Iteration

- Froze a 12-paper by 2-task benchmark across four domains, including B/F/S
  candidates, controls, schedules, provider identities, retries, statistical
  units, resource endpoints, and four required figure contracts.
- Added exact response selectors, twelve parser golden-case contracts, structured
  result-row cross-field semantics, and implementation-source audit gates.
- Preserved frozen parent bundle SHA
  `277bab0fba66a4144346d472ef3deadc010168353d47f939dc812501a2eff9b4`.
- Removed all local-model design from a new forward successor and promoted
  GPT-5.6 Luna to the fifth required remote slot.
- Froze 1,296 remote rows and zero local rows; Luna F/I repeats are observed
  repeatability only and do not claim seed control or determinism.
- Generated remote-only successor bundle SHA
  `e2615ea65ecc0c1145aa3e0f2fb7a36b8bc91a914bb94821b5cee40be9da99958`.
- Materialized and verified one 1,296-row remote schedule across 24 tasks.
- Bound 3,672 immutable files under bundle SHA
  `1f12dfdba63b1ddc65bd57fa8b1b625ba4259050e93ab4f108786c2023c5ccd7`.
- Added and verified the isolated remote executor and immutable execution
  contract; the complete forward suite passes (`141 passed`). Credential
  documents were audited without persisting values; no provider API had been
  called at that checkpoint.
- Committed and privately pushed the executor contract at `579fc90f`.
- Completed one format-only preflight for each of six exact aliases: all six
  succeeded on the first transport attempt, with no credential reflection.
- Executed 72 FG1 rows; every response exhausted the registered 1,024-token
  output budget and was classified malformed_or_no_submission.
- Stopped FG1 with 1,224 rows undispatched and preserved all terminal evidence.
- Committed and privately pushed FG1 invalid batch 001 at `e9bdbeda`.
- Froze a new 1,296-row FG2 request overlay that changes only the output budget
  from 1,024 to 8,192 and requires six unscored pilot requests before execution.
- Committed and privately pushed FG2 at `3ed3a533`.
- Ran six FG2 pilot requests: all were nontruncated, but Claude Opus 4.7 and
  DeepSeek V4 Flash wrapped output in Markdown, so only four strict submissions
  passed and no registered FG2 row was dispatched.
- Committed and privately pushed the invalid FG2 pilot at `13d027ce`.
- Froze FG3 with the same 8,192-token budget and one uniform bare-JSON format
  instruction. Its bundle SHA is
  `1a5212ee09f43b4e97737f83fc1365e0181942b790bd0a54920609d35b24766d`.
- Generated 1,296 new FG3 execution IDs plus six marked, unscored pilot
  requests; no FG3 provider call has started.
- Passed the FG3 verifier, 10 focused tests, the complete forward suite
  (`156 passed`), and a complete 1,308-file safety scan.
- Committed and privately pushed the frozen FG3 successor at `f03d0ce4`.
- Ran six marked, unscored FG3 pilot requests. All six exact aliases returned
  nontruncated strict submissions on their first transport attempt.
- Scanned all 32 pilot evidence files with zero credential reflections, zero
  generic credential-pattern matches, and no forbidden local-model design.
- Committed and privately pushed the passed FG3 pilot at `b388845c`.
- Executed exactly the first 72 registered FG3 rows: four paper-task units with
  24 B, 24 F, and 24 S rows. All 72 transports completed on their first attempt.
- Observed 70 hard-contract failures and two malformed/no-submission outcomes,
  zero operational successes, and 72 private scores of 0.0. These are valid
  frozen condition failures and no terminal response is rerun.
- Verified the exact contiguous schedule prefix and passed a fixed-minimum
  611-file safety scan; 1,224 registered rows remain undispatched.
- Committed and privately pushed batch 001 at `eea9cf56` before dispatching row
  73.
- Executed exactly rows 73-144 as FG3 batch 002. The 72 logical requests used 75
  transports because three registered TLS failures were retried; no terminal
  semantic response was rerun.
- Batch 002 produced 66 hard-contract failures, five malformed/no-submission
  outcomes, and one operational success in AGENT-TF-02 under S. Its private-score
  sum is 1.0 across 72 rows.
- Verified rows 1-144 as the exact contiguous prefix and passed a fixed-minimum
  1,189-file execution-tree safety scan; 1,152 rows remain undispatched.
- Committed and privately pushed batch 002 at `78b447ca` before dispatching row
  145.
- Executed exactly rows 145-216 as FG3 batch 003. All 72 logical requests
  completed on their first transport attempts; no semantic response was rerun.
- Batch 003 produced 61 hard-contract failures, 11 malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- Verified rows 1-216 as the exact contiguous prefix and passed a fixed-minimum
  1,768-file execution-tree safety scan; 1,080 rows remain undispatched.
- Executed exactly rows 217-288 as FG3 batch 004. All 72 logical requests
  completed on their first transport attempts; no semantic response was rerun.
- Batch 004 produced 68 hard-contract failures, four malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- Verified rows 1-288 as the exact contiguous prefix and passed a fixed-minimum
  2,347-file execution-tree safety scan; 1,008 rows remain undispatched.
- Executed exactly rows 289-360 as FG3 batch 005. All 72 logical requests
  completed on their first transport attempts; no semantic response was rerun.
- Batch 005 produced 62 hard-contract failures, ten malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- Verified rows 1-360 as the exact contiguous prefix and passed a fixed-minimum
  2,926-file execution-tree safety scan; 936 rows remain undispatched.
- Executed exactly rows 361-432 as FG3 batch 006. All 72 logical requests
  completed on their first transport attempts; no semantic response was rerun.
- Batch 006 produced 56 hard-contract failures, 16 malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- Verified rows 1-432 as the exact contiguous prefix and passed a fixed-minimum
  3,505-file execution-tree safety scan; 864 rows remain undispatched.
- Executed exactly rows 433-504 as FG3 batch 007. All 72 logical requests
  completed on their first transport attempts; no semantic response was rerun.
- Batch 007 produced 71 hard-contract failures, one malformed/no-submission
  outcome, zero operational successes, and a private-score sum of 0.0.
- Verified rows 1-504 as the exact contiguous prefix and passed a fixed-minimum
  4,084-file execution-tree safety scan; 792 rows remain undispatched.
- Executed exactly rows 505-576 as FG3 batch 008. All 72 logical requests
  completed on their first transport attempts; no semantic response was rerun.
- Batch 008 produced 70 hard-contract failures, two malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.71875. The
  partial score does not meet the hard contract and is not an operational success.
- Verified rows 1-576 as the exact contiguous prefix and passed a fixed-minimum
  4,663-file execution-tree safety scan; 720 rows remain undispatched.
- Executed rows 577-648 as batch 009: 68 hard-contract failures, four malformed
  outcomes, zero operational successes, 72 first-attempt transports, and score
  sum 0.0. The 5,242-file scan passed; 648 rows remain.
- Batch 010 consumed rows 649-720: 70 hard-contract failures, two malformed
  outcomes, zero operational successes, no retries, score sum 0.0; 576 remain.
- Batch 011 consumed rows 721-792: 68 hard-contract failures, four malformed
  outcomes, zero operational successes, no retries, score sum 0.0. The 7,706-file
  execution-tree safety scan and 156-test suite passed; 504 rows remain.
- Batch 012 consumed rows 793-864: 68 hard-contract failures, one malformed
  outcome, three operational successes, no retries, and score sum 3.0. Its 24
  DeepSeek primary, 24 GPT-5.5, and 24 GPT-5.6 Sol rows passed the 8,285-file
  execution-tree safety scan and 156-test suite; 432 rows remain.
- Batch 013 consumed rows 865-936: 68 hard-contract failures, three malformed
  outcomes, one terminal integrity/digest failure, no operational success, and
  score sum 0.0 across 71 scored rows. Its 72 logical requests used 89 transports
  because 16 HTTP 429 and one HTTP 502 failure were registered retries. The
  8,879-file execution-tree safety scan and 156-test suite passed; 360 rows remain.
- Batch 014 consumed rows 937-1008 for SE-PE-01: 61 hard-contract failures, 11
  malformed outcomes, no operational success, no retries, and score sum 0.0.
  Its GPT-5.6 Sol, GPT-5.6 Terra, and Claude Opus 4.7 rows passed the 9,457-file
  execution-tree safety scan and 156-test suite; 288 rows remain.
- Batch 015 consumed rows 1009-1080 for DATA-HDB-01: 71 hard-contract failures,
  one operational success, no malformed outcomes, no retries, and score sum
  6.25. Its GPT-5.5, GPT-5.6 Sol, and GPT-5.6 Terra rows passed the 10,036-file
  execution-tree safety scan and 156-test suite; 216 rows remain.
- Batch 016 consumed rows 1081-1152 across DATA-HDB-01 and AGENT-TF-01: 71
  hard-contract failures, one malformed outcome, no operational success, no
  retries, and score sum 1.4375. Its GPT-5.5, GPT-5.6 Sol, and Claude Opus 4.7
  rows passed the 10,615-file execution-tree safety scan and 156-test suite; 144
  rows remain.
- Batch 017 consumed rows 1153-1224: 24 hard-contract failures, 47
  integrity/digest failures, one provider/model-unavailable recovery, 248
  transport attempts, and 177 registered retries. Row 1156 was not replayed.
  The recomputed summary is byte-identical, the 9,967-file safety audit is clean,
  and the authoritative suite passes 158 tests; 72 rows remain.
- Batch 018 consumed rows 1225-1296. All 72 rows ended as
  `integrity_or_digest_failure` for `gpt_5_6_luna`; 360 transport attempts and
  288 transport retries were recorded, with HTTP 503 on every attempt and no
  valid private score. The cumulative 1,296-row outcomes are 1,093
  `hard_contract_failure`, 120 `integrity_or_digest_failure`, 77
  `malformed_or_no_submission`, five `operational_success`, and one
  `provider_or_model_unavailable`.
- Batch 018 has a 10,690-file safety audit with zero credential reflections,
  zero generic credential patterns, and zero forbidden local-model markers.
  The forward-extension suite passes 158 tests in the project `.venv`.
- The full registered FG3 schedule is complete. Only five rows are operational
  successes, so the result is process/availability evidence and a bounded
  benchmark, not a broad claim of method effectiveness.

## Current State

- The remote-only Stage `2.2` successor is committed and pushed at `6262956f`.
- The Stage `2.3` materialization anchor is committed and privately pushed at
  `b4a8605f`.
- The source manuscript is `paper/effectslice_aaai/main_v3.tex`.
- The standard `main_v3.pdf` was held open externally; the current-source verified
  build is `main_v3_build.pdf` until the clean copy is completed.
- FG1 and FG2 must not continue. The frozen FG3 successor is committed and
  privately pushed.
- The FG3 pilot and batches 001-016 are committed and pushed. Batch 017 is
  complete through row 1224 and must be committed and privately pushed before
  Batch 018 starts at row 1225.

## Residual Risk

- The registered papers are a purposeful benchmark, not a random population
  sample; paper remains the independent statistical unit.
- Source-audit identities are process evidence rather than externally
  authenticated identities.
- Local-model experiments remain prohibited. Provider execution must follow the
  immutable 1,296-row schedule, exact aliases, F/I byte identity, source audits,
  and retry semantics.
- Provider availability and descriptive resource endpoints remain separate from
  method-quality evidence.
