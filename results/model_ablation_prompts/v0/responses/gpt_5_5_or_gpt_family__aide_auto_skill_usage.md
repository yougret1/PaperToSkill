**Sufficiency**

The context is sufficient to produce an executable usage plan for applying the AIDE skill to a code-space search run. It is not sufficient to claim a completed model ablation, live GPT-5.5 run, provider billing, benchmark score, or model availability. The `gpt-5.5` alias must be verified against the provider model list before any live GPT-family response is claimed.

**Required Files, Commands, Tools, APIs**

Required local files:

- `generated_skills/aide_auto/SKILL.md`
- `papers/auto_notes/aide_auto_note.md`
- Target task specification for the code-space search run
- Harness configuration for running candidate Python scripts
- Output directory for solution nodes, logs, summaries, and scores

Required tools or commands:

- File search/read tools, for example `rg`, `sed`, or equivalent
- A script execution harness, for example:
  ```bash
  python candidate.py
  ```
- A scoring command or callable objective function, for example:
  ```bash
  python score.py --submission outputs/submission.csv
  ```
- A logging location for:
  - generated candidate scripts
  - execution logs
  - tracebacks
  - scalar scores
  - solution-tree metadata
  - run summaries

Simulated or live APIs:

- For a live GPT-family ablation run, use OpenAI Responses API:
  ```text
  POST /v1/responses
  ```
- Before claiming use of `gpt-5.5`, query the provider model list and confirm that `gpt-5.5` is available.
- If `gpt-5.5` is unavailable but another configured GPT-family candidate such as `gpt-5.4` is available, record the actual model alias used in response metadata.

**Source-Backed Instructions**

These steps come directly from the supplied AIDE skill context:

1. Frame the target task as a search over Python-script solution space with an objective function.

2. Represent the run as a solution tree:
   - each node is a candidate script
   - each edge is a transformation from a previous script
   - each node stores execution status, score, and logs
   - the best solution is selected by scalar objective score

3. Use a search policy that chooses among:
   - drafting a new solution
   - debugging a failed or invalid solution
   - improving a valid scored solution

4. Keep coding actions atomic:
   - one candidate script per action
   - one clear intended change per refinement
   - debugging should be grounded in concrete logs or tracebacks

5. Maintain a summarization operator over the solution tree:
   - best score so far
   - relevant hyperparameters
   - execution errors
   - debugging hints
   - promising and unpromising branches

6. Provide a static data or code preview before candidate generation:
   - dataset size if applicable
   - column names or file layout if applicable
   - train/test split information if applicable
   - relevant repository structure for a code-space search task

7. Track failure cases:
   - local optima from greedy search
   - repeated local patches
   - transfer limits for larger codebases
   - inference cost or budget exhaustion
   - contamination risk if benchmark data may overlap training corpora

**Inferred Adaptations**

These are adaptations for the requested harness usage, not directly completed evidence from the paper:

1. Treat each candidate implementation as a node stored on disk, for example:
   ```text
   runs/aide_search/nodes/0001/candidate.py
   runs/aide_search/nodes/0001/metadata.json
   runs/aide_search/nodes/0001/stdout.log
   runs/aide_search/nodes/0001/stderr.log
   ```

2. Use a JSON metadata record per node:
   ```json
   {
     "node_id": "0001",
     "parent_id": null,
     "action": "draft",
     "model": "actual_model_alias_here",
     "status": "pending|ran|failed|scored",
     "score": null,
     "objective_direction": "maximize",
     "artifacts": {
       "script": "candidate.py",
       "stdout": "stdout.log",
       "stderr": "stderr.log"
     }
   }
   ```

3. Use a fixed run budget:
   - maximum nodes
   - maximum wall-clock time
   - maximum failed attempts
   - maximum model calls
   - optional cost cap if live API pricing is available

4. Use deterministic local commands where possible:
   ```bash
   python candidate.py
   python score.py --run-dir runs/aide_search/nodes/0001
   ```

5. For non-ML code-space search, replace the data preview with a repository preview:
   ```bash
   rg --files
   rg "TODO|FIXME|error|score|eval|test"
   ```
   Then summarize relevant files, entrypoints, tests, and scoring hooks.

**Step-By-Step Usage Plan**

1. Load the skill context from:
   ```text
   generated_skills/aide_auto/SKILL.md
   ```

2. Read the source note for auditability:
   ```text
   papers/auto_notes/aide_auto_note.md
   ```

3. Initialize a run directory:
   ```text
   runs/aide_search/
   ```

4. Capture the target task definition:
   - objective
   - allowed files
   - runtime limits
   - scoring function
   - expected output artifacts

5. Build a static preview for the model prompt:
   - repository or dataset structure
   - key entrypoints
   - available tests
   - scoring command
   - constraints

6. Verify the GPT-family model alias before a live run:
   - query provider model list
   - prefer `gpt-5.5` if available
   - otherwise use an available configured GPT-family model such as `gpt-5.4`
   - record the actual alias in metadata

7. Start the solution tree with a draft action:
   - generate one candidate Python script or patch
   - save it as node `0001`
   - record parent as `null`
   - record action as `draft`

8. Execute the candidate through the harness:
   ```bash
   python candidate.py
   ```

9. Score the candidate if execution succeeds:
   ```bash
   python score.py --run-dir runs/aide_search/nodes/0001
   ```

10. Store logs and score:
   - stdout
   - stderr
   - traceback if any
   - scalar score if available
   - validity status

11. Update the solution-tree summary:
   - best valid node
   - failed nodes
   - recurring errors
   - promising improvements
   - known constraints

12. Select the next action:
   - `debug` if the best available candidate failed execution
   - `improve` if a valid candidate exists and the run budget remains
   - `draft` if the current branch is unpromising or stuck

13. Generate exactly one atomic change for the next node.

14. Repeat execution, scoring, logging, and summarization until a stop condition is met.

15. At the end, emit a final run report with:
   - actual model alias used
   - number of nodes attempted
   - best node ID
   - best score if produced by the local scorer
   - failed branches
   - stop condition
   - source-backed versus inferred method notes

**Validation Checks**

A run is valid only if:

- The model alias used was verified before the live call.
- Each candidate node has a saved script or patch.
- Each executed node has stdout/stderr logs.
- Each scored node has a scalar score from the declared scoring function.
- The solution tree records parent-child relationships.
- Debugging actions cite concrete error logs or tracebacks.
- Improvement actions cite the prior node and intended objective improvement.
- The final report does not claim benchmark results unless the benchmark was actually run.
- The final report does not claim live competition submission unless such submission actually occurred.

**Stop Conditions**

Stop the run when any of the following occurs:

- Node budget is exhausted.
- Wall-clock budget is exhausted.
- API/model budget is exhausted.
- No valid candidate is produced after the configured failure limit.
- The best score reaches a predefined target.
- The search repeats equivalent local patches without score improvement.
- Required local files, scorer, or execution harness are missing.
- The requested model alias cannot be verified and no approved fallback is available.

**Likely Failure Branch**

Failure branch: generated candidate crashes during execution.

How to log it:

```json
{
  "node_id": "0003",
  "parent_id": "0001",
  "action": "debug",
  "status": "failed",
  "score": null,
  "failure_type": "runtime_error",
  "stderr_path": "runs/aide_search/nodes/0003/stderr.log",
  "traceback_summary": "ImportError or task-specific runtime error from candidate execution",
  "next_policy_decision": "debug_from_traceback"
}
```

Required handling:

- Do not score the node unless the scorer supports failed submissions.
- Feed the traceback into the next debugging prompt.
- Keep the next coding action atomic.
- If similar failures repeat beyond the configured limit, stop or branch back to a fresh draft.

**Model-Ablation Metadata Status**

```json
{
  "model_slot": "gpt_5_5_or_gpt_family",
  "requested_alias": "gpt-5.5",
  "provider_status": "configured_from_local_api_docs",
  "api_path": "/v1/responses",
  "response_status": "pending",
  "actual_model_alias_used": null,
  "alias_verified": false,
  "completed_live_run": false,
  "scored_by_rubric": false
}
```
