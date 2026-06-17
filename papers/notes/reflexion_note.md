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

