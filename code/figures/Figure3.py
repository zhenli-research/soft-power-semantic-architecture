"""Fig. 3: annual family counts (a) and annual family prevalence (b).

Reads data/figure3_v3_plot_data.csv and writes outputs/Fig3.pdf and outputs/Fig3.tif
(119 x 118 mm, 600 dpi). Run from the repository root.
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import fontManager
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "data" / "figure3_v3_plot_data.csv"
OUT_DIR = Path(os.environ.get("SOFTPOWER_OUTPUT_DIR", str(REPO_ROOT / "outputs"))).expanduser().resolve()

MM_PER_IN = 25.4
WIDTH_MM, HEIGHT_MM = 119.0, 118.0

FAMILY_ORDER = ["F1", "F2", "F3", "F4", "F5"]
FAMILY_LABELS = {
    "F1": "F1 Statecraft", "F2": "F2 Influence & reputation",
    "F3": "F3 Culture & branding", "F4": "F4 Resources & strategy",
    "F5": "F5 Education & exchange",
}
FAMILY_COLORS = {"F1": "#59A14F", "F2": "#4E79A7", "F3": "#A47ACC", "F4": "#D9A620", "F5": "#E66A95"}
MARKERS = {"F1": "o", "F2": "s", "F3": "^", "F4": "D", "F5": "P"}
AXIS, GRID, NOTE = "#333333", "#E3E3E3", "#555B61"


def configure_style() -> None:
    available = {f.name for f in fontManager.ttflist}
    font = "Arial" if "Arial" in available else "Liberation Sans"
    if font != "Arial":
        print("Arial not found; using Liberation Sans (metric-compatible).")
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [font, "Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 7.0, "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "axes.unicode_minus": False,
    })


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_FILE)
    required = {"year", "family_id", "n_works", "prevalence_pct_recomputed", "plotted_in_panel_a", "plotted_in_panel_b"}
    if not required.issubset(data.columns):
        raise ValueError(f"{DATA_FILE.name} is missing columns: {sorted(required - set(data.columns))}")
    if len(data) != 180 or data.duplicated(["year", "family_id"]).any():
        raise ValueError(f"{DATA_FILE.name} should contain 180 unique year-family rows")
    return data


def style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
        ax.spines[spine].set_linewidth(0.65)
    ax.grid(axis="y", color=GRID, linewidth=0.45)
    ax.tick_params(axis="both", which="major", labelsize=7.0, width=0.6, length=3.0, pad=2)


def make_figure(data: pd.DataFrame) -> plt.Figure:
    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_IN, HEIGHT_MM / MM_PER_IN), dpi=300)
    ax_a = fig.add_axes([0.145, 0.500, 0.805, 0.250])
    ax_b = fig.add_axes([0.145, 0.070, 0.805, 0.250])

    handles = []
    for ax, selector, ycol in ((ax_a, "plotted_in_panel_a", "n_works"),
                               (ax_b, "plotted_in_panel_b", "prevalence_pct_recomputed")):
        subset = data[data[selector].astype(bool)]
        for family in FAMILY_ORDER:
            series = subset[subset.family_id.eq(family)].sort_values("year")
            line, = ax.plot(series.year, series[ycol], color=FAMILY_COLORS[family], marker=MARKERS[family],
                            lw=1.35, ms=4.0, markeredgecolor="white", markeredgewidth=0.45, zorder=3)
            if ax is ax_a:
                handles.append(line)
        style_axis(ax)
        ax.set_xlabel("Publication year", fontsize=7.0, labelpad=4)

    ax_a.set_xlim(1997.5, 2026.25); ax_a.set_ylim(0, 120)
    ax_a.set_xticks([2000, 2005, 2010, 2015, 2020, 2025]); ax_a.set_yticks(np.arange(0, 121, 20))
    ax_a.set_ylabel("Unique works per year", fontsize=7.0, labelpad=6)
    ax_b.set_xlim(2007.5, 2025.55); ax_b.set_ylim(0, 80)
    ax_b.set_xticks([2010, 2015, 2020, 2025]); ax_b.set_yticks(np.arange(0, 81, 20))
    ax_b.set_ylabel("Family prevalence (%)", fontsize=7.0, labelpad=6)

    # Panel titles and subtitles
    ax_a.text(-0.125, 1.27, "(a)", transform=ax_a.transAxes, fontsize=9, fontweight="bold", va="bottom")
    ax_a.text(-0.045, 1.27, "Annual family counts", transform=ax_a.transAxes, fontsize=8, fontweight="bold", va="bottom")
    ax_a.text(-0.045, 1.145, "Baseline-covered works; memberships are non-exclusive", transform=ax_a.transAxes, fontsize=7, color=NOTE, va="bottom")
    ax_b.text(-0.125, 1.27, "(b)", transform=ax_b.transAxes, fontsize=9, fontweight="bold", va="bottom")
    ax_b.text(-0.045, 1.27, "Annual family prevalence", transform=ax_b.transAxes, fontsize=8, fontweight="bold", va="bottom")
    ax_b.text(-0.045, 1.145, "Share of baseline-covered works; shown where annual n ≥ 10", transform=ax_b.transAxes, fontsize=7, color=NOTE, va="bottom")

    # Descriptive periods: dashed dividers between years, labels centered in each interval
    periods_a = [("1990–2007", 1997.5, 2007.5), ("2008–2015", 2007.5, 2015.5),
                 ("2016–2020", 2015.5, 2020.5), ("2021–2025", 2020.5, 2026.25)]
    periods_b = [("2008–2015", 2007.5, 2015.5), ("2016–2020", 2015.5, 2020.5), ("2021–2025", 2020.5, 2025.55)]
    for ax, periods, dividers in ((ax_a, periods_a, [2007.5, 2015.5, 2020.5]),
                                  (ax_b, periods_b, [2015.5, 2020.5])):
        for x in dividers:
            ax.axvline(x, color="#B8B8B8", lw=0.55, ls=(0, (2.2, 2.2)), zorder=0)
        trans = mpl.transforms.blended_transform_factory(ax.transData, ax.transAxes)
        for label, start, end in periods:
            ax.text((start + end) / 2, 1.045, label, transform=trans, ha="center", va="bottom", fontsize=7, color=NOTE)

    # 2025 end-point values in panel (a)
    endpoints = data[data.year.eq(2025)].set_index("family_id")
    offsets = {"F1": 0.0, "F2": -2.1, "F3": 1.8, "F4": 1.8, "F5": -2.1}
    for family in FAMILY_ORDER:
        value = endpoints.loc[family, "n_works"]
        ax_a.text(2025.32, value + offsets[family], str(int(value)), fontsize=7, fontweight="bold",
                  color=FAMILY_COLORS[family], va="center")

    fig.legend(handles, [FAMILY_LABELS[f] for f in FAMILY_ORDER], loc="upper center", bbox_to_anchor=(0.5, 0.995),
               ncol=3, fontsize=7, frameon=False, handlelength=2.0, handletextpad=0.4, columnspacing=1.2, markerscale=0.95)
    return fig


def export(fig: plt.Figure, stem: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{stem}.pdf", format="pdf", dpi=600)
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=600, facecolor="white")
    buffer.seek(0)
    with Image.open(buffer) as image:
        image.convert("RGB").save(OUT_DIR / f"{stem}.tif", format="TIFF", compression="tiff_lzw", dpi=(600, 600))


def main() -> None:
    configure_style()
    fig = make_figure(load_data())
    export(fig, "Fig3")
    plt.close(fig)
    print(f"Fig. 3 written to {OUT_DIR}")


if __name__ == "__main__":
    main()
