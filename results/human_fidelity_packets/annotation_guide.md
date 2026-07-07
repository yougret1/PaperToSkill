# Human Fidelity Annotation Guide

Evidence boundary: this guide prepares independent human review. It does not contain completed annotations.

## Workflow

1. Open the packet for one paper and read the generated skill, source-note excerpt, and artifact summary.
2. Score each criterion using the Likert scale: 5 = Strongly Agree, 4 = Agree, 3 = Neutral / Neither agree nor disagree, 2 = Disagree, 1 = Strongly Disagree.
3. Fill `evidence_locator` with a source-note line, source-map entry, generated-skill section, or packet section that supports the judgment.
4. Fill `evidence_note` with the shortest explanation needed to justify the score.
5. Fill `confidence_0_to_1`, `reviewer_id`, `review_date`, and `needs_discussion` (`true` or `false`).
6. If multiple reviewers score the same paper and criterion, append another row with the same `paper_id` and `criterion_id` but a distinct `reviewer_id`.
7. Run `scripts\summarize_human_fidelity_annotations.py --strict` before using the annotations in any claim.

## Completion Requirements

- All 24 paper-by-criterion cells must have at least one score from 1 to 5.
- Every scored row must include an evidence_locator and evidence_note.
- Every scored row must include reviewer_id, review_date, and confidence_0_to_1.
- Every scored row must include needs_discussion as true or false; use true when the score depends on ambiguous source support or inferred transfer guidance.
- Multiple reviewers may score the same paper-by-criterion cell by adding rows with the same paper_id and criterion_id and distinct reviewer_id values.
- Do not claim human validation until the summarizer reports annotation_status=complete and zero errors.

## Packets

| Paper | Packet | Rows |
| --- | --- | --- |
| AI Scientist-v2 | `results/human_fidelity_packets/ai_scientist_v2_human_fidelity_packet.md` | 6 |
| Reflexion | `results/human_fidelity_packets/reflexion_human_fidelity_packet.md` | 6 |
| AIDE | `results/human_fidelity_packets/aide_human_fidelity_packet.md` | 6 |
| Toolformer | `results/human_fidelity_packets/toolformer_human_fidelity_packet.md` | 6 |
