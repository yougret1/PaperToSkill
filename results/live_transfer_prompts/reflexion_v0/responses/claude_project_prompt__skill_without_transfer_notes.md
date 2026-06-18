# PaperToSkill Retry-and-Reflection Agent Run Plan

## Run Objective

Execute a local retry-and-reflection loop inspired by Reflexion to solve a coding or reasoning task. The agent will attempt the task, collect feedback, generate verbal self-reflections, store them in memory, and retry with improved context until success or maximum trials are reached.

## Role Table

| Role | Responsibility |
|------|----------------|
| **Actor** | Generate task attempts (code, reasoning chains, or action sequences) conditioned on current trajectory and accumulated reflections from long-term memory. |
| **Evaluator** | Score each attempt using available feedback sources: test execution results, heuristic checks, self-generated unit tests, or explicit correctness validation. |
| **Self-Reflection** | Convert feedback into verbal reflections that diagnose what went wrong, why, and what to try differently. Store reflections in long-term memory for future trials. |

## Memory Schema

| Memory Type | Contents | Persistence |
|-------------|----------|-------------|
| **Short-term** | Current trial's trajectory: task description, attempt, feedback, and reflection for this iteration only. | Cleared between trials. |
| **Long-term** | Accumulated self-reflections from previous trials, indexed by attempt number. Used to condition future Actor prompts. | Persists across all trials until task completion or failure. |

## Trial Loop

```
for trial in 1..max_trials:
  1. Actor generates attempt, conditioned on:
     - Task description
     - Long-term reflection memory from previous trials
  
  2. Evaluator collects feedback:
     - Execute tests, run environment simulation, or apply heuristic checks
     - Record pass/fail, error messages, or score
  
  3. If feedback indicates success:
     - Record final attempt and reflection count
     - Stop loop
  
  4. Self-Reflection generates verbal reflection:
     - Analyze feedback and current attempt
     - Produce structured reflection: what failed, why, what to change
  
  5. Update long-term memory:
     - Append reflection to memory buffer
     - Optionally apply sliding window if memory exceeds token budget
  
  6. Continue to next trial

If max_trials reached without success:
  - Record final state, failure reason, and all reflections
  - Report task as unsolved
```

## Feedback-Source Plan

| Source | Availability in Harness | Implementation |
|--------|-------------------------|----------------|
| **Environment feedback** | Partial – local file system, command execution available; no ALFWorld or interactive RL environments | Use terminal tool to run tests, execute scripts, and capture stderr/stdout as feedback. |
| **Self-generated unit tests** | Full – can write and execute tests for code tasks | Actor or separate tool writes unit tests, Evaluator runs them and parses results. |
| **Heuristic checks** | Full – can implement custom validation logic | Define task-specific heuristics (e.g., output format, constraint satisfaction) and apply them to attempts. |
| **Evaluator scoring** | Full – can use a separate LLM call or internal reasoning for correctness | Invoke a second prompt to score correctness, flag issues, or provide structured feedback. |

For this harness, **self-generated unit tests and heuristic checks are the primary feedback sources**. Environment feedback is available for local execution tasks but not for paper-specific environments like ALFWorld.

## Validation Plan

### Success Criteria (Measurable)

- **Code tasks**: All generated unit tests pass, or the solution passes a provided test suite.
- **Reasoning tasks**: Evaluator confirms the final answer matches ground truth or satisfies task constraints.
- **Decision-making tasks**: If a local simulation is available, the agent completes the task within trial budget.

### Failure Recording

- Record trial number at which task was abandoned.
- Capture final reflection explaining why the agent could not progress.
- Log repeated failure patterns (e.g., same error across 3+ trials indicates local minimum).

### Metrics

- **Success rate**: Fraction of tasks solved within max_trials.
- **Trial efficiency**: Average trials needed to reach success.
- **Reflection quality**: Manual audit of whether reflections correctly diagnose failures.

## Limitations (Source-Backed and Adapted)

### From Source Paper

- Reflexion can get stuck in local minima with no formal success guarantee (source lines 76-83, 527-533).
- Memory is limited to a sliding window; more advanced structures are suggested for future work (source lines 527-533).
- Tasks requiring very creative behavior or richer interaction remain difficult (source lines 741-776).

### Harness-Specific Limitations

- **No interactive RL environments**: ALFWorld and similar decision-making environments are not available in this harness. Code and reasoning tasks are substitutes.
- **No external oracle for all tasks**: For open-ended reasoning, the Evaluator must rely on heuristics or self-scoring rather than ground truth.
- **Token budget constraints**: Long-term memory may need aggressive truncation if trials exceed context window. Use sliding window or summarization.
- **No weight updates**: This is a feature, not a bug, but means the agent cannot learn patterns across unrelated tasks without explicit memory transfer.

## Transfer-Adaptation Note

**What changed for the target harness:**

The source paper evaluates Reflexion on ALFWorld (decision-making), HotPotQA (reasoning), and programming benchmarks with full environment feedback. This harness does not provide interactive RL environments or paper-specific datasets.

**Adaptations:**

1. **Task substitution**: Use local code generation tasks (e.g., implement a function, fix a bug, write a script) or reasoning tasks where ground truth can be checked via heuristics or self-generated tests.
2. **Feedback source shift**: Rely on test execution and heuristic validation instead of environment state transitions.
3. **Evaluator implementation**: Use a combination of terminal tool execution (for code) and structured LLM prompts (for reasoning) to replace paper-specific evaluators.
4. **Memory window enforcement**: Explicitly manage token budget by truncating or summarizing old reflections if trials exceed 5-10 iterations.
5. **No live experiments claimed**: This plan is a blueprint. Actual success metrics require execution and should be reported separately with real trial data.

**Preserved from source:**

- Actor/Evaluator/Self-Reflection architecture.
- Verbal reinforcement learning (no weight updates).
- Short-term trajectory vs. long-term reflection memory distinction.
- Retry-until-success-or-budget loop.
- Reflection generation from feedback.
