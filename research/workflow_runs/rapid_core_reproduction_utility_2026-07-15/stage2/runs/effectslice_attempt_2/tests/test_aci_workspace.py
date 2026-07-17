import errno
import sys
import unittest
import uuid
from dataclasses import FrozenInstanceError
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_workspace import (  # noqa: E402
    EditResult,
    OverlayWorkspace,
    SearchHit,
    WorkspaceError,
    normalize_newlines,
)


class OverlayWorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.fixture_root = RUN_ROOT / "tests" / "fixtures" / "aci_workspace"
        self.source_root = self.fixture_root / "locked_source"

    def workspace(self, **overrides):
        options = {
            "max_file_bytes": 1024,
            "max_search_results": 2,
            "max_open_lines": 3,
        }
        options.update(overrides)
        return OverlayWorkspace(self.source_root, **options)

    def test_search_is_literal_deterministic_and_bounded(self):
        workspace = self.workspace()

        hits = workspace.search("a.b")

        self.assertEqual(
            hits,
            (
                SearchHit("alpha.txt", 2, "literal a.b needle"),
                SearchHit("alpha.txt", 4, "literal a.b needle"),
            ),
        )
        self.assertNotIn("literal a.b third", tuple(hit.text for hit in hits))
        with self.assertRaises(FrozenInstanceError):
            hits[0].line_number = 99

    def test_search_can_be_scoped_to_a_source_subdirectory(self):
        workspace = self.workspace()

        hits = workspace.search("return 'old'", relative_dir="pkg")

        self.assertEqual(hits, (SearchHit("pkg/main.py", 2, "    return 'old'"),))
        self.assertEqual(
            workspace.search("literal a.b", relative_dir="alpha.txt"),
            (
                SearchHit("alpha.txt", 2, "literal a.b needle"),
                SearchHit("alpha.txt", 4, "literal a.b needle"),
            ),
        )

    def test_normalizes_windows_and_legacy_line_endings_for_exact_edits(self):
        self.assertEqual(
            normalize_newlines("first\r\nsecond\rthird\n"),
            "first\nsecond\nthird\n",
        )

    def test_open_lines_returns_a_bounded_one_based_inclusive_window(self):
        workspace = self.workspace(max_open_lines=2)

        self.assertEqual(
            workspace.open_lines("alpha.txt", 2, 3),
            ("literal a.b needle", "middle"),
        )
        with self.assertRaisesRegex(WorkspaceError, "line window exceeds"):
            workspace.open_lines("alpha.txt", 1, 3)

    def test_replace_exact_changes_only_the_overlay(self):
        workspace = self.workspace()
        source_before = (self.source_root / "pkg" / "main.py").read_text(encoding="utf-8")

        result = workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")

        self.assertEqual(result, EditResult("pkg/main.py", 1, True))
        self.assertEqual(
            workspace.open_lines("pkg/main.py", 1, 2),
            ("def value():", "    return 'new'"),
        )
        self.assertEqual(
            workspace.search("return 'new'"),
            (SearchHit("pkg/main.py", 2, "    return 'new'"),),
        )
        self.assertEqual(
            (self.source_root / "pkg" / "main.py").read_text(encoding="utf-8"),
            source_before,
        )
        with self.assertRaises(FrozenInstanceError):
            result.changed = False

    def test_replace_exact_rejects_missing_or_repeated_text(self):
        workspace = self.workspace()

        with self.assertRaisesRegex(WorkspaceError, "not found"):
            workspace.replace_exact("pkg/main.py", "missing text", "replacement")
        with self.assertRaisesRegex(WorkspaceError, "more than once"):
            workspace.replace_exact("alpha.txt", "literal a.b needle", "replacement")

    def test_replace_exact_rejects_oversize_content_without_mutating_prior_overlay(self):
        workspace = self.workspace(max_file_bytes=40)
        workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")
        diff_before = workspace.unified_diff()

        with self.assertRaisesRegex(WorkspaceError, "max_file_bytes"):
            workspace.replace_exact("pkg/main.py", "new", "x" * 64)

        self.assertEqual(workspace.open_lines("pkg/main.py", 2, 2), ("    return 'new'",))
        self.assertEqual(workspace.unified_diff(), diff_before)

    def test_replace_exact_rejects_control_bytes_without_mutating_prior_overlay(self):
        workspace = self.workspace()
        workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")
        diff_before = workspace.unified_diff()

        with self.assertRaisesRegex(WorkspaceError, "binary"):
            workspace.replace_exact("pkg/main.py", "new", "bad\x00content")

        self.assertEqual(workspace.open_lines("pkg/main.py", 2, 2), ("    return 'new'",))
        self.assertEqual(workspace.unified_diff(), diff_before)

    def test_replace_exact_rejects_non_utf8_text_without_mutating_prior_overlay(self):
        workspace = self.workspace()
        workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")
        diff_before = workspace.unified_diff()

        with self.assertRaisesRegex(WorkspaceError, "UTF-8"):
            workspace.replace_exact("pkg/main.py", "new", "\ud800")

        self.assertEqual(workspace.open_lines("pkg/main.py", 2, 2), ("    return 'new'",))
        self.assertEqual(workspace.unified_diff(), diff_before)

    def test_unified_diff_is_deterministic_git_apply_compatible_and_omits_unchanged_files(self):
        workspace = self.workspace()
        workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")

        expected = (
            "--- a/pkg/main.py\n"
            "+++ b/pkg/main.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def value():\n"
            "-    return 'old'\n"
            "+    return 'new'\n"
        )

        self.assertEqual(workspace.unified_diff(), expected)
        self.assertEqual(workspace.unified_diff(), expected)
        self.assertNotIn("unchanged.py", workspace.unified_diff())

    def test_reverting_an_edit_omits_the_file_from_the_diff(self):
        workspace = self.workspace()
        workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")
        result = workspace.replace_exact("pkg/main.py", "return 'new'", "return 'old'")

        self.assertEqual(result, EditResult("pkg/main.py", 1, True))
        self.assertEqual(workspace.unified_diff(), "")

    def test_unified_diff_rejects_output_above_the_diff_byte_budget(self):
        workspace = self.workspace(max_diff_bytes=40)
        workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")

        with self.assertRaisesRegex(
            WorkspaceError, "diff_byte_budget_exhausted"
        ) as caught:
            workspace.unified_diff()

        self.assertEqual(caught.exception.code, "diff_byte_budget_exhausted")

    def test_rejects_traversal_and_absolute_paths(self):
        workspace = self.workspace()

        with self.assertRaisesRegex(WorkspaceError, "escapes workspace"):
            workspace.resolve_relative("../outside.txt")
        with self.assertRaisesRegex(WorkspaceError, "absolute paths"):
            workspace.resolve_relative((self.source_root / "alpha.txt").resolve())

    def test_rejects_explicit_access_to_repository_metadata(self):
        workspace = self.workspace()

        with self.assertRaisesRegex(WorkspaceError, "excluded directory"):
            workspace.open_lines(".git/config", 1, 1)
        with self.assertRaisesRegex(WorkspaceError, "excluded directory"):
            workspace.search("secret", relative_dir=".git")

    def test_rejects_symlink_escape_when_symlinks_are_supported(self):
        symlink_fixture = self.fixture_root / "symlink_case"
        source_root = symlink_fixture / "locked_source"
        outside = symlink_fixture / "outside.txt"
        link = source_root / f"outside-link-{uuid.uuid4().hex}.txt"
        try:
            link.symlink_to(outside)
        except NotImplementedError as error:
            self.skipTest(f"symlinks are unavailable: {error}")
        except OSError as error:
            unavailable = getattr(error, "winerror", None) == 1314 or error.errno in {
                errno.EACCES,
                errno.EPERM,
            }
            if unavailable:
                self.skipTest(f"symlinks are unavailable: {error}")
            raise
        self.addCleanup(link.unlink)

        with self.assertRaisesRegex(WorkspaceError, "escapes workspace"):
            OverlayWorkspace(source_root).open_lines(link.name, 1, 1)

    def test_rejects_binary_files(self):
        with self.assertRaisesRegex(WorkspaceError, "binary"):
            self.workspace().open_lines("binary.dat", 1, 1)

    def test_rejects_files_over_the_read_limit(self):
        with self.assertRaisesRegex(WorkspaceError, "exceeds"):
            self.workspace(max_file_bytes=8).open_lines("large.txt", 1, 1)

    def test_search_raises_when_file_budget_blocks_a_late_match(self):
        workspace = self.workspace(max_search_files=1)

        with self.assertRaisesRegex(
            WorkspaceError, "search_file_budget_exhausted"
        ) as caught:
            workspace.search("return 'old'")

        self.assertEqual(caught.exception.code, "search_file_budget_exhausted")

    def test_search_raises_when_aggregate_byte_budget_blocks_an_absent_query(self):
        alpha_bytes = len((self.source_root / "alpha.txt").read_bytes())
        workspace = self.workspace(max_search_bytes=alpha_bytes)

        with self.assertRaisesRegex(
            WorkspaceError, "search_byte_budget_exhausted"
        ) as caught:
            workspace.search("not present anywhere")

        self.assertEqual(caught.exception.code, "search_byte_budget_exhausted")

    def test_rejects_nonpositive_search_and_diff_budgets(self):
        for option in ("max_search_files", "max_search_bytes", "max_diff_bytes"):
            with self.subTest(option=option), self.assertRaisesRegex(
                WorkspaceError, "positive integer"
            ):
                self.workspace(**{option: 0})


if __name__ == "__main__":
    unittest.main()
