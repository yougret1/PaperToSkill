# Related Work Gap Map

## Capability Groups

| Capability | Existing Examples | What PaperToSkill Reuses | Gap PaperToSkill Targets |
| --- | --- | --- | --- |
| Automated research workflows | AI Scientist-v2, Agent Laboratory | Phase structure, artifact discipline, experiment execution, writing/review loops | A paper-to-skill converter that lets users reuse those workflows outside the original system |
| Code and experiment search | AIDE, AI Scientist-v2 | Tree search, debug loops, solution selection, retained cases | Skill-level encoding of search policies and failure handling |
| Skill libraries and reuse | Voyager | Skill storage, retrieval, self-verification, compositional reuse | Natural-language skill extraction from papers, not only code skills learned in one environment |
| Reflection and memory | Reflexion | Verbal feedback, episodic memory, retry policy | Failure-branch preservation in generated skills |
| Tool and interface design | Toolformer, SWE-agent | Tool-call decisions, API assumptions, agent-computer interface constraints | Cross-harness transfer notes and tool-contract extraction |

## Reviewer Objections To Prepare For

- "This is only summarization." Response path: evaluate downstream task success,
  executable workflow coverage, and unsupported instruction rate, not only
  summary quality.
- "Generated skills may hallucinate." Response path: source-map every fragile
  step and include a fidelity judge or audit.
- "Skill usefulness is subjective." Response path: define task rubrics,
  baselines, and inter-rater or deterministic checks where possible.
- "The method may only work for agent papers." Response path: start with agent
  papers because they are operational, then add one tool-use and one
  theory-heavy stress case.
- "Cross-harness transfer is noisy." Response path: log tool contracts,
  environment assumptions, and intervention counts.

