import importlib.util
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_skillsbench_candidate_validation_amendment.py"
)
SPEC = importlib.util.spec_from_file_location(
    "build_skillsbench_candidate_validation_amendment", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def skill_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip()


class CandidateValidationAmendmentTests(unittest.TestCase):
    def test_screen_guard_rejects_candidate_arms_without_reading_rewards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            MODULE.atomic_json(root / "schedule.json", {"jobs": [{"condition": "B"}]})
            (root / "run_state.jsonl").write_text(
                json.dumps({"event": "finish", "condition": "P", "official_reward": "SECRET"})
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "screen state contains P/D"):
                MODULE.verify_screen_has_no_candidate_arms(root)

    def test_stage1_p2_preserves_body_assets_is_deterministic_and_reduces(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            official = root / "official"
            skill = official / "skill-a"
            skill.mkdir(parents=True)
            source_text = (
                "---\nname: skill-a\ndescription: A deliberately verbose routing description.\n---\n\n"
                "Run first:\n```bash\ntool --quarter 2025-q3\n```\n\n"
                "Run second:\n```bash\nother --quarter 2025-q3\n```\n"
            )
            (skill / "SKILL.md").write_text(source_text, encoding="utf-8")
            (skill / "scripts").mkdir()
            (skill / "scripts" / "tool.py").write_text("print('asset')\n", encoding="utf-8")

            class FakeConfig:
                def __init__(self, **_kwargs):
                    pass

            def fake_parse(path: Path):
                return SimpleNamespace(body=skill_body(path))

            def fake_reduce(path, output_dir, config, stage, tscg):
                self.assertEqual(1, stage)
                self.assertFalse(tscg)
                destination = output_dir / path.parent.name
                destination.mkdir(parents=True)
                body = skill_body(path)
                (destination / "SKILL.md").write_text(
                    f"---\nname: skill-a\ndescription: skill a.\n---\n\n{body}\n",
                    encoding="utf-8",
                )
                shutil.copytree(path.parent / "scripts", destination / "scripts")
                return SimpleNamespace(
                    output=destination,
                    original_stats=SimpleNamespace(description=10, body=40),
                    optimized_stats=SimpleNamespace(description=2, body=40),
                    stage_notes=["Stage 1 only"],
                )

            modules = {
                "skillreducer": types.ModuleType("skillreducer"),
                "skillreducer.config": types.ModuleType("skillreducer.config"),
                "skillreducer.parser": types.ModuleType("skillreducer.parser"),
                "skillreducer.pipeline": types.ModuleType("skillreducer.pipeline"),
            }
            modules["skillreducer"].__path__ = []
            modules["skillreducer.config"].Config = FakeConfig
            modules["skillreducer.parser"].parse_skill_md = fake_parse
            modules["skillreducer.pipeline"].reduce_skill = fake_reduce
            previous = {name: sys.modules.get(name) for name in modules}
            sys.modules.update(modules)
            try:
                hashes = []
                for number in (1, 2):
                    target = root / f"p2-{number}" / "skills"
                    target.mkdir(parents=True)
                    result = MODULE.generate_sec_p2(
                        official_skills=official,
                        target_skills=target,
                        reducer_root=root,
                    )
                    hashes.append(MODULE.sha256_tree(target))
                    candidate = target / "skill-a" / "SKILL.md"
                    self.assertEqual(skill_body(skill / "SKILL.md"), skill_body(candidate))
                    self.assertEqual(2, candidate.read_text(encoding="utf-8").count("--quarter"))
                    self.assertEqual(
                        MODULE.sha256_file(skill / "scripts" / "tool.py"),
                        MODULE.sha256_file(target / "skill-a" / "scripts" / "tool.py"),
                    )
                    self.assertGreater(result["eager_reduction"], 0)
                self.assertEqual(hashes[0], hashes[1])
            finally:
                for name, value in previous.items():
                    if value is None:
                        sys.modules.pop(name, None)
                    else:
                        sys.modules[name] = value


if __name__ == "__main__":
    unittest.main()
