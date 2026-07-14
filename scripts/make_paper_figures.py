"""Generate conceptual companion figures for the PaperToSkill paper."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "paper" / "aaai" / "images"

WHITE = "#FFFFFF"
INK = "#20302E"
MUTED_INK = "#596966"
LOCAL = "#19766A"
LOCAL_FILL = "#EAF5F2"
EXTERNAL = "#B64638"
EXTERNAL_FILL = "#FAECE9"
HAIRLINE = "#CAD5D2"

PDF_METADATA = {
    "Author": "PaperToSkill",
    "Creator": "scripts/make_paper_figures.py",
    "CreationDate": None,
    "ModDate": None,
}


def add_box(
    ax: Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    *,
    edge_color: str,
    fill_color: str,
    font_size: float = 8.0,
) -> None:
    """Add one labeled, rounded conceptual stage."""
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        linewidth=1.25,
        edgecolor=edge_color,
        facecolor=fill_color,
        zorder=2,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2,
        y + height / 2,
        label,
        ha="center",
        va="center",
        color=INK,
        fontsize=font_size,
        fontweight="medium",
        linespacing=1.18,
        zorder=3,
    )


def add_arrow(
    ax: Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str,
) -> None:
    """Connect conceptual stages with a compact directional arrow."""
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=9.5,
        linewidth=1.15,
        color=color,
        shrinkA=0,
        shrinkB=0,
        zorder=4,
    )
    ax.add_patch(arrow)


def new_canvas(size: tuple[float, float]) -> tuple[Figure, Axes]:
    """Create a fixed-size, axis-free canvas."""
    figure = plt.figure(figsize=size, facecolor=WHITE)
    axis = figure.add_axes((0.0, 0.0, 1.0, 1.0))
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.set_axis_off()
    return figure, axis


def save_figure(figure: Figure, destination: Path, *, title: str) -> None:
    """Save a deterministic one-page PDF."""
    figure.savefig(
        destination,
        format="pdf",
        facecolor=WHITE,
        edgecolor="none",
        metadata={**PDF_METADATA, "Title": title},
    )


def make_pipeline_figure(destination: Path) -> None:
    """Show the audited package pipeline and its external evidence layer."""
    figure, axis = new_canvas((7.0, 1.65))
    try:
        axis.text(
            0.025,
            0.875,
            "Audited package pipeline",
            ha="left",
            va="center",
            color=LOCAL,
            fontsize=8.0,
            fontweight="bold",
        )
        axis.add_patch(
            Rectangle(
                (0.025, 0.815),
                0.699,
                0.018,
                linewidth=0,
                facecolor=LOCAL,
                zorder=1,
            )
        )
        axis.text(
            0.766,
            0.875,
            "External-evidence layer",
            ha="left",
            va="center",
            color=EXTERNAL,
            fontsize=8.0,
            fontweight="bold",
        )
        axis.add_patch(
            Rectangle(
                (0.766, 0.815),
                0.209,
                0.018,
                linewidth=0,
                facecolor=EXTERNAL,
                zorder=1,
            )
        )

        stages = (
            ("Extracted paper\n+ source anchors", LOCAL, LOCAL_FILL),
            ("Operational note\n+ failure boundaries", LOCAL, LOCAL_FILL),
            ("Portable skill\n+ deterministic gates", LOCAL, LOCAL_FILL),
            ("Live reuse\n+ independent review", EXTERNAL, EXTERNAL_FILL),
        )
        positions = (0.025, 0.272, 0.519, 0.766)
        box_width = 0.209
        box_y = 0.275
        box_height = 0.41

        for x, (label, edge_color, fill_color) in zip(
            positions, stages, strict=True
        ):
            add_box(
                axis,
                x,
                box_y,
                box_width,
                box_height,
                label,
                edge_color=edge_color,
                fill_color=fill_color,
            )

        center_y = box_y + box_height / 2
        for index in range(3):
            arrow_color = LOCAL if index < 2 else EXTERNAL
            add_arrow(
                axis,
                (positions[index] + box_width + 0.006, center_y),
                (positions[index + 1] - 0.006, center_y),
                color=arrow_color,
            )

        axis.text(
            0.025,
            0.12,
            "Paper-grounded transformation",
            ha="left",
            va="center",
            color=MUTED_INK,
            fontsize=7.5,
        )
        axis.text(
            0.975,
            0.12,
            "Evidence beyond local validation",
            ha="right",
            va="center",
            color=EXTERNAL,
            fontsize=7.5,
        )

        save_figure(figure, destination, title="PaperToSkill Pipeline")
    finally:
        plt.close(figure)


def add_track(
    axis: Axes,
    *,
    y: float,
    track_label: str,
    labels: Sequence[str],
) -> None:
    """Add one four-step external-evidence track."""
    axis.text(
        0.025,
        y + 0.125,
        track_label,
        ha="left",
        va="center",
        color=EXTERNAL,
        fontsize=8.0,
        fontweight="bold",
        linespacing=1.12,
    )
    axis.add_patch(
        Rectangle(
            (0.167, y - 0.025),
            0.003,
            0.30,
            linewidth=0,
            facecolor=HAIRLINE,
            zorder=1,
        )
    )

    positions = (0.198, 0.397, 0.596, 0.795)
    box_width = 0.166
    box_height = 0.25
    for x, label in zip(positions, labels, strict=True):
        add_box(
            axis,
            x,
            y,
            box_width,
            box_height,
            label,
            edge_color=EXTERNAL,
            fill_color=EXTERNAL_FILL,
            font_size=7.7,
        )

    center_y = y + box_height / 2
    for index in range(3):
        add_arrow(
            axis,
            (positions[index] + box_width + 0.007, center_y),
            (positions[index + 1] - 0.007, center_y),
            color=EXTERNAL,
        )


def make_external_evidence_figure(destination: Path) -> None:
    """Show the two conceptual external-evidence tracks."""
    figure, axis = new_canvas((7.0, 2.15))
    try:
        add_track(
            axis,
            y=0.59,
            track_label="Live\nreal-reuse",
            labels=(
                "Model families",
                "Task slices",
                "Repeated seeds",
                "Paired outcomes",
            ),
        )
        add_track(
            axis,
            y=0.16,
            track_label="Independent\nreview",
            labels=(
                "Paper artifacts",
                "Independent raters",
                "Six criteria",
                "Scores + agreement",
            ),
        )

        axis.add_patch(
            Rectangle(
                (0.025, 0.485),
                0.95,
                0.006,
                linewidth=0,
                facecolor=HAIRLINE,
                zorder=1,
            )
        )

        save_figure(figure, destination, title="External Evidence Design")
    finally:
        plt.close(figure)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate the PaperToSkill conceptual PDF figures."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated PDF figures.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate both paper figures."""
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    make_pipeline_figure(output_dir / "papertoskill_pipeline.pdf")
    make_external_evidence_figure(output_dir / "external_evidence_design.pdf")


if __name__ == "__main__":
    main()
