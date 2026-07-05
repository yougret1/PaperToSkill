# SnapATAC2 Executable-Candidate Run Report

Evidence boundary: this diagnostic runner executes candidate scripts under the pre-registered SNAP executable-candidate contract. It writes runner-owned `candidate_output.json`, `artifact_manifest.json`, and `resource_record.json`, then invokes the existing SNAP scorer. It does not append to main raw rows or replace paper-facing main rows.

- Runner ID: `snapatac2_executable_candidate_runner_v0`
- Run ID: `phase111_gpt_snapatac2_executable_candidate_t1`
- Overall status: `complete`
- Raw rows policy: `not_appended_to_main_raw_rows`
- Main rows unchanged: True

| Task | Condition | Status | Score | Success | Failure | Candidate Output |
| --- | --- | --- | --- | --- | --- | --- |
| SNAP-T1 | summary | scored | 0.500 | False | missing_required_artifacts_or_metrics | results/real_reuse/runs/SNAP-T1/summary/phase111_gpt_snapatac2_executable_candidate_t1/candidate_output.json |
| SNAP-T1 | papertoskill | scored | 0.500 | False | missing_required_artifacts_or_metrics | results/real_reuse/runs/SNAP-T1/papertoskill/phase111_gpt_snapatac2_executable_candidate_t1/candidate_output.json |
