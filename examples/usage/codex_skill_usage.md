# Usage Example: Loading a Generated Skill in a Codex-Style Harness

## Goal

Use the Toolformer PaperToSkill artifact to plan a local tool-use experiment.

## Inputs

- Skill: `generated_skills/toolformer/SKILL.md`
- Source map: `generated_skills/toolformer/references/source_map.json`
- Live prompt packet: `results/live_transfer_prompts/toolformer_v0/codex_skill__full_skill.md`

## Procedure

1. Load `generated_skills/toolformer/SKILL.md` as the task skill or paste it into
   the harness context.
2. Use the live prompt packet as the task request.
3. Require the model to mark source-backed steps separately from inferred
   adaptations.
4. Save the response to:
   `results/live_transfer_prompts/toolformer_v0/responses/codex_skill__full_skill.md`
5. Score the response with the live-transfer response evaluator:

   ```powershell
   python scripts\evaluate_live_transfer_responses.py `
     --index results\live_transfer_prompts\toolformer_v0\index.json `
     --output-json results\live_transfer_prompts\toolformer_v0\evaluation.json `
     --output-md results\live_transfer_prompts\toolformer_v0\evaluation.md
   ```

## Expected Output Shape

- Sufficiency judgment.
- Required tools or simulated APIs.
- Step-by-step Toolformer-style data-generation plan.
- Validation checks and stop conditions.
- Source-backed versus inferred adaptation labels.
- At least one logged failure branch.

## Evidence Boundary

This example demonstrates how to run the usage task. The current Toolformer
Codex-style full-skill response exists and is scored in
`results/live_transfer_prompts/evaluation.md`; the other paper response sets
remain separate pending evidence.
