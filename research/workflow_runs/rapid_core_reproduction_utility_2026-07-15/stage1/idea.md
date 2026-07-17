# EffectSlice: Eligibility-Gated Certificates for Task-Local Procedural Effects

## Stage 1 Decision

EffectSlice v3 is the only candidate selected for Stage 2. It is an implementable, falsifiable proposal, not a validated result. IdeaSpark validation passed `5 pass, 0 warn, 0 fail`; `scoop-check` remains `revise` because collision coverage is degraded and older reduction families remain unresolved.

## Hypothesis

For one independently locked user task, a strict nonempty subset of a complete paper-derived skill can be certified only if:

1. the complete skill first has a sealed positive cost-adjusted effect over a same-scaffold no-skill baseline;
2. the subset is made from deterministic source-grounded procedural units;
3. its untouched paired effect remains equivalent to the complete skill;
4. its contracts and guardrails pass; and
5. every registered retained-unit deletion neighbor fails under one preregistered error family.

The expected benefit is fewer executed procedures and lower local cost without losing the complete artifact's measured task-local benefit. Failure or ambiguity returns an explicit abstention.

## Core Innovation

The defensible novelty is a **reducer-agnostic eligibility and certificate admission decision**. EffectSlice submits its own candidate and direct ClawTrace, Graph-of-Skills, and SkillRAE outputs to the same positive-full-effect, atom/source-validity, contract, guardrail, and sealed confirmation gate.

The proposal does **not** claim that pruning, subset search, SCC condensation, provenance, dependency closure, equivalence tests, statistical correction, or one-deletion minimality are new by themselves.

“提取、验证、修改、再验证”只是用户工作流，不是研究创新。这里真正可证伪的问题是：在完整 paper-derived skill 已被证明对一个锁定任务有净正效应之后，是否能对更小的非空过程子集给出可信的任务局部效应保持证书。

## Method

1. 冻结 paper-task manifest、完整技能 `F`、同脚手架无技能基线 `B`、评分器、契约、防护项、预算和统计族。
2. 用配对运行证明 `F` 的同时单侧下置信界严格高于 `delta_min`；否则返回 `no_validated_beneficial_effect`。
3. 用固定 CommonMark 解析器、精确 `source_map` 行跨度、可执行区域和契约角色编译四元过程原子；歧义直接弃权。
4. 构造依赖图并做 SCC condensation，只保留与原 dependency-closed 可行子集严格等价的商空间；超过 16 个 SCC 返回超范围。
5. 任意冻结 reducer 可在总查询预算 `Q=24` 内提出严格非空且小于 `F` 的候选，但必须给最终所有 deletion neighbors 预留预算。
6. 在 fresh paired runs 上计算候选相对 `F` 的效应间隔与 `M_tau`，同时检查契约和 guardrails。
7. 锁定 `T_star` 后完整扫描每个 retained-SCC deletion neighbor。
8. 在 untouched confirmation runs 上，对 EffectSlice、`M_tau` 置乱对照和三个直接基线使用同一封存 `H_C` 家族做准入。
9. 输出 `Cert_tau` 或具体拒绝/弃权原因；开发完成后再对至少四个全新 paper-task pairs 报告 held-out 结果。

完整的 12 步工程规格位于 `stage1/idea_spark/phase4/phase4_implementability.json`。

## Experiment Plan

开发阶段复用现有八个 real-reuse rows，只用于实现并冻结 parser、atomization、quotient、eligibility rule、margin、alpha families、query ledger、search worker、baseline adapters、scorers 和预算。随后新增至少四个真正未使用的 paper-task pairs，要求有 untouched source maps、完整技能、可执行资产和锁定评分器。

比较条件包括 `B`、完整技能 `F`、EffectSlice、`M_tau` 置乱负对照，以及 ClawTrace、Graph-of-Skills、SkillRAE 的直接输出。主要终点是 correctly admitted nonempty compact-artifact rate；所有错误准入和 gate abstentions 都留在分母。次要终点包括 false-admission rate、相对 `F` 的配对效应间隔、契约/guardrail noninferiority、过程数和本地成本降低，以及弃权原因分布。

成功要求 EffectSlice 在匹配任务与分支预算下优于三个直接基线的正确准入率，同时不提高错误准入；失败条件是没有准入优势、untouched runs 无法保持 `F` 的效应，或 `M_tau` 置乱不导致下游效应退化。

预算上界为 12 个任务、2,028 branch runs、24.3 GPU-days（80GB 级 GPU）和 `$3,500` API，含 15% 重跑预留。

## Baseline Expectation

ClawTrace、Graph-of-Skills 和 SkillRAE 都可能生成紧凑产物。EffectSlice 的预期差异不是“更会剪枝”，而是同一准入层能否在匹配预算下提高正确准入并降低错误准入。当前没有实验结果支持这一预期。

## Risk Factors and Limitations

- `scoop-check` 仍为 `revise`。候选专用检索词未发送到外部服务，behavior-preserving program reduction、statistical delta debugging、prompt pruning 和 minimal-sufficient rationale 仍是未排除的碰撞族。
- 证书只对一个 paper、一个锁定任务和最多 16 个 SCC 单元成立；不声称全局最小、跨任务或跨论文核心。
- 完整技能无净正效应、原子化歧义、依赖图无效或查询预算不足都会导致弃权；高弃权率可能是正确行为，但会降低实用覆盖。
- 四元原子化在异构技能与来源映射上可能很脆弱。
- 三个直接基线未必天然带精确来源跨度和可执行区域；必须先冻结中立归一化与不可表示输出的处理规则。
- 新的 held-out paper-task pairs、完整资产和可靠 scorer 尚未构建。
- 大型 multiple-testing family 可能导致统计功效不足。
- 现有 PaperToSkill 下游证据是单次且混合的，不能当作 EffectSlice 已有效的证据。
- 当前不含普通用户研究。要声称“帮助普通人快速复现和验证”，必须另做 time-to-correct-use、任务成功率、错误采用率和认知负担评估。

## Open Author Decisions

- `S1`: 明确评分器、契约、guardrails、缺失值规则、配对重采样单位、置信界和每个统计族的成员/校正规则。
- `S10`: 冻结多个 surviving candidates 之间的全序选择与 tie-break。
- `S11`: 冻结缺少精确 provenance 的直接基线输出如何归一化，以及不可表示时 reject、abstain 或 exclude 的规则。
- `S12`: 冻结 held-out paper-task population、抽样/排除规则和 false-admission 的外部参考程序。
