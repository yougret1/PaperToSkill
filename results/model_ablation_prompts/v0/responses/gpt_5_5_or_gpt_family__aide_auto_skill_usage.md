## Sufficiency

The provided `generated_skills/aide_auto/SKILL.md` context is **sufficient to draft an executable usage plan** for applying the AIDE-derived skill to a code-space search harness.

It is **not sufficient to claim a completed live ablation**, verified GPT-family model availability, benchmark scores, provider billing, or paper-faithful reproduction without auditing the cited source file and running/scoring the response under the expected evaluation pipeline.

---

## Required Local Files, Commands, Tools, or Simulated APIs

### Required files

- `generated_skills/aide_auto/SKILL.md`
  - The extracted AIDE skill context.
- `papers/auto_notes/aide_auto_note.md`
  - Source note for auditing source anchors.
- Target task files, for example:
  - `task/README.md`
  - `data/`
  - `starter_code/`
  - `evaluation.py` or equivalent scorer.
- Harness state directory, for example:
  - `runs/aide_search/`
  - `runs/aide_search/solution_tree.json`
  - `runs/aide_search/logs/`
  - `runs/aide_search/candidates/`

### Required tools

- Python runtime.
- Code execution sandbox or container.
- Local evaluator/scorer for objective function `h(script) -> scalar score`.
- Logging system for:
  - generated scripts,
  - execution logs,
  - tracebacks,
  - scores,
  - summaries,
  - failed branches.

### Optional or simulated APIs

- LLM coding operator API:
  - drafting,
  - debugging,
  - improving.
- Model-list API if doing a live GPT-family ablation:
  - `GET /v1/models`
  - Must verify whether `gpt-5.5`, `gpt-5.4`, or another GPT-family alias is actually available before claiming use.
- If unavailable in this environment, record model verification as **pending**, not completed.

---

## Source-Backed Instructions

These steps are directly supported by the provided AIDE skill context.

1. **Frame the task as search over Python scripts**
   - Treat each candidate solution as a Python program.
   - Define an objective function that executes the script and returns a scalar score.
   - Source-backed by workflow item 1.

2. **Maintain a solution tree**
   - Each node represents a candidate script.
   - Each edge represents an edit, draft, debug, or improvement action.
   - Store node metadata:
     - parent node,
     - action type,
     - score,
     - validity,
     - execution log path,
     - summary.
   - Source-backed by workflow item 2.

3. **Use a search policy with three action types**
   - `draft`: create an initial solution.
   - `debug`: repair a failed or invalid solution using logs or tracebacks.
   - `improve`: refine a valid solution to increase score.
   - Source-backed by workflow item 3.

4. **Keep coding actions atomic**
   - Each LLM-generated step should produce one coherent code modification or one new single-file program.
   - Ground debugging actions in executable feedback such as tracebacks.
   - Source-backed by workflow item 4.

5. **Summarize accumulated search context**
   - Preserve:
     - best scores,
     - key implementation choices,
     - hyperparameters,
     - failure causes,
     - debugging hints.
   - Use summaries instead of passing the full tree into every prompt.
   - Source-backed by workflow item 5.

6. **Provide a static data preview before coding**
   - Include:
     - dataset size,
     - column names,
     - train/test split information,
     - target column or output format,
     - example rows if safe and available.
   - Source-backed by workflow item 6.

7. **Track failure modes**
   - Log local optima, repeated patches, invalid submissions, execution failures, and cost/runtime budget issues.
   - Source-backed by failure cases and transfer notes.

---

## Inferred Adaptations for This Harness

These are practical adaptations for the requested code-space search run. They are not directly claimed as paper results.

1. **Use JSON for solution-tree persistence**
   - Store search state in `solution_tree.json`.

2. **Use a fixed run budget**
   - Example limits:
     - maximum candidates: `N`
     - maximum wall-clock time: `T`
     - maximum debug attempts per node: `K`
     - maximum LLM calls or token budget: `B`

3. **Use local scoring instead of benchmark submission**
   - The harness should call a local evaluator rather than claim live Kaggle, MLE-Bench, or RE-Bench results.

4. **Use deterministic candidate execution where possible**
   - Set random seeds.
   - Capture package versions.
   - Save stdout, stderr, traceback, and score.

5. **Use a simple greedy or best-first search policy**
   - Select the highest-scoring valid node for improvement.
   - Select failed but promising nodes for debugging.
   - Record this as an implementation choice and known limitation because the skill notes greedy search can reach local optima.

---

## Step-by-Step Usage Plan

### Step 1: Audit and load the skill

1. Read `generated_skills/aide_auto/SKILL.md`.
2. Optionally cross-check cited anchors in `papers/auto_notes/aide_auto_note.md`.
3. Record in run metadata:

```json
{
  "skill": "aide-auto-paper-skill",
  "skill_file": "generated_skills/aide_auto/SKILL.md",
  "source_file": "papers/auto_notes/aide_auto_note.md",
  "source_audited": false
}
```

Stop condition: if the skill file is missing or the source note cannot be located and source audit is required.

---

### Step 2: Prepare the target task interface

Define the objective function:

```bash
python evaluation.py --candidate runs/aide_search/candidates/node_000.py
```

The evaluator should return or write:

```json
{
  "valid": true,
  "score": 0.731,
  "metric": "local_validation_score",
  "runtime_seconds": 42.0,
  "error": null
}
```

If the script fails, it should return:

```json
{
  "valid": false,
  "score": null,
  "metric": "local_validation_score",
  "runtime_seconds": 3.2,
  "error": "Traceback or failure summary"
}
```

Stop condition: if no objective function exists, do not start AIDE-style search.

---

### Step 3: Create a static data preview

Generate a compact data report:

```bash
python tools/make_data_preview.py \
  --data data/ \
  --out runs/aide_search/data_preview.md
```

The preview should include:

- dataset sizes,
- file names,
- column names,
- target variable,
- split information,
- output/submission format,
- missing-value summary if relevant.

Stop condition: if the task requires data and the harness cannot expose even a minimal data preview.

---

### Step 4: Initialize the solution tree

Create:

```bash
mkdir -p runs/aide_search/candidates
mkdir -p runs/aide_search/logs
```

Initialize `solution_tree.json`:

```json
{
  "nodes": [],
  "best_node_id": null,
  "budget": {
    "max_candidates": 20,
    "max_debug_attempts_per_node": 2,
    "max_runtime_seconds": 7200
  }
}
```

---

### Step 5: Draft the first candidate

Prompt the coding operator with:

- task description,
- static data preview,
- evaluator command,
- expected output format,
- requirement to produce a single Python file.

Save output as:

```text
runs/aide_search/candidates/node_000.py
```

Add node metadata:

```json
{
  "node_id": "node_000",
  "parent_id": null,
  "action": "draft",
  "script_path": "runs/aide_search/candidates/node_000.py",
  "status": "pending_eval"
}
```

---

### Step 6: Execute and score the candidate

Run:

```bash
python evaluation.py \
  --candidate runs/aide_search/candidates/node_000.py \
  > runs/aide_search/logs/node_000.eval.json 2> runs/aide_search/logs/node_000.stderr.log
```

Update the node with:

- valid/invalid status,
- scalar score,
- runtime,
- error message if any,
- log paths.

Stop condition: if the evaluator itself crashes independently of the candidate.

---

### Step 7: Summarize the current tree

Create or update:

```text
runs/aide_search/search_summary.md
```

Include:

- current best node,
- best score,
- valid candidates,
- failed candidates,
- common errors,
- promising implementation ideas,
- known limitations.

This summary should be used in future coding prompts instead of the full raw history.

---

### Step 8: Select next action

Use a simple policy:

1. If no valid solution exists:
   - choose `debug` on the most recent failed node.
2. If a valid solution exists:
   - choose `improve` on the best valid node.
3. Periodically allow a new `draft` to avoid local optima.

Example policy record:

```json
{
  "selected_parent": "node_000",
  "next_action": "debug",
  "reason": "No valid solution exists; node_000 failed with import error."
}
```

---

### Step 9: Generate the next candidate

For a debug action, provide:

- parent script,
- traceback,
- evaluator command,
- data preview,
- search summary,
- instruction to make one atomic repair.

For an improve action, provide:

- best script,
- score,
- metric direction,
- search summary,
- instruction to make one atomic improvement.

Save as:

```text
runs/aide_search/candidates/node_001.py
```

Add an edge in the tree:

```json
{
  "from": "node_000",
  "to": "node_001",
  "action": "debug"
}
```

---

### Step 10: Repeat until budget or stop condition

Loop over:

1. select node/action,
2. generate candidate,
3. execute candidate,
4. score candidate,
5. update tree,
6. summarize.

Stop when any of the following occurs:

- maximum candidates reached,
- wall-clock budget reached,
- LLM-call or token budget reached,
- score target reached,
- repeated local patches detected,
- evaluator unavailable,
- no new valid candidates after configured attempts.

---

## Validation Checks

### Required checks

- Every candidate has:
  - script path,
  - parent ID,
  - action type,
  - execution status,
  - score or failure reason,
  - log path.
- Objective function returns a scalar score for valid candidates.
- Invalid candidates preserve stderr or traceback.
- Best node is selected only from valid scored candidates.
- Search summary reflects the actual tree state.
- No benchmark or live submission result is claimed unless actually run.

### Success criteria

A run is successful if:

1. At least one candidate executes successfully.
2. The solution tree records all attempted candidates.
3. The best valid candidate is identifiable.
4. Logs and summaries are sufficient to reproduce the search path.
5. Source-backed and inferred steps are clearly separated.

### Stop conditions

Stop immediately if:

- the evaluator is missing,
- data required by the task is inaccessible,
- candidate execution is unsafe,
- model alias verification is required for a live ablation but `/v1/models` cannot be checked,
- the harness would need to claim external benchmark results that were not actually produced.

---

## Likely Failure Branch

### Failure: repeated local patches with no score improvement

The AIDE skill notes that greedy search can get stuck in local optima and repeat local patches.

Example log entry:

```json
{
  "event": "failed_branch",
  "branch_root": "node_004",
  "failure_type": "local_optimum_or_repeated_patch",
  "symptoms": [
    "three consecutive improve actions changed minor hyperparameters only",
    "validation score did not improve",
    "candidate summaries repeated same idea"
  ],
  "affected_nodes": ["node_005", "node_006", "node_007"],
  "resolution": "stop improving this branch and start a fresh draft or select a different parent node",
  "source_backing": "AIDE skill failure case: greedy policy may lead to local optima"
}
```

Harness response:

1. Mark the branch as stalled.
2. Do not select the same parent again unless explicitly allowed.
3. Start a new draft or choose another valid node.
4. Preserve the failed branch in the solution tree for future skill revision.

---

## Model-Ablation Metadata Handling

For the GPT-family slot, the harness should not claim `gpt-5.5` usage until the provider model list is checked.

Record metadata like:

```json
{
  "requested_alias": "gpt-5.5",
  "alias_candidates": ["gpt-5.5", "gpt-5.4"],
  "model_list_verified": false,
  "actual_model_alias_used": null,
  "response_status": "pending"
}
```

If `/v1/models` later shows `gpt-5.5`, update:

```json
{
  "model_list_verified": true,
  "actual_model_alias_used": "gpt-5.5"
}
```

If unavailable but another GPT-family model is used, record the actual alias. Do not invent an unavailable alias or completed live results.
