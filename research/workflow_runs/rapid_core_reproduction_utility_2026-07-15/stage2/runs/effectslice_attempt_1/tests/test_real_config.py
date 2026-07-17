import json
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]


class RealConfigTest(unittest.TestCase):
    def test_every_declared_source_map_exists(self):
        config = json.loads(
            (RUN_ROOT / "configs/experiment_config.json").read_text(encoding="utf-8")
        )
        project_root = Path(config["project_root"])

        for paper_id, relative_path in config["source_maps"].items():
            with self.subTest(paper_id=paper_id):
                self.assertTrue(
                    (project_root / relative_path).is_file(),
                    f"missing configured source map: {relative_path}",
                )


if __name__ == "__main__":
    unittest.main()
