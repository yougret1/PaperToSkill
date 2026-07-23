# Next Actions

The accepted Stage `2` remains complete. The active work is a separate,
forward-only generalization extension required by the user.

## Immediate Gate

1. Commit and privately push the complete FG3 batch-001 evidence, summary, audit,
   stage report, and memory update.
2. Do not dispatch row 73 until the push succeeds.
3. Continue only the frozen schedule in batches of at most 72 rows, with an
   audit, summary, commit, and push between batches.
4. Preserve the pilot as unscored format evidence; do not include it in any
   experiment estimate or rerun a terminal semantic response.

## Stage 2.3 Materialization

1. The complete materialization anchor is generated, verified, committed, and
   privately pushed.
2. The executor contract is frozen, verified, committed, and privately pushed.
3. One format-only preflight per exact alias passed with six first-attempt
   successes and no credential persistence.
4. FG1 batch 001 then failed systematically: all 72 rows exhausted the 1,024
   output-token budget and were malformed. Do not continue FG1.
5. FG2 pilot showed 8,192 is adequate but two providers violated the bare-JSON
   contract. Do not run registered FG2 rows; create and pilot FG3.
6. FG3 is frozen under bundle
   `1a5212ee09f43b4e97737f83fc1365e0181942b790bd0a54920609d35b24766d`;
   its verifier, 156-test suite, and 1,308-file safety scan pass. No FG3 provider
   call had started at that frozen-successor checkpoint.
7. The six-request FG3 format pilot passes 6/6 with six first-attempt transport
   successes and a clean 32-file safety scan.
8. FG3 batch 001 consumed the exact first 72 schedule rows. It produced 70
   hard-contract failures and two malformed/no-submission outcomes, zero
   operational successes, and no transport retries. These are valid condition
   failures under the frozen plan, not reasons for semantic reruns.
9. The complete 611-file batch audit passes; 1,224 FG3 rows remain undispatched.

## Preservation Rules

- Keep the 858-file parent raw set, all 24 bound artifacts, and V4/V5 records
  immutable.
- Use `python -m pytest tests` from the EffectSlice attempt directory as the
  authoritative suite scope; repository-wide discovery also collects archived
  duplicate snapshots and is not a valid release signal.
- Keep paper as the independent unit and restrict FG1 inference to the purposeful,
  registered, domain-stratified benchmark.
- Report controls as exact task tables, not calibrated error rates or a confusion
  matrix.
- Keep usage, latency, and conditional cost descriptive rather than method-quality
  evidence.
- Do not mutate, supersede, or reinterpret V4/V5 preregistrations, raw outputs,
  or accepted stage reports; every new artifact lives under `forward_extensions`.
- Do not design or run local-model experiments. The remote-only successor has
  1296 remote rows and zero local rows.
