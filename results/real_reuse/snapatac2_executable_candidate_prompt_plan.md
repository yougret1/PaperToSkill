# SNAP Executable-Candidate Prompt Plan

Evidence boundary: This is a local prompt-packet plan only. It does not execute model calls, does not score task outputs, does not append raw rows, and does not replace main rows.

- Prompt mode: `full`

| Task | Condition | Prompt | Expected Script | Required Artifacts |
| --- | --- | --- | --- | --- |
| SNAP-T1 | summary | results/real_reuse/snapatac2_executable_candidate_prompts/SNAP-T1_summary.md | SNAP-T1_summary.py | embedding.csv, cell_features.csv, fragment_summary.json |
| SNAP-T1 | papertoskill | results/real_reuse/snapatac2_executable_candidate_prompts/SNAP-T1_papertoskill.md | SNAP-T1_papertoskill.py | embedding.csv, cell_features.csv, fragment_summary.json |
| SNAP-T2 | summary | results/real_reuse/snapatac2_executable_candidate_prompts/SNAP-T2_summary.md | SNAP-T2_summary.py | clusters.csv, marker_summary.json, embedding.csv |
| SNAP-T2 | papertoskill | results/real_reuse/snapatac2_executable_candidate_prompts/SNAP-T2_papertoskill.md | SNAP-T2_papertoskill.py | clusters.csv, marker_summary.json, embedding.csv |

Use these prompt packets only to generate paired Summary/PaperToSkill candidate scripts for the executable-candidate runner.
Provider latency, timeout, and retry counts remain availability metadata, not method-effectiveness metrics.
