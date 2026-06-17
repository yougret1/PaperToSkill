# PaperToSkill Live Transfer Prompt

## Harness

- Harness ID: `claude_project_prompt`
- Harness label: Claude-style project prompt harness

## Harness Instructions

Act as a project-level research assistant using the provided context as reusable project instructions. Produce a harness-neutral plan that a Claude-style agent could follow, including assumptions, unavailable tools, validation checks, and transfer-specific adaptations.

## Context Variant

- Variant ID: `generic_summary`
- Variant label: Generic prose summary baseline
- Source path: `baselines/ai_scientist_v2_generic_summary.md`
- Dropped sections: none

## Task

Given the PaperToSkill idea, produce a small local agent-run plan inspired by AI Scientist-v2. The plan must preserve generalized idea generation, the four-stage experiment manager, node lifecycle, debug/refine branching, replication and aggregation, visual review, limitations, ethics, and harness-transfer adaptations.

## Required Output Contract

- A concise run objective for the PaperToSkill experiment.
- A four-stage table covering preliminary investigation, hyperparameter tuning, research agenda execution, and ablation studies.
- A node lifecycle schema with plan, code/action, execution result or error, metrics, feedback, status, and next action.
- A debug/refine policy that treats buggy and non-buggy nodes differently.
- A replication and aggregation plan with random seeds and summarized metrics.
- A visual or VLM-style review plan for figures/tables/logs.
- Limitations, ethics, and disclosure notes copied or adapted from the source-backed skill.
- A transfer-adaptation note explaining what changed for the target harness.

## Evaluation Notes

- Do not claim live experimental success unless an actual run was executed.
- Preserve source-backed claims separately from harness-specific adaptations.
- Record missing tools or unavailable execution privileges as limitations, not silent assumptions.

## Context

# Generic Summary: AI Scientist-v2

The AI Scientist-v2 is an automated scientific discovery system that improves
on the original AI Scientist. It can generate research ideas, run experiments,
make plots, write manuscripts, and review papers. It removes some dependence on
human-authored templates and uses tree search to explore experiments. It also
uses a vision-language model to improve figures and captions.

The system was evaluated by generating three papers and submitting them to an
ICLR workshop. One generated paper received scores high enough for workshop
acceptance, while the others were not accepted. The authors argue that this is a
milestone for AI-generated scientific research, but they also note that the
quality is not yet comparable to top-tier conference papers.

Important limitations include hallucinated citations, insufficient rigor in some
generated experiments, and unresolved ethical questions about AI-generated
papers. The authors emphasize transparency, disclosure, and community norms for
AI-generated science.
