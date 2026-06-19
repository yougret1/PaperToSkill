#!/usr/bin/env python
"""Generate a validated AAAI submission decision record.

This helper writes the human decision record consumed by
check_aaai_submission_decision.py, but it does not choose an option by itself.
The research lead must explicitly pass the selected option and claim boundary.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


OPTION_IDS = {
    "submit_now_deterministic_offline",
    "wait_for_external_evidence",
}

SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")
REQUIRED_TEXT_FIELDS = {
    "decision_owner": "Decision owner",
    "decision_date": "Decision date",
    "claim_boundary": "Claim boundary",
    "evidence_policy": "Evidence policy",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def validate_secret_free(values: list[str]) -> None:
    combined = "\n".join(values)
    if SECRET_PATTERN.search(combined):
        raise ValueError("decision fields must not contain raw API-key-like material")


def validate_nonempty(label: str, value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} is required")
    return stripped


def available_options(preflight: dict[str, Any]) -> set[str]:
    return {
        str(option.get("id"))
        for option in preflight.get("options", [])
        if option.get("status") == "available_for_human_decision"
    }


def validate_against_preflight(selected_option: str, preflight: dict[str, Any], preflight_path: Path) -> None:
    if not preflight:
        raise ValueError(f"AAAI decision preflight is missing or empty: {preflight_path}")
    if preflight.get("overall_status") == "fail":
        raise ValueError("AAAI decision preflight has failing checks")
    if selected_option not in available_options(preflight):
        raise ValueError(f"selected option is not currently available in {preflight_path}: {selected_option}")


def render_decision_record(
    *,
    selected_option: str,
    decision_owner: str,
    decision_date: str,
    claim_boundary: str,
    evidence_policy: str,
) -> str:
    fields = {
        "decision_owner": validate_nonempty(REQUIRED_TEXT_FIELDS["decision_owner"], decision_owner),
        "decision_date": validate_nonempty(REQUIRED_TEXT_FIELDS["decision_date"], decision_date),
        "claim_boundary": validate_nonempty(REQUIRED_TEXT_FIELDS["claim_boundary"], claim_boundary),
        "evidence_policy": validate_nonempty(REQUIRED_TEXT_FIELDS["evidence_policy"], evidence_policy),
    }
    validate_secret_free([selected_option, *fields.values()])
    if selected_option not in OPTION_IDS:
        raise ValueError(
            "selected option must be submit_now_deterministic_offline or wait_for_external_evidence"
        )

    return "\n".join(
        [
            "# AAAI Submission Decision",
            "",
            f"Selected option: {selected_option}",
            f"Decision owner: {fields['decision_owner']}",
            f"Decision date: {fields['decision_date']}",
            f"Claim boundary: {fields['claim_boundary']}",
            f"Evidence policy: {fields['evidence_policy']}",
            "",
        ]
    )


def write_decision_record(
    *,
    output_path: Path,
    selected_option: str,
    decision_owner: str,
    decision_date: str,
    claim_boundary: str,
    evidence_policy: str,
    preflight_path: Path,
    skip_preflight_check: bool = False,
) -> str:
    record = render_decision_record(
        selected_option=selected_option,
        decision_owner=decision_owner,
        decision_date=decision_date,
        claim_boundary=claim_boundary,
        evidence_policy=evidence_policy,
    )
    if not skip_preflight_check:
        validate_against_preflight(selected_option, load_json(preflight_path), preflight_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(record, encoding="utf-8")
    return record


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate a validated AAAI submission decision record.")
    parser.add_argument("--selected-option", required=True, choices=sorted(OPTION_IDS))
    parser.add_argument("--decision-owner", required=True)
    parser.add_argument("--decision-date", required=True)
    parser.add_argument("--claim-boundary", required=True)
    parser.add_argument("--evidence-policy", required=True)
    parser.add_argument(
        "--preflight-json",
        type=Path,
        default=root / "results" / "aaai_submission_decision" / "decision.json",
        help="AAAI decision preflight report to validate option availability.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "research" / "aaai_submission_decision.md",
        help="Decision record path consumed by check_aaai_submission_decision.py.",
    )
    parser.add_argument(
        "--skip-preflight-check",
        action="store_true",
        help="Only for isolated tests; normal runs should validate the current preflight.",
    )
    args = parser.parse_args()

    try:
        write_decision_record(
            output_path=args.output,
            selected_option=args.selected_option,
            decision_owner=args.decision_owner,
            decision_date=args.decision_date,
            claim_boundary=args.claim_boundary,
            evidence_policy=args.evidence_policy,
            preflight_path=args.preflight_json,
            skip_preflight_check=args.skip_preflight_check,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
