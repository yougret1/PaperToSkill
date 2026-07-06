# Runbook

## Memory Rule

After any context compaction or session resume, read:

1. `memory/long_term_memory.md`
2. `memory/short_term_memory.md`

Then update short-term memory with the current phase, blockers, and next action.

## Phase Save And Push Recovery

Save phase-level progress to `origin/main` after verification when network
connectivity allows:

```powershell
git status -sb
git log -1 --oneline
git push origin main
```

If push fails with a GitHub HTTPS connectivity error, keep the local commit and
diagnose the transport separately from project correctness:

```powershell
git status -sb
git log -3 --oneline
git ls-remote --heads origin main
Test-NetConnection github.com -Port 443 | Format-List
```

Current status as of 2026-07-06: the temporary GitHub HTTPS transport blocker
recovered through the AAAI page-limit backup, the later
paper-finalization/submission-review chain, the paper-outline sync, the outline
claim-drift gate, the main-results boundary cleanup, the real-reuse
LLM-ablation handoff guard, the checkpoint-sync records, the outline
evidence-boundary sync, the limitations claim gate, the paper-facing
cost-boundary sync, the stale cost-scope claim guard, the checkpoint-record
guard sync, the recovered pre-submission gate rerun, the paper-conclusion
boundary sync record, the compact SNAP executable-candidate prompt contract,
and the follow-up record-sync/blocker metadata. The later Claude availability
metadata/push-blocker commits and their checkpoint-record backup also
recovered. The latest verified remote
checkpoint before claiming any later phase save is:

```text
91261dd145771f3325ed398d5d773d57b791ddb6 refs/heads/main
91261dd Record Claude metadata backup push blocker
```

The earlier failed remote-backup attempts for `501ffc8`, `48aabac`, `8bdd394`,
`95f1af3`, and `66e4763` remain GitHub transport metadata only. A later
`git push origin main` succeeded, and `git ls-remote --heads origin main`
verified the checkpoint above. Do not create `ok.txt` for GitHub status.

Follow-up record-only commits `93a2abf`, `af3ba31`, and `4a85147` initially
remained local-only because GitHub HTTPS transport failed after the verified
`43f9092` phase save. A later `git push origin main` recovered them together
with `3e18fc5`. A subsequent recovery push also advanced `main` through
`4ae3e76`, `a72c6d2`, `dfd5602`, and `bd3fe6e`, and `git ls-remote --heads
origin main` verified that recovery. The later paper-conclusion boundary sync
advanced and verified `e57df72`, the checkpoint above. Treat the earlier
failures as transport metadata only.

A follow-up record-sync/blocker chain records the verified `e57df72`
paper-conclusion boundary checkpoint in memory/runbook/goal-audit reports. Its
first `git push origin main` and immediate `git ls-remote --heads origin main`
both failed with `Recv failure: Connection was reset`. Treat this as GitHub
transport metadata only; keep the remote-backed baseline at `e57df72` until a
later push and remote check succeed.

A later `git push origin main` recovered the local
record-sync/blocker/Claude-availability chain. The compact SNAP prompt
checkpoint then pushed successfully, and `git ls-remote --heads origin main`
verified `245c2b276842de657103f89b5227b8fe53fa9f10 refs/heads/main`.
The follow-up compact checkpoint record-sync/blocker chain was later pushed
and independently verified at
`a7a9e3e772883e76404ee217a9ed51278c4c2477 refs/heads/main`. Treat earlier
connection resets as GitHub verification-transport metadata only.

The follow-up record-sync backup for that recovered checkpoint was later
pushed and independently verified at
`b770e2005bd881c4afa31be2571cfb01d5207971 refs/heads/main`. A later Claude
availability metadata commit `8ac4ddf Refresh Claude availability metadata`
and blocker-record commit `39c4e0f Record Claude availability push blocker`
were then pushed and independently verified at
`39c4e0ff7a5d500d3250ea7f6dd177a00672fa95 refs/heads/main`. Their first push
and immediate remote check failed with `Recv failure: Connection was reset`;
treat that earlier failure as transport metadata only.

The follow-up checkpoint-record backup commit `3ee014a Record recovered Claude
metadata backup` and blocker-record commit `91261dd Record Claude metadata
backup push blocker` were later pushed and independently verified at
`91261dd145771f3325ed398d5d773d57b791ddb6 refs/heads/main`. Their earlier
connection resets are GitHub transport metadata only.

Follow-up commits `45ef25b Sync remote checkpoint after LLM handoff guard` and
`0538ef1 Record checkpoint sync push blocker` first failed to back up because
GitHub HTTPS transport was unavailable. They are now included in the verified
`5786d7d` remote checkpoint; the earlier failures remain transport metadata,
not project correctness evidence.

The previously unbacked local commits are now remote-backed through the latest
AAAI page-limit checkpoint:

```text
77e8ada Add SNAP executable candidate runner
0983fbc Record SNAP runner push blocker
c4b4b99 Record GitHub push blocker for SNAP runner
2490a9b Update real-reuse stabilization queue
0832201 Sync memory after GitHub retry
4b216b6 Record recovered SNAP runner backup
0734bb9 Record renewed GitHub push blocker
ef8cbe0 Prepare SNAP executable candidate prompts
10a3d1d Record SNAP prompt push blocker
c3f9f05 Clarify SNAP prompt backup status
9829123 Run SNAP executable candidate diagnostics
db535e7 Record SNAP diagnostic checkpoint
fb0baed Sync SNAP diagnostic remote status
b6dc061 Complete SNAP executable candidate diagnostic
a976bbc Record SNAP diagnostic backup recovery
1c8098b Record SNAP backup recovery push blocker
2b823f6 Tighten submission review count checks
ef2bcf7 Record submission review push blocker
b550a26 Clarify SNAP executable candidate results
1727615 Record recovered submission review backup
01dfa6e Sync paper draft SNAP diagnostics
206fa5c Request human fidelity annotation
4532dd9 Sync resume checkpoint memory
bf95213 Record resume memory push blocker
69d23b1 Record recovered resume memory backup
abbd547 Record real-reuse claim checklist boundary
c030015 Record SNAP-T2 executable candidate availability
e1709d3 Record SNAP-T2 availability push blocker
f1c50d5 Sync resume baseline memory
4d2e040 Clarify resume remote memory baseline
ac3926c Guard current remote checkpoint records
3040ce3 Fix checkpoint record guard baseline
2eb5cd2 Stabilize checkpoint guard report detail
7c611f3 Record checkpoint guard push blocker
951a7b2 Fill real-reuse grounding gate evidence
bcd2104 Record grounding gate backup checkpoint
a04c757 Fill quality grounding table evidence
3ef89a6 Record quality table push blocker
cb52fe2 Bound failure branch reproducibility claim
eab454d Align failure branch claim evidence matrix
e2f070e Record recovered claim matrix backup
e110a03 Record claim matrix backup push blocker
bddd900 Record Claude direct availability recheck
9cc0683 Record recovered Claude backup checkpoint
5d11adc Mark deferred study tables explicitly
591a3f1 Record recovered deferred-table backup
34542ec Record deferred backup push blocker
317bdbe Record recovered deferred backup push
54b6780 Refresh Claude availability probe metadata
7a39bfb Record Claude probe push blocker
5d2b98c Record recovered Claude probe backup
6b344fd Gate SNAP-T2 availability artifacts
a9857b1 Record Claude availability recheck
febe844 Sync Claude checkpoint records
d8d968d Record SNAP-T2 retry provider block
583db16 Record SNAP-T2 retry push blocker
9eaeee7 Record recovered SNAP-T2 retry backup
b3441d5 Sync phase115 checkpoint records
cea43eb Record checkpoint sync push blocker
96fce87 Record SNAP-T2 phase116 provider block
2575adc Record recovered phase116 backup
5ad6b54 Add real-reuse LLM ablation family table
896456b Enforce AAAI main page limit
ad14de5 Record AAAI page-limit push blocker
2bc10bd Record recovered AAAI page-limit backup
501ffc8 Remove draft wording from real-reuse table
48aabac Record draft-language gate push blocker
8bdd394 Sync submission records with claim gate
6c5e6a2 Fix submission review stale count test
95f1af3 Record recovered submission test backup
66e4763 Record submission backup push blocker
055566e Sync outline LLM ablation status
71f841b Record recovered outline sync backup
73f4d83 Gate outline paper claim drift
fe499e5 Record outline claim gate checkpoint
21009eb Clarify real-reuse main table boundary
00d32cd Record main table boundary push blocker
1a7ae8c Record recovered main table boundary backup
905899c Guard real-reuse LLM ablation handoff
```

The first remote backup attempt for the AAAI page-limit repair failed with
`Recv failure: Connection was reset`, and the immediate remote check failed
with the same reset error. A later `git push origin main` recovered and
`git ls-remote --heads origin main` verified the current remote checkpoint.
This is GitHub transport metadata only.

Earlier `Recv failure: Connection was reset` and github.com port 443 failures
remain GitHub transport metadata, not project-correctness evidence. The
previously local-only record-sync commit after `db535e7` is now remote-backed.
The later local record-sync commit after `fb0baed` and the phase112 completion
commit are now remote-backed. The later submission-review and AAAI paper-text
sync commits, auxiliary draft/outline sync, human-fidelity request,
resume-memory records, and checkpoint-record guard baseline are also
remote-backed through `5d2b98c`, including the checkpoint-detail,
blocker-record, grounding-gate evidence-sync, follow-up checkpoint-record,
quality-grounding table, claim-boundary cleanup, and claim-evidence-matrix
boundary-sync commits, plus the recovered checkpoint record, push-blocker
record, Claude direct availability recheck, recovered Claude backup checkpoint,
deferred-study table marking, recovered deferred-table backup record, and
deferred-backup push-blocker record, recovered deferred backup push record,
refreshed Claude availability probe metadata, and Claude-probe push-blocker
record, plus the recovered Claude-probe backup record. Earlier `git ls-remote --heads
origin main` failures remain transport history.
Always inspect `git status -sb` and `git log -5 --oneline` before claiming a
clean phase save.

Local-only continuation note: follow-up record-sync commit `e2f070e Record
recovered claim matrix backup` initially remained local-only after `git push
origin main` failed with `Recv failure: Connection was reset`. A later push
recovered and verified `5d2b98c`; that specific historical local-only state
was resolved.

Recovered record-sync note: `b3441d5 Sync phase115 checkpoint records`
corrected the current checkpoint records after `9eaeee7` was verified. Its
first `git push origin main` failed with `Recv failure: Connection was reset`,
and the immediate `git ls-remote --heads origin main` failed with the same
reset error. The follow-up blocker record and phase116 provider-block record
were later pushed successfully, and `git ls-remote --heads origin main`
verified `96fce87967b207e1cd0a0b9b36ba8fb8795eff33 refs/heads/main`.

Re-run remote verification before making future remote-backed checkpoint
claims.

## Local Text-To-Skill Pipeline

Run the deterministic local pipeline from extracted paper text to note, skill,
source map, rubric evaluation, and manifest:

```powershell
python scripts\papertoskill_pipeline.py `
  --source papers\extracted\aide.txt `
  --output-dir results\pipeline_examples\aide_auto `
  --paper-id aide_auto `
  --title "AIDE: AI-Driven Exploration in the Space of Code" `
  --profile aide `
  --skill-name aide-auto-paper-skill `
  --rubric benchmarks\rubric_aide_v0.json
```

Evidence boundary: this command composes deterministic local scaffold steps. It
does not prove human semantic fidelity, live harness success, or reliable
arbitrary-PDF automation.

PDF input is supported when `pdftotext` is available on `PATH`; the manifest
records the generated extracted-text file:

```powershell
python scripts\papertoskill_pipeline.py `
  --source paper\aaai\papertoskill_aaai2027.pdf `
  --output-dir results\pipeline_examples\papertoskill_pdf `
  --paper-id papertoskill_pdf `
  --title "PaperToSkill" `
  --skill-name papertoskill-pdf-pipeline
```

## Planned Real-Reuse Experiments

Source of truth:

```text
research/real_reuse_experiment_plan.md
benchmarks/real_reuse/real_reuse_v0.json
benchmarks/real_reuse/tasks/
benchmarks/real_reuse/fixtures/
benchmarks/real_reuse/fixture_candidates/
benchmarks/real_reuse/asset_locks/
```

Current status: planned specification, per-task execution-contract specs,
fixture requirement manifests, candidate manifests, and asset locks are ready
for all eight tasks. All eight rows now have one GPT-family
Summary-vs-PaperToSkill run. After rerunning the same saved AIDE outputs with
a 300-second local scorer budget, AIDE-T1 scores 0.816/0.817 and AIDE-T2
scores 0.000/0.826. REF rows score 1.000/1.000, SWE-T2 scores 0.000/1.000,
SWE-T1 scores 0.000/0.000 due patch-apply failures, and SNAP rows are below
the pre-registered success threshold. Do not write the AAAI paper as if this
single-run pass establishes aggregate superiority over Summary.

Current experiment priority: stabilize the core real-reuse experiment first
under source-paper objective metrics. Collect auxiliary data during those core
runs when cheap, but run remaining auxiliary analyses only after the core
evidence is stable. Component ablation is appendix-only. User study is last and
only needed for user-efficiency or workflow-improvement claims.

Timing boundary: third-party LLM service latency, API timeouts, provider
retries, and request instability are not core effectiveness metrics. Give model
calls enough timeout/retry budget and record provider availability separately.
Only treat runtime/resource as a core metric when the selected source paper's
own task metric includes local runtime/resource; in that case rerun locally and
report comparable time/resource ratios.

Regenerate per-task specs from the master spec:

```powershell
python scripts\build_real_reuse_task_specs.py
```

Regenerate fixture requirement manifests from the task specs:

```powershell
python scripts\build_real_reuse_fixture_manifests.py
```

Regenerate candidate fixture-asset manifests from the task and fixture specs:

```powershell
python scripts\build_real_reuse_fixture_candidates.py
```

Regenerate preparation-time asset locks from the candidate manifests:

```powershell
python scripts\build_real_reuse_asset_locks.py
```

Regenerate the paper-facing main real-reuse table scaffold. When using the
default raw rows path, the table builder should use
`results/real_reuse/main_run_selection.json` to keep follow-up rows from
silently replacing the pre-registered main rows:

```powershell
python scripts\build_real_reuse_paper_tables.py
```

Regenerate the derived real-reuse failure-boundary analysis table. It should
use the same main-row selection policy as the main table:

```powershell
python scripts\build_real_reuse_failure_analysis.py
```

Regenerate the auxiliary Full Excerpt sanity check. The current pre-registered
AIDE-T1, SWE-T1, and SNAP-T1 subset has matched `full_excerpt` raw rows, so the
table fills Summary, PaperToSkill, Full Excerpt, and local context-token proxy
columns:

```powershell
python scripts\build_real_reuse_full_excerpt_sanity.py
```

Regenerate the SWE-agent skill/readiness gate from extracted paper text:

```powershell
python scripts\papertoskill_note_from_text.py --source papers\extracted\swe_agent.txt --output papers\auto_notes\swe_agent_auto_note.md --paper-id swe_agent --title "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" --profile swe_agent --report results\evaluations\swe_agent_auto_note_scaffold_v0.json
python scripts\papertoskill_extract.py --source papers\auto_notes\swe_agent_auto_note.md --output generated_skills\real_reuse\swe_agent --name swe-agent-paper-skill --title "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"
python scripts\evaluate_skill.py --skill generated_skills\real_reuse\swe_agent\SKILL.md --rubric benchmarks\rubric_swe_agent_v0.json --output results\evaluations\swe_agent_rubric_v0.json
python scripts\validate_source_spans.py --task benchmarks\tasks\swe_agent_auto_source_span_validation.json --output results\evaluations\swe_agent_auto_source_span_validation_v0.json
```

This gate checks the SWE-agent skill artifact only. It does not prepare
SWE-bench assets, run SWE-T1/T2, or produce downstream task-success evidence.

Prepare the two lightweight Reflexion fixture assets and condition contexts:

```powershell
python scripts\prepare_real_reuse_reflexion_fixture.py --task REF-T1 --dataset hotpotqa --config distractor --output-dir benchmarks\real_reuse\assets\REF-T1
python scripts\prepare_real_reuse_reflexion_fixture.py --task REF-T2 --dataset humaneval --output-dir benchmarks\real_reuse\assets\REF-T2
```

Prepare AIDE fixture assets after the human-provided Kaggle `train.csv` is
available. The target source file is intentionally outside the repo so no
Kaggle credentials or raw downloads are committed:

```powershell
python scripts\prepare_real_reuse_aide_fixture.py --task AIDE-T1 --train-csv C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\train.csv --output-dir benchmarks\real_reuse\assets\AIDE-T1
python scripts\prepare_real_reuse_aide_fixture.py --task AIDE-T2 --train-csv C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\train.csv --output-dir benchmarks\real_reuse\assets\AIDE-T2
```

The preparer writes model-visible `train.csv`, `validation_features.csv`,
baseline files, task prompts, and Summary contexts; it keeps
`validation_labels.csv` scorer-only. The current AIDE-T1/T2 fixtures were
materialized from the official local `train.csv` and used for the Phase 98
GPT-family single-run pass; synthetic data is not paper evidence.

Score a dry REF-T1 prediction or REF-T2 candidate without treating failure as a
script crash:

```powershell
python scripts\score_real_reuse_reflexion.py --task REF-T1 --prediction path\to\prediction.json --answer-key benchmarks\real_reuse\assets\REF-T1\answer_key.json
python scripts\score_real_reuse_reflexion.py --task REF-T2 --candidate path\to\candidate.py --tests benchmarks\real_reuse\assets\REF-T2\tests.json
```

Score an AIDE candidate or submission locally against hidden validation labels:

```powershell
python scripts\score_real_reuse_aide.py --task AIDE-T1 --candidate-script path\to\candidate_solution.py --workspace benchmarks\real_reuse\assets\AIDE-T1\starter_workspace --labels benchmarks\real_reuse\assets\AIDE-T1\validation_labels.csv --output-json path\to\metric.json
python scripts\score_real_reuse_aide.py --task AIDE-T2 --candidate-script path\to\candidate_solution.py --workspace benchmarks\real_reuse\assets\AIDE-T2\starter_workspace --labels benchmarks\real_reuse\assets\AIDE-T2\validation_labels.csv --output-json path\to\metric.json
```

Prepare SWE fixture assets from a local repository snapshot after a concrete
SWE-style repo/issue/test instance is available. The preparer can copy a local
snapshot or point to an external workspace, writes model-visible issue/test
context and task prompts, and keeps any gold/test patches scorer-only. For
SWE-bench parquet-backed rows, extract the locked problem statement and hidden
patches directly from the local parquet:

```powershell
python scripts\prepare_real_reuse_swe_fixture.py --task SWE-T1 --workspace-mode external --repo-source 'D:\a_work\gitee\sqlfluff__sqlfluff' --swe-bench-parquet 'D:\a_work\gitee\SWE-bench_Lite\data\dev-00000-of-00001.parquet' --test-command 'D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe -m pytest test/cli/commands_test.py::test__cli__command_directed -q' --output-dir benchmarks\real_reuse\assets\SWE-T1
python scripts\prepare_real_reuse_swe_fixture.py --task SWE-T2 --repo-source path\to\local_repo_snapshot --issue-file path\to\failing_test.md --test-command "python -m pytest path\to\tests" --output-dir benchmarks\real_reuse\assets\SWE-T2
```

Current SWE-T1 follow-up boundary: the first-pass SWE-T1 row remains the
paper-facing main row and is scored as 0.000/0.000 because both generated
patches failed to apply. The shared-source-context follow-up has already run as
`phase107_gpt_swe_t1_source_context_followup`: both Summary and PaperToSkill
still scored 0.000, but both patches applied and then failed the hidden target
test. Treat phase107 as diagnostic follow-up evidence about
task-contract/hidden-objective mismatch, not as a main-table replacement. The
issue-aligned revised scorer/test contract is now pre-registered and validated;
phase110 then ran a paired issue-aligned follow-up and scored Summary 1.000 and
PaperToSkill 1.000. Treat phase110 as diagnostic issue-aligned contract
closure for both conditions, not as PaperToSkill advantage and not as a
main-row replacement unless explicitly promoted later.

To reproduce or refresh the SWE-T1 source-context fixture, expose the same
locked SQLFluff source slice to both conditions:

```powershell
python scripts\prepare_real_reuse_swe_fixture.py --task SWE-T1 --workspace-mode external --repo-source 'D:\a_work\gitee\sqlfluff__sqlfluff' --swe-bench-parquet 'D:\a_work\gitee\SWE-bench_Lite\data\dev-00000-of-00001.parquet' --test-command 'D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe -m pytest test/cli/commands_test.py::test__cli__command_directed -q' --source-context-file 'D:\a_work\gitee\sqlfluff__sqlfluff\src\sqlfluff\rules\L031.py' --source-context-label 'src/sqlfluff/rules/L031.py @ 14e1a23a3166b9a645a16de96f694c77a5d4abb7' --output-dir benchmarks\real_reuse\assets\SWE-T1
```

Score a SWE patch locally by applying the candidate unified diff in an isolated
temporary copy of the prepared workspace and running the locked test command:

```powershell
python scripts\score_real_reuse_swe.py --task SWE-T1 --patch path\to\candidate.patch --workspace 'D:\a_work\gitee\sqlfluff__sqlfluff' --test-command-file benchmarks\real_reuse\assets\SWE-T1\target_test_command.txt --test-patch benchmarks\real_reuse\assets\SWE-T1\scorer_only\test.patch --output-json path\to\metric.json
python scripts\score_real_reuse_swe.py --task SWE-T2 --patch path\to\candidate.patch --workspace 'D:\a_work\gitee\astropy__astropy' --test-command-file benchmarks\real_reuse\assets\SWE-T2\target_test_command.txt --test-patch benchmarks\real_reuse\assets\SWE-T2\scorer_only\test.patch --output-json path\to\metric.json
```

To rerun SWE rows after a pre-registered scorer, prompt-contract,
source-context, budget, or patch-contract fix, run Summary and PaperToSkill
conditions with the same no-mid-run-human rule. The phase107 source-context
follow-up used a longer provider timeout/retry budget and a longer local
scorer timeout:

```powershell
$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
python scripts\run_real_reuse_swe.py --task SWE-T1 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --score-timeout-seconds 120 --run-id phaseXX_gpt_swe_source_context_followup
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_API_KEY -ErrorAction SilentlyContinue
```

To reproduce the phase110 SWE-T1 issue-aligned diagnostic follow-up, use the
pre-registered issue-aligned scorer directly as the test command and disable
the old hidden test patch:

```powershell
$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
python scripts\run_real_reuse_swe.py --task SWE-T1 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --score-timeout-seconds 120 --test-command-override "D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe D:\a_work\gitee\PaperToSkill\benchmarks\real_reuse\assets\SWE-T1\scorer_only\issue_aligned_check.py" --disable-test-patch --run-id phase110_gpt_swe_t1_issue_aligned_followup
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_API_KEY -ErrorAction SilentlyContinue
```

Then rebuild the dedicated diagnostic table and paper-table consistency report:

```powershell
python scripts\build_real_reuse_swe_t1_issue_aligned_followup.py
python scripts\check_paper_tables.py --strict
```

Do not treat missing credentials, provider errors, or missing SWE fixture assets
as model-quality failures. SWE-T1 and SWE-T2 each have one scored GPT-family
main run; SWE-T1 also has the phase107 shared-source-context follow-up and the
phase110 issue-aligned diagnostic follow-up. Do not turn any single task into
an aggregate SWE-agent or eight-task claim. All eight real-reuse rows have a
first-pass score, but the evidence is mixed and should be stabilized before
stronger claims.

Run the locked Reflexion Summary-vs-PaperToSkill rows with the GPT-family
Responses profile. Set the API key only in the shell, never in tracked files:

```powershell
$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
python scripts\run_real_reuse_reflexion.py --task REF-T1 --task REF-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --run-id phaseXX_gpt_reflexion_real_reuse
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_API_KEY -ErrorAction SilentlyContinue
```

The runner writes prompts, raw responses, metric JSON, and raw rows under
`results/real_reuse/`. It records provider/model errors as availability
evidence, not model-quality failures.

To rerun the locked AIDE rows, keep the same no-mid-run-human rule. The runner
accepts fixture responses for dry tests or live API credentials for real model
rows:

```powershell
$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
python scripts\run_real_reuse_aide.py --task AIDE-T1 --task AIDE-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --score-timeout-seconds 300 --run-id phaseXX_gpt_aide_real_reuse
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_API_KEY -ErrorAction SilentlyContinue
```

Do not treat missing credentials, provider errors, or missing Kaggle data as
model-quality failures. Current AIDE rows are scored from the official
Kaggle-derived local fixture: AIDE-T1 is solved by both Summary and
PaperToSkill under the extended 300-second local scorer, while AIDE-T2 is a
PaperToSkill-only success with the Summary candidate still timing out.

To rerun the locked SnapATAC2 rows after a pre-registered artifact, budget, or
task-contract follow-up, keep Summary and PaperToSkill paired under the same
locked fixture and no-mid-run-human rule:

```powershell
$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
python scripts\run_real_reuse_snapatac2.py --task SNAP-T1 --task SNAP-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --run-id phaseXX_gpt_snapatac2_real_reuse
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_API_KEY -ErrorAction SilentlyContinue
```

Current SNAP rows are scored over official miniature fixture assets, but both
tasks remain below the pre-registered success threshold. Treat them as
artifact-completion and resource-budget boundary evidence unless a
pre-registered rerun changes the raw rows.

Build the SNAP artifact-execution follow-up diagnosis before changing the SNAP
runner/scorer contract:

```powershell
python scripts\build_real_reuse_snapatac2_artifact_followup.py
```

Current diagnosis:
`results/real_reuse/snapatac2_artifact_followup.md` reports
`pre_registered_followup_needed`. The selected SNAP main rows are plan/JSON
outputs without executed artifacts and runtime/memory records; the miniature
fixtures are readable; `snapatac2` is not importable in the current Python
environment.

Run the paired executable-artifact follow-up without replacing the main rows:

```powershell
python scripts\run_real_reuse_snapatac2_executable_followup.py --run-id phase108_snapatac2_executable_artifact_followup
```

Current phase108 result:
`results/real_reuse/snapatac2_executable_artifact_followup.md` reports
`overall_status=complete`; all four SNAP-T1/T2 Summary/PaperToSkill rows score
1.000 under the existing SNAP scorer. The runner executes a pre-registered
controlled scaffold over the same miniature fixtures, records concrete
artifacts plus runtime/memory, and does not append to `raw_rows.jsonl`. Treat
this as diagnostic evidence that the artifact/runtime/memory contract can
close, not as a main-row replacement or PaperToSkill advantage.

Run executable SNAP candidate scripts under the pre-registered contract without
replacing the main rows:

```powershell
python scripts\build_real_reuse_snapatac2_executable_candidate_prompts.py
```

The prompt-packet builder writes
`results/real_reuse/snapatac2_executable_candidate_prompt_plan.{md,json}` and
four task/condition prompt packets under
`results/real_reuse/snapatac2_executable_candidate_prompts/`. These packets are
for future model calls that should return Python candidate scripts; the builder
does not call a model, score outputs, append raw rows, or replace main rows.
After phase113/115/116 SNAP-T2 Summary requests returned provider HTTP 524,
prefer the compact prompt contract before any future SNAP-T2 retry:

```powershell
python scripts\build_real_reuse_snapatac2_executable_candidate_prompts.py --compact
```

The compact builder writes
`results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.{md,json}`
and four shorter task/condition packets under
`results/real_reuse/snapatac2_executable_candidate_compact_prompts/`. Compact
packets keep the same runner interface, required artifacts, no-network rule,
scorer-only boundary, and main-row non-replacement policy, while using
deterministic summaries plus local paths and hashes instead of inlining every
visible asset.

To ask the default GPT-family model to generate paired candidate scripts from
the prompt packets, use a generous timeout/retry budget:

```powershell
$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
python scripts\run_real_reuse_snapatac2_executable_candidate_prompts.py --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --run-id phaseXX_snapatac2_executable_candidate_scripts
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\PAPERTOSKILL_GPT_OPENAI_API_KEY -ErrorAction SilentlyContinue
```

This script generates candidate `.py` files and a provider-availability report.
It still does not execute candidates, score outputs, append raw rows, or replace
main rows. The script now rewrites the report after each prompt packet so a
provider stall or interrupted long call preserves completed rows as a partial
generation record.

Current checkpoint:

- `phase111_gpt_snapatac2_executable_candidate_scripts` generated paired
  SNAP-T1 Summary/PaperToSkill scripts, but both scripts imported the
  POSIX-only `resource` module and failed on the Windows runner. The paired
  executable-candidate diagnostic run
  `phase111_gpt_snapatac2_executable_candidate_t1` scored both rows 0.500 with
  `missing_required_artifacts_or_metrics` because no artifacts were produced.
  This is diagnostic evidence only and does not replace the main SNAP rows.
- The prompt packets were tightened to require cross-platform Python and to
  avoid `resource`, network access, package installation, and writes outside
  `--artifact-dir` / `--result-json`.
- `phase112_gpt_snapatac2_executable_candidate_scripts_v2` now has paired
  revised `SNAP-T1_summary.py` and `SNAP-T1_papertoskill.py` scripts. The
  first long prompt-runner request hung and a direct curl request with a larger
  output budget returned repeated provider HTTP 524, both treated as
  availability metadata. A no-BOM direct Responses request with a shorter
  output budget produced the PaperToSkill script, after which the
  prompt-runner report was rebuilt with both scripts cached.
- The paired phase112 executable-candidate diagnostic run
  `phase112_gpt_snapatac2_executable_candidate_t1` scored both Summary and
  PaperToSkill 1.000 under the existing SNAP-T1 scorer. This is diagnostic
  contract-closure evidence for both conditions, not a main-row replacement or
  PaperToSkill advantage.

After paired Summary/PaperToSkill candidate scripts exist, run:

```powershell
python scripts\run_real_reuse_snapatac2_executable_candidate.py --candidate-dir path\to\candidate_scripts --task SNAP-T1 --task SNAP-T2 --condition summary --condition papertoskill --timeout-seconds 300 --run-id phaseXX_snapatac2_executable_candidate
```

Candidate scripts should accept `--task-id`, `--condition`, `--fragment`,
`--artifact-dir`, and `--result-json`. The runner writes runner-owned
`candidate_output.json`, `artifact_manifest.json`, `resource_record.json`, and
metric files before calling `scripts/score_real_reuse_snapatac2.py`. It does
not append to `results/real_reuse/raw_rows.jsonl` and does not replace
paper-facing main rows unless a later explicit promotion updates
`results/real_reuse/main_run_selection.json`.

Validate the real-reuse benchmark after task/spec/scorer edits or before
editing paper claims:

```powershell
python scripts\check_real_reuse_benchmark.py --strict
```

The preflight writes:

```text
results/real_reuse/spec_preflight.json
results/real_reuse/spec_preflight.md
results/real_reuse/main_results_plan.csv
results/real_reuse/main_results_plan.md
```

The expected status is `ready_to_implement` for the benchmark contract. That
means the benchmark spec, per-task specs, fixture requirement manifests,
candidate asset manifests, asset locks, prepared assets, skill gates, and
execution-layer script contracts are machine-checkable; it is not downstream
task-success evidence by itself.

Planned main task grid:

| Task ID | Source Paper | Domain | Main Metric Family |
| --- | --- | --- | --- |
| AIDE-T1 | AIDE | ML engineering | Validation score / Kaggle-style metric |
| AIDE-T2 | AIDE | ML engineering | Validation score / best-node score |
| SWE-T1 | SWE-agent | Software engineering | Tests passed / resolved |
| SWE-T2 | SWE-agent | Software engineering | Tests passed / resolved |
| REF-T1 | Reflexion | Reasoning / QA | Exact match / F1 / success |
| REF-T2 | Reflexion | Decision / programming | Success / pass rate |
| SNAP-T1 | SnapATAC2 | Single-cell omics | Runtime, memory, clustering/embedding metric |
| SNAP-T2 | SnapATAC2 | Single-cell omics | ARI/NMI/runtime/memory |

Current execution order:

1. Treat paper-facing main-row selection and dedicated SWE-T1 follow-ups as
   separate from the main table. `results/real_reuse/main_run_selection.json`
   keeps phase107 and phase110 from overwriting the first-pass SWE-T1
   main-table cells. `results/real_reuse/swe_t1_source_context_followup.{csv,md,json}`
   reports phase107; `results/real_reuse/swe_t1_issue_aligned_followup.{csv,md,json}`
   is the dedicated phase110 diagnostic table, backed by
   `results/real_reuse/swe_t1_issue_aligned_run_report.{md,json}`.
2. Continue stabilizing failure-heavy core real-reuse rows and paper-facing
   diagnostic summaries. SNAP artifact-completion / budget boundaries and the
   phase110 SWE-T1 issue-aligned follow-up should remain diagnostic unless
   explicitly promoted.
3. Pre-register any scorer, prompt-contract, source-context, budget, or
   artifact-contract change before rerunning a row.
4. Rerun affected Summary and PaperToSkill conditions under the same locked
   task, input/output, scorer, local setting, and no-mid-run-human rule.
5. Collect auxiliary data opportunistically during core reruns, including
   provider availability, failure reasons, context/token proxies, and raw rows
   needed for real-reuse LLM ablation.
6. Regenerate `results/real_reuse/main_results_plan.*`,
   `results/real_reuse/failure_analysis.*`, any affected paper tables, and
   readiness reports.
7. Aggregate LLM ablation, quality/grounding evidence, and optional appendix
   analyses only after the core rows are stable.
8. Keep user study last and optional, only for user-efficiency or usability
   claims.

Required boundaries:

- `Summary` is the main baseline.
- `Abstract` is not part of the main comparison.
- `Full Excerpt` is a small sanity check only.
- Original paper scores are `reported references` unless the same environment,
  data, input/output, metric, model/tool budget, and runtime setting are
  reproduced.
- The older saved-response model ablation is not a real-reuse result. LLM
  ablation must run on the real `paper-task` rows.

Build the pre-registered real-reuse LLM ablation command plan:

```powershell
python scripts\build_real_reuse_llm_ablation_plan.py
```

Current plan:
`results/real_reuse/llm_ablation_plan.md` selects AIDE-T2 and SWE-T2 as
positive PaperToSkill-only slices plus REF-T2 as a ceiling/control slice. It
uses GPT-family `gpt-5.5`, Claude-family `claude-opus-4-8`, and
DeepSeek-family `deepseek-v4-flash`, with 300-second provider timeouts, five
attempts, and five-second retry delays. Set provider environment variables
locally before executing any listed command, and never commit raw keys.

Aggregate collected real-reuse LLM ablation rows against the pre-registered
run IDs:

```powershell
python scripts\build_real_reuse_llm_ablation_results.py
```

Current aggregate:
`results/real_reuse/llm_ablation_summary.md` reports 12 collected scored rows
and 6 pending rows out of 18 expected rows. GPT-family rows are complete:
REF-T2 1.000/1.000, AIDE-T2 0.814/0.000 because the PaperToSkill candidate
timed out under the 300-second local scorer, and SWE-T2 0.000/0.000 because
both candidate patches fail to apply. DeepSeek-family rows are complete:
REF-T2 1.000/1.000, AIDE-T2 0.500/0.500 below the success threshold, and
SWE-T2 0.000/0.000 because both candidate patches fail to apply. Claude-family
REF-T2, AIDE-T2, and SWE-T2 were all attempted for both Summary and
PaperToSkill, but every Claude-family condition was blocked by provider HTTP
502 after five attempts and remains pending as a scored row. These are
auxiliary model/repetition rows, not main-row replacements and not aggregate
PaperToSkill advantage.

## AI-Scientist-v2 Environment

Recommended for stable runs:

```powershell
conda create -n papertoskill-ai-scientist python=3.11
conda activate papertoskill-ai-scientist
python -m pip install -r D:\a_work\gitee\ai-scientist-v2\requirements.txt
```

The current active Anaconda Python has been used for smoke work, but
`pip install -r requirements.txt` produced dependency conflicts. Use an isolated
environment before long experiments.

## LLM Endpoint

Use environment variables rather than tracked config files. Current
`coderxiaoc.com` routing is protocol-specific:

- Claude-family direct probes use Anthropic Messages at
  `https://coderxiaoc.com/v1/messages`.
- GPT-family direct probes use OpenAI Responses at
  `https://coderxiaoc.com/v1/responses`.
- The legacy AI-Scientist-v2 wrapper smoke still exercises the local
  `ai_scientist.llm` OpenAI-compatible client path, so keep its status separate
  from the protocol-specific direct probes.

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set Claude-family token locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
```

Current Claude Messages aliases:

```text
claude-opus-4-8
claude-opus-4-7
claude-opus-4-6
```

The dotted `claude-opus-4.8` spelling appeared in older attempts, but the
current direct-provider and handoff commands use the hyphenated model names
above. The GPT-family profile should be checked with the separate
`PAPERTOSKILL_GPT_*` environment variables and is expected by the user to use
aliases such as `gpt-5.5` and `gpt-5.4`.

## Connectivity Smoke Test

Claude Messages test:

```powershell
$headers = @{ Authorization = "Bearer $env:AI_SCIENTIST_OPENAI_API_KEY" }
$headers["anthropic-version"] = "2023-06-01"
$body = @{
  model = "claude-opus-4-8"
  messages = @(@{ role = "user"; content = "Reply exactly: PaperToSkill API OK" })
  max_tokens = 32
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Uri "$env:AI_SCIENTIST_OPENAI_BASE_URL/v1/messages" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

GPT Responses test:

```powershell
$headers = @{ Authorization = "Bearer $env:PAPERTOSKILL_GPT_OPENAI_API_KEY" }
$body = @{
  model = "gpt-5.5"
  input = "Reply exactly: PaperToSkill API OK"
  max_output_tokens = 32
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Uri "$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL/responses" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Earlier OpenAI-compatible chat-completion checks reached the server but failed
due to exhausted or unavailable provider accounts. Recheck with the current
protocol-specific env profile before making any availability claim.

## AI-Scientist-v2 LLM-Client Smoke

From `D:\a_work\gitee\PaperToSkill`, run a bounded one-call smoke through the
local AI-Scientist-v2 LLM client:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

python scripts\run_ai_scientist_v2_smoke.py --strict
```

The command prints the generated report paths plus an `overall_status`
summary. Use `--require-complete` when a CI or handoff step should exit
non-zero unless the provider returns a response satisfying the smoke contract:

```powershell
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete
```

To try the known Claude alias variants in one bounded tiny-marker run:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set Claude-family OpenAI-compatible key locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 30 --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

To try the GPT-family credential profile through the same AI-Scientist-v2
OpenAI-compatible client path, map the GPT key into
`AI_SCIENTIST_OPENAI_API_KEY` locally for this smoke only:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set GPT-family key locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 60 --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4
```

Current AI-Scientist-v2 smoke status:
`results/ai_scientist_v2_smoke/run_report.md` reports `complete`, 6 ready
checks, 0 pending checks, and 0 failed checks. The saved marker response uses
`claude-opus-4-8` and satisfies the tiny PaperToSkill smoke contract. This is
bounded client-integration evidence only; it is not a BFTS run, human semantic
validation, real-data validation, or broad live research-task success.

## Protocol-Specific Direct Provider Probe

Use the direct endpoint probe when provider availability needs diagnosis
separate from the local `ai_scientist.llm` wrapper:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set Claude-family token locally>"
python scripts\run_openai_compatible_direct_probe.py --wire-api anthropic_messages --strict --require-complete --timeout-seconds 30 --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6 `
  --output-json results\openai_compatible_direct_probe\claude_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\claude_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\claude_family\response.md
```

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set GPT-family key locally>"
python scripts\run_openai_compatible_direct_probe.py --wire-api openai_responses --strict --require-complete --timeout-seconds 60 --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4 `
  --output-json results\openai_compatible_direct_probe\gpt_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\gpt_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\gpt_family\response.md
```

Historical direct-probe diagnostic:
`results/openai_compatible_direct_probe/claude_family/run_report.md` reports
`wire_api=anthropic_messages`, attempted `claude-opus-4-8`,
`claude-opus-4-7`, and `claude-opus-4-6`, and is still blocked by HTTP 502
`Upstream service temporarily unavailable`. The GPT-family report uses
`wire_api=openai_responses`, attempted `gpt-5.5` and `gpt-5.4`, and is still
blocked by HTTP 502 `Upstream access forbidden`. This diagnostic bypasses
`ai_scientist.llm`. Keep this as historical provider diagnostics, not a current
blocker. Before making any new availability claim, rerun the relevant
protocol-specific probe or use the task runner's recorded call status. Model
calls should receive generous timeout and retry budget because the third-party
service is unstable.

## Model-Ablation Prompt Packets

From `D:\a_work\gitee\PaperToSkill`:

```powershell
python scripts\build_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --output-dir results\model_ablation_prompts\v0
```

The current prompt grid includes:

- `claude_opus_4_8`, trying candidate aliases `claude-opus-4-8`,
  `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6`;
- `gpt_5_5_or_gpt_family`, using the separate GPT credential profile and
  preferring `gpt-5.5` then `gpt-5.4` when listed;
- `deepseek_followup_slot`, currently configured in the older two-case
  saved-response protocol with `deepseek-v4-flash`.

Save live responses only under the `expected_response_path` fields in
`results/model_ablation_prompts/v0/index.json`. Do not commit raw API keys.

Run Claude/GPT-family availability and response collection:

```powershell
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\run_report.json `
  --output-md results\model_ablation_prompts\v0\run_report.md `
  --model-id claude_opus_4_8 `
  --model-id gpt_5_5_or_gpt_family
```

Score any saved responses:

```powershell
python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md
```

Estimate local output-token proxies for saved model responses:

```powershell
python scripts\evaluate_model_response_costs.py
```

Current status: the current two-case model-ablation protocol has 6/6 saved and
scored rows. GPT-family was refreshed through OpenAI Responses and completed
both rows with `gpt-5.5`; DeepSeek was run through Chat Completions and
completed both rows with `deepseek-v4-flash`. The latest Claude protocol
refresh used Anthropic Messages but was blocked by provider HTTP 502, so the
scored Claude rows come from previously saved response files. Local output-token
proxy accounting over all six saved responses reports 9,594 `o200k_base`
output tokens. This report is not provider billing, live downstream task
success, broad model-quality evidence, or success-per-dollar evidence.

Current Paper2Agent comparison status:
`results/tables/paper2agent_artifact_comparison.md` reports 7/7 ready criteria
and 0 failed criteria for a bounded source-backed artifact/workflow comparison.
It compares Paper2Agent's reported MCP workflow with current PaperToSkill
artifacts. It does not run Paper2Agent, deploy an MCP server, or claim
end-to-end baseline performance.

## Deferred Provider Billing Evidence Handoff

Provider billing and success-per-dollar are outside the current claim set.
Prefer local token/context proxies for the current paper scope. Only refresh
the blank provider-billing template if the research policy explicitly reopens
real provider-billing evidence:

```powershell
python scripts\summarize_provider_billing_evidence.py --init-template --strict
```

When real provider usage exports or invoices are available, fill
`results/provider_billing_evidence/billing_template.csv` and rerun:

```powershell
python scripts\summarize_provider_billing_evidence.py --strict
```

Current status:
`results/provider_billing_evidence/billing_summary.md` reports
`billing_status=pending`, 6 total rows, 0 measured rows, 6 pending rows, 0
errors, total billed USD 0, and success per dollar `n/a`. This is an auditable
handoff for future real billing rows, not provider billing evidence.

If the old saved-response DeepSeek slot must be changed, configure
`deepseek_followup_slot` with the helper script so only non-secret metadata is
written to `benchmarks/model_ablation_v0.json`:

```powershell
python scripts\configure_deepseek_followup.py `
  --model-alias <deepseek-model-alias> `
  --auth-env DEEPSEEK_API_KEY `
  --base-url-env DEEPSEEK_BASE_URL
```

Then rebuild the prompt packets, set those environment variables locally, and
run the same runner with `--model-id deepseek_followup_slot`. The runner skips
DeepSeek only while the placeholder alias remains unchanged.

Before and after editing the DeepSeek slot, generate the local handoff/preflight
report:

```powershell
python scripts\check_deepseek_followup.py --strict
```

Current status:
`results/deepseek_followup_handoff/handoff.md` reports `responses_present`, 7
ready checks, 0 pending checks, and 0 failed checks. The checked-in DeepSeek
slot uses `deepseek-v4-flash`, both expected response files exist, and the
saved-response evaluator scores both rows 6/6. Keep this separate from
provider billing and live downstream task success.

## Live-Transfer Response Collection

Existing live-transfer prompt packets live under
`results/live_transfer_prompts/*_v0/index.json`. Save responses only under each
row's `expected_response_path`. Do not commit raw API keys.

Run one live-transfer packet with the Claude-family profile:

```powershell
python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\toolformer_v0\index.json `
  --output-json results\live_transfer_prompts\toolformer_v0\run_report.json `
  --output-md results\live_transfer_prompts\toolformer_v0\run_report.md `
  --max-tokens 900
```

Repeat the same command for the other paper packet indexes and output paths:

```powershell
python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\ai_scientist_v2_v0\index.json `
  --output-json results\live_transfer_prompts\ai_scientist_v2_v0\run_report.json `
  --output-md results\live_transfer_prompts\ai_scientist_v2_v0\run_report.md `
  --max-tokens 900

python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\reflexion_v0\index.json `
  --output-json results\live_transfer_prompts\reflexion_v0\run_report.json `
  --output-md results\live_transfer_prompts\reflexion_v0\run_report.md `
  --max-tokens 900

python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\aide_v0\index.json `
  --output-json results\live_transfer_prompts\aide_v0\run_report.json `
  --output-md results\live_transfer_prompts\aide_v0\run_report.md `
  --max-tokens 900
```

Score saved live-transfer responses across all four paper packets:

```powershell
python scripts\evaluate_live_transfer_responses.py `
  --index results\live_transfer_prompts\ai_scientist_v2_v0\index.json `
  --index results\live_transfer_prompts\reflexion_v0\index.json `
  --index results\live_transfer_prompts\aide_v0\index.json `
  --index results\live_transfer_prompts\toolformer_v0\index.json `
  --output-json results\live_transfer_prompts\evaluation.json `
  --output-md results\live_transfer_prompts\evaluation.md
```

Current live-transfer status: all four live-transfer response sets have saved
responses across both harness prompt styles and all three context variants.
`results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24 scored
rows, 0 pending rows, and average normalized score 1.0 under deterministic
output-contract scoring. AI Scientist-v2, Reflexion, and AIDE rows score 11/11;
Toolformer rows score 9/9. AIDE has one provider fallback row:
`claude-opus-4-8` closed the connection, then `claude-opus-4-7` succeeded. This
is saved-response evidence, not human semantic fidelity, real live task success,
provider billing, or DeepSeek completion.

## Usage Example Gate

Verify that paper-facing usage examples are locally executable where they do
not require additional live model calls:

```powershell
python scripts\check_usage_examples.py `
  --output-json results\reproducibility\usage_example_report.json `
  --output-md results\reproducibility\usage_example_report.md `
  --strict
```

This checker validates the Codex-style skill usage files, the scored Toolformer
Codex-style response slot, the full live-transfer response evaluation, the
model-ablation prompt grid and response slots, an offline AIDE
extracted-text-to-note-to-skill chain, and a PDF-input pipeline
smoke run in a temporary directory. It does not execute additional
Claude/GPT/DeepSeek calls.

## Human-Fidelity Annotation Handoff

Regenerate the independent-review packets, annotation guide, blank annotation
template, checksum manifest, and reviewer zip bundle:

```powershell
python scripts\build_human_fidelity_packets.py
```

The reviewer-facing bundle is:

```text
results\human_fidelity_packets\human_fidelity_reviewer_bundle.zip
```

It contains `annotation_guide.md`, `annotation_template.csv`, the four
`*_human_fidelity_packet.md` files, a quick reviewer README, and
`reviewer_bundle_manifest.json` with SHA256 checksums. This bundle is a
handoff artifact only; it does not complete human validation.

Before using reviewer-filled annotations in a claim, summarize them with strict
validation:

```powershell
python scripts\summarize_human_fidelity_annotations.py --strict
```

Current status:
`results/human_fidelity_packets/annotation_guide.md` provides the reviewer
handoff, `annotation_template.csv` has 24 blank paper-by-criterion rows, and
`annotation_summary.md` reports `annotation_status=pending`, 0 scored rows, 24
pending paper-by-criterion cells, average confidence `n/a`, and 0 validation
errors. Multiple reviewers may append rows for the same paper-by-criterion cell
when `reviewer_id` values are distinct. The package
gate marks `human_fidelity_annotation_handoff_ready` and
`human_fidelity_reviewer_bundle_ready` ready, while completed human-fidelity
annotation remains pending.

## AAAI Paper Package

The official AAAI-27 author kit is stored under `paper/aaai/`.

Main draft:

```powershell
cd D:\a_work\gitee\PaperToSkill\paper\aaai
pdflatex papertoskill_aaai2027.tex
bibtex papertoskill_aaai2027
pdflatex papertoskill_aaai2027.tex
pdflatex papertoskill_aaai2027.tex
```

If `pdflatex` is unavailable in the local environment, treat the `.tex` package
as prepared but not rendered.

Verify the local AAAI package and generated PDF artifacts:

```powershell
python scripts\check_aaai_package.py `
  --output-json results\reproducibility\aaai_package_report.json `
  --output-md results\reproducibility\aaai_package_report.md `
  --strict
```

This checker verifies the author-kit SHA256, required package files, the
`aaai2027` style declaration/load marker, fresh PDF/log/bibliography artifacts,
and unresolved citation/reference/build-warning markers. Passing it does not
mean the paper is submission-final.

Verify that the AAAI result tables still match generated CSV result tables:

```powershell
python scripts\check_paper_tables.py `
  --output-json results\reproducibility\paper_table_report.json `
  --output-md results\reproducibility\paper_table_report.md `
  --strict
```

This checker compares `paper/aaai/papertoskill_tables.tex` against the
real-reuse main, failure-boundary, SWE-T1 source-context follow-up, SWE-T1
issue-aligned follow-up, SNAP executable-artifact follow-up, and Full Excerpt
sanity CSVs as well as `results/tables/main_results.csv`,
`transfer_ablation.csv`, `context_cost_proxy_tokenizer.csv`, and
`auto_note_comparison.csv`. Passing it prevents manuscript-table drift, but
does not add new empirical evidence.

Verify that paper-facing text avoids unsupported overclaims and includes the
required evidence-boundary statements:

```powershell
python scripts\check_paper_claims.py `
  --output-json results\reproducibility\paper_claim_report.json `
  --output-md results\reproducibility\paper_claim_report.md `
  --strict
```

This checker scans the AAAI manuscript and Markdown draft, but not
`paper/claim_checklist.md` because that file intentionally stores unsupported
phrases as negative examples.

## Submission-Review Handoff Gate

Verify that internal review, rebuttal, and submission checklist handoff files
match current evidence rather than stale earlier-phase status:

```powershell
python scripts\check_submission_review.py `
  --output-json results\reproducibility\submission_review_report.json `
  --output-md results\reproducibility\submission_review_report.md `
  --strict
```

Current status:
`results/reproducibility/submission_review_report.md` reports ready, 19 ready
checks, and 0 failed checks. It verifies that review handoff files describe the
24 scored saved live-transfer response rows, 6 scored and 0 pending
model-ablation rows, 0 scored and 24 pending human-fidelity cells, local token
accounting, the bounded AI-Scientist-v2 smoke/full live-run completion, and the
mixed eight-row real-reuse first pass. It also verifies that the auxiliary
real-reuse LLM ablation is described as 12/18 scored rows with Claude-family
provider-pending HTTP 502 rows, not as saved-response evidence or a main-row
replacement. It also verifies that the external-evidence closure queue and
execution packets are described as local handoff/checking artifacts while two
external-evidence items remain pending under `pending_external_evidence`:
human-fidelity annotation and the AAAI final decision.
Passing this gate does not mean the AAAI paper is submission-final.

## Goal Completion Gate

Verify the active user goal against current local evidence before deciding
whether to close the goal:

```powershell
python scripts\check_goal_completion.py `
  --output-json results\reproducibility\goal_completion_report.json `
  --output-md results\reproducibility\goal_completion_report.md `
  --strict
```

This checker is expected to report
`not_complete_pending_external_evidence` until human-fidelity annotation and
final AAAI submission readiness under the recorded wait policy are complete.
Passing `--strict` only fails on local requirement
failures; pending external evidence remains pending rather than a package
failure.

## External Evidence Closure Queue

Build the local closure queue that maps pending goal requirements to concrete
next actions:

```powershell
python scripts\check_external_evidence_closure.py --strict
```

Current status:
`results/external_evidence_closure/closure.md` reports
`overall_status=pending_external_evidence`, 3 ready checks, 0 pending checks,
and 0 failed checks. The queue covers human-fidelity annotation and the AAAI
submission decision.

This queue is a local planning and checking artifact. It does not complete any
of the external evidence items.

## External Evidence Execution Packets

Build executable handoff packets for each item in the external-evidence closure
queue:

```powershell
python scripts\check_external_evidence_packets.py --strict
```

Current status:
`results/external_evidence_packets/packets.md` reports
`overall_status=ready`, 8 ready checks, 0 pending checks, and 0 failed checks.
The two packets cover human-fidelity annotation and the AAAI submission
decision.
The human-fidelity packet now explicitly records the desktop `toHuman.md` /
`ok.txt` handoff workflow and the agent-side `ok.txt` cleanup command after
completed annotations are processed.

These packets list inputs, setup notes, run commands, validation commands,
completion criteria, escalation rules, and evidence boundaries. They do not
complete any external evidence by themselves.

The AAAI submission-decision packet now routes final-decision recording through
`scripts/generate_aaai_submission_decision.py`. After the human research lead
chooses exactly one option, run only the matching helper command, then rerun
`scripts/check_aaai_submission_decision.py --strict`,
`scripts/check_goal_completion.py --strict`, and
`scripts/check_reproducibility_package.py --strict`.

## AAAI Submission Decision Preflight

Build the local preflight for the final AAAI decision:

```powershell
python scripts\check_aaai_submission_decision.py --strict
```

Current status:
`results/aaai_submission_decision/decision.md` reports
`overall_status=ready`, `decision_status=recorded`,
`selected_option=wait_for_external_evidence`, 27 ready checks, 0 pending
checks, and 0 failed checks. The two available options remain:

- submit now as a deterministic/offline system paper with explicit limitations;
- wait for external evidence before making stronger live, human-fidelity,
  provider-economics, or AI-Scientist-v2 live-run claims.

The current recorded policy is to wait for named external evidence before
stronger final-submission claims. Do not rewrite this decision unless the
research lead explicitly changes the policy.

Prefer the validated helper when the research lead has made the decision:

```powershell
python scripts\generate_aaai_submission_decision.py `
  --selected-option submit_now_deterministic_offline `
  --decision-owner "<name or role>" `
  --decision-date YYYY-MM-DD `
  --claim-boundary "<accepted paper claim scope>" `
  --evidence-policy "<submit now with limitations, or wait for named evidence>"
python scripts\check_aaai_submission_decision.py --strict
```

Use `--selected-option wait_for_external_evidence` instead if the accepted
policy is to wait for the named external evidence rows.

## AI-Scientist-v2 Dry Run

From `D:\a_work\gitee\ai-scientist-v2`:

```powershell
python launch_scientist_bfts.py `
  --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json `
  --idea_idx 0 `
  --dry_run `
  --skip_writeup `
  --skip_review
```

This should create an `experiments/<timestamp>_papertoskill_extractor_attempt_0`
folder and exit before running the expensive agentic search.

## AI-Scientist-v2 Full Live-Run Handoff

Before attempting the full live/BFTS run, generate the local handoff/preflight
report:

```powershell
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
```

Current Phase 76 status:
`results/ai_scientist_v2_live_run_handoff/handoff.md` reports
`complete`, 16 ready checks, 0 pending checks, 0 failed checks, and one
completion directory. It checks the AI-Scientist-v2 root, launcher, dry-run/skip
flags, laptop-profile config, PaperToSkill seed idea, prior dry-run artifacts,
environment variable names, the smoke-completion evidence, completion artifacts,
and non-buggy best-node consistency.

The completed run is bounded integration and synthetic sensitivity evidence. Do
not treat it as human fidelity, real-data validation, or broad live research
task success.
