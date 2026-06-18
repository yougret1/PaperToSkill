# PaperToSkill Live Transfer: Reflexion Agent Plan

## Run Objective
Build a local retry-and-reflection agent that attempts coding tasks, receives feedback from test execution or build verification, generates self-reflection summaries after failures, stores those reflections in memory, and retries with access to prior lessons until success or retry budget exhaustion.

## Role Table

| Role | Responsibility |
|------|---------------|
| **Actor** | Implements the coding task using available file editing and terminal tools. Reads current short-term trajectory and long-term reflection memory before acting. |
| **Evaluator** | Scores outcomes by running tests, build steps, or verification commands. Returns binary success/failure or numeric score plus error logs. |
| **Self-Reflection** | Analyzes failure feedback and prior attempt trajectory. Generates natural language reflection explaining what went wrong, what was learned, and what to try differently next time. |

## Memory Schema

**Short-Term Trajectory History**
- Current trial number
- Actions taken in this trial (files edited, commands run)
- Evaluator feedback (pass/fail, error messages, test output)
- Cleared at end of each trial

**Long-Term Reflection Memory**
- Accumulated natural language reflections from all prior failures
- Each reflection tagged with trial number and failure type
- Persisted across trials, read by Actor before each new attempt
- Bounded by context window; oldest reflections dropped if limit approached

## Trial Loop

1. **Initialize**: Set trial counter to 1, max_trials to 3, long-term memory to empty.
2. **Act**: Actor reads long-term memory and short-term history, then implements or revises the solution.
3. **Evaluate**: Run verification (build/test). Collect feedback (exit code, error logs, test results).
4. **Check Success**: If feedback indicates success, exit loop with success.
5. **Reflect**: Self-Reflection reviews short-term trajectory and evaluator feedback, generates a reflection summary.
6. **Update Memory**: Append reflection to long-term memory.
7. **Retry Decision**: If trial counter < max_trials, increment and go to step 2. Otherwise, exit with failure.

## Feedback Source Plan

**Primary**: Execute project build or test commands and capture output.
- For projects with test frameworks: run test suite, parse results
- For projects without tests: run compile/build step, check for errors
- Exit code and stderr provide binary success signal plus diagnostic details

**Fallback Heuristics**:
- Syntax/linting checks if build unavailable
- File structure validation (required files exist, imports resolve)
- Self-generated smoke tests for simple functions

**Unavailable**: Human scoring, external evaluator APIs, specialized task environments beyond local repo.

## Validation Plan

**Success Criteria**:
- Binary: All tests pass and build completes without errors
- Measurable: Test pass rate (percentage of tests passing)
- Task completion within retry budget (≤ max_trials)

**Failure Recording**:
- Log each trial's actions, feedback, and reflection
- Record final outcome: success on trial N, or exhausted retries
- Preserve error messages and reflection content for post-run analysis

**Metrics to Track**:
- Trials to success (if successful)
- Types of failures encountered (syntax, logic, test, build)
- Reflection quality indicators (mentions specific error, proposes concrete alternative)

## Limitations

**Source-Backed**:
- Agent can still get stuck repeating similar failures despite reflections
- Memory bounded by context window; simple FIFO dropping loses nuance
- Method may not discover creative solutions for complex tasks
- Relies on quality of self-generated reflection; weak reflection yields weak improvement

**Harness-Specific Adaptations**:
- No separate reflection model; single agent performs all roles sequentially
- No external reward signal or human feedback; depends entirely on automated verification
- Missing tools: Cannot execute in sandboxed environments, no multi-agent orchestration
- Context compaction may discard reflection memory before retry budget exhausted
- Cannot guarantee reflection will identify root cause if error logs are ambiguous

## Transfer Adaptation Note

**What Changed for Target Harness**:
- Collapsed Actor/Evaluator/Self-Reflection into sequential steps within a single agent conversation, rather than separate model instances
- Replaced paper's environment-specific reward functions with local build/test verification
- Long-term memory implemented as conversation context rather than external vector store
- Retry policy simplified to fixed budget (no adaptive stopping based on reflection confidence)
- Evaluation limited to tasks with executable verification; reasoning-only tasks require explicit test scaffolding

**Preserved from Source**:
- Core cycle: act → evaluate → reflect → retry with memory
- Distinction between ephemeral trajectory and persistent reflection memory
- Verbal reinforcement principle (natural language feedback instead of weight updates)
- Multi-trial learning within episode
