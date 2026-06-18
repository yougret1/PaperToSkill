# PaperToSkill Retry-and-Reflection Agent Run Plan

## Run Objective

Build and execute a local Reflexion-inspired coding agent that attempts a programming task, collects feedback from test failures or linting, generates natural-language reflection on what went wrong, stores reflections in memory, and retries the task using accumulated lessons—demonstrating measurable improvement across trials.

---

## Role Table

| Role | Responsibility |
|------|----------------|
| **Actor** | Generates or modifies code to solve the programming task. Reads long-term reflection memory before each attempt. Produces executable artifacts (source files, tests, configs). |
| **Evaluator** | Runs tests, linters, type checkers, or build commands. Scores the attempt (pass/fail, test count, error messages). Returns structured feedback to Self-Reflection. |
| **Self-Reflection** | Converts Evaluator feedback into natural-language lessons. Identifies root causes (logic errors, missing edge cases, incorrect assumptions). Writes actionable advice for the next trial. |

---

## Memory Schema

### Short-Term Memory (Trajectory History)
- **Scope:** Current trial only
- **Contents:** Code written, commands executed, test outputs, error logs
- **Format:** Chronological execution log per trial
- **Lifetime:** Cleared at trial start; preserved in trial archive after reflection

### Long-Term Memory (Reflection Memory)
- **Scope:** Across all trials
- **Contents:** Natural-language reflections from previous failures, patterns identified, strategies that failed, constraints discovered
- **Format:** Numbered reflection entries with trial ID, failure reason, lesson learned
- **Lifetime:** Persists and accumulates; Actor reads before each new attempt
- **Storage:** `reflexion_memory.md` markdown file with structured entries

---

## Trial Loop

```
FOR trial = 1 TO max_trials:
  1. Actor reads long-term reflection memory
  2. Actor generates/modifies code for the task
  3. Evaluator runs validation (tests, linters, build)
  4. Evaluator collects feedback (pass/fail, error messages, metrics)
  
  IF success criteria met:
    STOP: Task complete
  
  5. Self-Reflection converts feedback to natural-language lesson
  6. Self-Reflection appends lesson to long-term memory
  7. Short-term trajectory archived to trial log
  
  IF retry conditions met:
    CONTINUE to next trial
  ELSE:
    STOP: Max trials exhausted or stuck pattern detected
```

---

## Feedback Source Plan

### Primary Sources (executable locally)
- **Unit tests:** Run project test suite; collect pass/fail counts and failure messages
- **Linters/formatters:** Run language-specific linters (eslint, pylint, clippy); collect rule violations
- **Type checkers:** Run TypeScript tsc, mypy, etc.; collect type errors
- **Build commands:** Run compile/build steps; collect compilation errors

### Heuristic Scoring
- **Binary:** Task passes all tests = success; any test failure = retry
- **Progressive:** Count of passing tests as improvement signal across trials
- **Error pattern matching:** Detect repeated error messages indicating stuck loops

### Self-Generated Tests
- If task lacks tests, Actor generates basic test cases in trial 1
- Evaluator validates against these self-generated tests in subsequent trials

### Unavailable (limitations)
- No external human evaluation or LLM-as-judge scoring in this local harness
- No interactive environment feedback (e.g., web browser, simulator state)

---

## Validation Plan

### Success Criteria (stop conditions)
- All unit tests pass
- No linter errors
- Build completes successfully
- Task requirements document satisfied (manual checklist if needed)

### Failure Recording
- **Per-trial log:** `trial_N_log.md` with code snapshot, commands run, full error output
- **Reflection entry:** `reflexion_memory.md` appended with trial N reflection
- **Metrics tracked:**
  - Test pass count per trial
  - Unique error types encountered
  - Number of reflections accumulated
  - Trial at which success achieved (or failure after max trials)

### Measurable Improvement Signal
- Increase in passing test count across trials
- Reduction in repeated error messages
- Successful completion in fewer trials than baseline (no reflection)

---

## Limitations

### Source-Backed (from paper)
- Agents can still get stuck repeating similar mistakes despite reflections
- Memory is bounded by context window; simple sliding window does not scale to very long task histories
- Some tasks require more creative exploration than verbal reinforcement reliably discovers
- Reflection quality depends on the richness of feedback; sparse or ambiguous error messages limit improvement

### Harness-Specific Adaptations
- **No weight updates:** Reflexion uses verbal feedback, not gradient updates—preserved in this plan
- **Local execution only:** No multi-agent environments, web tasks, or external APIs
- **Synchronous trials:** No parallel exploration; each trial completes before the next starts
- **Manual task scoping:** User must provide a well-defined programming task with testable success criteria
- **No human-in-the-loop:** Evaluator is fully automated; no manual scoring or human feedback injection
- **Context budget:** Long reflection memory may exceed context limits on very long runs; manual summarization may be needed

---

## Transfer-Adaptation Note

**What changed for the Codex harness:**

1. **Task domain:** Original paper tested decision-making (AlfWorld), reasoning (HotPotQA), and programming (HumanEval). This plan focuses exclusively on **local programming tasks** executable in a development environment.

2. **Feedback mechanism:** Paper used environment rewards, question-answering accuracy, and test case pass rates. This plan uses **linters, type checkers, unit tests, and build output**—tools native to software development.

3. **Memory implementation:** Paper's memory was context-injected text. This plan uses a **persistent markdown file** (`reflexion_memory.md`) that survives across trials and can be version-controlled.

4. **Evaluator scope:** Paper's evaluator was task-specific (RL reward, QA score, unit test). This plan's Evaluator is a **multi-tool orchestrator** (runs tests, linters, build) and aggregates signals.

5. **Reflection generation:** Paper used a separate LLM call for self-reflection. This plan treats Self-Reflection as a **sub-role within the same agent**, generating reflections inline after Evaluator feedback.

6. **Retry policy:** Paper used fixed trial budgets. This plan adds **early stopping on repeated errors** (stuck detection) and **success-on-first-pass** (if task is trivial).

7. **Validation:** Paper reported aggregate metrics over benchmark datasets. This plan produces **single-task trial logs** with per-attempt forensics, suitable for debugging and learning from individual runs.

**What was preserved:**
- Actor/Evaluator/Self-Reflection role separation
- Short-term trajectory vs. long-term reflection memory distinction
- Feedback-to-reflection conversion as the core learning mechanism
- Retry loop with memory-informed attempts
- No model weight updates (verbal reinforcement only)
- Acknowledgment of stuck-loop and sparse-feedback limitations
