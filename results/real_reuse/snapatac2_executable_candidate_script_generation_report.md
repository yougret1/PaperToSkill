# SNAP Executable-Candidate Script Generation Report

Evidence boundary: This run only generates candidate Python scripts from prompt packets. It does not execute candidates, score outputs, append raw rows, or replace paper-facing main rows.

- Run ID: `phase112_gpt_snapatac2_executable_candidate_scripts_v2`
- Overall status: `partial`
- Status counts: {'success': 1}
- Model family: `GPT-family`
- Model alias: `gpt-5.5`
- Candidate script dir: `D:\a_work\gitee\PaperToSkill\results\real_reuse\snapatac2_executable_candidate_scripts\phase112_gpt_snapatac2_executable_candidate_scripts_v2`
- Selected packet count: 4
- Recorded row count: 1

Interruption note: The phase112 live GPT-family run produced `SNAP-T1_summary.py` from the revised cross-platform prompt. The next provider request did not return after an extended wait; the matching long-running Python generation process was stopped and this partial record was preserved. Treat the missing three candidate scripts as provider-availability / incomplete-generation metadata, not method-quality evidence.

| Task | Condition | Status | Script | Call Status |
| --- | --- | --- | --- | --- |
| SNAP-T1 | summary | success | results/real_reuse/snapatac2_executable_candidate_scripts/phase112_gpt_snapatac2_executable_candidate_scripts_v2/SNAP-T1_summary.py | live_endpoint_response_file_present |

