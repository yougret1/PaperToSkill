# Real-Reuse Summary Baseline: AIDE-T1

This context is the Summary baseline for the locked AIDE real-reuse task. It
summarizes the source-paper method only. It does not include hidden validation
labels or scorer-only thresholds.

# Generic Summary: AIDE

AIDE frames machine-learning engineering as search over executable Python
solutions. It keeps a tree of candidate scripts, evaluates each candidate with
an objective metric, records feedback, and uses that feedback to draft, debug,
or improve the next candidate.

The method emphasizes concise task context, static data previews, measured
validation scores, and choosing the best solution based on the objective
function rather than narrative confidence.

Known limitations include local optima, repeated local patches, benchmark/data
contamination concerns, and dependence on the available runtime and objective
metric.
