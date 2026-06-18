# PaperToSkill Usage Examples

These examples are paper-facing experiment artifacts. They show how a user or
agent can apply the generated skills, but they are not completed live model
results.

## Examples

- `codex_skill_usage.md`: use a generated `SKILL.md` in a Codex-style harness.
- `auto_note_scaffold_usage.md`: generate an auditable note scaffold from
  extracted paper text, then convert it to a skill.
- `model_ablation_usage.md`: run the prepared Claude/GPT-family prompt grid and
  later add DeepSeek using the same protocol.

## Local Verification

Run the usage-example gate from the repository root:

```powershell
python scripts\check_usage_examples.py `
  --output-json results\reproducibility\usage_example_report.json `
  --output-md results\reproducibility\usage_example_report.md `
  --strict
```

The gate checks example files, prompt and response slots, and an offline
auto-note-to-skill example chain. It does not execute live model calls.

## Evidence Boundary

The current repository supports deterministic/offline readiness. Live response
files, model-specific scoring, provider billing, and human semantic annotations
remain pending external evidence.
