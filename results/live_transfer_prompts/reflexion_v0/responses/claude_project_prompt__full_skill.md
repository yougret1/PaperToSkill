# PaperToSkill Retry-and-Reflection Agent Run Plan

## Run Objective

Execute a local Reflexion-inspired retry loop on a small coding or reasoning task. The agent will attempt the task, collect feedback, generate a verbal self-reflection, store it in long-term memory, and retry with the accumulated reflections in context until success or max trials are reached.

## Role Table

| Role | Responsibility |
|------|----------------|
| **Actor** | Generate task attempts (code, reasoning steps, or actions) conditioned on short-term trajectory history and long-term reflection memory. |
| **Evaluator** | Score each attempt using available feedback sources: test execution results, heuristic checks, or explicit correctness validation. |
| **Self-Reflection** | Analyze failed attempts and evaluator feedback to produce verbal reflections that diagnose errors and suggest alternative approaches. Store reflections in long-term memory. |

## Memory Schema

| Memory Type | Content | Persistence |
|-------------|---------|-------------|
| **Short-term (trajectory history)** | Current trial's action sequence, intermediate states, and immediate feedback. Resets each trial. | Cleared between trials |
| **Long-term (reflection memory)** | Accumulated self-reflections from all previous failed trials. Each reflection includes: the failed approach, observed error, and hypothesized fix. | Persists across trials |

## Trial Loop

```
1. Actor generates attempt, conditioned on long-term reflection memory
2. Evaluator collects feedback:
   - Execute code/tests if available
   - Apply heuristic checks (syntax, format, constraint satisfaction)
   - Compare output to expected result
3. If evaluator marks attempt correct:
   - Log success, record trial count, exit loop
4. If evaluator marks attempt incorrect:
   - Self-Reflection analyzes failure and generates verbal reflection
   - Append reflection to long-term memory
   - If trial count < max_trials (default: 12):
     - Retry from step 1
   - Else:
     - Log failure, record final state, exit loop
```

## Feedback-Source Plan

**Available sources** (descending preference):
1. **Environment feedback**: Execute code and capture test results, runtime errors, or assertion failures.
2. **Self-generated tests**: Actor writes unit tests for the task; evaluator runs them.
3. **Heuristic scoring**: Check syntax validity, length constraints, format compliance, or keyword presence.
4. **Evaluator LLM scoring**: Ask evaluator to judge correctness when executable feedback is unavailable.

**For this run**: Use file editing tools to write code, terminal commands to execute tests, and parse output for pass/fail signals. Fall back to heuristic checks if execution is blocked.

## Validation Plan

**Success criteria** (one must be met):
- All test cases pass within max_trials attempts.
- Evaluator confirms correctness using ground-truth comparison.
- Task-specific metric (e.g., HumanEval pass@1, exact-match accuracy) exceeds baseline.

**Failure recording**:
- Log trial number, attempted solution, feedback received, and generated reflection for each failed attempt.
- Record whether failure was due to max-trial limit, persistent error, or environment constraint.
- Track whether reflections converged (repeated similar diagnoses) indicating local minima.

**Measurable outcomes**:
- Success rate over N task samples.
- Average trials-to-success for solved tasks.
- Reflection quality: whether reflections correctly diagnosed the error category.

## Limitations

**Copied from source-backed skill**:
- Reflexion can get stuck in local minima with no formal guarantee of success. (Source: lines 76-83, 527-533)
- Memory uses a sliding window; more advanced retrieval structures are suggested for future work. (Source: lines 527-533)
- Some tasks remain difficult where creative behavior or richer interaction is required. (Source: lines 741-776)

**Harness-specific limitations**:
- No interactive environment scaffolding (ALFWorld, WebShop) available; limited to local code execution and file manipulation.
- Cannot reproduce paper's exact HotPotQA or HumanEval benchmarks without dataset access and evaluation harness setup.
- Self-reflection quality depends on LLM capability; no separate trained reflection model.
- Sliding-window memory implemented as simple text buffer; no semantic retrieval or episodic memory compression.

## Transfer-Adaptation Note

**What changed for Claude-style project prompt harness**:

1. **Replaced framework-specific commands**: Paper assumes external environments (ALFWorld, WebShop). Adapted to use file editing tools and terminal commands available in this harness.

2. **Simplified feedback pipeline**: Paper uses gym-style environments with reward signals. Here, feedback comes from test execution output parsing or heuristic checks since interactive RL environments are unavailable.

3. **Unified Actor/Evaluator/Self-Reflection into single agent**: Paper implies separate model calls or prompting stages. This harness uses one LLM performing all three roles through structured prompting and tool use.

4. **Memory as text buffer**: Paper's sliding window is implemented as a plaintext reflection log passed in context. No external memory store or retrieval mechanism.

5. **Task scope narrowed**: Instead of full decision-making or web navigation tasks, this run targets small local coding or reasoning problems that can be validated with file I/O and command execution.

6. **No weight updates or RL training**: Paper's "verbal reinforcement learning" is preserved as reflection-based prompting, but the harness has no model fine-tuning capability.

**Preserved source-backed steps**:
- Actor conditions on long-term reflection memory.
- Evaluator scores each attempt and triggers reflection generation on failure.
- Self-Reflection produces verbal analysis stored persistently.
- Trial loop continues until success or max-trials limit.
