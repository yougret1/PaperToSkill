# PaperToSkill Paper Outline

Evidence boundary: this outline is grounded in deterministic/offline artifacts
from four curated real-paper notes. It should not be read as evidence of live
cross-harness agent task success until the prepared prompt packets are executed.
Phases 19-20 additionally include deterministic extracted-text-to-note
scaffolds for Toolformer and AIDE; these are separate from the curated-note main
benchmark. Phase 21 adds an AAAI-27 LaTeX package and usage examples. Phase 22
adds a model-ablation runner/evaluator and a live-attempt report, but the
current endpoint is blocked by provider/model availability.

## Working Title

PaperToSkill: Turning Research Papers into Portable Agent Skills

## Abstract Claim

Research papers often contain reusable agent workflows, but those workflows are
hard for non-expert users to operationalize. PaperToSkill studies whether a
paper can be converted into a compact, human-editable skill that preserves
procedural knowledge, source grounding, validation checks, failure branches, and
transfer notes. On four curated agent-method papers, generated skills pass
deterministic structural rubrics, preserve more task-relevant operational
coverage than summary baselines, remain under a 1200-word compactness budget,
and show stronger offline transfer readiness when transfer notes are retained.

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
- full skills score 10/10 on offline transfer readiness, while removing
  transfer notes drops readiness to 7.6/10 in all four cases.
- the failure-case archive records 27 cases: 21 paper-reported limitations or
  failure branches and 6 project-level failure/fix records.
- the reproducibility package checker reports local package readiness with
  pending live-response, model-ablation-response, and human-annotation evidence
  separated from local failures: 134 ready checks, 7 pending checks, and 0
  failed checks.
- the model-ablation live attempt records that `claude-opus-4-8` is listed but
  blocked by provider account availability, and that no GPT-family alias is
  listed on the current endpoint.
- in a separate auto-note comparison, the Toolformer extracted-text scaffold
  produces a 1,179-word skill scoring 20/20 on the deterministic rubric,
  9.3/10 on context coverage, 10/10 transfer readiness, and 1.0 source support
  rate; the AIDE extracted-text scaffold produces a 998-word skill scoring
  20/20, 8.467/10 context coverage, 9.5/10 transfer readiness, and 1.0 source
  support rate.

Interpretation: PaperToSkill preserves operational paper details that short
summaries omit. The result is an artifact-readiness and coverage result, not yet
a live agent success-rate result.

### 6. Limitations

Current limitations:

- main benchmark inputs are curated paper notes; the automatic note scaffolds
  are validated only on Toolformer and AIDE extracted text;
- metrics are deterministic and lexical/section based;
- live cross-harness execution is blocked by remote provider availability;
- Claude/GPT-family/DeepSeek model ablation prompts are prepared and the live
  runner/evaluator exists, but the current attempt is blocked/unavailable and
  response rows remain unscored;
- no human fidelity annotation or inter-rater agreement yet;
- human-fidelity review packets and a summarizer are prepared, but annotation
  remains pending;
- cost evidence is compactness-oriented and not yet a full token-price study;
- the failure-case archive is provenance evidence, not an outcome study showing
  that recording failures improves final task success;
- the reproducibility package is ready locally but still lacks live response
  logs and completed human annotations;
- benchmark is focused on agent-method papers.

### 7. Conclusion

PaperToSkill shows that papers can be translated into compact, source-grounded
skills with measurable offline advantages over summaries. The next stage is live
execution across harnesses, human fidelity review, and stress tests on papers
that are less directly procedural.

## Figure And Table Plan

| Item | Source Artifact | Purpose |
| --- | --- | --- |
| Figure 1: PaperToSkill pipeline | `scripts/papertoskill_extract.py`; `skill/SKILL.md` | Show paper note to skill/source-map flow |
| Table 1: Main results | `results/tables/main_results.md` | Coverage, source support, compactness |
| Table 2: Transfer ablation | `results/tables/transfer_ablation.md` | Effect of transfer notes |
| Table 3: Source grounding | `results/tables/compactness_source_grounding.md` | Source support and compactness |
| Table 4: Context cost proxy | `results/tables/context_cost_proxy.md` | Full paper vs skill context size and cost proxy |
| Table 5: Auto-note comparison | `results/tables/auto_note_comparison.md` | Curated vs extracted-text Toolformer and AIDE note scaffolds |
| Appendix: Human-fidelity packets | `results/human_fidelity_packets/` | Prepared review packets and blank annotation template |
| Appendix: Human-fidelity summary | `results/human_fidelity_packets/annotation_summary.md` | Pending annotation status and validation summary |
| Appendix: Failure-case archive | `results/failure_cases/failure_case_archive.md` | Paper-reported and project-level failure/limitation cases |
| Appendix: Reproducibility package | `results/reproducibility/package_report.md` | Local package readiness and pending external evidence |
| Appendix: Review/rebuttal package | `research/review_report.md`; `research/rebuttal_bank.md` | Adversarial risks and evidence-bounded responses |
| Appendix: Prompt packets | `results/live_transfer_prompts/` | Inputs for later live transfer runs |
| Appendix: Model ablation prompts | `results/model_ablation_prompts/v0/` | Claude/GPT-family/DeepSeek prompt grid, live-attempt report, and pending response evaluation |
| Appendix: AAAI package | `paper/aaai/` | Official AAAI-27 template provenance and LaTeX draft |
