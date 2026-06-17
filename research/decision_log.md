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
