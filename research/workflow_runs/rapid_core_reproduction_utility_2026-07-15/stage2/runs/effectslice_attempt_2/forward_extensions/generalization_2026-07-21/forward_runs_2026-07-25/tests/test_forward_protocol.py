from __future__ import annotations

import sys
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

import controls_v2  # noqa: E402
import full_grid_registration as registration  # noqa: E402
import full_grid_runner as runner  # noqa: E402


class FullGridProtocolTests(unittest.TestCase):
    def synthetic_schedules(self) -> dict[str, list[dict[str, object]]]:
        schedules: dict[str, list[dict[str, object]]] = {}
        for repeat_id in registration.REPEAT_IDS:
            rows = []
            for source_index in range(1, registration.ROWS_PER_REPEAT + 1):
                # Mirror the source schedule property that block rows need not be
                # contiguous while preserving their relative source order.
                block_id = (source_index - 1) % 6 + 1
                rows.append(
                    {
                        "block_id": block_id,
                        "execution_id": f"{repeat_id}-{source_index}",
                        "logical_cell_id": f"cell-{source_index}",
                        "repeat_sequence_index": source_index,
                        "model_slot_id": "deepseek_primary",
                    }
                )
            schedules[repeat_id] = rows
        return schedules

    def test_registered_accounting(self) -> None:
        self.assertEqual(registration.ROWS_PER_REPEAT, 1296)
        self.assertEqual(registration.TOTAL_REPEAT_ROWS, 3888)
        self.assertEqual(controls_v2.REGISTERED_ROWS, 96)
        self.assertEqual(
            registration.TOTAL_REPEAT_ROWS + controls_v2.REGISTERED_ROWS, 3984
        )

    def test_repeat_execution_ids_are_distinct_and_stable(self) -> None:
        source_id = "fg5-source-example"
        ids = {
            registration.execution_id(repeat_id, source_id)
            for repeat_id in registration.REPEAT_IDS
        }
        self.assertEqual(len(ids), 3)
        self.assertEqual(
            ids,
            {
                registration.execution_id(repeat_id, source_id)
                for repeat_id in registration.REPEAT_IDS
            },
        )

    def test_transport_namespaces_are_repeat_specific(self) -> None:
        ids = {
            runner.transport_request_id(
                repeat_id, "preflight", "deepseek_primary"
            )
            for repeat_id in registration.REPEAT_IDS
        }
        self.assertEqual(len(ids), 3)

    def test_block_balanced_18_wave_schedule(self) -> None:
        jobs = registration.interleaved_dispatch(self.synthetic_schedules())
        self.assertEqual(len(jobs), 3888)
        self.assertEqual(len({job["execution_id"] for job in jobs}), 3888)
        self.assertEqual(
            Counter(job["repeat_id"] for job in jobs),
            {"FG6": 1296, "FG7": 1296, "FG8": 1296},
        )
        self.assertEqual({job["wave_index"] for job in jobs}, set(range(1, 19)))

        for block_id, expected_order in registration.BLOCK_REPEAT_ORDER.items():
            block_jobs = [job for job in jobs if job["block_id"] == block_id]
            observed_order = []
            for wave_position in (1, 2, 3):
                wave = [
                    job
                    for job in block_jobs
                    if job["block_wave_position"] == wave_position
                ]
                self.assertEqual(len(wave), registration.BLOCK_SIZE)
                self.assertEqual(len({job["repeat_id"] for job in wave}), 1)
                self.assertEqual(
                    [job["block_row_index"] for job in wave], list(range(1, 217))
                )
                observed_order.append(wave[0]["repeat_id"])
            self.assertEqual(tuple(observed_order), expected_order)

        for repeat_id in registration.REPEAT_IDS:
            source_indices = [
                job["source_sequence_index"]
                for job in jobs
                if job["repeat_id"] == repeat_id
            ]
            self.assertEqual(sorted(source_indices), list(range(1, 1297)))


class ControlsProtocolTests(unittest.TestCase):
    def test_deterministic_classifier(self) -> None:
        self.assertEqual(
            controls_v2.deterministic_control_state(
                digest_valid=True,
                contract_results={"case-1": True, "case-2": True},
            ),
            "Admit",
        )
        self.assertEqual(
            controls_v2.deterministic_control_state(
                digest_valid=True,
                contract_results={"case-1": True, "case-2": False},
            ),
            "Reject",
        )
        self.assertEqual(
            controls_v2.deterministic_control_state(
                digest_valid=False, contract_results=None
            ),
            "Invalid",
        )

    def test_control_factorial_accounting(self) -> None:
        self.assertEqual(len(controls_v2.ANCHOR_TASKS), 4)
        self.assertEqual(len(controls_v2.REGISTRIES), 2)
        self.assertEqual(len(controls_v2.ARMS), 4)
        self.assertEqual(len(controls_v2.REPETITIONS), 3)
        self.assertEqual(
            len(controls_v2.ANCHOR_TASKS)
            * len(controls_v2.REGISTRIES)
            * len(controls_v2.ARMS)
            * len(controls_v2.REPETITIONS),
            96,
        )

    def test_extended_path_atomic_write(self) -> None:
        scratch_root = EXPERIMENT_ROOT / "tmp"
        scratch_root.mkdir(exist_ok=True)
        scratch = Path(tempfile.mkdtemp(prefix="long-path-test-", dir=scratch_root))
        extended_scratch = controls_v2.fg1.windows_extended_path(scratch)
        target = extended_scratch / ("x" * 96 + ".json")
        try:
            controls_v2.fg1.atomic_write(target, b"{}\n")
            self.assertEqual(target.read_bytes(), b"{}\n")
            self.assertGreater(len(str(target)), 260)
        finally:
            shutil.rmtree(extended_scratch)


if __name__ == "__main__":
    unittest.main()
