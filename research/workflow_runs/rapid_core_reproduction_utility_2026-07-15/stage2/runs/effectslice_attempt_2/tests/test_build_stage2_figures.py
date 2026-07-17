import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_stage2_figures import build_stage2_figures, collect_figure_data  # noqa: E402


class BuildStage2FiguresTest(unittest.TestCase):
    def test_collects_only_recorded_confirmation_and_discovery_values(self):
        data = collect_figure_data(RUN_ROOT)

        self.assertEqual(data["tasks"], ["SNAP-MFSE", "Toolformer filter"])
        self.assertEqual(data["confirmation_scores"]["SNAP-MFSE"], [0.0, 1.0, 1.0])
        self.assertEqual(
            data["confirmation_scores"]["Toolformer filter"],
            [0.0, 1.0, 44.0 / 59.0],
        )
        self.assertEqual(data["preservation_violations"]["SNAP-MFSE"], [0, 0])
        self.assertEqual(
            data["preservation_violations"]["Toolformer filter"], [0, 15]
        )
        self.assertEqual(data["actions"]["SNAP-MFSE"], [16, 7, 16])
        self.assertEqual(data["actions"]["Toolformer filter"], [16, 5, 16])

    def test_builds_manuscript_figure_and_traceability_report(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            result = build_stage2_figures(RUN_ROOT, Path(tmp))
            figure = Path(result["figure"])
            report_path = Path(result["report"])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            magic = figure.read_bytes()[:8]

        self.assertEqual(magic, b"\x89PNG\r\n\x1a\n")
        self.assertGreater(report["figure_width_inches"], 6)
        self.assertEqual(report["dpi"], 300)
        self.assertEqual(len(report["data_sources"]), 6)
        self.assertIn("sealed confirmation", report["traceability_notes"][0].lower())


if __name__ == "__main__":
    unittest.main()
