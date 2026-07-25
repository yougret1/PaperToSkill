# Forward Controls and Full-Grid Repetitions

This directory is a forward-only successor containing exactly four new
experiments:

1. Controls-v2.
2. FG6 full-grid independent exact-protocol repetition.
3. FG7 full-grid independent exact-protocol repetition.
4. FG8 full-grid independent exact-protocol repetition.

Each of FG6-FG8 contains 1,296 registered calls. These runs are independent
exact-protocol repetitions. Model slots without an API seed field must not be
described as random-seed runs.

All registrations are frozen and verified before the first provider call.
Only ambiguous transport failures may be retried under the frozen retry
policy. A completed semantic response is terminal even when unfavorable.

Registered semantic calls are Controls-v2 96, FG6 1,296, FG7 1,296, and FG8
1,296, for 3,984 total. Operational preflights and transport retries are
excluded from this accounting. Technical Invalid outcomes remain in every
registered denominator.

Authoritative artifacts:

- `joint_freeze.json`: joint immutable protocol binding.
- `no_call_verification.json`: pre-call integrity and accounting result.
- `registration/controls_v2/`: Controls-v2 registration and deterministic layer.
- `registration/full_grid/`: three full-grid schedules and the 18-wave dispatch.
- `RUN_LOG.md`: chronological failures, fixes, hashes, calls, and verifications.
- `CHECKLIST.md`: completion gate for the four experiments.

No API credential value is stored here. Runtime credential source metadata is
recorded without credential values.
