# PaperToSkill Reflexion Retry-and-Reflection Agent Run Plan

## Run Objective

Execute a local Reflexion-inspired retry loop on a small coding task where an Actor generates code, an Evaluator checks correctness, and a Self-Reflection model produces verbal feedback. Store reflections in long-term memory and condition future attempts on both trajectory history and accumulated reflections. Stop when the Evaluator marks the solution correct or maximum trials are reached.

---

## Role Table

| Role | Responsibility | Implementation |
|------|----------------|----------------|
| **Actor** | Generate code solutions conditioned on task, trajectory history (short-term memory), and reflections (long-term memory) | Kiro agent writing code based on task prompt + memory context |
| **Evaluator** | Judge correctness of Actor output using tests, execution, or scoring heuristics | Run unit tests, execute code, check output against expected behavior |
| **Self-Reflection** | Convert Evaluator feedback into verbal reflections explaining what went wrong and how to improve | Kiro agent analyzing failure logs and generating structured reflection text |

---

## Memory Schema

| Memory Type | Content | Persistence | Usage |
|-------------|---------|-------------|-------|
| **Short-term (Trajectory)** | Current trial's attempt: code generated, commands run, test results, execution logs | Cleared after each trial or retained for single retry cycle | Provides immediate context for Self-Reflection |
| **Long-term (Reflections)** | Accumulated verbal reflections from past failed trials | Persisted across all trials in `reflexion_memory.md` | Prepended to Actor's next attempt to guide improvement |

---

## Trial Loop

```
Initialize:
  - task_prompt = coding task specification
  - max_trials = 3
  - long_term_memory = []
  - trial_count = 0

Loop:
  1. trial_count += 1
  2. Actor generates code conditioned on task_prompt + long_term_memory
  3. Save code to file (e.g., `solution_trial_{trial_count}.py`)
  4. Evaluator runs validation:
     - Execute code
     - Run unit tests if available
     - Check output against expected behavior
  5. Collect feedback:
     - If PASS: record success, exit loop
     - If FAIL: capture error messages, test failures, execution logs
  6. Self-Reflection generates verbal reflection from feedback:
     - What failed?
     - Why did it fail?
     - What should change in the next attempt?
  7. Append reflection to long_term_memory
  8. Write reflection to `reflexion_memory.md`
  9. If trial_count >= max_trials: exit loop with failure status

Stop Conditions:
  - Evaluator marks solution correct (PASS)
  - Maximum trials reached
  - Unrecoverable error (e.g., no test framework available)
```

---

## Feedback Source Plan

| Source | Method | Availability |
|--------|--------|--------------|
| **Environment execution** | Run generated code and capture stdout/stderr, exit codes | ✅ Available via terminal commands |
| **Unit tests** | Run project test suite or self-generated tests | ✅ Available if test framework exists or can be created |
| **Heuristic checks** | Syntax validation, linting, type checking | ✅ Available via language-specific tools |
| **Evaluator scoring** | Manual scoring rubric or model-based correctness judgment | ⚠️ Requires explicit rubric or human confirmation |

**Selected approach**: Combine environment execution + unit tests as primary feedback, with heuristic checks as secondary validation.

---

## Validation Plan

### Success Criteria
- Actor generates code that passes all Evaluator checks within max_trials
- At least one reflection is generated and stored in long-term memory
- Each trial's code is saved as a file artifact
- Reflection memory is cumulative and correctly conditioned into next attempt

### Measurable Metrics
- **Pass rate**: Did the final solution pass validation? (binary)
- **Trials to success**: Number of attempts before passing
- **Reflection quality**: Does reflection explain failure cause and suggest actionable improvement? (manual review)
- **Memory usage**: Is long-term memory correctly prepended to Actor's next prompt?

### Failure Recording
- Log each failed trial with:
  - Trial number
  - Generated code snapshot
  - Evaluator feedback (errors, test results)
  - Generated reflection
- Save all logs to `reflexion_experiment_log.md`

---

## Limitations

**Source-backed limitations** (from paper):
- Reflexion can still get stuck in local minima with no formal guarantee of success. Source: lines 76-83, 527-533.
- Memory is limited to a sliding window in the paper; more advanced structures are future work. Source: lines 527-533.
- Some environments remain difficult, especially where creative behavior or richer interaction is required. Source: lines 741-776.

**Harness-specific limitations**:
- No access to ALFWorld, HotPotQA, or HumanEval environments from the paper's validation.
- Actor and Self-Reflection are implemented as Kiro agent responses, not separate fine-tuned models.
- Evaluator is limited to local test execution and heuristic checks, not a trained reward model.
- Long-term memory is implemented as markdown file persistence, not vector embeddings or retrieval.
- Maximum trials is set to 3 for local testing; paper experiments used up to 12 iterations.
- No formal metrics (22% ALFWorld improvement, 91% HumanEval pass@1) can be claimed without reproducing paper benchmarks.

---

## Transfer Adaptation Note

**What changed for the Codex harness**:
- **Actor/Evaluator/Self-Reflection roles** preserved, but implemented as Kiro agent capabilities (code generation, test execution, feedback analysis) rather than separate models.
- **Short-term and long-term memory** preserved, but stored as local files (`reflexion_memory.md`, trial logs) instead of in-framework memory buffers.
- **Feedback sources** adapted from paper's environment rewards to local test execution and error logs.
- **Validation metrics** adapted from paper benchmarks (ALFWorld, HotPotQA, HumanEval) to local task completion and reflection quality.
- **Retry policy** preserved (iterate until success or max trials), but max_trials reduced from paper's 12 to 3 for local testing.
- **Paper-backed workflow steps** (lines 189-193, 201-217, 244-255, 257-266, 269-276) are preserved in the trial loop structure.

**What remains source-backed**:
- Core method: verbal reinforcement instead of weight updates.
- Memory distinction: trajectory (short-term) vs. reflections (long-term).
- Trial loop: Actor → Evaluator → Self-Reflection → Memory update → Retry.
- Feedback conversion: turn environment signals into actionable verbal reflections.

**What is harness-specific**:
- File-based memory persistence.
- Local test execution as Evaluator.
- Kiro agent as unified Actor/Self-Reflection implementation.
- No live comparison to paper's reported metrics.
