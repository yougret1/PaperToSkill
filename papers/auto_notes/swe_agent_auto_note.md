# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

## Source

- Paper ID: `swe_agent`
- Extracted text: `papers/extracted/swe_agent.txt`
- Extraction notes: Automatic deterministic scaffold from extracted text. It
  should be audited against the paper before being treated as validated paper
  knowledge.

## Abstract

... performance of language model agents. As a result of this exploration, we introduce SWE-agent: a system that facilitates LM agents to autonomously use computers to solve software engineering tasks. SWE-agents custom agent-computer interface (ACI) significantly enhances an agents ability to ...

Source anchors: lines 14-32.

## Methods

1. Frame the method as an agent-computer interface that shapes commands, documentation,
   state, history, and feedback: ... back to the LM. It also tracks the history of all
   previous commands and observations and, at each step, manages how these should be
   formatted and combined with .... Source anchors: lines 135-139.
2. Keep ACI actions simple, compact, efficient, and paired with concise environment
   feedback: ... Actions should be simple and easy to understand for agents. Many bash
   commands have documentation that includes dozens of options. Simple commands with a
   few options and .... Source anchors: lines 148-152.
3. Use SWE-agent's ReAct loop with thoughts, commands, execution feedback, and common
   Linux utilities when needed: ... search, navigate, edit, and execute code commands.
   The ACI com- prises several principal components, including search/navigation, file
   viewer, file editor, and context .... Source anchors: lines 173-177.
4. Localize code with LM-friendly search and navigation commands such as find_file,
   search_file, and search_dir: ... an issue. We introduce the special commands
   find_file, search_file, and search_dir, which output a summary of search results when
   searching for filenames and strings within files .... Source anchors: lines 178-182.
5. Inspect code through the file viewer with bounded windows, line numbers, scrolling,
   and goto: ... that the agent write a more specific query. File viewer. After finding
   a file they want to view, agents use the interactive file viewer by calling the
   command open on the .... Source anchors: lines 235-239.
6. Apply focused multiline edits through the edit command and immediately inspect the
   updated file view: ... with the file viewer, allowing agents to replace a specific
   range of lines in the open file. This command takes 3 required arguments: the start
   line, end line, and replacement .... Source anchors: lines 244-248.
7. Use editing guardrails such as linting feedback and discarded invalid edits to avoid
   error propagation: ... files in an IDE, we integrate a code linter into the edit
   function to alert the agent of mistakes it may have introduced when editing a file.
   Select errors from the linter .... Source anchors: lines 250-254.
8. Manage context with command documentation, demonstrations, malformed-response
   feedback, and collapsed old observations: Context management. The SWE-agent system
   uses informative prompts, error messages, and history processors to keep agent
   context concise and informative. Agents receive .... Source anchors: lines 255-259.

## Experiments

- Evaluate on SWE-bench full test, SWE-bench Lite, and HumanEvalFix with automated
  software-engineering metrics: ... Experimental Setup Datasets. We primarily evaluate
  on the SWE-bench dataset, which includes 2,294 task instances from 12 different
  repositories of popular Python packages [20]. .... Source anchors: lines 268-272.
- Compare against non-interactive RAG and Shell-only or Basic CLI baselines under the
  reported settings: Baselines. We compare SWE-agent to two baselines. The first setting
  is the non-interactive, retrieval- augmented generation (RAG) baselines established in
  Jimenez et al. [20]. .... Source anchors: lines 287-291.
- Report % Resolved or pass@1, average cost, and the per-instance budget boundary: ...
  after interaction. Metrics. We report % Resolved or pass@1 as the main metric, which
  is the proportion of instances for which all tests pass successfully after the model
  .... Source anchors: lines 294-298.
- Record the main SWE-bench and HumanEvalFix performance numbers as reported references:
  ... solving 12.47% (286/2,294) of the full SWE-bench test set and 18.00% (54/300) of
  the Lite split. As shown in Table 1, compared to RAG on Lite, SWE-agent is 8-13x more
  costly .... Source anchors: lines 309-313.
- Use ACI ablations to separate the effect of editor, search, file viewer, context, and
  demonstrations: ... 3: SWE-bench Lite performance under ablations to the SWE-agent
  interface, which is denoted by . We consider different approaches to searching and
  editing (see Figures 5 and .... Source anchors: lines 366-370.
- Track configuration search over window size, history processing, and decoding
  temperature: ... edits were submitted automatically. Configuration search. During the
  design process of SWE-agent, we arrived at the final ACI design through qualitative
  analysis of .... Source anchors: lines 299-303.

## Limitations

- Run generated code in sandboxed or ephemeral containers rather than on an unprotected
  personal machine: ... framework are both carried out in sand-boxed code environments,
  which is made possible with Docker. Executing code in a Docker container ensures that
  its effects are .... Source anchors: lines 7688-7692.
- Verify official repositories and datasets to avoid malicious evaluation infrastructure
  or injected instructions: ... malicious code or instructions to generate malicious
  code. For instance, an unofficial repository claiming to host an inference/evaluation
  harness for SWE-agent/bench could .... Source anchors: lines 7696-7700.
- Do not ignore misuse risks when software-engineering agents can produce offensive or
  malicious code: ... of software engineering agents being deployed in the real world.
  Prior works have conceptualized and put forth prototypes of agents that can carry out
  offensive security .... Source anchors: lines 7703-7707.
- Treat the ACI development process as manually crafted unless an automated
  interface-design loop is actually implemented: ... in this work, the ACI development
  process and case studies are done manually. Many components of SWE-agent were crafted
  from observations of recurring behavior within a .... Source anchors: lines 7737-7741.
- Do not assume ACI principles transfer unchanged beyond programmatic
  software-engineering and code-generation tasks: ... the scope of SWE-agent is
  exclusively focused on programmatic tasks like software en- gineering and code
  generation. Were curious to see whether the same principles of .... Source anchors:
  lines 7746-7750.
- Watch for editing failure cascades, repeated failed edits, and recovery degradation:
  ... minority of edit actions raise a linting error; out of 2,294 task instances, 1,185
  (51.7%) of SWE-agent w/ GPT-4 Turbo trajectories have 1+ failed edits. While agents
  .... Source anchors: lines 593-597.

## Transfer Notes

- Treat this file as an audit scaffold, not a final skill.
- Keep each generated skill instruction tied to source anchors or mark it as an
  inference.
- Save the JSON selection report or generated skill source map with the skill so
  later audits can trace each line range.
- Re-run source-span validation after converting this note into `SKILL.md`.
- Compare the resulting skill against any curated note before using it in a
  live agent workflow.
