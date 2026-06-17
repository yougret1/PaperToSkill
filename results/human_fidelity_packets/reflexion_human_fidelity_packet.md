# Human Fidelity Review Packet: Reflexion

Evidence boundary: this packet is an input for human review. It is not a completed annotation.

## Review Instructions

- Review the generated skill against the curated source note and extracted paper text.
- Use source anchors where available, but judge semantic fidelity rather than lexical overlap alone.
- Record one score per criterion and cite the source span or skill section that justifies the score.
- Mark unsupported or inferred transfer guidance explicitly instead of folding it into source-backed fidelity.

## Score Scale

- 0: Missing or contradicts the paper.
- 1: Present but vague, materially incomplete, or weakly grounded.
- 2: Mostly faithful with minor omissions or wording issues.
- 3: Faithful, operationally useful, and source-supported.

## Artifact Summary

- Generated skill: `generated_skills/reflexion/SKILL.md`
- Curated source note: `papers/notes/reflexion_note.md`
- Extracted paper text: `papers/extracted/reflexion.txt`
- Source map: `generated_skills/reflexion/references/source_map.json`
- Source-span report: `results/evaluations/reflexion_source_span_validation_v0.json`
- Deterministic skill coverage: 8.267/9
- Source-span support rate: 1.0
- Invalid source-span ranges: 0
- Source-map entries: 11
- Skill words: 479
- Source note words: 437

## Criteria

| Criterion | Question | Score | Evidence note |
| --- | --- | --- | --- |
| Central contribution fidelity | Does the skill preserve the paper's central contribution without overclaiming? |  |  |
| Operational workflow fidelity | Does the skill preserve the executable workflow, roles, stages, or search policy needed to reuse the method? |  |  |
| Validation and evidence fidelity | Does the skill preserve the paper's validation protocol, evaluation domains, and reported evidence without distorting them? |  |  |
| Failure and limitation fidelity | Does the skill preserve important limitations, failure modes, and stop conditions? |  |  |
| Source grounding | Are source-backed instructions traceable to the cited note or extracted-paper spans? |  |  |
| Transfer boundary discipline | Does the skill separate paper-backed content from inferred transfer guidance and harness-specific adaptation? |  |  |

## Generated Skill

```markdown
---
name: reflexion-paper-skill
description: Use when applying the paper-derived method from Reflexion Language Agents with Verbal Reinforcement Learning as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# Reflexion: Language Agents with Verbal Reinforcement Learning

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/notes/reflexion_note.md`

## Paper Snapshot

Reflexion is a framework for teaching language agents through verbal reinforcement
instead of weight updates. The agent reflects on feedback, stores reflective text in
episodic memory, and uses that memory to improve later attempts. The paper evaluates the
approach on decision-making, reasoning, and programming tasks and reports large gains
over strong baselines. Source anchors: extracted text lines 25-42.

## Central Contribution

Reflexion is a framework for teaching language agents through verbal reinforcement
instead of weight updates.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Use an Actor, Evaluator, and Self-Reflection model rather than weight updates. Source anchors: lines 189-193.
2. Turn feedback into verbal self-reflections and store them in memory for later trials. Source anchors: lines 201-217, 244-255, 257-266.
3. Treat short-term memory as trajectory history and long-term memory as accumulated self-reflections. Source anchors: lines 257-266.
4. Iterate trials until the evaluator marks the trajectory correct, while the actor conditions future actions on the memory buffer. Source anchors: lines 269-276.
5. Support multiple feedback sources, including environment feedback, heuristics, self-generated unit tests, and evaluator scoring. Source anchors: lines 69-75, 232-247.

## Validation

- Decision-making on ALFWorld, with Reflexion improving by 22% absolute over strong baselines in 12 iterative steps. Source anchors: lines 84-91, 289-318.
- Reasoning on HotPotQA, with Reflexion improving by 20%. Source anchors: lines 84-91, 362-378, 390-426.
- Programming on HumanEval, MBPP, Rust translation, and LeetcodeHardGym, with HumanEval Python pass@1 reported at 91%. Source anchors: lines 84-91, 430-505.

## Failure Cases

- Reflexion can still get stuck in local minima and has no formal guarantee of success. Source anchors: lines 76-83, 527-533.
- The memory component is limited to a sliding window in the paper, and the authors suggest more advanced structures for future work. Source anchors: lines 527-533.
- Some environments and tasks remain difficult, especially where very creative behavior or richer interaction is required. Source anchors: lines 741-776.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
```

## Curated Source Note Excerpt

```markdown
# Reflexion: Language Agents with Verbal Reinforcement Learning

## Source

- Paper ID: `reflexion`
- arXiv: `https://arxiv.org/abs/2303.11366`
- PDF: `papers/raw/reflexion.pdf`
- Extracted text: `papers/extracted/reflexion.txt`
- Render check: `output/pdf/reflexion/page-01.png`
- Extraction notes: PDF has 19 pages. `pdftotext -layout` produced
  `papers/extracted/reflexion.txt`. Page 1 was visually rendered and inspected.

## Abstract

Reflexion is a framework for teaching language agents through verbal
reinforcement instead of weight updates. The agent reflects on feedback, stores
reflective text in episodic memory, and uses that memory to improve later
attempts. The paper evaluates the approach on decision-making, reasoning, and
programming tasks and reports large gains over strong baselines.

Source anchors: extracted text lines 25-42.

## Methods

1. Use an Actor, Evaluator, and Self-Reflection model rather than weight
   updates. Source anchors: lines 189-193.
2. Turn feedback into verbal self-reflections and store them in memory for
   later trials. Source anchors: lines 201-217, 244-255, 257-266.
3. Treat short-term memory as trajectory history and long-term memory as
   accumulated self-reflections. Source anchors: lines 257-266.
4. Iterate trials until the evaluator marks the trajectory correct, while the
   actor conditions future actions on the memory buffer. Source anchors:
   lines 269-276.
5. Support multiple feedback sources, including environment feedback,
   heuristics, self-generated unit tests, and evaluator scoring. Source anchors:
   lines 69-75, 232-247.

## Experiments

- Decision-making on ALFWorld, with Reflexion improving by 22% absolute over
  strong baselines in 12 iterative steps. Source anchors: lines 84-91,
  289-318.
- Reasoning on HotPotQA, with Reflexion improving by 20%. Source anchors:
  lines 84-91, 362-378, 390-426.
- Programming on HumanEval, MBPP, Rust translation, and LeetcodeHardGym, with
  HumanEval Python pass@1 reported at 91%. Source anchors: lines 84-91,
  430-505.

## Limitations

- Reflexion can still get stuck in local minima and has no formal guarantee of
  success. Source anchors: lines 76-83, 527-533.
- The memory component is limited to a sliding window in the paper, and the
  authors suggest more advanced structures for future work. Source anchors:
  lines 527-533.
- Some environments and tasks remain difficult, especially where very creative
  behavior or richer interaction is required. Source anchors: lines 741-776.

## Transfer Notes

- Reflexion is especially relevant for PaperToSkill because it makes memory and
  failure-reflection first-class objects.
- A skill derived from this paper should preserve the actor/evaluator/self-
  reflection loop, the short-term vs long-term memory split, and the policy of
  storing lessons from failed attempts.
- For a local harness, treat unavailable environment actions or feedback
  sources as a limitation and fall back to planning or analysis mode.
```
