"""Fig. 4: sensitivity of the recurrent structure to the recurrence threshold and clustering parameters.

(a) recurrent phrases, communities and structural coverage at df >= 3, 4 and 5;
(b) ARI and AMI: minimum and maximum over the 11 robustness runs whose parameters
    differ from the primary configuration, and agreement of the df >= 4 and df >= 5
    partitions with the df >= 3 partition;
(c) recall of the five families at df >= 4 and df >= 5.

Reads data/threshold_sensitivity_results.csv, data/robustness_results.csv and
data/family_stability_results.csv; the df >= 3 reference values are computed from
data/recurrent_phrase_dictionary_df3.csv, data/community_family_mapping.csv,
data/work_phrase_incidence_df3.csv and data/corpus_manifest.csv. Values are plotted
at the precision shown in the figure. Writes outputs/Fig4.pdf and outputs/Fig4.tif
(119 x 135 mm, 600 dpi). Run from the repository root.
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
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = Path(os.environ.get("SOFTPOWER_OUTPUT_DIR", str(REPO_ROOT / "outputs"))).expanduser().resolve()

MM_PER_IN = 25.4
WIDTH_MM, HEIGHT_MM = 119.0, 135.0
PRIMARY = {"k": 15, "resolution": 1.0, "seed": 42}
FAMILIES = ["F1", "F2", "F3", "F4", "F5"]
BLUE, LIGHT, DARK, TEXT, NOTE = "#4E79A7", "#75B0DE", "#2B7FC3", "#202020", "#555B61"


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


def load_values() -> dict:
    threshold = pd.read_csv(DATA_DIR / "threshold_sensitivity_results.csv").set_index("threshold")
    stability = pd.read_csv(DATA_DIR / "family_stability_results.csv").set_index("threshold")
    robustness = pd.read_csv(DATA_DIR / "robustness_results.csv")
    phrases = pd.read_csv(DATA_DIR / "recurrent_phrase_dictionary_df3.csv")
    communities = pd.read_csv(DATA_DIR / "community_family_mapping.csv")
    incidence = pd.read_csv(DATA_DIR / "work_phrase_incidence_df3.csv")
    corpus = pd.read_csv(DATA_DIR / "corpus_manifest.csv")
    alt = ["df>=4", "df>=5"]

    # (a) df >= 3 reference values and the two stricter thresholds
    coverage_df3 = 100 * incidence.work_id.nunique() / len(corpus)
    panel_a = {
        "Recurrent phrases": [len(phrases), *threshold.loc[alt, "retained_phrase_count"].astype(int)],
        "Communities": [len(communities), *threshold.loc[alt, "cluster_count"].astype(int)],
        "Coverage (%)": [round(coverage_df3, 2), *[round(100 * v, 2) for v in threshold.loc[alt, "document_coverage"]]],
    }

    # (b) runs identical to the primary configuration are excluded from the Min/Max summary
    is_primary = (robustness.k.eq(PRIMARY["k"]) & robustness.resolution.eq(PRIMARY["resolution"])
                  & robustness.seed.eq(PRIMARY["seed"]))
    alternative = robustness[~is_primary]
    if len(robustness) != 14 or len(alternative) != 11:
        raise ValueError("robustness_results.csv should contain 14 runs, 11 of them non-primary")
    panel_b = {}
    for metric, run_col, thr_col in (("ARI", "ARI_vs_corrected_primary", "ARI_vs_df3"),
                                     ("AMI", "AMI_vs_corrected_primary", "AMI_vs_df3")):
        panel_b[metric] = [alternative[run_col].min(), alternative[run_col].max(),
                           *[round(v, 3) for v in threshold.loc[alt, thr_col]]]

    # (c) family recall at df >= 4 and df >= 5
    panel_c = {f: tuple(round(stability.loc[t, f"{f}_recall"], 3) for t in alt) for f in FAMILIES}
    return {"a": panel_a, "b": panel_b, "c": panel_c}


def style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(NOTE)
        ax.spines[spine].set_linewidth(0.55)
    ax.grid(axis="y", color="#E7E7E7", lw=0.42)
    ax.tick_params(axis="both", labelsize=7, width=0.5, length=2.5, pad=2)


def make_figure(values: dict) -> plt.Figure:
    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_IN, HEIGHT_MM / MM_PER_IN), dpi=300)

    # (a) three small line charts
    axis_settings = {
        "Recurrent phrases": ((90, 290), [100, 150, 200, 250], lambda v: str(int(v))),
        "Communities": ((4, 8), [4, 5, 6, 7, 8], lambda v: str(int(v))),
        "Coverage (%)": ((40, 55.0), [40, 44, 48, 52], lambda v: f"{v:.2f}%"),
    }
    x = np.arange(3)
    for left, (title, series) in zip((0.145, 0.440, 0.735), values["a"].items()):
        ylim, yticks, fmt = axis_settings[title]
        ax = fig.add_axes([left, 0.745, 0.230, 0.155])
        ax.plot(x, series, color=BLUE, lw=1.2, zorder=2)
        ax.scatter(x, series, s=30, c=[BLUE, LIGHT, DARK], edgecolors="white", linewidths=0.55, zorder=3)
        ax.set_title(title, fontsize=8, fontweight="bold", pad=5)
        ax.set_xlim(-0.18, 2.75); ax.set_ylim(*ylim)
        ax.set_xticks(x, ["df ≥ 3", "df ≥ 4", "df ≥ 5"]); ax.set_yticks(yticks)
        style_axis(ax)
        for xi, yi in zip(x, series):
            ax.annotate(fmt(yi), (xi, yi), xytext=(6, 6), textcoords="offset points", ha="left", va="bottom",
                        fontsize=7, color=TEXT, zorder=5)
    fig.text(0.022, 0.965, "(a)", fontsize=9, fontweight="bold")

    # (b) agreement with the df >= 3 partition
    ax_ari = fig.add_axes([0.145, 0.435, 0.345, 0.185])
    ax_ami = fig.add_axes([0.600, 0.435, 0.345, 0.185])
    positions = [0.0, 0.75, 2.00, 2.75]
    for ax, (metric, bars) in zip((ax_ari, ax_ami), values["b"].items()):
        ax.bar(positions, bars, width=0.42, color=[BLUE, BLUE, LIGHT, DARK], zorder=3)
        for xpos, value in zip(positions, bars):
            ax.text(xpos, value + 0.035, f"{value:.3f}", ha="center", va="bottom", fontsize=7)
        ax.set_title(metric, fontsize=8, fontweight="bold", pad=7)
        ax.set_xlim(-0.52, 3.25); ax.set_ylim(0, 1.13)
        ax.set_xticks(positions, ["Min", "Max", "df ≥ 4", "df ≥ 5"]); ax.set_yticks(np.arange(0, 1.01, .2))
        style_axis(ax)
        ax.text(0.375, -0.20, "Fixed vocabulary", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7, color=NOTE)
        ax.text(2.375, -0.20, "Stricter threshold", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7, color=NOTE)
    ax_ari.set_ylabel("Agreement with df ≥ 3", fontsize=7, labelpad=6)
    fig.text(0.022, 0.650, "(b)", fontsize=9, fontweight="bold")

    # (c) family recall
    ax_c = fig.add_axes([0.145, 0.052, 0.735, 0.205])
    fams = list(values["c"]); xc = np.arange(len(fams)); width = .28
    v4 = [values["c"][f][0] for f in fams]; v5 = [values["c"][f][1] for f in fams]
    b4 = ax_c.bar(xc - width / 2, v4, width, label="df ≥ 4", color=LIGHT, zorder=3)
    b5 = ax_c.bar(xc + width / 2, v5, width, label="df ≥ 5", color=DARK, zorder=3)
    for i, (bar, value) in enumerate(zip(b4, v4)):
        extra = 0.030 if fams[i] in {"F3", "F4"} else 0.020
        ax_c.text(bar.get_x() + bar.get_width() - 0.012, value + extra, f"{value:.2f}", ha="right", va="bottom", fontsize=7, zorder=5)
    for i, (bar, value) in enumerate(zip(b5, v5)):
        extra = 0.060 if fams[i] in {"F3", "F4"} else 0.020
        ax_c.text(bar.get_x() + 0.012, value + extra, f"{value:.2f}", ha="left", va="bottom", fontsize=7, zorder=5)
    ax_c.set_xlim(-.55, 4.55); ax_c.set_ylim(0, 1.22); ax_c.set_xticks(xc, fams); ax_c.set_yticks(np.arange(0, 1.01, .2))
    ax_c.set_ylabel("Family recall", fontsize=7, labelpad=6)
    style_axis(ax_c)
    ax_c.legend(loc="upper center", bbox_to_anchor=(.5, 1.20), ncol=2, fontsize=7, frameon=False, handlelength=1.2, columnspacing=.9)
    fig.text(0.022, 0.295, "(c)", fontsize=9, fontweight="bold")
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
    fig = make_figure(load_values())
    export(fig, "Fig4")
    plt.close(fig)
    print(f"Fig. 4 written to {OUT_DIR}")


if __name__ == "__main__":
    main()
