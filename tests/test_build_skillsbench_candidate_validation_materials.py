import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_skillsbench_candidate_validation_materials.py"
)
SPEC = importlib.util.spec_from_file_location(
    "build_skillsbench_candidate_validation_materials", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CandidateValidationMaterialsTests(unittest.TestCase):
    def test_frontmatter_only_is_a_strict_source_prefix(self):
        source = "---\nname: demo\ndescription: test\n---\n\n# Procedure\nDo work.\n"
        reduced = MODULE.frontmatter_only(source)
        self.assertEqual(reduced, "---\nname: demo\ndescription: test\n---\n")
        self.assertTrue(source.startswith(reduced))
        self.assertLess(len(reduced), len(source))

    def test_frontmatter_only_rejects_unbounded_input(self):
        with self.assertRaises(RuntimeError):
            MODULE.frontmatter_only("# No frontmatter\n")


if __name__ == "__main__":
    unittest.main()
