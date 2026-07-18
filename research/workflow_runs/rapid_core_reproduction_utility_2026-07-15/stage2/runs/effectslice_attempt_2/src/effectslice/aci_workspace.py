from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path


def normalize_newlines(text: str) -> str:
    """Normalize model-visible source text to the ACI's LF edit contract."""

    return text.replace("\r\n", "\n").replace("\r", "\n")


class WorkspaceError(ValueError):
    """Raised when a workspace operation is invalid or unsafe."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        self.code = code
        if code is not None:
            message = f"{code}: {message}"
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class SearchHit:
    path: str
    line_number: int
    text: str


@dataclass(frozen=True, slots=True)
class EditResult:
    path: str
    replacements: int
    changed: bool


class OverlayWorkspace:
    """Provide bounded text operations over a read-only source tree."""

    _SKIPPED_DIRECTORY_NAMES = frozenset(
        {
            ".git",
            ".mypy_cache",
            ".pytest_cache",
            ".tox",
            "__pycache__",
            "build",
            "dist",
        }
    )

    def __init__(
        self,
        source_root: str | Path,
        *,
        max_file_bytes: int = 1_000_000,
        max_search_results: int = 100,
        max_open_lines: int = 200,
        max_search_files: int = 10_000,
        max_search_bytes: int = 10_000_000,
        max_diff_bytes: int = 4_000_000,
    ) -> None:
        self._max_file_bytes = self._positive_limit(max_file_bytes, "max_file_bytes")
        self._max_search_results = self._positive_limit(
            max_search_results, "max_search_results"
        )
        self._max_open_lines = self._positive_limit(max_open_lines, "max_open_lines")
        self._max_search_files = self._positive_limit(
            max_search_files, "max_search_files"
        )
        self._max_search_bytes = self._positive_limit(
            max_search_bytes, "max_search_bytes"
        )
        self._max_diff_bytes = self._positive_limit(max_diff_bytes, "max_diff_bytes")
        try:
            self._source_root = Path(source_root).resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as error:
            raise WorkspaceError("source root does not exist") from error
        if not self._source_root.is_dir():
            raise WorkspaceError("source root must be a directory")
        self._originals: dict[str, str] = {}
        self._overlay: dict[str, str] = {}

    @staticmethod
    def _positive_limit(value: int, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise WorkspaceError(f"{name} must be a positive integer")
        return value

    def resolve_relative(self, relative_path: str | Path) -> Path:
        try:
            path = Path(relative_path)
        except (TypeError, ValueError) as error:
            raise WorkspaceError("path must be a valid relative path") from error
        if path.is_absolute():
            raise WorkspaceError("absolute paths are not allowed")
        excluded_parts = {
            part.casefold()
            for part in path.parts
            if part.casefold() in self._SKIPPED_DIRECTORY_NAMES
        }
        if excluded_parts:
            excluded = ", ".join(sorted(excluded_parts))
            raise WorkspaceError(f"path uses an excluded directory: {excluded}")
        try:
            resolved = (self._source_root / path).resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as error:
            raise WorkspaceError(f"path does not exist: {path}") from error
        try:
            resolved.relative_to(self._source_root)
        except ValueError as error:
            raise WorkspaceError(f"path escapes workspace: {path}") from error
        return resolved

    def search(
        self,
        literal: str,
        *,
        relative_dir: str | Path = ".",
    ) -> tuple[SearchHit, ...]:
        if not isinstance(literal, str) or not literal:
            raise WorkspaceError("search literal must be a non-empty string")
        search_root = self.resolve_relative(relative_dir)
        if search_root.is_file():
            candidates = (search_root,)
        elif search_root.is_dir():
            candidates = self._iter_candidate_files(search_root)
        else:
            raise WorkspaceError(f"search root is not a file or directory: {relative_dir}")
        hits: list[SearchHit] = []
        seen_paths: set[str] = set()
        files_inspected = 0
        bytes_inspected = 0
        for candidate in candidates:
            files_inspected += 1
            if files_inspected > self._max_search_files:
                raise WorkspaceError(
                    f"search exceeds max_search_files={self._max_search_files}",
                    code="search_file_budget_exhausted",
                )
            relative_path = candidate.relative_to(self._source_root).as_posix()
            try:
                resolved = self.resolve_relative(relative_path)
            except WorkspaceError:
                continue
            key = resolved.relative_to(self._source_root).as_posix()
            if key in seen_paths:
                continue
            seen_paths.add(key)
            candidate_bytes = self._search_candidate_bytes(resolved, key)
            if candidate_bytes > self._max_search_bytes - bytes_inspected:
                raise WorkspaceError(
                    (
                        f"search exceeds max_search_bytes={self._max_search_bytes} "
                        f"after {bytes_inspected} bytes"
                    ),
                    code="search_byte_budget_exhausted",
                )
            bytes_inspected += candidate_bytes
            try:
                _, text = self._read_current(relative_path)
            except WorkspaceError:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                if literal not in line:
                    continue
                hits.append(SearchHit(key, line_number, line))
                if len(hits) == self._max_search_results:
                    return tuple(hits)
        return tuple(hits)

    def _iter_candidate_files(self, search_root: Path):
        stack = list(reversed(self._directory_entries(search_root)))
        while stack:
            candidate = stack.pop()
            if candidate.is_symlink():
                if candidate.is_file():
                    yield candidate
                continue
            if candidate.is_dir():
                if candidate.name in self._SKIPPED_DIRECTORY_NAMES:
                    continue
                stack.extend(reversed(self._directory_entries(candidate)))
            elif candidate.is_file():
                yield candidate

    @staticmethod
    def _directory_entries(directory: Path) -> list[Path]:
        try:
            return sorted(directory.iterdir(), key=lambda path: path.name)
        except OSError as error:
            raise WorkspaceError(f"unable to traverse directory: {directory}") from error

    def _search_candidate_bytes(self, resolved: Path, key: str) -> int:
        if key in self._overlay:
            return len(self._overlay[key].encode("utf-8"))
        if key in self._originals:
            return len(self._originals[key].encode("utf-8"))
        try:
            source_size = resolved.stat().st_size
        except OSError as error:
            raise WorkspaceError(f"unable to inspect file: {key}") from error
        return min(source_size, self._max_file_bytes + 1)

    def open_lines(
        self,
        relative_path: str | Path,
        start_line: int,
        end_line: int,
    ) -> tuple[str, ...]:
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (start_line, end_line)
        ):
            raise WorkspaceError("line numbers must be integers")
        if start_line < 1 or end_line < start_line:
            raise WorkspaceError("line window must be one-based and ordered")
        if end_line - start_line + 1 > self._max_open_lines:
            raise WorkspaceError("line window exceeds max_open_lines")
        _, text = self._read_current(relative_path)
        lines = text.splitlines()
        return tuple(lines[start_line - 1 : end_line])

    def replace_exact(
        self,
        relative_path: str | Path,
        old_text: str,
        new_text: str,
    ) -> EditResult:
        if not isinstance(old_text, str) or not old_text:
            raise WorkspaceError("old_text must be a non-empty string")
        if not isinstance(new_text, str):
            raise WorkspaceError("new_text must be a string")
        key, current = self._read_current(relative_path)
        occurrences = current.count(old_text)
        if occurrences == 0:
            raise WorkspaceError("old_text not found")
        if occurrences > 1:
            raise WorkspaceError("old_text occurs more than once")
        updated = current.replace(old_text, new_text, 1)
        self._validate_overlay_text(updated, key)
        if updated == self._originals[key]:
            self._overlay.pop(key, None)
        else:
            self._overlay[key] = updated
        return EditResult(key, 1, updated != current)

    def unified_diff(self) -> str:
        chunks: list[str] = []
        diff_bytes = 0
        for key in sorted(self._overlay):
            original = self._originals[key]
            updated = self._overlay[key]
            if original == updated:
                continue
            lines = difflib.unified_diff(
                original.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=f"a/{key}",
                tofile=f"b/{key}",
                lineterm="\n",
            )
            for line in lines:
                if line.endswith("\n"):
                    output_lines = (line,)
                elif line.startswith((" ", "+", "-")):
                    output_lines = (line + "\n", "\\ No newline at end of file\n")
                else:
                    output_lines = (line + "\n",)
                for output_line in output_lines:
                    encoded_size = len(output_line.encode("utf-8"))
                    if encoded_size > self._max_diff_bytes - diff_bytes:
                        raise WorkspaceError(
                            "unified diff exceeds max_diff_bytes",
                            code="diff_byte_budget_exhausted",
                        )
                    chunks.append(output_line)
                    diff_bytes += encoded_size
        return "".join(chunks)

    def _validate_overlay_text(self, text: str, key: str) -> None:
        try:
            data = text.encode("utf-8")
        except UnicodeEncodeError as error:
            raise WorkspaceError(
                f"updated content must be UTF-8 encodable: {key}"
            ) from error
        if len(data) > self._max_file_bytes:
            raise WorkspaceError(f"updated content exceeds max_file_bytes: {key}")
        if any(byte < 32 and byte not in (9, 10, 13) for byte in data):
            raise WorkspaceError(f"binary updated content is not supported: {key}")

    def _read_current(self, relative_path: str | Path) -> tuple[str, str]:
        resolved = self.resolve_relative(relative_path)
        if not resolved.is_file():
            raise WorkspaceError(f"path is not a file: {relative_path}")
        key = resolved.relative_to(self._source_root).as_posix()
        if key not in self._originals:
            self._originals[key] = self._read_source_file(resolved, key)
        return key, self._overlay.get(key, self._originals[key])

    def _read_source_file(self, resolved: Path, key: str) -> str:
        try:
            with resolved.open("rb") as source_file:
                data = source_file.read(self._max_file_bytes + 1)
        except OSError as error:
            raise WorkspaceError(f"unable to read file: {key}") from error
        if len(data) > self._max_file_bytes:
            raise WorkspaceError(f"file exceeds max_file_bytes: {key}")
        if any(byte < 32 and byte not in (9, 10, 13) for byte in data):
            raise WorkspaceError(f"binary files are not supported: {key}")
        try:
            return normalize_newlines(data.decode("utf-8"))
        except UnicodeDecodeError as error:
            raise WorkspaceError(f"binary or non-UTF-8 file is not supported: {key}") from error
