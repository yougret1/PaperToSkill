# Section 06 Targeted Repeatability Report

## Scope

Four byte-identical identity-control pairs were selected because the two arms
were operationally discordant after reaching the same final protocol. One exact
wire request per pair was frozen and issued twice to `deepseek-v4-flash` with
temperature 0 and top-p 1.0. The source requests contain no API seed field.

All eight calls completed in one transport attempt. There were no availability,
transport, HTTP, response-format, integrity, or incomplete-dispatch outcomes.

## Results

| Case | Source protocol | Replica 1 | Replica 2 | Repeatability |
| --- | --- | --- | --- | --- |
| `AGENT-TF-01`, block 3, A | FG5 exact-output | Success `[T,T]` | Success `[T,T]` | Full agreement |
| `AGENT-TF-01`, block 4, B | FG5 exact-output | Failure `[T,F]` | Failure `[T,F]` | Full agreement |
| `NLP-LLM-01`, block 4, B | FG5 exact-output | Failure `[F,F]` | Success `[T,T]` | Operational disagreement |
| `SE-PE-01`, block 3, A | Payload/interface | Failure `[F,F]` | Failure `[T,F]` | Vector disagreement |

The aggregate is 3 operational successes and 5 hard-contract failures. Two of
four cases reproduce exactly across both replicas. One case flips operational
success, and one remains a failure while changing its hard-contract vector.

## Interpretation

The targeted repeats confirm that deterministic decoding settings do not make
the remote semantic evaluation deterministic. They also show that instability
is case-dependent: two requests are stable across these repeats, while two are
not. The result supports retaining repeatability as an explicit limitation on
the F/S/B conclusions.

This successor does not repair the registered identity control, revise any
frozen FG3/FG4/FG5 result, estimate a population-level random-seed effect, or
substitute for the deferred FG6 comprehensive multi-seed experiment.
