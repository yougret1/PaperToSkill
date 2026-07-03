# PaperToSkill Human Fidelity Reviewer Bundle

Evidence boundary: this bundle prepares independent review. It does not contain completed human annotations.

## Files

- `annotation_guide.md`: scoring protocol and workflow.
- `annotation_template.csv`: file reviewers should fill.
- `*_human_fidelity_packet.md`: one packet per paper.
- `reviewer_bundle_manifest.json`: file list and SHA256 checksums.

## Review Workflow

1. Read `annotation_guide.md`.
2. Open each paper packet listed below.
3. Fill every row in `annotation_template.csv` with score/evidence/confidence/reviewer metadata.
4. Leave unreviewed rows blank; do not convert missing review rows into zero scores.
5. Return the filled `annotation_template.csv` to the PaperToSkill repository owner.

## Paper Packets

| Paper | Packet |
| --- | --- |
| AI Scientist-v2 | `ai_scientist_v2_human_fidelity_packet.md` |
| Reflexion | `reflexion_human_fidelity_packet.md` |
| AIDE | `aide_human_fidelity_packet.md` |
| Toolformer | `toolformer_human_fidelity_packet.md` |

## Claim Boundary

PaperToSkill cannot claim human validation until the strict summarizer reports all 24 rows scored with no errors.
