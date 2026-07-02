**State whether the context is sufficient for the requested usage task**
The context (the curated `SKILL.md`) is **sufficient** to plan a tool-use data-generation experiment following the Toolformer method. It provides a verified workflow, validation checks, failure cases, and transfer notes. The plan below adapts these to a concrete experiment while respecting the source anchors and separating inferred choices.

---

**Required local files, commands, tools, or simulated APIs**

| Item | Description | Source / Inferred |
|------|-------------|-------------------|
| Plain LM dataset (`train.txt`, `val.txt`) | Text corpus for augmentation, e.g., C4 subset or WikiText. | Inferred (choose any text dataset) |
| Base language model (e.g., GPT-J 6B) | Pre‑trained model to be fine‑tuned. | Inferred (Toolformer paper used GPT-J; plan uses same class) |
| Tool APIs (at least 3–5 text‑to‑text backends) | Calculator (eval), Wikipedia search (retrieve snippet), Calendar (date info), QA model (optional), Translation (optional). All must accept text input and return text output. | Inferred (select subset from paper’s five tools) |
| Few‑shot prompts per API | Short prompt with 2–3 demonstrations in the format: `<API>tool_name\ninput</API>`. | Source‑backed (Workflow step 3, lines 123–152) |
| Script to sample candidate API calls | Using the base LM with the few‑shot prompts to annotate the dataset. | Source‑backed (step 2, lines 105–115) |
| Script to execute proposed calls | Calls the actual tool backend for each sampled API call. | Source‑backed (step 4, lines 123–132) |
| Script to filter calls | Compute loss reduction metric: `loss_no_call - loss_with_call_and_result` ≥ threshold. | Source‑backed (step 5, lines 134–171) |
| Fine‑tuning harness (e.g., Hugging Face Trainer) | Fine‑tune
