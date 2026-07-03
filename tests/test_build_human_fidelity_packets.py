import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
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
            self.assertIn("## Completion Requirements", packet_text)
            self.assertIn("## Generated Skill", packet_text)
            self.assertIn("## Curated Source Note Excerpt", packet_text)

            self.assertTrue((output_dir / "annotation_guide.md").exists())
            guide_text = (output_dir / "annotation_guide.md").read_text(encoding="utf-8")
            self.assertIn("confidence_0_to_1", guide_text)
            self.assertIn("scripts\\summarize_human_fidelity_annotations.py --strict", guide_text)

            with (output_dir / "annotation_template.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(24, len(rows))
            self.assertEqual("", rows[0]["score_0_to_3"])
            self.assertEqual("central_contribution", rows[0]["criterion_id"])
            self.assertIn("packet_path", rows[0])
            self.assertIn("evidence_locator", rows[0])
            self.assertIn("confidence_0_to_1", rows[0])
            self.assertIn("needs_discussion", rows[0])

            bundle_readme = output_dir / "reviewer_bundle_README.md"
            bundle_manifest = output_dir / "reviewer_bundle_manifest.json"
            bundle_zip = output_dir / "human_fidelity_reviewer_bundle.zip"
            self.assertTrue(bundle_readme.exists())
            self.assertTrue(bundle_manifest.exists())
            self.assertTrue(bundle_zip.exists())
            manifest = json.loads(bundle_manifest.read_text(encoding="utf-8"))
            self.assertEqual(24, manifest["required_annotation_rows"])
            archive_paths = {item["archive_path"] for item in manifest["files"]}
            self.assertIn("human_fidelity_review/annotation_template.csv", archive_paths)
            self.assertIn("human_fidelity_review/ai_scientist_v2_human_fidelity_packet.md", archive_paths)
            with zipfile.ZipFile(bundle_zip) as archive:
                names = set(archive.namelist())
            self.assertIn("human_fidelity_review/REVIEWER_README.md", names)
            self.assertIn("human_fidelity_review/reviewer_bundle_manifest.json", names)
            self.assertIn("human_fidelity_review/toolformer_human_fidelity_packet.md", names)


if __name__ == "__main__":
    unittest.main()
