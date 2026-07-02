# Paper2Agent Artifact Comparison

Evidence boundary: this is a bounded source-backed artifact/workflow comparison. It does not run Paper2Agent, deploy an MCP server, or claim baseline performance.

- Overall status: ready
- Ready criteria: 7
- Failed criteria: 0
- Paper2Agent extracted text words: 9895
- PaperToSkill skill words: 882

## Comparison

| Criterion | Status | Paper2Agent | PaperToSkill | Interpretation |
| --- | --- | --- | --- | --- |
| Required inputs | ready | paper plus associated codebase | paper-derived note or extracted text; codebase optional | Paper2Agent optimizes for executable paper agents, while PaperToSkill can work when only paper text is available. |
| Generated artifact | ready | MCP server with tools, resources, and prompts | compact natural-language skill with references and transfer notes | The two systems expose paper knowledge through different artifact types rather than direct drop-in replacements. |
| Setup burden | ready | configure environment and deploy or connect an MCP server | load one skill file plus local reference artifacts into an agent harness | PaperToSkill has lower setup burden for reading and transfer, but lacks executable MCP tools. |
| Validation checks | ready | iterative MCP tests and downstream case-study benchmarks | deterministic rubric, source-span, transfer-readiness, compactness, and saved-response checks | Both use validation, but Paper2Agent validates executable tools and PaperToSkill validates source-grounded skill artifacts. |
| Failure handling | ready | remove failing MCP decorators/tools and report codebase limitations | record failure branches, stop conditions, and unsupported evidence boundaries | PaperToSkill's distinctive contribution is making failure branches editable inside the skill artifact. |
| Source traceability | ready | tool/resource links and recorded workflow traces | source map and source-span validation tied to skill sections | Both care about provenance; PaperToSkill makes source boundaries central to the natural-language artifact. |
| Runtime dependency | ready | MCP runtime plus downstream agent connection | text skill usable across compatible agent harnesses | This is the main positioning gap: server-backed executable agents versus portable skill instructions. |

## Evidence Snippets

### Required inputs

- Paper2Agent evidence: Paper2Agent : Reimagining Research Papers As Interactive and Reliable AI Agents Jiacheng Miao1,2 , Joe R. Davis1 ,
- PaperToSkill evidence: on checks, failure cases, and transfer notes. --- # Toolformer: Language Models Can Teach Themselves to Use Tools This skill converts the source paper's operational contribution into an agent workflow. It is a scaffolded extraction and should be audited against the source before being used as validated paper knowledge. ## Source - Source file: `papers/notes/toolform

### Generated artifact

- Paper2Agent evidence: projects. A Paper2Agent automatically converts papers into AI agents Paper MCP servers Remote server Input: papers <Paper>_mcp.py
- PaperToSkill evidence: transferable method, assumptions, workflow, validation checks, limitations, failure cases, and cross-harness transfer notes into a concise SKILL.md artifact. --- # PaperToSkill Convert a paper into an agent skill, not a summary. Preserve the paper's operational contribution, evidence boundaries, and failure cases in a compact form another agent can use. ## Input

### Setup burden

- Paper2Agent evidence: server and then exposes that server to an AI agent interface. The process has four stages: (i) codebase identification and extraction, (ii) environment configuration, (iii) tool synthesis and MCP server generation, and (iv) testing, refinement, and deployment, followed by agent connection. We implemented this multi-agent AI system in Claude Code. We design an orchestrator agent that
- PaperToSkill evidence: ll'' to mean a natural-language operational artifact with an entry-point \texttt{SKILL.md}, similar to formats used by agent harnesses that load task-specific instructions. Unlike a summary, a skill is not only explanatory. It should specify when to use the method, which inputs are required, which steps to execute, how to validate progress, which failures to wat

### Validation checks

- Paper2Agent evidence: tarts with codebase extraction and automated environment setup for reproducibility. Core analytical features are wrapped as MCP tools, then validated through iterative testing. The resulting MCP server is deployed remotely and integrated with an AI agent, enabling natural-language interaction with the paper’s methods and analyses.
- PaperToSkill evidence: benchmark over AI Scientist-v2, Reflexion, AIDE, and Toolformer, PaperToSkill generates skills that score 20/20 on deterministic structural rubrics, preserve more deterministic operational coverage than generic-summary and abstract-only baselines, remain under a 1200-word compactness budget, and substantially reduce deterministic input-token proxy size relative to

### Failure handling

- Paper2Agent evidence: in a loop of generating tests, executing them, diagnosing failures, and applying fixes. If functions re- peatedly fail, their MCP decorators are removed, and they will not be included in the MCP server. All results and logs are recorded for transparency. Paper2Agent contains six steps: 1. Locate and download the codebase. Identify the official repository linke
- PaperToSkill evidence: are exactly the parts needed when a user wants an agent to apply a paper rather than merely explain it. The benchmark also reveals useful failure modes. During the AIDE case, the initial extractor capped workflow, validation, and failure candidates too aggressively, which dropped data-preview and LLM-cost content. Earlier phases also exposed title parsing, source-audit

### Source traceability

- Paper2Agent evidence: th around the variant, toggle different modalities—such as RNA-seq, ATAC- seq, or ChIP-seq histone tracks. Moreover, each MCP tool embeds a traceable link to the original GitHub source code, ensuring transparency and reproducibility. By connecting an AI agent with the AlphaGenome MCP, the system creates the AlphaGenome agent. Next, we benchmarked the Paper2Agent-gener
- PaperToSkill evidence: -470.", "Tool use emerges with model scale; smaller models benefit less from the provided APIs. Source anchors: lines 433-496." ], "source_map": { "sections": [ { "title": "Source", "line": 3, "level": 2, "characters": 355 }, { "title": "Abstract", "line": 13, "level": 2, "ch

### Runtime dependency

- Paper2Agent evidence: projects. A Paper2Agent automatically converts papers into AI agents Paper MCP servers Remote server Input: papers <Paper>_mcp.py
- PaperToSkill evidence: pact, human-editable skills that preserve operational knowledge, validation checks, failure branches, transfer notes, and source boundaries without requiring an MCP server or a runnable paper codebase. \section{Method} PaperToSkill represents each converted paper as a skill package. The main file is \texttt{SKILL.md}; optional references include a source map that links generated skill b
