# AAAI 2025-2026 Section-Structure Review for SkillAudit

## Scope and Evidence

This review uses five locally available papers whose AAAI proceedings metadata was independently matched through Crossref/OpenAlex/Semantic Scholar. The line counts below refer to page-preserving PDF text extraction, not LaTeX source lines. They are useful for comparing section scale, but the rendered page is the authoritative layout evidence.

| Paper | Proceedings evidence | Local PDF | Why it is relevant |
|---|---|---|---|
| CITI: Enhancing Tool Utilizing Ability in Large Language Models Without Sacrificing General Performance | AAAI 2025, DOI `10.1609/aaai.v39i22.34573` | `../papers/2025 - CITI Enhancing Tool Utilizing Ability in Large Language Models Without Sacrificing General Performance.pdf` | Tool-learning method, staged method narrative, architecture figure, component ablation |
| Automated Creation of Reusable and Diverse Toolsets for Enhancing LLM Reasoning | AAAI 2025, DOI `10.1609/aaai.v39i23.34664` | `../papers/2025 - Automated Creation of Reusable and Diverse Toolsets for Enhancing LLM Reasoning.pdf` | Closest accepted paper for reusable executable tools; explicit preliminaries, algorithm, objectives, staged evaluation |
| Prompt Compression with Context-Aware Sentence Encoding for Fast and Improved LLM Inference | AAAI 2025, DOI `10.1609/aaai.v39i23.34639` | `../papers/2025 - Prompt Compression with Context-Aware Sentence Encoding for Fast and Improved LLM Inference.pdf` | Closest accepted paper for compression; dedicated Problem Definition and formal compression objective |
| MCP-AgentBench: Evaluating Real-World Language Agent Performance with MCP-Mediated Tools | AAAI 2026, DOI `10.1609/aaai.v40i37.40347` | `../papers/2026 - MCP-AgentBench Evaluating Real-World Language Agent Performance with MCP-Mediated Tools.pdf` | Agent benchmark design, evaluation validity, outcome-oriented metric, workflow figure |
| AutoTool: Efficient Tool Selection for Large Language Model Agents | AAAI 2026, DOI `10.1609/aaai.v40i37.40389` | `../papers/2026 - AutoTool Efficient Tool Selection for Large Language Model Agents.pdf` | Dedicated Problem Statement, concise method overview, graph representation, efficiency experiments |

Online retrieval limitations are preserved under `literature_search/stage1/retrieval/`. DBLP had intermittent TLS/rate-limit failures; Crossref and at least one additional source verified the key 2025 records, while Crossref verified the 2026 proceedings records.

## What the Accepted Papers Actually Do

### 1. Prompt Compression with Context-Aware Sentence Encoding (AAAI 2025)

**Problem Definition length:** PDF page 3, extracted lines 245-272, about 28 lines and one continuous two-column paragraph.

**Paragraph functions:**

1. Opens by defining the input context, compressed context, token lengths, and compression ratio. The math stays inline because each expression is short and only supports the prose-level objective.
2. States the behavioral objective: reduce the ratio while matching the original prompt's downstream performance.
3. Contrasts that objective with token-deletion failures: incoherence, grammatical damage, and semantic loss.
4. Introduces the sentence-level solution and its differentiating component, a context-aware sentence encoder.
5. Ends with a roadmap: dataset construction, encoder training, then inference. This last sentence is a transition contract with the next subsections.

**Equations and figures:** The Problem Definition itself has no numbered display equation. The method later uses six display equations for probability distributions, context-aware embeddings, the contrastive loss, and the masked-token loss. Figure 2 appears when the data-construction pipeline becomes too complex for prose alone. Its caption narrates the start, verification step, negative selection, and output.

**Experiment narrative:** Datasets -> implementation details -> evaluation protocols -> results. The paper defines how it will be judged before presenting the main table, then interprets results and ablations.

**Lesson for SkillAudit:** Keep the opening formulation compact. Put local symbols inline; reserve display equations for the atom identity, operational-success predicate, and decision rule that the rest of the paper references.

### 2. AutoTool (AAAI 2026)

**Problem Statement length:** PDF page 3, extracted lines 252-272, about 21 lines in two paragraphs. The following Overview is about 13 lines.

**Paragraph functions:**

1. Defines the agent action, observation, task goal, tool set, and the existing LLM policy. It immediately names the cost problem.
2. Defines historical trajectories and states the exact construction objective: a training-free algorithm that selectively bypasses predictable LLM calls.
3. The Overview opens by pointing to Figure 2, gives the two modules in execution order, states the fallback rule, and ends by promising module-level detail.

**Equations and figures:** Action selection and trajectory tuples remain inline because they are short setup notation. The central Comprehensive Inertia Potential Score is displayed and numbered because it is reused as the actual selection rule. Figure 2 is a full-width method overview with three panels: complete workflow, inertia sensing, and parameter filling. The caption explains both success and fallback paths.

**Experiment narrative:** Experimental setup -> speedup -> overhead analysis -> sensitivity analysis. The section is claim-organized: primary benefit first, cost mechanism second, parameter stability last.

**Lesson for SkillAudit:** State the baseline method and its limitation before introducing our objective. The overview figure must show both the normal decision path and the invalid/fallback path.

### 3. Automated Creation of Reusable and Diverse Toolsets (AAAI 2025)

**Preliminaries length:** PDF page 3, extracted lines 238-265, about 28 lines. The complete method occupies extracted lines 236-674, roughly four rendered pages.

**Paragraph functions:**

1. Defines training/test datasets, input/solution pairs, the toolset, and the desired test-time role.
2. Lists two objectives, tool reusability and toolset diversity, with observable measurements for both.
3. Connects each objective to one stage of the proposed framework.
4. Ends with a section roadmap and points forward to the metric definitions.

**Equations, algorithm, and figures:** Algorithm 1 appears beside the preliminaries and exposes the complete two-stage control flow. Display equations define the knowledge tree, tool-effectiveness score, joint optimization loss, and augmented-agent mapping. Figure 2 carries the detailed creation/evolution pipeline. The loss is displayed because it combines several objectives and is referenced later as the optimization guide.

**Experiment narrative:** Experimental setup -> main results -> ablation study -> framework-specific analysis. The accepted paper does not narrate the chronology of model development; it narrates the evidence needed for the contribution.

**Lesson for SkillAudit:** Name the decision objectives and observable fields before implementation detail. A compact algorithm is appropriate because the protocol has a fixed order and explicit early Invalid branch.

### 4. CITI (AAAI 2025)

**Problem formulation:** There is no dedicated Problem Formulation section. The paper first runs a motivation/analysis section and then starts Methodology with a 12-line overview (extracted lines 471-482).

**Opening paragraph functions:**

1. Restates the method goal as a response to the preceding analysis.
2. Explains the high-level division between important and unimportant components.
3. Points to Figure 4 and names three training stages in order.
4. Ends by promising detailed explanation of each technique.

**Equations and figures:** Figure 4 occupies the top of page 5 and serves as the architecture anchor. Equations (6)-(11) define the router, mixture output, importance matrix, routing loss, component score, and final training loss. Short symbol assignments stay inline; multi-term functions that drive training are displayed and numbered.

**Experiment narrative:** Datasets -> implementation details -> evaluation metrics -> baselines -> overall results -> ablation studies. Related Work appears after experiments, showing that section order is flexible when the motivation analysis needs to precede the method.

**Lesson for SkillAudit:** The first method paragraph must name every major stage in execution order. Details should then follow that order exactly.

### 5. MCP-AgentBench (AAAI 2026)

**Problem formulation:** No dedicated formal subsection. The benchmark section begins with a 9-line roadmap (extracted lines 140-148), followed by about 170 lines of data-construction methodology and about 58 lines defining MCP-Eval.

**Paragraph functions:**

1. Opens by stating what the section builds and enumerating the construction components.
2. Ends the roadmap by naming the statistics and evaluator that close the section.
3. The construction subsection names three stages, the assisting model, and the human-in-the-loop validity check before any stage detail.
4. Each stage then begins with its purpose, gives the procedure, and closes with the resulting artifact or quality guarantee.

**Equations and figures:** Figure 2 combines the data-construction and evaluation workflows, making the benchmark/evaluator boundary visible. The Pass Rate and judge mapping are displayed because they are the benchmark's authoritative outcome definitions. Figure 3 is descriptive dataset characterization, while Table 1 is the main model comparison.

**Experiment narrative:** Experimental setup -> main model comparison -> capability findings. The paper reports an explicit formatting incompatibility for one model instead of silently turning it into a performance number, which directly supports SkillAudit's Invalid/diagnostic distinction.

**Lesson for SkillAudit:** A benchmark or protocol paper needs a validity story before performance. Interface incompatibilities belong in the results as measurement findings, not in an unstructured error log.

## Cross-Paper Pattern

Across these accepted papers, the formulation/preliminaries block is usually **about 20-30 extracted lines**, or roughly one-quarter to one-half of a two-column page. Two papers omit a dedicated formulation subsection, but their method still begins with a compact objective-and-roadmap paragraph. None places commit history, debugging chronology, or post-hoc repair details in the problem definition.

The recurring narrative is:

1. Define the object and observable objective.
2. State why the existing route is insufficient.
3. Name the proposed mechanism or protocol.
4. Show the complete information flow in a figure or algorithm.
5. Expand modules in exactly the order shown.
6. Define evaluation metrics before presenting results.
7. Organize experiments by claims (main effect, ablation/control, robustness/sensitivity), not development versions.

## Inline Math vs. Display Equations

Use **inline math** when a symbol or short relation is local to one sentence: `C in {B,F,S}`, a context length `L`, an action `a_t`, or a short tuple introduced only to support prose. Inline math preserves reading flow and avoids visually overstating minor notation.

Use a **display equation** when the expression is one of the paper's reusable contracts:

- a central object definition with several fields;
- an objective or loss with several terms;
- a multi-condition acceptance rule;
- a metric that tables and later paragraphs cite;
- a piecewise decision with semantically distinct branches.

Number a display equation only when later text refers to it or when it is central enough to deserve a stable identifier. A short expression should not be displayed merely because it contains math. Conversely, SkillAudit's operational-success predicate and Accept/Reject/Invalid rule should be displayed because they determine every reported result.

## Sentence-Level Purpose of the New SkillAudit Formulation

The rewritten `src/4.method.tex` uses the following sentence sequence:

| Sentence role | Why it is present |
|---|---|
| Introduce paper `P`, full specification `F`, and candidate `S` | Establish the evaluated objects before any implementation detail |
| State that neither `F` completeness nor `S` faithfulness is assumed | Prevent the full specification from being treated as an oracle |
| Ask whether `S` substitutes for `F` under task `t` and boundary `Omega` | State the exact scientific claim |
| Introduce `B/F/S` | Make the causal comparison explicit |
| Define source-addressed atoms and the dependency graph | Connect the behavioral claim to paper provenance |
| Define the atom tuple in Equation (1) | Give every later evidence field a stable meaning |
| Define candidate closure and deterministic rendering | Separate structural eligibility from behavioral sufficiency |
| Define matched execution and terminal fields | Specify what one experimental row means |
| Define operational success in Equation (2) | Create the authoritative metric used by every table |
| State that counts are finite-schedule evidence | Block unjustified population claims |

The next subsection immediately points to the overview figure, names all protocol stages, and then follows them in the same order: source construction -> frozen boundary -> validity -> decision -> evidence record. The method ends on the reusable output contract, not on implementation history.

## What Was Incorporated into the Draft

- A compact, assumption-aware Problem Formulation.
- One full-width overview figure with explicit provenance, B/F/S matching, validity, and decision flow.
- Display equations only for the atom identity, operational success, frozen boundary, decision rule, and evidence record.
- A complete protocol algorithm with an explicit Invalid branch.
- Experiments organized by RQ1-RQ3 rather than V3/V4/V5 chronology.
- Separate evidence layers for the complete focused suite and the 1,296-row interface-dominated stress test.
- A precise table of all five operational successes with a warning that they do not form paired effects.
- A failure-decomposition figure and a forward interface check.
- Conclusions scoped to local acceptance and corrected future cross-paper evaluation.
