# Experiment Queue

## Ready

| ID | Question | Command | Expected Output | Gate |
| --- | --- | --- | --- | --- |
| E0 | Does the deterministic extractor create a valid skill and source map? | `python -m unittest discover -s tests -v` | 1 passing unittest | Execution |
| E1 | Can PaperToSkill convert the paper-like seed note into a retained skill case? | `python scripts\papertoskill_extract.py --source examples\papertoskill_paper_note.md --output generated_skills\papertoskill_paper_note --name papertoskill-paper-note` | `generated_skills/papertoskill_paper_note/SKILL.md` and `references/source_map.json` | Execution |
| E2 | Can the abstract-only seed still produce a fallback scaffold? | `python scripts\papertoskill_extract.py --source ai_scientist_inputs\papertoskill.md --output generated_skills\papertoskill_seed --name papertoskill-seed --title "PaperToSkill Seed"` | fallback skill with generic workflow and source map | Execution |
| E2.5 | Can a real paper-derived note generate a scored retained skill? | `python scripts\papertoskill_extract.py --source papers\notes\ai_scientist_v2_note.md --output generated_skills\ai_scientist_v2 --name ai-scientist-v2-paper-skill` then `python scripts\evaluate_skill.py --skill generated_skills\ai_scientist_v2\SKILL.md --rubric benchmarks\rubric_v0.json --output results\evaluations\ai_scientist_v2_rubric_v0.json` | generated AI Scientist-v2 skill and v0 rubric score | Execution |

## Pending Remote LLM Recovery

| ID | Question | Command | Expected Output | Blocker |
| --- | --- | --- | --- | --- |
| E3 | Can AI-Scientist-v2 run a tiny PaperToSkill agentic search? | `python launch_scientist_bfts.py --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json --idea_idx 0 --skip_writeup --skip_review` | experiment logs under `ai-scientist-v2/experiments` | Remote provider account pool exhausted |
| E4 | Can an LLM-assisted extractor improve method-step fidelity over the deterministic scaffold? | TBD after endpoint works | paired deterministic vs LLM-assisted generated skills | Remote provider account pool exhausted |

## Next Design Work

| ID | Question | Needed Artifact |
| --- | --- | --- |
| E5 | Which benchmark papers should enter the first manual evaluation? | paper PDFs or extracted notes for core split |
| E6 | How should unsupported instruction rate be scored? | rubric and evaluator script |
| E7 | How should harness transfer be simulated before real Claude/Codex paired runs? | prompt templates and task manifests |
