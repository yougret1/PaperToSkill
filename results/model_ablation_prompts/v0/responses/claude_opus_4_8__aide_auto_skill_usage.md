# PaperToSkill Model-Ablation Usage Plan

## Context Sufficiency Assessment

**Status:** Sufficient with caveats.

The provided skill context is adequate for planning a code-space search run following AIDE's methodology. The workflow steps are source-backed with line anchors, validation checks reference specific benchmarks and metrics, and failure cases are documented. However, the context is a scaffolded extraction requiring audit against the original paper before production use.

**Gaps:**
- No concrete implementation of the search policy algorithm
- Missing details on the scoring function h : S → R
- Summarization operator ψ(T) mechanics are referenced but not detailed
- No code examples for the coding operator f

## Required Local Resources

### Files
- `papers/auto_notes/aide_auto_note.md` (source paper notes, referenced but not required for execution)
- `generated_skills/aide_auto/SKILL.md` (the provided skill file)
- `workspace/search_run/` (target directory for search artifacts)
- `workspace/search_run/solution_tree.json` (solution tree state)
- `workspace/search_run/logs/` (execution logs, error traces)

### Commands & Tools
- Python 3.8+ interpreter
- JSON parser for solution tree persistence
- File system tools (read, write, search)
- Terminal command execution for running generated scripts
- LLM API client (OpenAI-compatible, base URL https://coderxiaoc.com/v1)

### Simulated APIs
- `search_policy.select_node(tree)` → returns node to refine
- `coding_operator.draft(idea)` → generates Python script
- `coding_operator.debug(script, error_log)` → repairs script
- `coding_operator.improve(script, hint)` → optimizes script
- `objective_function.score(script, output)` → returns scalar score
- `summarization_operator.compress(tree)` → context summary

## Step-by-Step Usage Plan

### Phase 1: Setup (Source-backed)
1. **Frame the problem** as code optimization per workflow step 1
   - Define solution space S as single-file Python scripts
   - Define objective function h that evaluates scripts and returns scalar scores
   - _Source: lines 139-143, 130-134_

2. **Initialize solution tree T**
   - Create root node with initial script or problem statement
   - Set up node structure: {id, script, score, parent, action_taken}
   - Set up edge structure: represents draft/debug/improve transitions
   - _Source: lines 130-134_

3. **Prepare static data preview**
   - Extract dataset size, column names, data splits
   - Include in all coding prompts as static context
   - _Source: lines 212-216_

### Phase 2: Search Loop (Source-backed core, inferred harness)
4. **Select node to refine**
   - Apply search policy to tree T
   - Choose between drafting new solution, debugging failed solution, or improving working solution
   - _Source: lines 219-223_
   - **Inferred adaptation:** Use greedy best-first selection until policy details are available

5. **Apply coding operator**
   - **If drafting:** Generate new script from idea or plan
   - **If debugging:** Inspect error logs and emit repair
   - **If improving:** Apply feature-engineering or optimization hint
   - Keep action atomic and single-file
   - _Source: lines 167-171, 219-223_

6. **Execute and evaluate**
   - Run generated Python script in isolated environment
   - Capture stdout, stderr, and exit code
   - If execution succeeds, apply objective function h
   - If execution fails, capture error traceback
   - _Source: lines 130-134 (implicit in "scalar score")_

7. **Update solution tree**
   - Add new node with script, score (if successful), and error log (if failed)
   - Link to parent with edge labeled by action type
   - _Source: lines 130-134_

8. **Apply summarization operator ψ(T)**
   - Compress tree context to avoid saturating LLM prompt
   - Preserve performance metrics, hyperparameters, debugging hints
   - _Source: lines 201-205_

9. **Check stop conditions**
   - Maximum iterations reached
   - Score threshold exceeded
   - Budget exhausted (time or LLM inference cost)
   - No improvement in last N iterations
   - **Inferred adaptation:** Set N=5 and time budget=30 minutes for initial test runs

10. **If not stopped, return to step 4**

### Phase 3: Output (Inferred from validation section)
11. **Select best solution**
    - Traverse tree T, return node with highest score
    - _Source: lines 130-134 (implicit in solution tree purpose)_

12. **Generate run report**
    - Total nodes explored
    - Best score achieved
    - LLM inference cost estimate
    - Execution time
    - _Source: lines 744-748 (cost tracking), validation sections_

## Source-Backed vs Inferred Adaptations

### Source-Backed (with line anchors)
- Code optimization framing (139-143)
- Solution tree structure (130-134)
- Three action types: draft, debug, improve (219-223)
- Atomic single-file outputs (167-171)
- Summarization operator (201-205)
- Static data preview (212-216)
- Validation benchmarks (241-245, 336-340, 413-417, 461-465, 494-498)
- Failure cases (398-404, 487-491, 499-503, 744-748)

### Inferred Adaptations
- Greedy best-first search policy (paper mentions "simple greedy policy" at 487-491 but no algorithm)
- Node selection tiebreaking rules
- Objective function implementation (only described as h : S → R)
- Summarization compression ratio and mechanics
- Stop condition thresholds (iterations, score, budget)
- Error log parsing format
- Solution tree serialization format

## Validation Checks

### Success Criteria
1. **Tree growth:** At least 5 nodes added to solution tree
2. **Action diversity:** All three action types (draft, debug, improve) attempted
3. **Executable output:** At least one script executes without error
4. **Score improvement:** Best score improves from iteration 1 to iteration N
5. **Context compression:** Summarization operator invoked when tree exceeds size threshold
6. **Static preview:** Data preview appears in all coding prompts

### Stop Conditions
1. Maximum iterations (e.g., 20)
2. Score threshold (domain-specific)
3. Time budget exhausted
4. LLM API failures exceed retry limit
5. No score improvement in 5 consecutive iterations

### Validation Against Paper Benchmarks (for future live runs)
- **Do not claim** Weco-Kaggle scores without running all 63 competitions
- **Do not claim** MLE-Bench medals without submitting to live benchmark harness
- **Do not claim** RE-Bench scores without 6-hour automation runs
- **Do claim** methodology alignment if workflow steps 1-6 are followed

## Likely Failure Branch

### Failure Scenario: Local Optima Trap
**Description:** Search gets stuck refining a mediocre solution instead of exploring alternatives.

**Source backing:** Lines 487-491 identify greedy policy leading to local optima as a known limitation.

**Detection:**
- Best score plateaus for >5 iterations
- All recent actions are "improve" on same node
- Tree has shallow depth (few branches explored)

**Logging:**
```json
{
  "failure_type": "local_optima_trap",
  "evidence": {
    "plateau_iterations": 7,
    "last_actions": ["improve", "improve", "improve", "improve", "improve"],
    "tree_depth": 3,
    "best_score_history": [0.65, 0.67, 0.68, 0.68, 0.68, 0.68, 0.68]
  },
  "timestamp": "2026-01-15T10:23:45Z",
  "recommended_mitigation": "Inject exploration bonus or force draft action"
}
```

**Recovery:**
- Force draft action on new idea
- Add exploration bonus to node selection
- Reset to earlier promising node and branch differently

### Additional Failure Branches

**Data contamination risk** (lines 400-404):
- Cannot rule out training data overlap without live competition submission
- Log: `{"failure_type": "contamination_risk", "benchmark": "static", "mitigation": "note as limitation"}`

**Multi-file codebase failure** (lines 499-503):
- Method assumes single-file scripts; may repeat local patches in larger codebases
- Log: `{"failure_type": "codebase_scope_exceeded", "files_touched": 1, "required_files": >1}`

**LLM cost overrun** (lines 744-748):
- Some tasks incur high inference costs
- Log: `{"failure_type": "budget_exceeded", "cost_usd": X, "budget_usd": Y, "iterations_completed": N}`

## Model Alias Verification Note

**Do not claim** a live run with `claude-opus-4-8` or `gpt-5.5` until:
1. The alias is verified against the provider's current model list via API
2. A response is received and saved under the expected response path
3. The response is scored using the same rubric across all model slots

**Process for adding DeepSeek slot:**
1. Follow the same verification process
2. Add to alias candidates list
3. Run the same usage plan
4. Score against the same rubric

---

**Output status:** Plan complete. No live run performed. No invented results, scores, or unavailable model claims.
