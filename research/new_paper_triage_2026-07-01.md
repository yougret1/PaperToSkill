# New Paper Triage: 2026-07-01

Evidence boundary: this triage compares the three newly added papers against
PaperToSkill. It decides citation and experiment priority; it does not claim new
PaperToSkill benchmark results.

## Summary Decision

| Paper | Relationship | Add Citation? | Add Experiment Now? | Reason |
| --- | --- | --- | --- | --- |
| Paper2Agent | Direct competing/adjacent system | Yes, core related work | Completed a bounded artifact/workflow comparison; full MCP baseline remains later | It converts papers plus codebases into MCP servers and interactive paper agents. This is the closest external system to PaperToSkill. |
| AgenticSciML | Adjacent research-agent workflow | Yes, background related work | No immediate PaperToSkill experiment | It shows multi-agent debate, method memory, and evolutionary search for scientific discovery, but it is not a paper-to-skill converter. |
| Reasoning Manifolds | Theory/evaluation paper | Optional future-work citation only | No | It is useful as a non-procedural stress case, but it does not directly compete with paper-to-skill or paper-to-agent systems. |

## Paper2Agent

What it does: Paper2Agent analyzes a paper and its associated codebase, builds
an MCP server with tools/resources/prompts, runs iterative tests, deploys the
server, and connects it to an agent such as Claude Code. Its case studies cover
AlphaGenome, TISSUE, ScanPy, and AI co-scientist collaboration.

Why it matters for PaperToSkill: this is the strongest related work. It shares
the broad goal of turning papers into reusable agent-facing artifacts. The gap
is artifact type and operating assumption: Paper2Agent targets executable MCP
agents and needs codebase/environment/tool testing, while PaperToSkill targets
compact, source-grounded, human-editable skills that can be inspected and moved
between harnesses even when no runnable codebase is available.

Required paper update: cite Paper2Agent in Related Work and state the gap
directly: MCP paper agents versus portable natural-language skills.

Current comparison: `results/tables/paper2agent_artifact_comparison.md` now
contains a bounded source-backed skill-vs-MCP artifact/workflow comparison. It
measures required inputs, generated artifact type, setup burden, word/token
size, source traceability, failure handling, and validation checks. It does not
run Paper2Agent, deploy an MCP server, or claim PaperToSkill outperforms
Paper2Agent as an end-to-end executable baseline.

## AgenticSciML

What it does: AgenticSciML uses more than 10 specialized agents, structured
debate, retrieval-augmented method memory, ensemble-guided evolutionary search,
and numerical evaluation to discover SciML strategies.

Why it matters for PaperToSkill: it supports the broader motivation that
research-agent workflows are becoming complex reusable procedures. It is not a
paper conversion system, so it should be positioned as background rather than a
main baseline.

Required paper update: cite it as adjacent agentic-science workflow evidence.

Recommended future experiment: none now. It may become a source paper if we add
a harder research-workflow conversion case.

## Reasoning Manifolds

What it does: the paper studies LLM reasoning as inference-time dynamics in
internal representation space and proposes label-free diagnostics from manifold
structure and information volume.

Why it matters for PaperToSkill: it is a good stress case for papers whose
contribution is theoretical or diagnostic rather than a step-by-step agent
workflow.

Required paper update: no main related-work citation needed now. Keep it as a
future stress case or limitations example.

Recommended future experiment: only after the current procedural benchmark is
stable. The test would ask whether PaperToSkill can produce a useful skill for
non-procedural theory/evaluation papers without inventing executable workflow
steps.

## Immediate Action Items

1. Add Paper2Agent and AgenticSciML to the AAAI bibliography.
2. Update Related Work to distinguish PaperToSkill from Paper2Agent.
3. Keep Reasoning Manifolds out of the main experiment until a dedicated
   non-procedural stress-case protocol exists.
4. If stronger evidence is needed later, extend the bounded comparison into an
   executable Paper2Agent/MCP baseline run.
