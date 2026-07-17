# Stage 1 Candidate Comparison

| Candidate | Decision | Main reason |
|---|---|---|
| ClaimProbe | Reject | Too few paper-level residuals for sign/rank calibration; cited deconfounding recipe was not actually implemented. |
| BoundaryProbe | Reject | Repackages causal transportability/local response surfaces for a new application. |
| Sequential Triage | Reject | Subsumed by cost-sensitive multi-fidelity Bayesian optimization. |
| LocalClaim | Reject | Standard component ablation at paper-operator granularity. |
| FactorGate | Reject | Classical 2x2 factorial attribution plus existing components. |
| Obligation Witness | Reject | Program slicing/delta debugging/source-map composition without a new load-bearing mechanism. |
| EffectSlice v1 | Reject | Vacuous preservation was possible when the full artifact had negligible effect. |
| EffectSlice v2 | Reject | Empty/no-skill-equivalent slices and underspecified atom/error ledgers remained possible. |
| **EffectSlice v3** | **Select for Stage 2** | Hard-floor defects are closed; the remaining claim is a reducer-agnostic eligibility/certificate admission decision tested against direct compact-artifact baselines. |

The selected idea is not “extract, validate, modify, and revalidate.” That is a workflow goal, not a research mechanism. The narrower research claim is whether a strict nonempty paper-derived procedural subset can be admitted only after the complete artifact is proven useful and the subset preserves its cost-adjusted task effect, contracts, and guardrails on untouched runs.

The `scoop-check` decision remains `revise`, not `advance`: direct neighbors partially overlap, candidate-specific search terms were not sent to external services, and behavior-preserving program reduction plus statistical delta debugging remain unresolved. Stage 2 should treat novelty as provisional until that targeted audit is closed.
