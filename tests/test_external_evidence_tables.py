import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES_TEX = ROOT / "paper" / "aaai" / "papertoskill_external_evidence_tables.tex"


def labeled_table(tex: str, label: str) -> str:
    label_position = tex.index(rf"\label{{{label}}}")
    table_start = tex.rfind(r"\begin{table", 0, label_position)
    table_end = tex.find(r"\end{table", label_position)
    if table_start < 0 or table_end < 0:
        raise ValueError(f"Could not find table environment for {label}")
    return tex[table_start:table_end]


def table_body_rows(tex: str, label: str) -> list[list[str]]:
    table = labeled_table(tex, label)
    midrule_position = table.index(r"\midrule") + len(r"\midrule")
    bottomrule_position = table.index(r"\bottomrule", midrule_position)
    body = table[midrule_position:bottomrule_position]

    rows = []
    for row in body.split(r"\\"):
        content = " ".join(
            line.strip()
            for line in row.splitlines()
            if line.strip() and not line.lstrip().startswith("%")
        )
        if content:
            rows.append([cell.strip() for cell in content.split("&")])
    return rows


def captions(tex: str) -> list[str]:
    command = r"\caption{"
    extracted = []
    position = 0
    while True:
        command_position = tex.find(command, position)
        if command_position < 0:
            return extracted

        argument_start = command_position + len(command)
        depth = 1
        cursor = argument_start
        while cursor < len(tex) and depth:
            if tex[cursor] == "{" and (cursor == 0 or tex[cursor - 1] != "\\"):
                depth += 1
            elif tex[cursor] == "}" and (cursor == 0 or tex[cursor - 1] != "\\"):
                depth -= 1
            cursor += 1
        if depth:
            raise ValueError("Unclosed caption")

        extracted.append(tex[argument_start : cursor - 1])
        position = cursor


def table_caption(tex: str, label: str) -> str:
    extracted = captions(labeled_table(tex, label))
    if len(extracted) != 1:
        raise ValueError(f"Expected exactly one caption for {label}")
    return extracted[0]


class ExternalEvidenceTablesTest(unittest.TestCase):
    def setUp(self):
        self.tex = TABLES_TEX.read_text(encoding="utf-8")

    def test_live_real_reuse_table_has_final_size_pending_rows(self):
        rows = table_body_rows(self.tex, "tab:external-live-real-reuse")

        self.assertEqual(9, len(rows))
        for row in rows:
            self.assertEqual(7, len(row), row)
            self.assertEqual([r"\pendingevidencevalue"] * 4, row[2:6], row)
            self.assertEqual("Pending external evidence", row[-1], row)

    def test_independent_human_table_has_final_size_pending_rows(self):
        rows = table_body_rows(self.tex, "tab:external-independent-human")

        self.assertEqual(6, len(rows))
        for row in rows:
            self.assertEqual(7, len(row), row)
            self.assertEqual([r"\pendingevidencevalue"] * 5, row[1:6], row)
            self.assertEqual("Pending external evidence", row[-1], row)

    def test_pending_value_renders_as_two_literal_hyphens(self):
        self.assertIn(
            r"\newcommand{\pendingevidencevalue}{\texttt{-{}-}}",
            self.tex,
        )

    def test_target_captions_are_exact_and_make_no_schedule_or_completion_claims(self):
        forbidden_words = ("planned", "preregistered", "completed", "future")
        expected_captions = {
            "tab:external-live-real-reuse": "Cross-model live real-reuse evaluation.",
            "tab:external-independent-human": "Expanded independent human evaluation.",
        }

        for label, expected_caption in expected_captions.items():
            with self.subTest(label=label):
                caption = table_caption(self.tex, label)
                self.assertEqual(expected_caption, caption)
                lowercase_caption = caption.lower()
                for word in forbidden_words:
                    self.assertNotIn(word, lowercase_caption)


if __name__ == "__main__":
    unittest.main()
