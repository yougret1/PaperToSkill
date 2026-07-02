# Claim Source Map

| Draft Claim | Source Status | Supporting Source | Notes |
| --- | --- | --- | --- |
| AI Scientist-v2 uses an end-to-end workflow that formulates hypotheses, runs experiments, analyzes data, and writes manuscripts. | Source-backed | [arXiv 2504.08066](https://arxiv.org/abs/2504.08066) | Useful as both development engine and benchmark paper. |
| AIDE frames machine learning engineering as code optimization with tree search over solutions. | Source-backed | [arXiv 2502.13138](https://arxiv.org/abs/2502.13138) | Useful for extracting search/debug policy. |
| Agent Laboratory structures research assistance into literature review, experimentation, and report writing with human feedback. | Source-backed | [arXiv 2501.04227](https://arxiv.org/abs/2501.04227), [project page](https://agentlaboratory.github.io/) | Useful for human-control checkpoints. |
| Voyager includes an automatic curriculum, executable skill library, and iterative prompting with feedback/self-verification. | Source-backed | [arXiv 2305.16291](https://arxiv.org/abs/2305.16291), [project page](https://voyager.minedojo.org/) | Good fit for skill-library extraction. |
| Reflexion reinforces agents using verbal reflection stored in episodic memory rather than weight updates. | Source-backed | [arXiv 2303.11366](https://arxiv.org/abs/2303.11366) | Supports failure-branch and memory design. |
| SWE-agent's custom agent-computer interface improves agent software-engineering behavior. | Source-backed | [arXiv 2405.15793](https://arxiv.org/abs/2405.15793) | Supports harness/tool-contract framing. |
| Toolformer trains models to decide which APIs to call, when to call them, and how to incorporate results. | Source-backed | [arXiv 2302.04761](https://arxiv.org/abs/2302.04761), [OpenReview](https://openreview.net/forum?id=Yacmpz84TH) | Supports tool-use extraction. |
| Paper2Agent converts papers and associated codebases into MCP tools, resources, prompts, tests, and interactive paper agents. | Source-backed | arXiv:2509.06917 | Closest competing work; supports the need to position PaperToSkill as compact skill conversion rather than MCP server generation. |
| AgenticSciML coordinates specialized agents with debate, retrieval-augmented method memory, and evolutionary search for SciML discovery. | Source-backed | doi:10.1038/s44387-026-00102-5; arXiv:2511.07262 | Background for multi-agent scientific workflow reuse, not a paper-to-skill converter. |
| Reasoning Manifolds proposes label-free diagnostics of LLM inference dynamics from internal representations. | Source-backed | arXiv:2605.08142 | Future non-procedural stress case candidate; not central related work for current PaperToSkill claims. |
| PaperToSkill skills outperform generic summaries. | Hypothesis | TBD | Needs benchmark results before promotion. |
| Failure-branch extraction improves reproducibility. | Hypothesis | TBD | Needs ablation or reviewer audit evidence. |
