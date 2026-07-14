import ast
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_paper_figures.py"
COMMITTED_FIGURES = ROOT / "paper" / "aaai" / "images"
FIGURE_CONTRACTS = {
    "papertoskill_pipeline.pdf": {
        "size": (Decimal("504"), Decimal("118.8")),
        "title": "PaperToSkill Pipeline",
    },
    "external_evidence_design.pdf": {
        "size": (Decimal("504"), Decimal("154.8")),
        "title": "External Evidence Design",
    },
}


def load_figure_module():
    spec = importlib.util.spec_from_file_location("make_paper_figures_under_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MakePaperFiguresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdfinfo = shutil.which("pdfinfo")
        if cls.pdfinfo is None:
            raise unittest.SkipTest("pdfinfo is not available on PATH")

    def run_generator(self, output_dir):
        env = os.environ.copy()
        env["MPLCONFIGDIR"] = str(output_dir / "mplconfig")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir", str(output_dir)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(
            0,
            result.returncode,
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}",
        )

    def read_pdfinfo(self, figure):
        result = subprocess.run(
            [self.pdfinfo, str(figure)],
            check=False,
            capture_output=True,
            text=True,
        )
        details = (
            f"{figure.name}\nstdout:\n{result.stdout}"
            f"\n\nstderr:\n{result.stderr}"
        )
        self.assertEqual(0, result.returncode, details)

        fields = {}
        for line in result.stdout.splitlines():
            field, separator, value = line.partition(":")
            if separator:
                fields[field.strip().casefold()] = value.strip()
        return fields, details

    def assert_pdf_contract(self, figure, contract):
        contents = figure.read_bytes()
        self.assertTrue(contents.startswith(b"%PDF"), figure.name)
        self.assertGreater(len(contents), 1000, figure.name)

        fields, details = self.read_pdfinfo(figure)
        try:
            page_count = int(fields["pages"])
        except (KeyError, ValueError) as error:
            self.fail(f"Invalid or missing Pages field: {error}\n{details}")
        self.assertEqual(1, page_count, details)

        page_size = fields.get("page size", "")
        size_match = re.search(
            r"(?P<width>\d+(?:\.\d+)?)\s*x\s*"
            r"(?P<height>\d+(?:\.\d+)?)\s*pts\b",
            page_size,
            flags=re.IGNORECASE,
        )
        self.assertIsNotNone(size_match, f"Invalid Page size field\n{details}")
        actual_size = (
            Decimal(size_match.group("width")),
            Decimal(size_match.group("height")),
        )
        self.assertEqual(contract["size"], actual_size, details)

        self.assertEqual(contract["title"], fields.get("title"), details)
        self.assertNotIn("creationdate", fields, details)
        self.assertNotIn("moddate", fields, details)

    def test_generated_pdf_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            self.run_generator(output_dir)

            generated_names = {path.name for path in output_dir.glob("*.pdf")}
            self.assertEqual(set(FIGURE_CONTRACTS), generated_names)
            for filename, contract in FIGURE_CONTRACTS.items():
                with self.subTest(filename=filename):
                    self.assert_pdf_contract(output_dir / filename, contract)

    def test_generation_is_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            first_output = Path(tmp) / "first"
            second_output = Path(tmp) / "second"
            self.run_generator(first_output)
            self.run_generator(second_output)

            for filename in FIGURE_CONTRACTS:
                with self.subTest(filename=filename):
                    self.assertEqual(
                        (first_output / filename).read_bytes(),
                        (second_output / filename).read_bytes(),
                    )

    def test_generated_pdfs_match_committed_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            self.run_generator(output_dir)

            for filename in FIGURE_CONTRACTS:
                with self.subTest(filename=filename):
                    self.assertEqual(
                        (COMMITTED_FIGURES / filename).read_bytes(),
                        (output_dir / filename).read_bytes(),
                    )

    def test_construction_error_closes_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"MPLCONFIGDIR": tmp}):
                module = load_figure_module()

            before = set(module.plt.get_fignums())
            after = before
            try:
                with mock.patch.object(
                    module, "add_box", side_effect=RuntimeError("construction failed")
                ):
                    with self.assertRaisesRegex(RuntimeError, "construction failed"):
                        module.make_pipeline_figure(Path(tmp) / "pipeline.pdf")
                after = set(module.plt.get_fignums())
            finally:
                for figure_number in after - before:
                    module.plt.close(figure_number)

            self.assertEqual(before, after)

    def test_source_does_not_use_empirical_plotting_calls(self):
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(SCRIPT))
        forbidden_calls = {"bar", "plot", "scatter", "errorbar"}

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                called_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                called_name = node.func.attr
            else:
                continue
            with self.subTest(called_name=called_name, line=node.lineno):
                self.assertNotIn(called_name, forbidden_calls)


if __name__ == "__main__":
    unittest.main()
