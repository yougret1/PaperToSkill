import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "benchflow_windows_compat.py"
SPEC = importlib.util.spec_from_file_location("benchflow_windows_compat", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


@unittest.skipUnless(importlib.util.find_spec("benchflow"), "BenchFlow environment is not active")
class BenchFlowWindowsCompatTests(unittest.TestCase):
    def test_container_paths_remain_posix(self):
        import benchflow.sandbox.lockdown as lockdown
        import benchflow.sandbox.setup as setup

        MODULE.patch_skill_injection()
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp) / "task"
            skills = Path(tmp) / "skills"
            (task / "environment").mkdir(parents=True)
            (skills / "alpha").mkdir(parents=True)
            (skills / "alpha" / "SKILL.md").write_text("skill", encoding="utf-8")
            dockerfile = task / "environment" / "Dockerfile"
            dockerfile.write_text("FROM ubuntu:24.04\n", encoding="utf-8")

            setup._inject_skills_into_dockerfile(task, skills)
            text = dockerfile.read_text(encoding="utf-8")
            raw = dockerfile.read_bytes()

        self.assertIn("mkdir -p /root/.agents", text)
        self.assertNotIn("mkdir -p \\root", text)
        self.assertNotIn(b"\r\n", raw)
        lockdown._validate_locked_path("/oracle")
        command = lockdown._legacy_root_tool_link_cmd("/root/.cache", "/home/agent/.cache")
        self.assertIn("mkdir -p /home/agent", command)
        self.assertNotIn("\\home", command)

    def test_codex_installer_applies_configured_model_catalog_patch(self):
        import benchflow.agents.install as agent_install

        MODULE.patch_codex_acp_installer()
        command = agent_install.AGENT_INSTALLERS["codex-acp"]
        self.assertIn("benchflow-codex-acp-model-patch.cjs", command)
        self.assertIn("/opt/benchflow/node/bin/node", command)
        self.assertNotIn("gpt-5.6-sol", command)


if __name__ == "__main__":
    unittest.main()
