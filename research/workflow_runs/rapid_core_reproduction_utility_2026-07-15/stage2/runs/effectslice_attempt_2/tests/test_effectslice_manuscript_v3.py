from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[7]
PAPER_ROOT = PROJECT_ROOT / "paper" / "effectslice_aaai"


def test_main_entrypoint_selects_v3_before_legacy_drafts():
    lines = (PAPER_ROOT / "main.tex").read_text(encoding="utf-8").splitlines()

    assert lines[0] == r"\input{main_v3}"
    assert lines[1] == r"\endinput"


def test_v3_uses_generated_v4_v5_evidence_and_preserves_scope():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")

    assert r"\input{generated_results_v3}" in source
    assert "finite-schedule" in source
    assert re.search(r"planted\s+redundancy smoke test", source)
    assert r"\VFourCalibrationDecision" in source
    assert r"\AllProviderConversations" in source
    assert r"\ToolformerNaturalSSuccesses" in source
    assert "not a population estimate" in source
    assert re.search(r"(?:does|do)\s+not\s+establish\s+broad\s+automatic", source)
    assert "count-level SLA, not block-level behavioral" in source
    assert "Independent outcome/count crosschecks" in source


def test_v3_uses_registered_v4_outcomes_not_legacy_confirmation_counts():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")

    assert not re.search(r"(?:59/59|44/59|15/59)", source)
    assert "EffectSliceProviderConversations" not in source
    assert re.search(r"(?:17/18|0/18|5/6)", source)
    assert "case-level Clopper" not in source
    assert "post-hoc adapters" in source
    assert "new private case blocks" in source


def test_v3_formalizes_rendering_provenance_and_redundant_registered_field():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")

    assert r"A_S\subsetneq A" in source
    assert r"F=R(A)" in source
    assert r"S=R(A_S)" in source
    assert "logically implied" in source
    assert "source-addressed provenance" in source
    assert (
        r"\mathcal{E}=(d_{\mathrm{pre}},M_{\mathrm{post}},"
        r"\sigma,\mathcal{O},\delta)"
    ) in source
    assert "pre-run commitment root" in source
    assert "digest-indexed archival manifest" in source
    assert r"generated\_results\_manifest\_v5.json" in source
    assert "effectslice-paper-results-manifest.v5" in source
    assert re.search(r"does\s+not\s+retroactively\s+preregister", source)


def test_v3_uses_one_binary_admission_vocabulary():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")

    assert "binary finite-schedule Admit/Reject" in source
    assert "do not admit under this registered boundary" in source
    assert "Invalid/No record" in source
    assert "exact 64/64 success" in source
    assert "Pass" in source and "Admit" in source
    assert "abstain" not in source.lower()
    assert "abstention" not in source.lower()


def test_v3_discloses_v5_selection_and_limits_the_natural_admission():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")

    assert "Prefix 04 existed before V4 but was selected after" in source
    assert "zero provider calls" in source
    assert r"\texttt{6538e8d}" in source
    assert "post-V4 selection bias" in source
    assert "not cross-paper or paper-wide equivalence" in source
    assert "nor an implementation of SkillReducer" in source
    assert re.search(r"descriptive\s+count\s+across\s+sequential\s+schedules", source)
    assert re.search(r"expectation\s+metadata\s+only", source)


def test_v3_does_not_imply_a_paired_cross_schedule_candidate_comparison():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")

    assert "can distinguish an insufficient subset" not in source
    assert re.search(
        r"in\s+a\s+separately\s+registered\s+later\s+schedule,\s+a\s+local\s+admission",
        source,
    )
    assert re.search(r"project-local\s+ordered\s+prefix\s+reducer", source)


def test_v3_avoids_unmeasured_speed_and_ambiguous_grounding_terms():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8").lower()

    for forbidden in ("epistemic", "source fidelity", "rapid", "quick"):
        assert forbidden not in source


def test_api_first_boundary_remains_explicit():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8").lower()

    assert "deepseek-v4-flash" in source
    assert "trusted deepseek endpoint" in source
    assert "model inference stayed at the vendor api" in source
    assert "local gpu was not used" in source
    assert "qwen" not in source


def test_v3_resolves_final_review_positioning_and_semantics():
    source = (PAPER_ROOT / "main_v3.tex").read_text(encoding="utf-8")
    abstract = source.split(r"\begin{abstract}", 1)[1].split(r"\end{abstract}", 1)[0]
    conclusion = source.split(r"\section{Conclusion}", 1)[1]

    assert "proof-of-concept, reducer-agnostic" in abstract
    assert "protocol and evidence package" in conclusion
    assert "not a slicing algorithm" in source
    assert "operationalize a source-addressed atom schema" in source
    assert "their coupling into a candidate-specific substitution decision" in source
    assert "Paper2Agent as an upstream full-agent generator" in source
    assert "whole-skill marginal utility" in source
    assert "full-artifact insufficiency from subset-only insufficiency" in source
    assert "post-selected candidate can earn a valid local" in source
    assert "Candidate rows use \\emph{Admit/Reject}" in source
    assert "control and integrity checks use" in source
    assert "Provider or transport exhaustion, scorer failure" in source
    assert "valid scorer result exists" in source
    assert "complete atom-ID inventory" in source
    assert "full locator, instruction, role, and dependency" in source
    assert "archived result-root snapshots contain 1096 files in total" in source
    assert "858 schema-selected canonical raw-evidence files" in source
    assert "bit-level audit and offline count recomputation" in source
    assert "historical absolute paths" in source
    assert "one admission among three" not in abstract
    assert "one admission among three" not in conclusion
