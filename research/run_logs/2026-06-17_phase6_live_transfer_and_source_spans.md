# Run Log: 2026-06-17 Phase 6 Live Transfer Protocol And Source Spans

## Objective

Prepare live cross-harness execution artifacts and strengthen source-grounding
checks before the remote LLM endpoint recovers.

## API Re-Test

- `/v1/models` succeeded and listed `claude-opus-4-8`.
- `/v1/chat/completions` still failed with HTTP 502:
  `All available accounts exhausted`.

## Live Transfer Prompt Packets

- Task spec: `benchmarks/tasks/ai_scientist_v2_live_transfer.json`
- Command:

```powershell
python scripts\build_live_transfer_prompts.py --task benchmarks\tasks\ai_scientist_v2_live_transfer.json --output-dir results\live_transfer_prompts\ai_scientist_v2_v0
```

- Output: six prompt packets covering two harness styles and three context
  variants:
  - Codex-style full skill
  - Codex-style skill without transfer notes
  - Codex-style generic summary
  - Claude-style full skill
  - Claude-style skill without transfer notes
  - Claude-style generic summary

## Source-Span Validation

- Task spec: `benchmarks/tasks/ai_scientist_v2_source_span_validation.json`
- Command:

```powershell
python scripts\validate_source_spans.py --task benchmarks\tasks\ai_scientist_v2_source_span_validation.json --output results\evaluations\ai_scientist_v2_source_span_validation_v0.json
```

## Results

| Metric | Value |
| --- | ---: |
| Total anchored claims | 16 |
| Supported | 15 |
| Weak | 1 |
| Invalid ranges | 0 |
| Support rate | 0.938 |

## Failure And Fix

The first source-span validation pass used Python `splitlines()`, which treats
form-feed characters from `pdftotext` as line boundaries. Manual anchors and
`rg` line numbers count newline-delimited lines, so this shifted some spans and
caused false unsupported judgments. The validator now splits source text only on
`\n`, and a regression test covers form-feed handling.

## Evidence Boundary

The source-span validator checks line-anchor validity and lexical overlap. It is
stronger than section-level source-map audit, but it is still not a human
factuality annotation. The live transfer prompt packets are execution-ready
inputs, not live run results.

## Verification

```powershell
python -m unittest discover -s tests -v
```

Result: 8 tests passed.

