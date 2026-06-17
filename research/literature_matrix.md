# Literature Matrix

This is a Phase 1 seed matrix. Statements are source-backed by the linked paper
pages or project pages, but they are not yet a full related-work review.

| Paper | Problem | Reusable Method | Evaluation Signal | Why It Matters For PaperToSkill | Source |
| --- | --- | --- | --- | --- | --- |
| The AI Scientist-v2 | End-to-end automated scientific discovery remains hard to generalize beyond templates. | Progressive agentic tree search with an experiment manager, experiment execution, analysis, plotting, writing, and review. | Submitted autonomous manuscripts to an ICLR workshop; one exceeded average human acceptance threshold according to the paper page. | Directly matches the user's requested development engine and supplies a research automation workflow to translate into skill form. | [arXiv 2504.08066](https://arxiv.org/abs/2504.08066) |
| AIDE | ML engineering requires expensive trial-and-error across code solutions. | Frame ML engineering as code optimization and search over solution trees, reusing and refining promising code. | Evaluated on Kaggle, OpenAI MLE-Bench, and METR RE-Bench according to the paper page. | Supplies a tree-search/debugging pattern for extraction into procedural skills. | [arXiv 2502.13138](https://arxiv.org/abs/2502.13138) |
| Agent Laboratory | Scientific discovery is slow and expensive from idea to report. | Three-stage research workflow with literature review, experimentation, report writing, and human feedback. | Reports reduced expense and researcher assessment of outputs according to the paper page. | Gives a multi-agent research workflow and human-control checkpoints that PaperToSkill should preserve. | [arXiv 2501.04227](https://arxiv.org/abs/2501.04227) |
| Voyager | Open-ended agents need continual exploration and reusable skills. | Automatic curriculum, executable skill library, and iterative prompting using environment feedback and self-verification. | Reports more unique items, longer travel, and faster tech-tree milestones than prior methods according to the paper page. | A strong example where "skill" is already central, useful for testing conversion fidelity. | [arXiv 2305.16291](https://arxiv.org/abs/2305.16291) |
| Reflexion | Language agents struggle to learn efficiently from trial-and-error without weight updates. | Verbal reflections stored in episodic memory to improve future decisions. | Reports improvements across sequential decision-making, coding, and reasoning tasks according to the paper page. | Helps PaperToSkill encode failure branches and reflection loops. | [arXiv 2303.11366](https://arxiv.org/abs/2303.11366) |
| SWE-agent | LM agents need interfaces designed around agent capabilities for software engineering. | Agent-computer interface for navigation, editing, and test execution. | Evaluated on SWE-bench and HumanEvalFix according to the paper page. | Useful for transfer notes and harness/tool-contract extraction. | [arXiv 2405.15793](https://arxiv.org/abs/2405.15793) |
| Toolformer | LMs struggle with arithmetic, lookup, and similar tasks where tools help. | Self-supervised API-call data generation to decide when and how to call tools. | Reports improved zero-shot downstream task performance according to the paper page. | Tests whether PaperToSkill can extract tool-use rules rather than only agent workflows. | [arXiv 2302.04761](https://arxiv.org/abs/2302.04761) |

## Initial Gap

Existing work often introduces a workflow, tool interface, memory mechanism, or
skill library inside a specific system. PaperToSkill's gap is the conversion
layer: preserving such operational knowledge from arbitrary papers into compact,
human-editable skills with validation, failure branches, and transfer notes.

