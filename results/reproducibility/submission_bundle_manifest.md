# Submission Bundle Manifest

Evidence boundary: this manifest records local package files, hashes, and gate statuses. It does not claim final submission readiness or completed external evidence.

- Overall status: ready_with_pending_external_evidence
- Ready checks: 11
- Failed checks: 0

## Files

| ID | Present | Bytes | SHA256 | Path |
| --- | --- | --- | --- | --- |
| aaai_pdf | yes | 174034 | 8889b4b7b51893580ad4abec4d40b99aef781afb15ed14cc406d7a28d5f9e453 | paper/aaai/papertoskill_aaai2027.pdf |
| aaai_tex | yes | 24848 | dfb88bcdd4063c9054192746f0b71a8405b7bea57242d95af04444401d3bcacf | paper/aaai/papertoskill_aaai2027.tex |
| aaai_tables | yes | 10557 | 301b44711734e819452ea1421e1ddd3282bf7285d3c13dc2d172256c548fefce | paper/aaai/papertoskill_tables.tex |
| aaai_supporting_tables | yes | 1306 | ac327860b659327f7b9e0a844a0d6701e72ff4f355e178982f1734967520d20c | paper/aaai/papertoskill_supporting_tables.tex |
| aaai_refs | yes | 3017 | db0bfb929e7c083d06dc10c56cf814e6e382c623bc5390a9b31cd31ccdd5e35a | paper/aaai/papertoskill_refs.bib |
| aaai_readme | yes | 1280 | 08f6412ca328a8e297fc1cdab4bcf9d5a230864f910e55fec46c94ddd1ef47b9 | paper/aaai/README.md |
| aaai_style | yes | 16915 | 391bce82815bf698b8e382dd3ae7e30c75d7ab46df140cb295b1266016bc8623 | paper/aaai/aaai2027.sty |
| aaai_bst | yes | 30207 | 5db7765ba99de5c1e4686f9b3940a0add9c5e702f2164514462bec130ccb6e3c | paper/aaai/aaai2027.bst |
| aaai_author_kit | yes | 5495535 | e28c6ac9bc6eb3b4e2d849547d2cefb5162610ee39d0a12e0dc62d1126b44a7d | paper/aaai/AuthorKit27.zip |
| aaai_package_report | yes | 3839 | 86e7ef29cce00993e08e8ed9cf726424f107bb72a3a7d67f9665ab1a95ef2ca4 | results/reproducibility/aaai_package_report.json |
| paper_claim_report | yes | 14660 | 0e8998c76819805ff5fc8bba8df4203eb6e7c1b446fdad8fb27e0420030c8438 | results/reproducibility/paper_claim_report.json |
| paper_table_report | yes | 88969 | 03d9afa9ea59bc2d50a5f825905b9281cc786c5e6c0524de9776fa0179407563 | results/reproducibility/paper_table_report.json |
| submission_review_report | yes | 6707 | 8aba4e39e701974c077be2d8134180508fa4f58cdae6f942329af8bc752946fc | results/reproducibility/submission_review_report.json |
| package_report | yes | 96841 | a61b1e48636659ad652c77ac58287868218d5e51095e346412aefb5e8445e929 | results/reproducibility/package_report.json |
| goal_completion_report | yes | 17093 | bfdb87ee3cbff55340910c2dfd1df7ae62853d3812b64bd8653e53514c2d5213 | results/reproducibility/goal_completion_report.json |
| external_closure_report | yes | 2912 | 6300acd439ae24a0e8f36c02ebbc924a2b522b00fd1114c065372c9eec302516 | results/external_evidence_closure/closure.json |
| external_packets_report | yes | 10446 | 5687838eee38e09f22d95cfd0f37605369c0dfdfa3bb68264be31543e9c50669 | results/external_evidence_packets/packets.json |
| aaai_submission_decision_report | yes | 10306 | 80b42507176e3ccba3fb497e01a58a47c4ec769119a2df1cf0ce6a37cdf60321 | results/aaai_submission_decision/decision.json |
| human_fidelity_summary | yes | 2629 | 9c17a037adff51537a5a1428576dcc4bddefc9e658ded7f423b825147de92bc4 | results/human_fidelity_packets/annotation_summary.json |
| submission_checklist | yes | 11067 | 1fe8073157d2e3e10e4a48e139c6ae80273f42104b6a39679d52eeb2227a498c | research/submission_checklist.md |
| review_report | yes | 15178 | 3f9791bfd0f0b6f0b0210a31f0fe30020180f3013252e1b675109d4868ac03a2 | research/review_report.md |
| rebuttal_bank | yes | 12820 | 5d82b4781b0fb7a2355f7e876f5cffe3294f8ef7372420eb466d54da13577435 | research/rebuttal_bank.md |

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| submission_bundle_files_present | ready | all files present | submission bundle manifest inputs |
| submission_bundle_aaai_package_report_status | ready | overall_status=ready | results/reproducibility/aaai_package_report.json |
| submission_bundle_paper_claim_report_status | ready | overall_status=ready | results/reproducibility/paper_claim_report.json |
| submission_bundle_paper_table_report_status | ready | overall_status=ready | results/reproducibility/paper_table_report.json |
| submission_bundle_submission_review_report_status | ready | overall_status=ready | results/reproducibility/submission_review_report.json |
| submission_bundle_package_report_status | ready | overall_status=ready_with_pending_external_evidence | results/reproducibility/package_report.json |
| submission_bundle_goal_completion_report_status | ready | overall_status=not_complete_pending_external_evidence | results/reproducibility/goal_completion_report.json |
| submission_bundle_external_closure_report_status | ready | overall_status=pending_external_evidence | results/external_evidence_closure/closure.json |
| submission_bundle_external_packets_report_status | ready | overall_status=ready | results/external_evidence_packets/packets.json |
| submission_bundle_aaai_submission_decision_report_status | ready | overall_status=ready | results/aaai_submission_decision/decision.json |
| submission_bundle_external_evidence_boundary_current | ready | package=ready_with_pending_external_evidence; goal=not_complete_pending_external_evidence; human_fidelity=pending; selected_option=wait_for_external_evidence | results/reproducibility/package_report.json; results/reproducibility/goal_completion_report.json |
