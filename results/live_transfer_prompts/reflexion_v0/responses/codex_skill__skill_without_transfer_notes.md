# PaperToSkill Reflexion Live Transfer Plan

## Run Objective

Demonstrate a Reflexion-style retry-and-reflection loop on a small local coding task. The agent will attempt to solve a programming problem, collect feedback (via test execution or self-evaluation), generate a verbal self-reflection, store it in memory, and retry with the reflection as context. The run stops after success or a max-trial budget.

---

## Role Table

| Role | Responsibility |
|------|----------------|
| **Actor** | Generates code or solution attempts using current short-term trajectory and long-term reflection memory as context |
| **Evaluator** | Scores the trajectory using test execution, static checks, or heuristic validation; provides binary success/fail signal and diagnostic feedback |
| **Self-Reflection** | Converts evaluator feedback and trajectory into a verbal reflection describing what went wrong, why, and what to try next; stores reflection in long-term memory |

---

## Memory Schema

| Memory Type | Content | Lifecycle |
|-------------|---------|-----------|
| **Short-term (trajectory history)** | Current trial's actions, intermediate outputs, and evaluator feedback | Cleared or summarized between trials |
| **Long-term (reflection memory)** | Accumulated verbal self-reflections from prior failed trials | Persists across trials; used as conditioning context for Actor |

---

## Trial Loop

```
for trial in 1..max_trials:
  1. Actor generates solution conditioned on long-term reflection memory
  2. Evaluator runs validation (tests, checks, heuristics)
  3. If success → stop with success
  4. If failure:
     a. Collect feedback (error logs, test failures, diagnostic output)
     b. Self-Reflection converts feedback into verbal reflection
     c. Append reflection to long-term memory
     d. Clear or summarize short-term trajectory
  5. If trial == max_trials → stop with failure

Record: trial count, final success/fail, reflection history, final artifact
```

**Retry condition**: Evaluator returns failure AND trial < max_trials  
**Stop condition**: Evaluator returns success OR trial == max_trials

---

## Feedback-Source Plan

| Source | Description | Implementation |
|--------|-------------|----------------|
| **Environment feedback** | Test execution output (pass/fail, error messages) | Run tests via CLI, capture stdout/stderr |
| **Heuristic checks** | Linting, static analysis, code formatting | Run linters/formatters, check exit code |
| **Self-generated tests** | Actor writes tests alongside solution | Execute actor-generated test file |
| **Evaluator scoring** | LLM-based qualitative review of correctness, clarity, edge cases | Actor or separate LLM call scores solution against requirements |

For this local run, **test execution** is the primary feedback source. Heuristics and self-generated tests are optional secondary checks.

---

## Validation Plan

**Success criteria** (measurable):
- All tests pass (exit code 0)
- Solution file is syntactically valid (no parse errors)
- Reflection memory is non-empty after first failure (confirms reflection generation)

**Failure recording**:
- Log trial number, evaluator feedback, generated reflection, and code snapshot per trial
- Final report: total trials, success/fail status, reflection count, last error message

**Validation script**:
```bash
# After each trial:
python solution.py && echo "PASS" || echo "FAIL"
# Check reflection.log for new entry
# Aggregate results in trial_log.json
```

---

## Limitations

**Source-backed** (from paper):
- No formal guarantee of success; agent can still get stuck in local minima (lines 76-83, 527-533)
- Memory component is limited to a sliding window; more advanced structures not implemented (lines 527-533)
- Difficult tasks requiring creative behavior or richer interaction may fail (lines 741-776)

**Harness-specific**:
- No multi-environment orchestration (ALFWorld, HotPotQA) — limited to single local coding task
- No multi-model Actor/Evaluator separation — single LLM plays all roles with prompt engineering
- No external scoring API or human evaluation — relies on automated test execution
- Max trial budget is small (e.g., 3–5 trials) due to context and time constraints
- Reflection quality depends on feedback richness; sparse errors may yield shallow reflections

---

## Transfer-Adaptation Note

**What changed for Codex harness**:

1. **Single-LLM simplification**: Original paper uses separate Actor, Evaluator, and Self-Reflection models. This plan uses one LLM (me) prompted to take on each role sequentially within a trial.

2. **Local file-based memory**: Long-term reflection memory is stored in `reflections.log` (plain text, one reflection per line). Short-term trajectory is stored in `trial_N/` directories with code snapshots and logs.

3. **Test-driven feedback**: Original paper evaluates on environments (ALFWorld), QA benchmarks (HotPotQA), and programming benchmarks (HumanEval). This plan uses local test execution (pytest, unittest, or simple assert-based scripts) as the evaluator signal.

4. **Small trial budget**: Original paper runs 12 iterative steps on decision tasks, multi-step reasoning chains, and programming suites. This plan caps at 3–5 trials for a single small problem (e.g., "implement a function that X").

5. **No baseline comparison**: Original paper reports improvements over ReAct, CoT baselines. This plan is a single-run demonstration, not a comparative evaluation.

**Preserved from paper**:
- Actor/Evaluator/Self-Reflection role separation (prompt-level)
- Short-term trajectory + long-term reflection memory distinction
- Feedback → verbal reflection → retry loop structure
- Multi-source feedback compatibility (tests, heuristics, self-eval)

---

## Example Run Artifact Structure

```
reflexion_run/
├── problem.md               # Task description
├── reflections.log          # Long-term memory (one reflection per trial)
├── trial_1/
│   ├── solution.py
│   ├── test_output.txt
│   └── evaluator_feedback.txt
├── trial_2/
│   ├── solution.py
│   ├── test_output.txt
│   └── evaluator_feedback.txt
├── trial_3/
│   ├── solution.py
│   ├── test_output.txt
│   └── evaluator_feedback.txt
└── run_report.json          # Final trial count, success/fail, reflection count
```

---

**No live experiments were executed.** This plan is a harness-ready scaffold for a future run.
