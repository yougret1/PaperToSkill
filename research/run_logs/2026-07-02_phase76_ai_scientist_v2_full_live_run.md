# Phase 76: AI-Scientist-v2 Full Live Run Closure

Date: 2026-07-02

## Command And Output

The bounded AI-Scientist-v2 path now has both smoke and full-run completion
evidence.

Smoke evidence:

```powershell
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 60 --max-tokens 128 --model-alias claude-opus-4-8 --model-alias claude-opus-4-7 --model-alias claude-opus-4-6
```

Current report:

- `results/ai_scientist_v2_smoke/run_report.md`: `overall_status=complete`.
- Saved marker response: `results/ai_scientist_v2_smoke/response.md`.

Full run command shape:

```powershell
cd D:\a_work\gitee\ai-scientist-v2
Remove-Item Env:\AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE -ErrorAction SilentlyContinue
Remove-Item Env:\AI_SCIENTIST_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\OPENAI_BASE_URL -ErrorAction SilentlyContinue
$env:ANTHROPIC_BASE_URL='https://coderxiaoc.com'
$env:ANTHROPIC_API_KEY='<set Claude-family token locally>'
python launch_scientist_bfts.py `
  --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json `
  --idea_idx 0 `
  --skip_writeup `
  --skip_review
```

Completion directory:

- `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`

Current handoff report:

- `results/ai_scientist_v2_live_run_handoff/handoff.md`: `overall_status=complete`,
  16 ready checks, 0 pending checks, 0 failed checks, 1 completion directory.

## Stage Results

Stage 1, initial implementation:

- Produced a runnable offline synthetic benchmark after an earlier HF model
  download failure.
- Best non-buggy result: skill task-success rate 0.80, full excerpt 0.80,
  abstract 0.20, generic summary 0.00, no context 0.00.
- Skill average token cost was 86.2 versus 113.2 for full excerpt.

Stage 2, baseline tuning:

- Repeated the same deterministic result.
- `n_epochs` tuning did not improve metrics, which is expected because the
  selected agent is deterministic and not actually learning.

Stage 3, creative research:

- The HF/semantic-data branch is retained as a failed branch only.
- The branch attempted real/scientific dataset loading and semantic scoring,
  but the generated findings record invalid dataset loading/synthetic padding
  and missing `sentence_transformers`.
- Do not promote these numbers into the main paper as valid real-data results.

Stage 4, ablation:

- Retrieval-depth sensitivity ran on the synthetic benchmark.
- Skill validation task-success rate stayed 0.80 for K=1,2,3,5 and rose to
  1.00 for K=all.
- Treat this as AI-Scientist-v2-generated sensitivity evidence, not the final
  main-paper component ablation.

## Fix Applied To AI-Scientist-v2

`D:\a_work\gitee\ai-scientist-v2\ai_scientist\treesearch\journal.py` was
patched so `get_best_node(only_good=False)` still avoids selecting buggy nodes
when any good node exists.

Verification:

```powershell
python -m py_compile ai_scientist\treesearch\journal.py
```

A small runtime assertion also verified that a good node is selected over a
higher-metric buggy node. Existing run artifacts were refreshed so Stage 1-3
best nodes point to non-buggy `4e81fec5722241bb9a18b8de3cb8a7cc`, and Stage 4
points to non-buggy `ed279bad001141d4892d20bd675c19ec`.

## Report Refresh

The stale external-evidence state was refreshed in dependency order:

```powershell
python scripts\check_external_evidence_closure.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

Current status:

- External evidence closure queue: 2 items, 0 failed checks.
- External evidence execution packets: 2 packets, 0 failed checks.
- Goal completion: 77 ready, 3 pending, 0 failed.
- Reproducibility package: 305 ready, 1 pending, 0 failed.

## Evidence Boundary

This phase completes the bounded AI-Scientist-v2 smoke and full-live-run
requirements for the local project gate. It does not complete human semantic
fidelity, prove reliable arbitrary-PDF-to-skill automation, prove provider
economics, or make the AAAI paper submission-final.
