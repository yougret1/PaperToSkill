from __future__ import annotations

import sys
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from effectslice.public_test_bridge import PublicTestBridge  # noqa: E402


def test_public_bridge_applies_overlay_and_runs_locked_command():
    source_root = RUN_ROOT / "tests" / "fixtures" / "aci_workspace" / "locked_source"
    workspace = OverlayWorkspace(source_root)
    workspace.replace_exact("pkg/main.py", "return 'old'", "return 'new'")
    bridge = PublicTestBridge(
        workspace=source_root,
        command=(
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "assert \"return 'new'\" in Path('pkg/main.py').read_text(); "
                "print('public pass')"
            ),
        ),
    )

    result = bridge.evaluate(workspace.unified_diff(), evaluation_id="step-01")

    assert result.passed is True
    assert result.returncode == 0
    assert "public pass" in result.feedback
    assert "return 'old'" in (source_root / "pkg" / "main.py").read_text()


def test_public_bridge_rejects_empty_diff_without_running_command():
    source_root = RUN_ROOT / "tests" / "fixtures" / "aci_workspace" / "locked_source"
    bridge = PublicTestBridge(
        workspace=source_root,
        command=(sys.executable, "-c", "raise SystemExit(99)"),
    )

    result = bridge.evaluate("", evaluation_id="step-01")

    assert result.passed is False
    assert result.returncode is None
    assert "non-empty source diff" in result.feedback


def test_registered_task_public_tests_run_on_patched_workspace():
    fixtures = [
        (
            RUN_ROOT / "task_workspaces" / "snap_mfse_v1",
            "snap_core.py",
            '    raise NotImplementedError("implement the paper-core reproduction task")',
            (
                "    matrix = counts @ counts.T\n"
                "    values, vectors = np.linalg.eigh(matrix)\n"
                "    order = np.argsort(values)[::-1][:n_components]\n"
                "    return values[order], vectors[:, order]"
            ),
            "test_snap_core_public.py",
        ),
        (
            RUN_ROOT / "task_workspaces" / "toolformer_filter_v1",
            "toolformer_filter.py",
            '    raise NotImplementedError("implement the paper-core reproduction task")',
            (
                "    with_mean = np.mean(logp_with_result, axis=1)\n"
                "    without_mean = np.minimum(\n"
                "        np.mean(logp_call_only, axis=1),\n"
                "        np.mean(logp_no_call, axis=1),\n"
                "    )\n"
                "    margins = with_mean - without_mean\n"
                "    return margins >= tau_filter, margins"
            ),
            "test_toolformer_filter_public.py",
        ),
    ]
    for source_root, source_file, old_text, new_text, public_test in fixtures:
        workspace = OverlayWorkspace(source_root)
        workspace.replace_exact(source_file, old_text, new_text)
        bridge = PublicTestBridge(
            workspace=source_root,
            command=(sys.executable, "-m", "pytest", public_test, "-q"),
        )

        result = bridge.evaluate(
            workspace.unified_diff(), evaluation_id=f"task-{source_file}"
        )

        assert result.passed is True, result.feedback
        assert result.returncode == 0
