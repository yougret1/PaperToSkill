# Next Actions

The accepted Stage `2` remains complete. The active work is a separate,
forward-only generalization extension required by the user.

## Immediate Gate

1. The authoritative suite passes (`156 passed in 117.40s`).
2. Commit and privately push the complete batch-009 evidence, summaries, audit,
   stage report, and memory update.
3. Do not dispatch row 649 until the push succeeds.
4. Continue only the frozen schedule in batches of at most 72 rows, with an
   audit, summary, commit, and push between batches.
5. Preserve the pilot as unscored format evidence; do not include it in any
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
10. Batch 001 was privately pushed at `eea9cf56`. Batch 002 then consumed rows
    73-144 with 66 hard-contract failures, five malformed/no-submission outcomes,
    and one operational success. Three registered TLS failures caused three
    transport retries; no completed semantic response was rerun.
11. The complete batch-002 execution tree contains 1,189 files and passes all
    credential and forbidden-local-design safety gates; 1,152 rows remain.
12. Batch 002 was privately pushed at `78b447ca`. Batch 003 then consumed rows
    145-216 with 61 hard-contract failures, 11 malformed/no-submission outcomes,
    and zero operational successes. All 72 transports completed on their first
    attempts and no semantic response was rerun.
13. The complete batch-003 execution tree contains 1,768 files and passes all
    credential and forbidden-local-design safety gates; 1,080 rows remain.
14. Batch 004 consumed rows 217-288 with 68 hard-contract failures, four
    malformed/no-submission outcomes, and zero operational successes. The
    complete 2,347-file execution tree passes all credential and
    forbidden-local-design safety gates; 1,008 rows remain.
15. Batch 005 consumed rows 289-360 with 62 hard-contract failures, ten
    malformed/no-submission outcomes, and zero operational successes. The
    complete 2,926-file execution tree passes all credential and
    forbidden-local-design safety gates; 936 rows remain.
16. Batch 006 consumed rows 361-432 with 56 hard-contract failures, 16
    malformed/no-submission outcomes, and zero operational successes. The
    complete 3,505-file execution tree passes all credential and
    forbidden-local-design safety gates; 864 rows remain.
17. Batch 007 consumed rows 433-504 with 71 hard-contract failures, one
    malformed/no-submission outcome, and zero operational successes. The
    complete 4,084-file execution tree passes all credential and
    forbidden-local-design safety gates; 792 rows remain.
18. Batch 008 consumed rows 505-576 with 70 hard-contract failures, two
    malformed/no-submission outcomes, and zero operational successes. Its
    private-score sum of 0.71875 belongs to a hard-contract failure. The complete
    4,663-file execution tree passes all credential and forbidden-local-design
    safety gates; 720 rows remain.
19. Batch 009 consumed rows 577-648 with 68 hard-contract failures, four
    malformed outcomes, zero operational successes, and no transport retries.
    Its 5,242-file safety scan passes; 648 rows remain.

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
