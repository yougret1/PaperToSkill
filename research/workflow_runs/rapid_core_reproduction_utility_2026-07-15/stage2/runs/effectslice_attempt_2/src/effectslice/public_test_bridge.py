from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class PublicTestBridgeError(ValueError):
    """Raised when the locked public-test channel is misconfigured."""


@dataclass(frozen=True, slots=True)
class PublicTestEvaluation:
    feedback: str
    passed: bool
    returncode: int | None


class PublicTestBridge:
    """Run a fixed public command against a patch in an isolated copy."""

    _ENV_ALLOWLIST = frozenset(
        {
            "COMSPEC",
            "HOMEDRIVE",
            "HOMEPATH",
            "LOCALAPPDATA",
            "NUMBER_OF_PROCESSORS",
            "OS",
            "PATH",
            "PATHEXT",
            "PROCESSOR_ARCHITECTURE",
            "SYSTEMDRIVE",
            "SYSTEMROOT",
            "TEMP",
            "TMP",
            "USERPROFILE",
            "WINDIR",
        }
    )

    def __init__(
        self,
        *,
        workspace: str | Path,
        command: Sequence[str],
        timeout_seconds: float = 60.0,
        max_output_chars: int = 4_000,
    ) -> None:
        self._workspace = Path(workspace).resolve()
        if not self._workspace.is_dir():
            raise PublicTestBridgeError("workspace must be an existing directory")
        if (
            not isinstance(command, (list, tuple))
            or not command
            or any(not isinstance(part, str) or not part for part in command)
        ):
            raise PublicTestBridgeError("command must be a non-empty string sequence")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or timeout_seconds <= 0
        ):
            raise PublicTestBridgeError("timeout_seconds must be positive")
        if (
            isinstance(max_output_chars, bool)
            or not isinstance(max_output_chars, int)
            or max_output_chars < 1
        ):
            raise PublicTestBridgeError("max_output_chars must be positive")
        self._command = tuple(command)
        self._timeout_seconds = float(timeout_seconds)
        self._max_output_chars = max_output_chars

    @property
    def command(self) -> tuple[str, ...]:
        return self._command

    def evaluate(self, diff_text: str, *, evaluation_id: str) -> PublicTestEvaluation:
        if not isinstance(diff_text, str) or not diff_text:
            return self._feedback(
                status="rejected",
                message="public test requires a non-empty source diff",
                returncode=None,
            )
        if not isinstance(evaluation_id, str) or not evaluation_id:
            raise PublicTestBridgeError("evaluation_id must be non-empty")

        with tempfile.TemporaryDirectory(prefix="effectslice-public-test-") as temporary:
            temporary_root = Path(temporary)
            candidate_root = temporary_root / "workspace"
            shutil.copytree(
                self._workspace,
                candidate_root,
                ignore=shutil.ignore_patterns(
                    ".git", ".pytest_cache", "__pycache__", "*.pyc"
                ),
            )
            patch_path = temporary_root / "candidate.patch"
            patch_path.write_text(diff_text, encoding="utf-8", newline="\n")
            applied = subprocess.run(
                [
                    "git",
                    "apply",
                    "--recount",
                    "--whitespace=nowarn",
                    "--ignore-space-change",
                    str(patch_path),
                ],
                cwd=candidate_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
                env=self._sanitized_environment(),
            )
            if applied.returncode != 0:
                return self._feedback(
                    status="failed",
                    message="candidate patch could not be applied for public testing",
                    returncode=applied.returncode,
                    stderr=applied.stderr,
                )
            try:
                completed = subprocess.run(
                    list(self._command),
                    cwd=candidate_root,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=self._timeout_seconds,
                    env=self._sanitized_environment(),
                )
            except subprocess.TimeoutExpired as error:
                return self._feedback(
                    status="timeout",
                    message=f"public test timed out after {self._timeout_seconds:g} seconds",
                    returncode=None,
                    stdout=self._as_text(error.stdout),
                    stderr=self._as_text(error.stderr),
                )
            return self._feedback(
                status="passed" if completed.returncode == 0 else "failed",
                message="locked public test completed",
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )

    def _feedback(
        self,
        *,
        status: str,
        message: str,
        returncode: int | None,
        stdout: str = "",
        stderr: str = "",
    ) -> PublicTestEvaluation:
        payload = {
            "message": message,
            "returncode": returncode,
            "status": status,
            "stderr": self._tail(stderr),
            "stdout": self._tail(stdout),
        }
        return PublicTestEvaluation(
            feedback=json.dumps(payload, sort_keys=True, separators=(",", ":")),
            passed=status == "passed",
            returncode=returncode,
        )

    def _tail(self, value: str) -> str:
        return self._as_text(value)[-self._max_output_chars :]

    @staticmethod
    def _as_text(value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value

    @classmethod
    def _sanitized_environment(cls) -> dict[str, str]:
        environment = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in cls._ENV_ALLOWLIST
        }
        environment.update(
            {
                "NO_PROXY": "*",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
            }
        )
        return environment
