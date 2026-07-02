### Sufficiency Assessment
The provided skill context is **sufficient** for planning a code-space search run, but it requires localized adaptation. The workflow steps (1–6) outline the core AIDE method: solution tree, search policy, coding operators, summarization, data preview. Validation and failure cases are documented. The plan below translates those into an executable sequence for a hypothetical target harness.

### Required Local Artifacts & Tools
- **Files:**
  - `SKILL.md` (this context).
  - Target task description (e.g., `task.yaml` with dataset path, objective, constraints).
  - Python script that implements the AIDE loop (not provided – will be built from workflow steps).
  - Dataset file(s) for data preview (e.g., CSV in `data/`).
- **Commands / Tools:**
  - Python 3.10+ with `requests` or `openai` client library for LLM API calls.
  - Shell command: `python run_aide.py --config config.yaml --task task.yaml`
- **Simulated APIs:**
  - LLM endpoint (e.g., `https://api.deepseek.com/chat/completions` using `deepseek-v4-flash` alias).
  - Scoring function (must be implemented locally, e.g., accuracy or F1 for a classification dataset).

### Step-by-Step Run Plan

#### 1. Initialize the Search
- **Source-backed:** Use Workflow step 2 – create an empty solution tree `T` with root node placeholder.
- **Inferred adaptation:** Define `scoring_function(solution_script: str) -> float` according to target task. Store in `evaluator.py`.
- **Command:** `python aide_init.py --task task.yaml --output tree_init.json`

#### 2. Data Preview & Static Context
- **Source-backed:** Workflow step 6 – extract dataset shape, column names, target variable, train/test split.
- **Inferred adaptation:** Parse CSV from `data/`; compute basic stats (size, class balance). Embed as static prompt preamble.
- **Validation:** Preview output matches paper description (small, static metadata).

#### 3. First Draft Generation
- **Source-backed:** Workflow step 3 – use coding operator `draft(problem, data_preview) -> solution_script`.
- **Inferred adaptation:** Call LL
