import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_blind_candidate_annotations.py"
)
SPEC = importlib.util.spec_from_file_location("run_blind_candidate_annotations", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class BlindCandidateAnnotationTests(unittest.TestCase):
    def test_cli_accepts_effective_pool_tasks_and_two_fresh_reviewers(self):
        args = MODULE.parse_args(
            [
                "--p-pool",
                "effective-p",
                "--tasks",
                "task-a",
                "task-b",
                "--reviewer",
                "fresh-a:model-a",
                "--reviewer",
                "fresh-b:model-b",
            ]
        )
        self.assertEqual(Path("effective-p"), args.p_pool)
        self.assertEqual(["task-a", "task-b"], args.tasks)
        self.assertEqual(
            [("fresh-a", "model-a"), ("fresh-b", "model-b")], args.reviewers
        )

    def test_run_uses_only_bound_blind_inputs_without_reading_outcomes_or_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skillsbench = root / "skillsbench"
            materials = root / "materials"
            effective_p = root / "effective-p"
            output = root / "labels" / "blind_labels.json"
            task = "task-a"

            write(skillsbench / "tasks" / task / "task.md", "PUBLIC CONTRACT")
            write(
                skillsbench
                / "tasks"
                / task
                / "environment"
                / "skills"
                / "SKILL.md",
                "OFFICIAL SKILL",
            )
            write(
                materials
                / "candidate_pool"
                / "P"
                / task
                / "skills"
                / "SKILL.md",
                "OLD P MUST NOT BE READ",
            )
            write(
                materials
                / "candidate_pool"
                / "D"
                / task
                / "skills"
                / "SKILL.md",
                "DESTRUCTIVE CANDIDATE",
            )
            write(effective_p / task / "skills" / "SKILL.md", "EFFECTIVE P2")
            write(materials / "outcomes" / "private.json", "TOP_SECRET_OUTCOME")

            missing_api_document = root / "credentials-must-not-be-read.md"
            args = argparse.Namespace(
                materials=materials,
                skillsbench_root=skillsbench,
                p_pool=effective_p,
                tasks=[task],
                reviewers=["fresh-a:model-a", "fresh-b:model-b"],
                api_document=missing_api_document,
                output=output,
            )
            prompts: list[str] = []

            def fake_request(url: str, api_key: str, model: str, prompt: str) -> dict:
                prompts.append(prompt)
                return {
                    "task_id": task,
                    "P_label": "intended-preserving",
                    "D_label": "destructive",
                    "P_rationale": "P keeps the public contract.",
                    "D_rationale": "D removes a required procedure.",
                }

            with mock.patch.object(
                MODULE, "load_credentials", return_value=("not-a-real-key", "https://api.test")
            ) as load_credentials, mock.patch.object(
                MODULE, "request_label", side_effect=fake_request
            ) as request_label:
                payload = MODULE.run(args)

            load_credentials.assert_called_once_with(missing_api_document)
            self.assertFalse(missing_api_document.exists())
            self.assertEqual(2, request_label.call_count)
            self.assertEqual(2, len(prompts))
            self.assertTrue(all("EFFECTIVE P2" in prompt for prompt in prompts))
            self.assertTrue(all("OLD P MUST NOT BE READ" not in prompt for prompt in prompts))
            self.assertTrue(all("TOP_SECRET_OUTCOME" not in prompt for prompt in prompts))

            expected_task_hash = MODULE.sha256_tree(effective_p / task / "skills")
            expected_pool_hash = MODULE.sha256_tree(effective_p)
            binding = payload["input_bindings"]["effective_P_pool"]
            self.assertEqual("--p-pool", binding["source"])
            self.assertEqual(expected_pool_hash, binding["tree_sha256"])
            self.assertEqual(expected_task_hash, binding["task_skills_sha256"][task])
            self.assertEqual(
                ["fresh-a", "fresh-b"],
                [row["reviewer_id"] for row in payload["reviewers"]],
            )
            self.assertEqual(
                {expected_task_hash},
                {row["P_skills_sha256"] for row in payload["records"]},
            )

            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload, saved)
            for reviewer_id in ("fresh-a", "fresh-b"):
                raw_path = (
                    output.parent / "blind_annotation_raw" / f"{reviewer_id}.json"
                )
                raw = json.loads(
                    raw_path.read_text(encoding="utf-8")
                )
                self.assertEqual(
                    expected_pool_hash,
                    raw["input_bindings"]["effective_P_pool"]["tree_sha256"],
                )
                self.assertEqual("prohibited", raw["outcome_access"])

    def test_defaults_remain_the_original_tasks_pool_and_reviewers(self):
        args = MODULE.parse_args([])
        self.assertEqual(list(MODULE.TASKS), args.tasks)
        self.assertIsNone(args.p_pool)
        self.assertEqual(MODULE.DEFAULT_REVIEWERS, MODULE.reviewer_specs_for(args))


if __name__ == "__main__":
    unittest.main()
