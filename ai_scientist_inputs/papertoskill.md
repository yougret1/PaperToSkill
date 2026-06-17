# Title: PaperToSkill: Turning Research Papers into Reusable Agent Skills

## Keywords

paper extraction, agent skills, research transfer, workflow distillation,
LLM agents, reproducibility, compactness, cross-harness transfer

## TL;DR

How can a research paper be converted into a compact, human-editable skill that
lets an agent reuse the paper's main contribution, validation logic, and failure
cases?

## Abstract

Modern LLM and agent research produces many methods that could improve everyday
workflows, but most people cannot directly operationalize a paper's method
section into a reliable agent workflow. We propose PaperToSkill, a system that
converts research papers into reusable agent skills. A skill is a concise,
natural-language artifact that defines when it should be used, what inputs it
requires, how an agent should execute the method, how outputs should be
validated, and which limitations or failure cases must be respected.

The central hypothesis is that paper-derived skills can preserve procedural
knowledge better than generic summaries while using less context than full paper
excerpts. PaperToSkill treats extraction as a structured process: identify the
paper's contribution, separate claims from evidence, extract the operational
workflow, encode assumptions and tool contracts, add validation checks, and
record failure branches. The resulting skill should be editable by non-experts
and portable across agent harnesses.

Experiments should evaluate fidelity, downstream task success, compactness cost,
and cross-harness transfer. Baselines include no paper context, abstract-only
summaries, generic LLM summaries, and full paper excerpts. Ablations should
remove failure-case extraction, validation checks, source mapping, and transfer
notes. The project should also study negative results: successful applications
alone are insufficient for a system that claims to turn research into practice.

