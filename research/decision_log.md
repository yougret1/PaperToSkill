# Decision Log

## 2026-06-17: Create Durable Memory Before Development

- Decision: maintain at least two memory files, long-term and short-term.
- Rationale: the user explicitly requested local memory to survive context
  compaction.
- Status: accepted.

## 2026-06-17: Keep PaperToSkill Artifacts In Their Own Repo

- Decision: store research artifacts in `D:\a_work\gitee\PaperToSkill` and use
  `D:\a_work\gitee\ai-scientist-v2` as the execution engine.
- Rationale: `ai-scientist-v2` already has unrelated local modifications; keeping
  PaperToSkill artifacts separate reduces accidental churn.
- Status: accepted.

## 2026-06-17: Do Not Commit Raw API Key

- Decision: record endpoint/model and environment-variable names, but not the
  raw API key, in tracked files.
- Rationale: the user said secrecy is not important for now, but avoiding secret
  commits keeps the repository safer without blocking local execution.
- Status: accepted.

## 2026-06-17: Initial Contribution Shape

- Decision: treat PaperToSkill as both a system and a paper artifact, not merely
  a prompt.
- Rationale: the idea needs measurable claims, reusable output, and transfer
  evaluation to become research rather than a simple utility.
- Status: working decision.

## 2026-06-17: Use Dashed Model Alias Locally

- Decision: use `claude-opus-4-8` in local AI-Scientist-v2 configs and runbooks.
- Rationale: the endpoint's `/v1/models` response advertises
  `claude-opus-4-8`, while the dotted spelling `claude-opus-4.8` is not listed.
- Status: accepted until the provider documents a different alias.

## 2026-06-17: Pause Long Remote Runs Until Provider Accounts Recover

- Decision: do not start long LLM-dependent AI-Scientist-v2 runs yet.
- Rationale: direct chat completion reached the server but failed with exhausted
  account-pool errors.
- Status: accepted.

## 2026-06-17: Draft Paper From Validated Offline Evidence First

- Decision: create a paper draft package before adding more benchmark cases.
- Rationale: three real-paper cases are enough to define the paper narrative,
  supported claims, table plan, and evidence boundary. Writing now exposes
  missing evidence, especially live cross-harness execution, human fidelity
  annotation, and token-price accounting.
- Status: accepted for Phase 11.

## 2026-06-17: Treat Cost As A Deterministic Proxy Until Live Pricing Exists

- Decision: add a local token/cost proxy experiment using
  `ceil(characters / 4)` and a configurable price per million input-token proxy.
- Rationale: the paper needs an economic/compactness result, but live provider
  billing and tokenizer-exact model prices are not yet available. A deterministic
  proxy supports reproducible relative context-size claims without overstating
  real cost savings.
- Status: accepted for Phase 12.

## 2026-06-17: Prepare Human-Fidelity Packets Without Inventing Scores

- Decision: create a human-fidelity review protocol, paper-specific packets, and
  a blank annotation template, but keep annotation status as `pending`.
- Rationale: source-span validation is useful but not equivalent to semantic
  human review. Preparing the packets makes the missing study executable while
  avoiding false claims of completed human validation.
- Status: accepted for Phase 13.

## 2026-06-17: Summarize Human-Fidelity Annotations As Pending Until Scored

- Decision: add a deterministic annotation summarizer that treats blank score
  rows as pending rather than negative evidence.
- Rationale: the paper needs a reproducible path from human annotations to
  results, but the current template is intentionally blank. The summarizer makes
  the pending boundary machine-readable and validates future filled rows.
- Status: accepted for Phase 14.

## 2026-06-17: Treat Failure Branches As First-Class Evidence Artifacts

- Decision: build a failure-case archive that aggregates paper-reported
  limitations with project-level failure/fix records.
- Rationale: the user's paper outlook explicitly values failed branches for
  real deployable projects. Archiving them improves provenance and prevents the
  draft from telling a success-only story.
- Status: accepted for Phase 15.

## 2026-06-17: Separate Local Reproducibility From External Evidence

- Decision: add a reproducibility package checker that reports local package
  readiness separately from pending live responses and human annotations.
- Rationale: the project has many deterministic/offline artifacts that are ready
  for review, but live LLM calls and independent human scoring remain blocked or
  uncollected. A gate with `ready`, `pending`, and `fail` states prevents both
  hidden local breakage and overclaiming.
- Status: accepted for Phase 16.

## 2026-06-17: Prepare Rebuttals Without Strengthening Unsupported Claims

- Decision: create an internal review report and rebuttal bank before adding
  stronger paper language.
- Rationale: the current package has enough deterministic/offline evidence to
  be reviewable, but likely reviewer objections must be answered with evidence
  boundaries intact.
- Status: accepted for Phase 17.

## 2026-06-17: Add Toolformer As A Tool-Use Stress Case

- Decision: add Toolformer as the fourth curated real-paper benchmark case.
- Rationale: prior evidence focused on agent/research/ML-engineering workflows.
  Toolformer adds a tool-use and API-contract paper, reducing but not removing
  the benchmark-diversity risk.
- Status: accepted for Phase 18.

## 2026-06-17: Add Deterministic Text-To-Note Scaffold Before Claiming PDF Automation

- Decision: add `scripts/papertoskill_note_from_text.py`, a deterministic
  extracted-text-to-note scaffold, and evaluate the Toolformer auto-note-derived
  skill separately from the curated-note main benchmark.
- Rationale: the largest current automation gap is the manually curated note
  step. A source-anchored scaffold reduces that gap while preserving the
  evidence boundary that automatic notes must be audited and are not yet a
  reliable arbitrary-PDF conversion claim.
- Status: accepted for Phase 19.

## 2026-06-17: Extend Auto-Note Scaffold With AIDE Profile

- Decision: add an AIDE-specific selection profile for the deterministic
  extracted-text-to-note scaffold and evaluate the AIDE auto-note-derived skill
  separately from the curated-note main benchmark.
- Rationale: Toolformer is a tool/API-contract paper; AIDE stresses a different
  code and ML-engineering workflow with solution-tree search, coding actions,
  benchmark metrics, data-contamination limits, greedy/local-optima caveats, and
  LLM cost analysis. A second profile tests whether the scaffold can be adapted
  beyond the first Toolformer case while preserving the audit-scaffold boundary.
- Status: accepted for Phase 20.

## 2026-06-18: Use Official AAAI-27 LaTeX Template For Paper Package

- Decision: download the official AAAI-27 author kit from
  `https://aaai.org/authorkit27/`, keep the template provenance in
  `paper/aaai/README.md`, and create an AAAI-formatted PaperToSkill draft.
- Rationale: the user requested that the final paper use the AAAI TeX template;
  as of 2026-06-18 the official AAAI author-kit endpoint provides the AAAI-27
  package with `aaai2027.sty`.
- Status: accepted for Phase 21.

## 2026-06-18: Treat Claude/GPT/DeepSeek Ablations As Prepared Until Responses Exist

- Decision: create model-ablation prompt packets for Claude Opus 4.8,
  a GPT-family slot requested as GPT 5.5, and a DeepSeek follow-up slot, but
  mark response files and scoring as pending external evidence.
- Rationale: model aliases and provider availability are unstable. The Claude
  endpoint has previously advertised `claude-opus-4-8`, while chat completion
  has failed due to provider capacity; GPT 5.5 must be verified at run time.
- Status: accepted for Phase 21.

## 2026-06-18: Record Live Model-Ablation Attempts As Availability Evidence

- Decision: add a reusable live runner and response evaluator, run the Claude
  and GPT-family slots against the current endpoint, and classify failures as
  provider/model availability evidence unless response files are saved and
  scored.
- Rationale: the user requested Claude Opus 4.8 and GPT-family ablation before
  adding DeepSeek. The current endpoint lists `claude-opus-4-8`, but chat
  completions fail with HTTP 503 because no provider accounts are available,
  and no GPT-family model alias is listed. Treating these as completed or
  negative-quality model results would overclaim.
- Status: accepted for Phase 22.
