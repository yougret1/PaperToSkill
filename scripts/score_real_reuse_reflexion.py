#!/usr/bin/env python
"""Score locked Reflexion real-reuse outputs."""

from __future__ import annotations

import argparse
import json
import re
import string
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def maybe_json(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def normalize_answer(text: str) -> str:
    text = text.lower()
    text = "".join(" " if char in string.punctuation else char for char in text)
    tokens = [token for token in text.split() if token not in {"a", "an", "the"}]
    return " ".join(tokens)


def token_f1(prediction: str, answer: str) -> float:
    prediction_tokens = normalize_answer(prediction).split()
    answer_tokens = normalize_answer(answer).split()
    if not prediction_tokens and not answer_tokens:
        return 1.0
    if not prediction_tokens or not answer_tokens:
        return 0.0
    overlap = Counter(prediction_tokens) & Counter(answer_tokens)
    common = sum(overlap.values())
    if common == 0:
        return 0.0
    precision = common / len(prediction_tokens)
    recall = common / len(answer_tokens)
    return 2 * precision * recall / (precision + recall)


def prediction_answer(path: Path) -> str:
    data = maybe_json(path)
    if data is not None:
        for key in ("final_answer", "answer", "prediction", "output"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        nested = data.get("result")
        if isinstance(nested, dict):
            for key in ("final_answer", "answer", "prediction"):
                value = nested.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    text = path.read_text(encoding="utf-8").strip()
    match = re.search(r"final\s*answer\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def score_ref_t1(prediction_path: Path, answer_key_path: Path) -> dict[str, Any]:
    answer_key = load_json(answer_key_path)
    prediction = prediction_answer(prediction_path)
    answers = [str(answer_key.get("answer", ""))]
    answers.extend(str(alias) for alias in answer_key.get("aliases", []))
    exact = max(normalize_answer(prediction) == normalize_answer(answer) for answer in answers)
    f1 = max(token_f1(prediction, answer) for answer in answers)
    threshold = float(answer_key.get("f1_success_threshold", 1.0))
    success = bool(exact or f1 >= threshold)
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": "REF-T1",
        "metric_name": "exact_match_or_f1",
        "task_score": 1.0 if exact else f1,
        "success": success,
        "exact_match": bool(exact),
        "f1": f1,
        "normalized_prediction": normalize_answer(prediction),
        "normalized_answers": [normalize_answer(answer) for answer in answers],
        "prediction_path": prediction_path.as_posix(),
        "answer_key_path": answer_key_path.as_posix(),
        "evidence_boundary": (
            "Objective answer-key scoring for one locked REF-T1 output. This "
            "does not compare Summary and PaperToSkill or claim aggregate "
            "downstream effectiveness."
        ),
    }


def candidate_text(path: Path) -> str:
    data = maybe_json(path)
    if data is not None:
        for key in ("candidate_code", "second_attempt_output", "code", "output"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return path.read_text(encoding="utf-8").strip()


def extract_python_code(text: str) -> str:
    match = re.search(r"```(?:python|py)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def candidate_program(candidate_path: Path, tests: dict[str, Any]) -> str:
    entry_point = str(tests["entry_point"])
    code = extract_python_code(candidate_text(candidate_path))
    if f"def {entry_point}" not in code:
        prompt = str(tests["prompt"])
        code = prompt.rstrip() + "\n" + code.strip() + "\n"
    return (
        code.rstrip()
        + "\n\n"
        + str(tests["test"]).strip()
        + f"\n\ncheck({entry_point})\nprint('PASS')\n"
    )


def run_candidate(program: str, timeout_seconds: float) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "candidate_check.py"
        script_path.write_text(program, encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-I", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )


def score_ref_t2(candidate_path: Path, tests_path: Path, timeout_seconds: float) -> dict[str, Any]:
    tests = load_json(tests_path)
    program = candidate_program(candidate_path, tests)
    try:
        completed = run_candidate(program, timeout_seconds)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(
            args=exc.cmd or [],
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "timeout",
        )
        timed_out = True

    success = completed.returncode == 0 and "PASS" in completed.stdout
    stderr = completed.stderr or ""
    failure_reason = ""
    if timed_out:
        failure_reason = "timeout"
    elif not success:
        failure_reason = stderr.strip().splitlines()[-1] if stderr.strip() else f"returncode={completed.returncode}"

    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": "REF-T2",
        "metric_name": "second_attempt_success",
        "task_score": 1.0 if success else 0.0,
        "success": bool(success),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": stderr[-2000:],
        "failure_reason": failure_reason,
        "candidate_path": candidate_path.as_posix(),
        "tests_path": tests_path.as_posix(),
        "evidence_boundary": (
            "Objective checker scoring for one locked REF-T2 candidate. This "
            "does not compare Summary and PaperToSkill or claim aggregate "
            "downstream effectiveness."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score locked Reflexion real-reuse outputs.")
    parser.add_argument("--task", choices=["REF-T1", "REF-T2"], required=True)
    parser.add_argument("--prediction", type=Path, help="REF-T1 prediction text or JSON file.")
    parser.add_argument("--answer-key", type=Path, help="REF-T1 hidden answer-key JSON.")
    parser.add_argument("--candidate", type=Path, help="REF-T2 candidate Python output file.")
    parser.add_argument("--tests", type=Path, help="REF-T2 hidden tests JSON.")
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    if args.task == "REF-T1":
        if not args.prediction or not args.answer_key:
            parser.error("REF-T1 requires --prediction and --answer-key")
        result = score_ref_t1(args.prediction, args.answer_key)
    else:
        if not args.candidate or not args.tests:
            parser.error("REF-T2 requires --candidate and --tests")
        result = score_ref_t2(args.candidate, args.tests, args.timeout_seconds)

    if args.output_json:
        write_json(args.output_json, result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
