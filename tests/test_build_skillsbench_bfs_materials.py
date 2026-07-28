import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_skillsbench_bfs_materials.py"
SPEC = importlib.util.spec_from_file_location("build_skillsbench_bfs_materials", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SkillsBenchMaterialsTests(unittest.TestCase):
    def test_rank_is_stable(self):
        self.assertEqual(MODULE.rank("seed", "task"), MODULE.rank("seed", "task"))
        self.assertNotEqual(MODULE.rank("seed", "task"), MODULE.rank("seed", "other"))

    def test_resource_filter_enforces_limits(self):
        good = MODULE.TaskMetadata("t", "medium", "natural-science", "public", 4, 8192, 0, 3600, 1)
        too_large = MODULE.TaskMetadata("t", "medium", "natural-science", "public", 5, 8192, 0, 3600, 1)
        self.assertTrue(MODULE.resource_eligible(good))
        self.assertFalse(MODULE.resource_eligible(too_large))

    def test_tree_hash_changes_with_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "a.txt"
            path.write_text("one", encoding="utf-8")
            first = MODULE.sha256_tree(root)
            path.write_text("two", encoding="utf-8")
            self.assertNotEqual(first, MODULE.sha256_tree(root))


if __name__ == "__main__":
    unittest.main()
