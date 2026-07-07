# Submission Bundle Manifest

Evidence boundary: this manifest records local package files, hashes, and gate statuses. It does not claim final submission readiness or completed external evidence.

- Overall status: ready_with_pending_external_evidence
- Ready checks: 11
- Failed checks: 0

## Files

| ID | Present | Bytes | SHA256 | Path |
| --- | --- | --- | --- | --- |
| aaai_pdf | yes | 174234 | 246970b002c4ea889f678dca225fc5c15143cc567c784f2010c18c70385b511f | paper/aaai/papertoskill_aaai2027.pdf |
| aaai_tex | yes | 25140 | 207004dbff13739e813afde22c6821c41797b7bb09bfdba5da5f67981ab392f8 | paper/aaai/papertoskill_aaai2027.tex |
| aaai_tables | yes | 10557 | 301b44711734e819452ea1421e1ddd3282bf7285d3c13dc2d172256c548fefce | paper/aaai/papertoskill_tables.tex |
| aaai_supporting_tables | yes | 1306 | ac327860b659327f7b9e0a844a0d6701e72ff4f355e178982f1734967520d20c | paper/aaai/papertoskill_supporting_tables.tex |
| aaai_refs | yes | 3017 | db0bfb929e7c083d06dc10c56cf814e6e382c623bc5390a9b31cd31ccdd5e35a | paper/aaai/papertoskill_refs.bib |
| aaai_readme | yes | 1268 | 27962ea52913425444a1e0fceb62d1e2475a026c693ad83f8a6334242bbb7455 | paper/aaai/README.md |
| aaai_style | yes | 16915 | 391bce82815bf698b8e382dd3ae7e30c75d7ab46df140cb295b1266016bc8623 | paper/aaai/aaai2027.sty |
| aaai_bst | yes | 30207 | 5db7765ba99de5c1e4686f9b3940a0add9c5e702f2164514462bec130ccb6e3c | paper/aaai/aaai2027.bst |
| aaai_author_kit | yes | 5495535 | e28c6ac9bc6eb3b4e2d849547d2cefb5162610ee39d0a12e0dc62d1126b44a7d | paper/aaai/AuthorKit27.zip |
| aaai_package_report | yes | 3839 | e797a683cd76656e561935a0c41e600c6649b2361990da1869f0624efcf4b1b7 | results/reproducibility/aaai_package_report.json |
| paper_claim_report | yes | 14899 | b216a93e1b161bcae19ad8764446fe0cecb75b32a50ad9f166af22a415053803 | results/reproducibility/paper_claim_report.json |
| paper_table_report | yes | 88969 | 03d9afa9ea59bc2d50a5f825905b9281cc786c5e6c0524de9776fa0179407563 | results/reproducibility/paper_table_report.json |
| submission_review_report | yes | 6686 | 80da398a44ba279df5ff963d731ac8d67abfe7f77ff557b5d3db2177cae8564d | results/reproducibility/submission_review_report.json |
| package_report | yes | 96785 | ec6d03d709cc000cac706327144789344b350b8ad66bf6efc799c5dd5877b69c | results/reproducibility/package_report.json |
| goal_completion_report | yes | 17048 | 7fd9e4e7628d621d8e858cab8045b094c4f9cc405591a5563b1f35a6aee6b678 | results/reproducibility/goal_completion_report.json |
| external_closure_report | yes | 2293 | 4fd5251e07807f0a42a19ddf33c61bace196e5a7f25b57ece7677c4784070625 | results/external_evidence_closure/closure.json |
| external_packets_report | yes | 7094 | 24fb88536d93e14db059256ed641e5271e605af6a908d36eb269018e49ae4dcd | results/external_evidence_packets/packets.json |
| aaai_submission_decision_report | yes | 10275 | 0866c22c3ee6d23bc448e14ceeeca761f4161d9e0a41bf7dca1e15e584d90003 | results/aaai_submission_decision/decision.json |
| human_fidelity_summary | yes | 2639 | 883ea1e61b4020f43a7d8a426eb393c1b923256cb2f9143b92d5b1aecce4b3c8 | results/human_fidelity_packets/annotation_summary.json |
| repo_readme | yes | 7392 | 0c8da6c030f47e272af3c7f8ec2df170fa861511e6de140f8203dae476667c57 | README.md |
| artifact_map | yes | 79969 | ee5584a68a93722c7ed6689192b20b1d36b1436832f36fc1e76fd44f8b92c1ff | research/artifact_map.md |
| runbook | yes | 71573 | f339567244eb917e946030f4243f180e3f3ef917324692b801b3ce48312211ca | research/runbook.md |
| goal_completion_audit | yes | 20978 | 9b4ce030896b269b77822684b3c3059325acd828abce80829a84f63dfff6bf63 | research/goal_completion_audit.md |
| submission_checklist | yes | 11547 | f7b4b770e346dfaa8697d012681231bcd9e03ff57275ad2cde76c1e602c68fbc | research/submission_checklist.md |
| review_report | yes | 15285 | 571e8ac2909eeaea81fc09591aa38eb9d43e3b62006854c35eff828cd5918770 | research/review_report.md |
| rebuttal_bank | yes | 13061 | cd1e38fcdb6eaea5faeb935163452f96d8ee2ca9c0bf61c1d7e8d89d7072a848 | research/rebuttal_bank.md |

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| submission_bundle_files_present | ready | all files present | submission bundle manifest inputs |
| submission_bundle_aaai_package_report_status | ready | overall_status=ready | results/reproducibility/aaai_package_report.json |
| submission_bundle_paper_claim_report_status | ready | overall_status=ready | results/reproducibility/paper_claim_report.json |
| submission_bundle_paper_table_report_status | ready | overall_status=ready | results/reproducibility/paper_table_report.json |
| submission_bundle_submission_review_report_status | ready | overall_status=ready | results/reproducibility/submission_review_report.json |
| submission_bundle_package_report_status | ready | overall_status=ready | results/reproducibility/package_report.json |
| submission_bundle_goal_completion_report_status | ready | overall_status=not_complete_pending_external_evidence | results/reproducibility/goal_completion_report.json |
| submission_bundle_external_closure_report_status | ready | overall_status=pending_external_evidence | results/external_evidence_closure/closure.json |
| submission_bundle_external_packets_report_status | ready | overall_status=ready | results/external_evidence_packets/packets.json |
| submission_bundle_aaai_submission_decision_report_status | ready | overall_status=ready | results/aaai_submission_decision/decision.json |
| submission_bundle_external_evidence_boundary_current | ready | package=ready; goal=not_complete_pending_external_evidence; human_fidelity=complete; selected_option=wait_for_external_evidence | results/reproducibility/package_report.json; results/reproducibility/goal_completion_report.json |
