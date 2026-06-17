# AIDE: AI-Driven Exploration in the Space of Code

## Source

- Paper ID: `aide_auto`
- Extracted text: `papers/extracted/aide.txt`
- Extraction notes: Automatic deterministic scaffold from extracted text. It
  should be audited against the paper before being treated as validated paper
  knowledge.

## Abstract

... innovative solutions or research hypotheses. To address this challenge, we introduce AI-Driven Exploration (AIDE), a machine learning engi- neering agent powered by large language models (LLMs). AIDE frames machine learning engineering as a code optimization problem, and formulates trial-and ...

Source anchors: lines 12-34.

## Methods

1. Frame ML engineering as a search over Python-script solution space with an objective
   function: ... in place, AIDE can systematically explore the code solution space, as
   shown. Source anchors: lines 139-143.
2. Represent the run as a solution tree with nodes, edges, scores, and best-solution
   selection: ... h : S R, evaluates the code and provides a scalar score. All
   discovered solutions are stored in a solution tree, T , whose nodes correspond to
   scripts and edges represent an .... Source anchors: lines 130-134.
3. Use a search policy that chooses drafting, debugging, and improving actions: ...
   instantiation for machine learning uses (i) a search policy to select which solution
   to refine next, (ii) a coding operator f for generating code by drafting, debugging,
   or improving solutions, and (iii) .... Source anchors: lines 219-223.
4. Keep coding actions atomic and grounded in executable feedback such as error logs or
   tracebacks: ... or feature-engineering idea), then emits a single-file Python program
   imple- menting that plan. Debugging, which focuses on repairing buggy solutions. By
   inspecting error logs .... Source anchors: lines 167-171.
5. Use a summarization operator to preserve performance metrics, hyperparameters, and
   debugging hints: Summarization Operator ((T )). Despite the flexibility to generate
   arbitrarily large numbers of solutions, we avoid saturating the LLMs prompt by
   applying a context summarization operator, (T ). Instead of .... Source anchors:
   lines 201-205.
6. Provide a static data preview with dataset size, column names, and data splits before
   coding: Data Preview in Coding Prompts. In addition to dynamic updates from (T ),
   AIDE for machine learning includes a small static data preview in each prompt, giving
   the LLM basic knowledge of dataset size or .... Source anchors: lines 212-216.

## Experiments

- Evaluate on Weco-Kaggle, MLE-Bench, and RE-Bench when reproducing the paper's
  benchmark story: ... to build Wecos internal Kaggle benchmark, called Weco-Kaggle, for
  evaluating AIDEs performance in machine learning. This set consists of 63 competitions
  of varied complexity and data size, spanning domains .... Source anchors: lines
  241-245.
- Record Weco-Kaggle Lite 51.38 Exceeds % of humans and baseline comparison: ... Results
  on Weco-Kaggle Lite. Table 1 compares AIDE against multiple baselines, in- cluding H2O
  AutoML, AutoGPT, and a human competitor utilizing ChatGPT, averaged over the 16
  tabular Kaggle tasks of .... Source anchors: lines 336-340.
- Record MLE-Bench pass@1 evidence, including 16.9% Any Medal: ... rates and ultimately
  more competition medals. Table 3 highlights key results of AIDE compared to other
  agents. The reported Any Medal (%) column shows the fraction of competitions on which
  the .... Source anchors: lines 413-417.
- Record MLE-Bench Lite 92.4% valid-submission lift: ... evident when comparing
  performance on the MLE-bench Lite subset, as shown in Figure 3. Using o1-preview with
  AIDE significantly improved performance across all metrics compared to using
  o1-preview .... Source anchors: lines 461-465.
- Record RE-Bench performance and six-hour automation limits: ... average performance
  over time across the seven RE-Bench environ- ments. Since LLMs can implement solutions
  much faster, allowing for more iteration cycles, AIDE managed to outperform humans
  within the .... Source anchors: lines 494-498.
- Compare against baselines and ablations that isolate the search system's contribution:
  ... are encouraged to read and cite the papers from OpenAI (Chan et al., 2024) and
  METR (2024) .... Source anchors: lines 235-239.

## Limitations

- Treat data contamination as a risk when benchmark data may overlap with training
  corpora: ... recency, the only way to fully ensure no data contamination would be to
  submit the agents solutions to live competitions. .... Source anchors: lines 400-404.
- Do not claim live competition submissions when the paper only identifies them as the
  contamination-control ideal: ... agent performance and competition recency, the only
  way to fully ensure no data contamination would be to submit the agents solutions to
  live .... Source anchors: lines 398-402.
- Treat greedy policy and local optima as search limitations: ... scientists eventually
  caught up, as AIDE adopts a simple greedy policy that may lead to local optima on
  challenging R&D .... Source anchors: lines 487-491.
- Check whether the method transfers to larger codebases before claiming broad
  software-engineering scope: ... larger codebases or where a single improvement
  involved multiple steps of interaction. For example, in Agent for Rust CodeContests,
  AIDE was prone to repeating local patches instead of discovering new .... Source
  anchors: lines 499-503.
- Track LLM inference cost as part of the run budget: ... 7 illustrates the per-task LLM
  inference cost for AIDE across the Weco-Kaggle benchmark, using GPT-4 Turbo
  (gpt-4-0125-preview) with pricing data from early 2024. Although certain tasks incur
  higher .... Source anchors: lines 744-748.

## Transfer Notes

- Treat this file as an audit scaffold, not a final skill.
- Keep each generated skill instruction tied to source anchors or mark it as an
  inference.
- Save the JSON selection report or generated skill source map with the skill so
  later audits can trace each line range.
- Re-run source-span validation after converting this note into `SKILL.md`.
- Compare the resulting skill against any curated note before using it in a
  live agent workflow.
