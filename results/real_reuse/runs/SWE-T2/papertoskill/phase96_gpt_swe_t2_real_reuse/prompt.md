# Real-Reuse Condition: papertoskill

You are running a locked SWE-agent PaperToSkill real-reuse task. Use only the model-visible context and task prompt below. Do not request gold patches, hidden test patches, or scorer-only assets.

# Condition Context

---
name: swe-agent-paper-skill
description: Use when applying the paper-derived method from SWE-agent Agent-Computer Interfaces Enable Automated Software Engineering as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/auto_notes/swe_agent_auto_note.md`

## Paper Snapshot

... performance of language model agents. As a result of this exploration, we introduce
SWE-agent: a system that facilitates LM agents to autonomously use computers to solve
software engineering tasks. SWE-agents custom agent-computer interface (ACI)
significantly enhances an agents ability to ... Source anchors: lines 14-32.

## Central Contribution

As a result of this exploration, we introduce SWE-agent: a system that facilitates LM
agents to autonomously use computers to solve software engineering tasks.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Frame the method as an agent-computer interface that shapes commands, documentation, state, history, and feedback: ... back to the LM. It also tracks the history of all previous commands and observations and, at each step, manages how these should be formatted and combined with .... Source anchors: lines 135-139.
2. Keep ACI actions simple, compact, efficient, and paired with concise environment feedback: ... Actions should be simple and easy to understand for agents. Many bash commands have documentation that includes dozens of options. Simple commands with a few options and .... Source anchors: lines 148-152.
3. Use SWE-agent's ReAct loop with thoughts, commands, execution feedback, and common Linux utilities when needed: ... search, navigate, edit, and execute code commands. The ACI com- prises several principal components, including search/navigation, file viewer, file editor, and context .... Source anchors: lines 173-177.
4. Localize code with LM-friendly search and navigation commands such as find_file, search_file, and search_dir: ... an issue. We introduce the special commands find_file, search_file, and search_dir, which output a summary of search results when searching for filenames and strings within files .... Source anchors: lines 178-182.
5. Inspect code through the file viewer with bounded windows, line numbers, scrolling, and goto: ... that the agent write a more specific query. File viewer. After finding a file they want to view, agents use the interactive file viewer by calling the command open on the .... Source anchors: lines 235-239.
6. Apply focused multiline edits through the edit command and immediately inspect the updated file view: ... with the file viewer, allowing agents to replace a specific range of lines in the open file. This command takes 3 required arguments: the start line, end line, and replacement .... Source anchors: lines 244-248.
7. Use editing guardrails such as linting feedback and discarded invalid edits to avoid error propagation: ... files in an IDE, we integrate a code linter into the edit function to alert the agent of mistakes it may have introduced when editing a file. Select errors from the linter .... Source anchors: lines 250-254.
8. Manage context with command documentation, demonstrations, malformed-response feedback, and collapsed old observations: Context management. The SWE-agent system uses informative prompts, error messages, and history processors to keep agent context concise and informative. Agents receive .... Source anchors: lines 255-259.

## Validation

- Evaluate on SWE-bench full test, SWE-bench Lite, and HumanEvalFix with automated software-engineering metrics: ... Experimental Setup Datasets. We primarily evaluate on the SWE-bench dataset, which includes 2,294 task instances from 12 different repositories of popular Python packages [20]. .... Source anchors: lines 268-272.
- Compare against non-interactive RAG and Shell-only or Basic CLI baselines under the reported settings: Baselines. We compare SWE-agent to two baselines. The first setting is the non-interactive, retrieval- augmented generation (RAG) baselines established in Jimenez et al. [20]. .... Source anchors: lines 287-291.
- Report % Resolved or pass@1, average cost, and the per-instance budget boundary: ... after interaction. Metrics. We report % Resolved or pass@1 as the main metric, which is the proportion of instances for which all tests pass successfully after the model .... Source anchors: lines 294-298.
- Record the main SWE-bench and HumanEvalFix performance numbers as reported references: ... solving 12.47% (286/2,294) of the full SWE-bench test set and 18.00% (54/300) of the Lite split. As shown in Table 1, compared to RAG on Lite, SWE-agent is 8-13x more costly .... Source anchors: lines 309-313.
- Use ACI ablations to separate the effect of editor, search, file viewer, context, and demonstrations: ... 3: SWE-bench Lite performance under ablations to the SWE-agent interface, which is denoted by . We consider different approaches to searching and editing (see Figures 5 and .... Source anchors: lines 366-370.
- Track configuration search over window size, history processing, and decoding temperature: ... edits were submitted automatically. Configuration search. During the design process of SWE-agent, we arrived at the final ACI design through qualitative analysis of .... Source anchors: lines 299-303.

## Failure Cases

- Run generated code in sandboxed or ephemeral containers rather than on an unprotected personal machine: ... framework are both carried out in sand-boxed code environments, which is made possible with Docker. Executing code in a Docker container ensures that its effects are .... Source anchors: lines 7688-7692.
- Verify official repositories and datasets to avoid malicious evaluation infrastructure or injected instructions: ... malicious code or instructions to generate malicious code. For instance, an unofficial repository claiming to host an inference/evaluation harness for SWE-agent/bench could .... Source anchors: lines 7696-7700.
- Do not ignore misuse risks when software-engineering agents can produce offensive or malicious code: ... of software engineering agents being deployed in the real world. Prior works have conceptualized and put forth prototypes of agents that can carry out offensive security .... Source anchors: lines 7703-7707.
- Treat the ACI development process as manually crafted unless an automated interface-design loop is actually implemented: ... in this work, the ACI development process and case studies are done manually. Many components of SWE-agent were crafted from observations of recurring behavior within a .... Source anchors: lines 7737-7741.
- Do not assume ACI principles transfer unchanged beyond programmatic software-engineering and code-generation tasks: ... the scope of SWE-agent is exclusively focused on programmatic tasks like software en- gineering and code generation. Were curious to see whether the same principles of .... Source anchors: lines 7746-7750.
- Watch for editing failure cascades, repeated failed edits, and recovery degradation: ... minority of edit actions raise a linting error; out of 2,294 task instances, 1,185 (51.7%) of SWE-agent w/ GPT-4 Turbo trajectories have 1+ failed edits. While agents .... Source anchors: lines 593-597.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.

# Locked Task Prompt

# SWE-T2 Locked SWE-agent Task Prompt

Task type: failing-test-to-patch

You have a local repository snapshot in the starter workspace. The issue or
failing-test context is:

Modeling's `separability_matrix` does not compute separability correctly for nested CompoundModels
Consider the following model:



```python

from astropy.modeling import models as m

from astropy.modeling.separable import separability_matrix



cm = m.Linear1D(10) & m.Linear1D(5)

```



It's separability matrix as you might expect is a diagonal:



```python

>>> separability_matrix(cm)

array([[ True, False],

       [False,  True]])

```



If I make the model more complex:

```python

>>> separability_matrix(m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5))

array([[ True,  True, False, False],

       [ True,  True, False, False],

       [False, False,  True, False],

       [False, False, False,  True]])

```



The output matrix is again, as expected, the outputs and inputs to the linear models are separable and independent of each other.



If however, I nest these compound models:

```python

>>> separability_matrix(m.Pix2Sky_TAN() & cm)

array([[ True,  True, False, False],

       [ True,  True, False, False],

       [False, False,  True,  True],

       [False, False,  True,  True]])

```

Suddenly the inputs and outputs are no longer separable?



This feels like a bug to me, but I might be missing something?

Verification command:

```powershell
python -m pytest astropy/modeling/tests/test_separable.py::test_separable[compound_model6-result6] astropy/modeling/tests/test_separable.py::test_separable[compound_model9-result9]
```

Return a single unified diff patch. The patch must apply cleanly from the
workspace root. Keep the change minimal, inspect files before editing, and do
not claim success unless the verification command passes.

# Output Contract

Return exactly one unified diff patch. The patch must apply from the starter workspace root and should be minimal.
