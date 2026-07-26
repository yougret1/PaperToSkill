from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

import remote_execution_runner as runner


GENERIC_CREDENTIAL_PATTERNS = (
    re.compile(rb"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}(?![A-Za-z0-9])"),
    re.compile(
        rb"(?i)(?:authorization\s*:\s*bearer|api[-_ ]?key\s*[:=])"
        rb"\s*[\"']?[A-Za-z0-9_./+=-]{16,}"
    ),
)
OPAQUE_RESPONSE_FIELD = re.compile(
    rb'("encrypted_content"\s*:\s*")[^"]*(")'
)
FORBIDDEN_LOCAL_MODEL_MARKERS = (
    b"Qwen/Qwen2.5-Coder-7B-Instruct",
    b"open_seed_anchor",
    b"open_anchor_runtime_manifest",
    b"open_deterministic_anchor",
    b"generated_token_ids",
    b"local_executions",
    b"global_local_anchor_schedule",
)


class AuditError(RuntimeError):
    pass


def generic_scan_content(content: bytes) -> bytes:
    """Remove opaque response ciphertext only from heuristic-pattern scanning."""
    return OPAQUE_RESPONSE_FIELD.sub(rb'\1<opaque-response-field>\2', content)


def iter_files(roots: Iterable[Path]) -> list[Path]:
    files: set[Path] = set()
    for root in roots:
        resolved = runner.windows_extended_path(root)
        if resolved.is_file():
            files.add(resolved)
            continue
        if not resolved.is_dir():
            raise AuditError(f"scan root does not exist: {root}")
        files.update(path for path in resolved.rglob("*") if path.is_file())
    return sorted(files, key=lambda path: path.as_posix())


def audit(
    docs_dir: Path, roots: Iterable[Path], minimum_files: int
) -> tuple[dict[str, object], bool]:
    credentials, _ = runner.load_credentials(docs_dir.resolve())
    credential_values = tuple(
        value.encode("utf-8") for value in credentials.values() if value
    )
    files = iter_files(roots)
    exact_hits: list[str] = []
    generic_hits: list[str] = []
    local_design_hits: list[str] = []
    for path in files:
        content = path.read_bytes()
        if any(value in content for value in credential_values):
            exact_hits.append(str(path))
        heuristic_content = generic_scan_content(content)
        if any(
            pattern.search(heuristic_content)
            for pattern in GENERIC_CREDENTIAL_PATTERNS
        ):
            generic_hits.append(str(path))
        if any(marker in content for marker in FORBIDDEN_LOCAL_MODEL_MARKERS):
            local_design_hits.append(str(path))
    result = {
        "schema_version": "effectslice-artifact-safety-audit.v1",
        "files_scanned": len(files),
        "minimum_files_required": minimum_files,
        "complete_enumeration": len(files) >= minimum_files,
        "exact_credential_reflection_count": len(exact_hits),
        "exact_credential_reflection_files": exact_hits,
        "generic_credential_pattern_match_count": len(generic_hits),
        "generic_credential_pattern_files": generic_hits,
        "forbidden_local_model_design_match_count": len(local_design_hits),
        "forbidden_local_model_design_files": local_design_hits,
        "credential_values_recorded": False,
    }
    passed = (
        len(files) >= minimum_files
        and not exact_hits
        and not generic_hits
        and not local_design_hits
    )
    return result, passed


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", type=Path, required=True)
    parser.add_argument("--min-files", type=int, default=1)
    parser.add_argument("roots", type=Path, nargs="+")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.min_files < 1:
        raise AuditError("--min-files must be positive")
    result, passed = audit(args.docs_dir, args.roots, args.min_files)
    result["status"] = "passed" if passed else "failed"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, runner.ExecutionError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
