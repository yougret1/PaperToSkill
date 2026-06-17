import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_human_fidelity_packets.py"
CONFIG = ROOT / "benchmarks" / "human_fidelity_review_v0.json"


class BuildHumanFidelityPacketsTest(unittest.TestCase):
    def test_generates_review_packets_and_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "human_fidelity_packets"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--config",
                    str(CONFIG),
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            index = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(4, len(index["packets"]))
            packet_names = [Path(row["packet_path"]).name for row in index["packets"]]
            self.assertEqual(
                [
                    "ai_scientist_v2_human_fidelity_packet.md",
                    "reflexion_human_fidelity_packet.md",
                    "aide_human_fidelity_packet.md",
                    "toolformer_human_fidelity_packet.md",
                ],
                packet_names,
            )

            packet_text = (output_dir / packet_names[0]).read_text(encoding="utf-8")
            self.assertIn("Central contribution fidelity", packet_text)
            self.assertIn("## Generated Skill", packet_text)
            self.assertIn("## Curated Source Note Excerpt", packet_text)

            with (output_dir / "annotation_template.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(24, len(rows))
            self.assertEqual("", rows[0]["score_0_to_3"])
            self.assertEqual("central_contribution", rows[0]["criterion_id"])


if __name__ == "__main__":
    unittest.main()
