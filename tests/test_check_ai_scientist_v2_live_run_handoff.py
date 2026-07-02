import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_ai_scientist_v2_live_run_handoff.py"
sys.path.insert(0, str(ROOT / "scripts"))

from check_ai_scientist_v2_live_run_handoff import build_report  # noqa: E402


class CheckAIScientistV2LiveRunHandoffTest(unittest.TestCase):
    def test_current_handoff_is_complete_after_bounded_live_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "handoff.json"
            output_md = Path(tmp) / "handoff.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["ai_scientist_v2_live_seed_idea_selected"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_dry_run_artifacts_present"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_smoke_complete"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_completion_artifacts_present"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_successful_stage_attempt_present"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_best_nodes_not_buggy"])
            commands = "\n".join(report["next_commands"])
            self.assertIn("ANTHROPIC_BASE_URL", commands)
            self.assertIn("Remove-Item Env:\\AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE", commands)
            self.assertTrue(output_md.exists())

    def test_complete_smoke_without_completion_artifacts_is_ready_to_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ai_root = tmp_path / "ai-scientist-v2"
            ai_root.mkdir()
            (ai_root / "launch_scientist_bfts.py").write_text(
                "--dry_run --skip_writeup --skip_review",
                encoding="utf-8",
            )
            (ai_root / "bfts_config.yaml").write_text(
                "agent:\n  num_workers: 1\n  code:\n    model: claude-opus-4-8\n",
                encoding="utf-8",
            )
            dry_run_dir = ai_root / "experiments" / "2026-06-19_papertoskill_extractor_attempt_0"
            dry_run_dir.mkdir(parents=True)
            (dry_run_dir / "idea.json").write_text("{}", encoding="utf-8")
            (dry_run_dir / "idea.md").write_text("idea", encoding="utf-8")
            (dry_run_dir / "bfts_config.yaml").write_text("config", encoding="utf-8")
            seed = tmp_path / "seed.json"
            seed.write_text(
                json.dumps([{"Name": "papertoskill_extractor", "Title": "PaperToSkill"}]),
                encoding="utf-8",
            )
            smoke = tmp_path / "smoke.json"
            smoke.write_text(json.dumps({"overall_status": "complete"}), encoding="utf-8")

            report = build_report(tmp_path, ai_root, seed, Path("bfts_config.yaml"), smoke, 0)
            self.assertEqual("ready_to_run", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["ai_scientist_v2_live_smoke_complete"])
            self.assertEqual("pending", statuses["ai_scientist_v2_live_completion_artifacts_present"])
            commands = "\n".join(report["next_commands"])
            self.assertIn("ANTHROPIC_API_KEY", commands)
            self.assertNotIn("AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'", commands)


if __name__ == "__main__":
    unittest.main()
