from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import analyze_confirmation_v3 as frozen_analyzer


RUN_ROOT = Path(__file__).resolve().parent
POSTRUN_ROOT = RUN_ROOT.parent.parent / "postrun" / "derived" / RUN_ROOT.name
PROVENANCE_SCHEMA = "effectslice-confirmation-v3-analysis-replay.v1"


class AnalysisReplayError(ValueError):
    """Raised when frozen analysis inputs cannot be replayed exactly."""


class _CanonicalPromptBytes(bytes):
    def decode(self, encoding: str = "utf-8", errors: str = "strict") -> str:
        return (
            super()
            .decode(encoding, errors)
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AnalysisReplayError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise AnalysisReplayError(f"{label} must be a JSON object")
    return value


def _replace_bytes(path: Path, payload: bytes) -> None:
    destination = Path(path)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _within(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def verify_frozen_analyzer(family_paths: list[Path], analyzer_path: Path) -> str:
    analyzer = Path(analyzer_path).resolve()
    actual = _sha256(analyzer.read_bytes())
    expected_values = set()
    for family_path in family_paths:
        family = _json_object(family_path, "registered family")
        bindings = family.get("bindings")
        binding = bindings.get("analyzer") if isinstance(bindings, dict) else None
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256", "status"}:
            raise AnalysisReplayError("registered analyzer binding is invalid")
        if binding.get("status") != "bound":
            raise AnalysisReplayError("registered analyzer is not bound")
        if family.get("analyzer_path") != binding.get("path"):
            raise AnalysisReplayError("registered analyzer path metadata differs")
        if family.get("analyzer_sha256") != binding.get("sha256"):
            raise AnalysisReplayError("registered analyzer digest metadata differs")
        registered_path = Path(binding["path"])
        if not registered_path.is_absolute():
            registered_path = RUN_ROOT / registered_path
        if registered_path.resolve() != analyzer:
            raise AnalysisReplayError("registered analyzer path does not resolve to the analyzer")
        expected_values.add(binding["sha256"])
    if expected_values != {actual}:
        raise AnalysisReplayError("frozen analyzer digest does not match its families")
    return actual


@contextmanager
def corrected_task_prompt_canonicalization() -> Iterator[None]:
    original_snapshot = frozen_analyzer._snapshot_bytes
    original_audit_condition = frozen_analyzer._audit_condition

    def corrected(path: Path, expected_sha256: str, label: str) -> bytes:
        payload = original_snapshot(path, expected_sha256, label)
        if label == "task prompt snapshot":
            return _CanonicalPromptBytes(payload)
        return payload

    def corrected_condition(*args: Any, **kwargs: Any) -> dict[str, Any]:
        family = kwargs.get("family")
        output_dir = kwargs.get("output_dir")
        if not isinstance(family, dict) or output_dir is None:
            raise frozen_analyzer.AnalysisInputError(
                "condition task prompt replay inputs are invalid"
            )
        prompt_path = Path(output_dir) / "verified_inputs" / "task_prompt.md"
        try:
            payload = prompt_path.read_bytes()
            text = payload.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise frozen_analyzer.AnalysisInputError(
                "task prompt snapshot cannot be replayed"
            ) from exc
        if _sha256(payload) != family.get("task_prompt_file_sha256"):
            raise frozen_analyzer.AnalysisInputError(
                "task prompt snapshot digest mismatch"
            )
        canonical_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if _sha256(canonical_text.encode("utf-8")) != family.get(
            "task_prompt_canonical_text_sha256"
        ):
            raise frozen_analyzer.AnalysisInputError(
                "canonical task prompt snapshot digest mismatch"
            )
        legacy_text_digest = _sha256(text.strip().encode("utf-8"))
        adapted_family = dict(family)
        adapted_family["task_prompt_canonical_text_sha256"] = legacy_text_digest
        adapted_kwargs = dict(kwargs)
        adapted_kwargs["family"] = adapted_family
        return original_audit_condition(*args, **adapted_kwargs)

    frozen_analyzer._snapshot_bytes = corrected
    frozen_analyzer._audit_condition = corrected_condition
    try:
        yield
    finally:
        frozen_analyzer._snapshot_bytes = original_snapshot
        frozen_analyzer._audit_condition = original_audit_condition


def _historical_bindings(progress_path: Path, run_root: Path) -> dict[Path, str]:
    progress = _json_object(progress_path, "historical progress view")
    records = progress.get("records")
    if not isinstance(records, list):
        raise AnalysisReplayError("historical progress records are invalid")
    bindings: dict[Path, str] = {}
    for record in records:
        if not isinstance(record, dict) or record.get("task_key") != "toolformer_filter":
            raise AnalysisReplayError("historical view contains a non-Toolformer record")
        if record.get("status") not in {"completed", "preserved"}:
            continue
        output_dir = Path(record.get("output_dir", "")).resolve()
        if not _within(output_dir, run_root):
            raise AnalysisReplayError("historical output directory escapes the run root")
        manifest = _json_object(output_dir / "pair_manifest.json", "historical pair manifest")
        verified = manifest.get("verified_family_inputs")
        if not isinstance(verified, dict):
            raise AnalysisReplayError("historical verified inputs are missing")
        for binding in verified.values():
            if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
                raise AnalysisReplayError("historical input binding is invalid")
            path = Path(binding["path"]).resolve()
            expected = binding["sha256"]
            if not _within(path, run_root) or not path.is_file() or path.is_symlink():
                raise AnalysisReplayError("historical input path is missing or unsafe")
            if path in bindings and bindings[path] != expected:
                raise AnalysisReplayError("historical input has conflicting digests")
            bindings[path] = expected
    return bindings


@contextmanager
def historical_eol_replay(
    progress_path: Path, run_root: Path = RUN_ROOT
) -> Iterator[list[dict[str, str]]]:
    bindings = _historical_bindings(Path(progress_path), Path(run_root))
    originals: dict[Path, bytes] = {}
    changed: list[dict[str, str]] = []
    try:
        for path, expected in sorted(bindings.items(), key=lambda item: item[0].as_posix()):
            payload = path.read_bytes()
            actual = _sha256(payload)
            if actual == expected:
                continue
            try:
                normalized = (
                    payload.decode("utf-8")
                    .replace("\r\n", "\n")
                    .replace("\r", "\n")
                    .encode("utf-8")
                )
            except UnicodeError as exc:
                raise AnalysisReplayError("historical input is not UTF-8 text") from exc
            if _sha256(normalized) != expected:
                raise AnalysisReplayError(
                    f"historical input differs beyond newline encoding: {path}"
                )
            originals[path] = payload
            _replace_bytes(path, normalized)
            changed.append(
                {
                    "path": path.relative_to(Path(run_root).resolve()).as_posix(),
                    "original_sha256": actual,
                    "replay_sha256": expected,
                }
            )
        yield changed
    finally:
        restore_errors = []
        for path, payload in originals.items():
            try:
                _replace_bytes(path, payload)
                if path.read_bytes() != payload:
                    restore_errors.append(path.as_posix())
            except OSError:
                restore_errors.append(path.as_posix())
        if restore_errors:
            raise AnalysisReplayError(
                "historical inputs could not be restored: " + ", ".join(restore_errors)
            )


def _write_json(path: Path, value: dict[str, Any]) -> None:
    payload = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() == payload:
        return
    _replace_bytes(destination, payload)


def run_analysis(
    *,
    progress_path: Path,
    historical_progress_path: Path,
    output_path: Path,
    derived_root: Path,
    provenance_path: Path,
) -> dict[str, Any]:
    family_root = RUN_ROOT / "artifacts" / "toolformer_filter" / "confirmation_v3"
    analyzer_path = RUN_ROOT / "analyze_confirmation_v3.py"
    analyzer_sha256 = verify_frozen_analyzer(
        [family_root / "identity" / "family.json", family_root / "planted" / "family.json"],
        analyzer_path,
    )
    with historical_eol_replay(historical_progress_path) as changed:
        with corrected_task_prompt_canonicalization():
            result = frozen_analyzer.write_analysis(
                progress_path,
                output_path,
                include_historical_negative_control=True,
                historical_v2_progress_path=historical_progress_path,
                derived_root=derived_root,
            )
    analysis_payload = Path(output_path).read_bytes()
    provenance = {
        "schema_version": PROVENANCE_SCHEMA,
        "orchestrator_path": Path(__file__).resolve().as_posix(),
        "orchestrator_sha256": _sha256(Path(__file__).read_bytes()),
        "frozen_analyzer_path": analyzer_path.resolve().as_posix(),
        "frozen_analyzer_sha256": analyzer_sha256,
        "posthoc_corrections": [
            {
                "correction_id": "task_prompt_canonical_newline_decode",
                "scope": "task prompt snapshot decode after exact raw-byte verification",
                "reason": (
                    "The frozen analyzer hashed decoded CRLF text against the registered "
                    "universal-newline LF canonical digest."
                ),
            },
            {
                "correction_id": "condition_task_prompt_legacy_crlf_digest",
                "scope": (
                    "condition result task_prompt_sha256 comparison after exact "
                    "snapshot-byte and canonical-text verification"
                ),
                "reason": (
                    "The frozen runner persisted the digest of stripped CRLF text, "
                    "while the registered family stored the stripped LF-canonical "
                    "text digest."
                ),
            }
        ],
        "v3_progress_path": Path(progress_path).resolve().as_posix(),
        "v3_progress_sha256": _sha256(Path(progress_path).read_bytes()),
        "historical_progress_path": Path(historical_progress_path).resolve().as_posix(),
        "historical_progress_sha256": _sha256(Path(historical_progress_path).read_bytes()),
        "temporarily_normalized_inputs": changed,
        "restored_input_count": len(changed),
        "analysis_path": Path(output_path).resolve().as_posix(),
        "analysis_sha256": _sha256(analysis_payload),
        "registered_schedule_length": result["registered_schedule_length"],
        "strict_subset_admitted": result["strict_subset_admitted"],
    }
    _write_json(provenance_path, provenance)
    return provenance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the frozen V3 analyzer with an exact historical V2 replay"
    )
    parser.add_argument(
        "--progress-path",
        type=Path,
        default=RUN_ROOT
        / "experiment_results"
        / "confirmation_v3"
        / "confirmation_v3_progress.json",
    )
    parser.add_argument(
        "--historical-progress-path",
        type=Path,
        default=RUN_ROOT
        / "derived"
        / "confirmation_v3_historical_v2"
        / "toolformer_progress.json",
    )
    parser.add_argument(
        "--derived-root",
        type=Path,
        default=POSTRUN_ROOT / "confirmation_v3",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=POSTRUN_ROOT / "confirmation_v3" / "analysis.json",
    )
    parser.add_argument(
        "--provenance-path",
        type=Path,
        default=POSTRUN_ROOT / "confirmation_v3" / "analysis.provenance.json",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_analysis(
        progress_path=args.progress_path,
        historical_progress_path=args.historical_progress_path,
        output_path=args.output_path,
        derived_root=args.derived_root,
        provenance_path=args.provenance_path,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
