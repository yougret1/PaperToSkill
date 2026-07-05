# PaperToSkill Paper Outline

Evidence boundary: this outline is grounded in deterministic/offline artifacts,
saved-response output-contract rows, and the current first-pass real-reuse
stress test. The saved live-transfer and saved model-ablation rows have been
collected and scored, but they are not evidence of human semantic fidelity,
provider billing, or live downstream task success. Phases 19-20 additionally
include deterministic extracted-text-to-note scaffolds for Toolformer and AIDE;
these are separate from the curated-note main benchmark. Phase 21 adds an
AAAI-27 LaTeX package and usage examples. Phases 22, 36, 37, and 73 add
model-ablation runner/evaluator evidence: Claude-family, GPT-family, and
DeepSeek rows are saved and scored for the older two-case protocol, while the
current real-reuse LLM ablation remains 12/18 scored with Claude-family rows
provider-pending. A local output-token proxy covers the six saved older
model-ablation responses; it is not provider billing evidence. Phase 40
completes saved and scored live-transfer responses for all four paper packets
under the deterministic output-contract evaluator. Phase 74 adds a bounded
source-backed Paper2Agent artifact/workflow comparison; this is positioning
evidence, not a live MCP baseline. Phase 79 starts the next-stage real-reuse
experiment plan in `research/real_reuse_experiment_plan.md`; Phase 87 partially
executes the Reflexion slice with one GPT-family Summary-vs-PaperToSkill run,
and later phases complete a first GPT-family pass over all eight real-reuse
rows. The first pass is mixed and failure-heavy, so it must not be described as
aggregate downstream effectiveness.

## Working Title

PaperToSkill: Turning Research Papers into Portable Agent Skills

## Abstract Claim

Current evidence-bounded claim:

Research papers often contain reusable agent workflows, but those workflows are
hard for non-expert users to operationalize. PaperToSkill studies whether a
paper can be converted into a compact, human-editable skill that preserves
procedural knowledge, source grounding, validation checks, failure branches, and
transfer notes. On four curated agent-method papers, generated skills pass
deterministic structural rubrics, preserve more task-relevant operational
coverage than summary baselines, remain under a 1200-word compactness budget,
and show stronger offline transfer readiness when transfer notes are retained.

Current downstream boundary claim:

PaperToSkill should be evaluated on original-paper-style input/output tasks to
test whether agents or users can reuse the source paper's method from the skill
and obtain acceptable real task outcomes. A first single-run GPT-family pass
over eight such tasks is complete, but it is mixed and failure-heavy rather
than a validation of aggregate downstream effectiveness.

## Contribution Bullets

1. A paper-to-skill schema for converting paper contributions into portable
   agent instructions with workflow steps, validation checks, failure branches,
   source anchors, and transfer notes.
2. A deterministic extraction scaffold that converts curated paper notes into
   `SKILL.md` artifacts plus source maps, plus a first extracted-text-to-note
   scaffold for auditable pre-processing.
3. A benchmark package over four real agent-method papers: AI Scientist-v2,
   Reflexion, AIDE, and Toolformer.
4. An evaluation suite for structural validity, context-coverage against
   summaries, source-span support, compactness, and offline transfer readiness.
5. A provenance discipline for separating validated claims, inferred transfer
   guidance, blocked live experiments, and failure branches.
6. A first single-run real-reuse stress test over eight `paper-task` rows
   across AIDE, SWE-agent, Reflexion, and SnapATAC2, with Toolformer and
   AI Scientist-v2 retained as sanity/auxiliary cases.

## Section Plan

### 1. Introduction

Core problem: useful LLM/agent methods remain trapped in papers. Summaries help
people understand the idea, but they often omit operational details an agent
needs to reuse the method.

Key framing: a skill is a compact, natural-language operational artifact. It can
be inspected by humans, edited without code, and loaded by agents as procedural
context.

Supported contribution: PaperToSkill is a conversion layer from papers into
skills, not a claim that every paper can be fully automated from PDF alone.

### 2. Related Work

Organize by capability rather than chronology:

- Automated research workflows: AI Scientist-v2, Agent Laboratory.
- Code and experiment search: AIDE.
- Skill libraries and reuse: Voyager.
- Reflection and memory: Reflexion.
- Tool and agent interfaces: Toolformer, SWE-agent.

Gap: existing work introduces powerful workflows inside specific systems.
PaperToSkill targets extraction and transfer of those workflows into compact,
source-grounded skill artifacts.

### 3. Method

Describe the PaperToSkill schema:

- identity and contribution;
- when to use the skill;
- required inputs;
- workflow steps;
- validation checks;
- failure cases;
- transfer notes;
- source notes and source map.

Describe extraction:

- generate automatic note scaffolds from extracted text for Toolformer and AIDE
  using line-window selection and source anchors;
- normalize source note sections;
- collect candidate bullets from abstract, methods, experiments, limitations,
  and transfer sections;
- rank and cap candidates for compactness;
- emit `SKILL.md` and `references/source_map.json`;
- preserve source-backed and inferred transfer material separately.

### 4. Experiments

Current completed benchmark:

Papers:

- AI Scientist-v2: automated research workflow and agentic tree search.
- Reflexion: verbal reflection, episodic memory, retry policy.
- AIDE: code-space tree search for ML engineering.
- Toolformer: self-supervised tool-use data generation and API-call filtering.

Baselines and ablations:

- generated skill;
- generic summary;
- abstract-only context;
- generated skill without `Transfer Notes`.

Metrics:

- deterministic skill rubric;
- context-coverage score;
- transfer-readiness score;
- source-span support rate;
- word count and compactness budget;
- unsupported instruction rate where available.

Real-reuse first-pass benchmark:

- Main candidate papers: AIDE, SWE-agent, Reflexion, and SnapATAC2.
- Main unit: one `paper-task`, meaning a task that preserves the source
  paper's input/output shape and metric family.
- Task count: eight tasks, two per main paper/domain.
- Main condition comparison: `Summary` versus `PaperToSkill`.
- Full excerpts: small sanity check only, not the main table.
- Model ablation: rerun a subset or all eight real-reuse tasks across
  Claude-family, GPT-family, and DeepSeek-family slots using the same runner,
  budget, prompts, and scoring logic.
- Source of truth: `research/real_reuse_experiment_plan.md`.

### 5. Results

Main results from `results/tables/main_results.md`:

- all four generated skills score 20/20 on the deterministic skill rubric;
- generated skills outperform generic-summary and abstract-only baselines on
  deterministic context coverage across all four papers;
- source support rates are 0.938, 1.0, 1.0, and 1.0 with zero invalid line
  ranges;
- skills remain under 1200 words;
- generated skills use 2.39%, 4.28%, 9.65%, and 6.16% of full extracted
  paper `o200k_base` tokenizer-aware input-token proxies;
- saved Claude/GPT-family/DeepSeek model-ablation responses total 9,594 local
  `o200k_base` output tokens across six measured rows;
- full skills score 10/10 on offline transfer readiness, while removing
  transfer notes drops readiness to 7.6/10 in all four cases.
- the failure-case archive records 27 cases: 21 paper-reported limitations or
  failure branches and 6 project-level failure/fix records.
- the reproducibility package checker reports local package readiness with
  bounded AI-Scientist-v2 smoke/full-run evidence complete, while pending
  human-annotation and final-submission evidence remain separated from local
  failures.
- all four live-transfer response sets have saved Claude-family responses across
  Codex-style and Claude-style harness prompts and all three context variants;
  the aggregate evaluator reports 24/24 scored rows, 0 pending rows, and 1.0
  average normalized score. AI Scientist-v2, Reflexion, and AIDE rows score
  11/11; Toolformer rows score 9/9.
- the model-ablation protocol has 6 saved and scored rows in the current
  protocol; GPT-family completed both rows with `gpt-5.5`, DeepSeek completed
  both rows with `deepseek-v4-flash`, and the latest Claude protocol refresh was
  provider-blocked so the scored Claude rows come from earlier saved response
  files.
- the bounded Paper2Agent artifact/workflow comparison reports 7/7 ready
  criteria across required inputs, artifact type, setup burden, validation,
  failure handling, source traceability, and runtime dependency.
- in a separate auto-note comparison, the Toolformer extracted-text scaffold
  produces a 1,179-word skill scoring 20/20 on the deterministic rubric,
  9.3/10 on context coverage, 10/10 transfer readiness, and 1.0 source support
  rate; the AIDE extracted-text scaffold produces a 998-word skill scoring
  20/20, 8.467/10 context coverage, 9.5/10 transfer readiness, and 1.0 source
  support rate.

Interpretation: PaperToSkill preserves operational paper details that short
summaries omit. The deterministic result remains an artifact-readiness and
coverage result, while the real-reuse first pass is downstream stress-test
evidence rather than aggregate success-rate evidence.

Current real-reuse interpretation: all eight rows now have one GPT-family
Summary-vs-PaperToSkill pass. After rerunning the same saved AIDE outputs with
an extended 300-second local scorer budget, AIDE-T1 scores 0.816/0.817 and is
solved by both conditions, while AIDE-T2 scores 0.000/0.826 and becomes a
PaperToSkill-only success. SWE-T1 scores 0.000/0.000 because patches fail to
apply. SWE-T2 scores 0.000/1.000 and is another positive row for PaperToSkill.
REF-T1/T2 score 1.000/1.000, validating the runner/scorer path without showing
advantage over Summary. SNAP-T1/T2 score 0.000/0.500 and 0.200/0.400, but both
remain below the success threshold. The correct paper claim is mixed first-pass
evidence plus failure-boundary analysis, not aggregate downstream effectiveness.
SNAP phase108 and phase112 follow-ups are diagnostic: the controlled scaffold
and the model-generated SNAP-T1 executable-candidate scripts both close the
artifact/execution contract for Summary and PaperToSkill, so they do not
replace the locked main rows or show PaperToSkill advantage.

### 6. Limitations

Current limitations:

- main benchmark inputs are curated paper notes; the automatic note scaffolds
  are validated only on Toolformer and AIDE extracted text;
- metrics are deterministic and lexical/section based;
- live-transfer saved-response coverage is complete for the current prompt
  packets, but the scorer is a deterministic output-contract check rather than
  human semantic fidelity or real live task success;
- Claude/GPT-family/DeepSeek model ablation rows are saved and scored for the
  current prompt protocol, but this is saved-response evidence rather than live
  task success, provider economics, or broad model-quality proof;
- the bounded Paper2Agent comparison is source-backed artifact/workflow
  positioning, not an executable MCP baseline run;
- no human fidelity annotation or inter-rater agreement yet;
- human-fidelity review packets, a reviewer handoff guide, a stricter blank
  annotation template, and a summarizer are prepared, but annotation remains
  pending;
- cost evidence includes local input/output token proxies, not provider bills
  or a full token-price study;
- the failure-case archive is provenance evidence, not an outcome study showing
  that recording failures improves final task success;
- the reproducibility package is ready locally but still lacks completed human
  annotations and final submission readiness under the recorded wait policy;
  provider billing remains outside the current claim set, and the completed
  bounded AI-Scientist-v2 smoke/full-run evidence is not human fidelity,
  real-data validation, or broad live task-success evidence;
- benchmark is focused on agent-method papers.

### 7. Conclusion

PaperToSkill shows that papers can be translated into compact, source-grounded
skills with measurable offline advantages over summaries and a completed
first-pass real-reuse stress test. The next stage is to repeat and expand the
original-style paper tasks, add human fidelity review, run a full executable
Paper2Agent/MCP baseline if feasible, and stress test papers whose methods are
less directly procedural.

## Figure And Table Plan

| Item | Source Artifact | Purpose |
| --- | --- | --- |
| Figure 1: PaperToSkill pipeline | `scripts/papertoskill_extract.py`; `skill/SKILL.md` | Show paper note to skill/source-map flow |
| Table 1: Real-reuse main experiment | `results/real_reuse/main_results_plan.md` | Eight Summary-vs-PaperToSkill paper-task rows; AIDE-T2 and SWE-T2 are PaperToSkill-only successes, AIDE-T1 and REF rows are solved by both, and SWE-T1/SNAP remain boundary rows |
| Table 2: Real-reuse failure-boundary analysis | `results/real_reuse/failure_analysis.md` | Row-level boundary modes and follow-up method contracts for the first-pass real-reuse rows |
| Diagnostic tables: SWE-T1 and SNAP follow-ups | `results/real_reuse/swe_t1_source_context_followup.md`; `results/real_reuse/swe_t1_issue_aligned_followup.md`; `results/real_reuse/snapatac2_executable_artifact_followup.md`; `results/real_reuse/snapatac2_executable_candidate_run_report.md` | Paired diagnostic follow-ups; they clarify task/artifact contracts without replacing main rows or showing aggregate advantage |
| Table 3: Deterministic/offline quality results | `results/tables/main_results.md` | Coverage, source support, compactness |
| Table 4: Transfer ablation | `results/tables/transfer_ablation.md` | Effect of transfer notes |
| Table 5: Source grounding | `results/tables/compactness_source_grounding.md` | Source support and compactness |
| Table 6: Context cost proxy | `results/tables/context_cost_proxy.md`; `results/tables/model_response_cost_proxy.md` | Full paper vs skill context size plus saved-response output-token proxy |
| Table 7: Auto-note comparison | `results/tables/auto_note_comparison.md` | Curated vs extracted-text Toolformer and AIDE note scaffolds |
| Appendix: Human-fidelity packets | `results/human_fidelity_packets/` | Prepared review packets, handoff guide, and blank annotation template |
| Appendix: Human-fidelity summary | `results/human_fidelity_packets/annotation_summary.md` | Pending annotation status and validation summary |
| Appendix: Failure-case archive | `results/failure_cases/failure_case_archive.md` | Paper-reported and project-level failure/limitation cases |
| Appendix: Reproducibility package | `results/reproducibility/package_report.md` | Local package readiness and pending external evidence |
| Appendix: Review/rebuttal package | `research/review_report.md`; `research/rebuttal_bank.md` | Adversarial risks and evidence-bounded responses |
| Appendix: Prompt packets | `results/live_transfer_prompts/` | Live prompt packets, run reports, saved responses, and deterministic output-contract scoring |
| Appendix: Model ablation prompts | `results/model_ablation_prompts/v0/` | Claude/GPT-family/DeepSeek prompt grid, live-attempt reports, and saved/scored rows under the current protocol |
| Appendix: Model response cost proxy | `results/tables/model_response_cost_proxy.md` | Local output-token proxy for saved Claude/GPT-family model-ablation responses |
| Appendix: AAAI package | `paper/aaai/` | Official AAAI-27 template provenance and LaTeX draft |
| Appendix: Paper2Agent artifact comparison | `results/tables/paper2agent_artifact_comparison.md` | Source-backed skill-vs-MCP artifact/workflow positioning table |
| Real reuse main results | `results/real_reuse/main_results_plan.md`; `results/real_reuse/raw_rows.jsonl` | Eight first-pass Summary-vs-PaperToSkill paper-task rows; mixed downstream and failure-boundary evidence |
| Real reuse failure analysis | `results/real_reuse/failure_analysis.md`; `results/real_reuse/raw_rows.jsonl` | Derived first-pass boundary modes; not new task-success evidence |
| Auxiliary: real-reuse LLM ablation | `results/real_reuse/llm_ablation_summary.md`; `results/real_reuse/llm_ablation_family_summary.csv`; `research/real_reuse_experiment_plan.md` | Cross-model stability slice with GPT-family and DeepSeek-family scored rows and Claude-family provider-pending rows; auxiliary evidence only, not a main-table replacement |
