"""Fig. 2: t-SNE projection of the 256 recurrent phrases (a) and family co-membership (b).

Panel (a) uses the stored t-SNE coordinates in data/figure2a_visualization_coordinates.csv
(the projection is not recomputed); panel (b) counts works shared by each pair of families
in data/family_work_membership.csv. The figure has the same content as the published
Fig. 2 in an earlier two-panel layout. Writes outputs/Figure2_public.{svg,pdf,png,tif}.
Run from the repository root.
"""
from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = Path(os.environ.get("SOFTPOWER_OUTPUT_DIR", str(REPO_ROOT / "outputs"))).expanduser().resolve()
PROJECTION_FILE = DATA_DIR / "figure2a_visualization_coordinates.csv"
MEMBERSHIP_FILE = DATA_DIR / "family_work_membership.csv"
FAMILIES = ["F1", "F2", "F3", "F4", "F5"]
COMMUNITIES = [f"C{i}" for i in range(1, 8)]
EXPECTED_COUNTS = {"C1": 53, "C2": 48, "C3": 44, "C4": 37, "C5": 30, "C6": 25, "C7": 19}
EXPECTED_MATRIX = np.array([[670, 101, 156, 57, 49], [101, 215, 59, 19, 13], [156, 59, 333, 22, 24], [57, 19, 22, 182, 11], [49, 13, 24, 11, 105]], dtype=int)
COMMUNITY_LABELS = {"C1": "C1 Influence &\nreputation", "C2": "C2 Public\ndiplomacy", "C3": "C3 Foreign\npolicy", "C4": "C4 Culture", "C5": "C5 Resources", "C6": "C6 Branding", "C7": "C7 Education"}
COMMUNITY_COLORS = {"C1": "#4E79A7", "C2": "#F28E2B", "C3": "#59A14F", "C4": "#A47ACC", "C5": "#D9A620", "C6": "#4EABB8", "C7": "#E66A95"}
FAMILY_LABELS = {"F1": "F1 Statecraft", "F2": "F2 Influence &\nreputation", "F3": "F3 Culture &\nbranding", "F4": "F4 Resources &\nstrategy", "F5": "F5 Education &\nexchange"}


def configure_style() -> None:
    mpl.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"], "svg.fonttype": "none", "pdf.fonttype": 42, "font.size": 7.0, "axes.linewidth": 0.65, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def load_projection() -> pd.DataFrame:
    data = pd.read_csv(PROJECTION_FILE)
    required = {"phrase", "df", "final_cluster_id", "family_id", "tsne_1", "tsne_2"}
    if not required.issubset(data.columns):
        raise ValueError(f"Figure 2a input is missing: {sorted(required - set(data.columns))}")
    if len(data) != 256 or data["phrase"].nunique() != 256:
        raise ValueError("Figure 2a requires 256 unique phrases")
    counts = data["final_cluster_id"].value_counts().sort_index().to_dict()
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"Community sizes differ from the expected values: {counts}")
    return data


def co_membership_matrix() -> pd.DataFrame:
    memberships = pd.read_csv(MEMBERSHIP_FILE)
    if not {"work_id", "family_id"}.issubset(memberships.columns):
        raise ValueError("Family membership file must contain work_id and family_id")
    sets = {family: set(memberships.loc[memberships["family_id"].eq(family), "work_id"]) for family in FAMILIES}
    matrix = pd.DataFrame([[len(sets[left] & sets[right]) for right in FAMILIES] for left in FAMILIES], index=FAMILIES, columns=FAMILIES, dtype=int)
    if not np.array_equal(matrix.to_numpy(), EXPECTED_MATRIX):
        raise ValueError(f"Family co-membership differs from the expected values: {matrix.to_numpy().tolist()}")
    return matrix


def draw_projection(ax: mpl.axes.Axes, data: pd.DataFrame) -> None:
    for community in COMMUNITIES:
        subset = data.loc[data["final_cluster_id"].eq(community)]
        ax.scatter(subset["tsne_1"], subset["tsne_2"], s=14, color=COMMUNITY_COLORS[community], edgecolors="white", linewidths=0.28, alpha=0.86, zorder=3)
    positions = {"C1": (9.5, 13.2), "C2": (-9.8, 6.5), "C3": (-1.8, 19.4), "C4": (-1.2, -10.8), "C5": (-2.5, -16.3), "C6": (16.0, 7.2), "C7": (-13.0, 13.4)}
    for community, (x, y) in positions.items():
        text = ax.text(x, y, COMMUNITY_LABELS[community].replace("\n", " "), ha="center", va="center", fontsize=7.2, color=COMMUNITY_COLORS[community], fontweight="bold", zorder=4)
        text.set_path_effects([pe.withStroke(linewidth=1.1, foreground="white")])
    ax.set_xlabel("t-SNE 1", fontsize=8, labelpad=6); ax.set_ylabel("t-SNE 2", fontsize=8, labelpad=6); ax.tick_params(axis="both", labelsize=7, colors="#333333")
    ax.spines["left"].set_color("#555555"); ax.spines["bottom"].set_color("#555555"); ax.set_xlim(float(data.tsne_1.min()) - 1.25, float(data.tsne_1.max()) + 1.25); ax.set_ylim(float(data.tsne_2.min()) - 1.25, float(data.tsne_2.max()) + 1.25); ax.grid(False)


def draw_matrix(ax: mpl.axes.Axes, matrix: pd.DataFrame) -> mpl.cm.ScalarMappable:
    blue = LinearSegmentedColormap.from_list("soft_blues", ["#F7FBFF", "#D6E9F8", "#8FC1E8", "#2B7FC3"]); norm = Normalize(vmin=0, vmax=150)
    for i, left in enumerate(FAMILIES):
        for j, right in enumerate(FAMILIES):
            value = int(matrix.loc[left, right]); face = "#EFEFEF" if i == j else blue(norm(value)); ax.add_patch(Rectangle((j, i), 1, 1, facecolor=face, edgecolor="#F4F4F4", lw=0.65)); ax.text(j + .5, i + .5, str(value), ha="center", va="center", fontsize=7.8, color="#262626" if i == j or value < 95 else "white")
    ax.set(xlim=(0, 5), ylim=(5, 0), aspect="equal"); ax.set_xticks(np.arange(5) + .5, FAMILIES, fontsize=7); ax.set_yticks(np.arange(5) + .5, [FAMILY_LABELS[f] for f in FAMILIES], fontsize=6.7); ax.tick_params(axis="x", length=0, labeltop=True, labelbottom=False, pad=5); ax.tick_params(axis="y", length=0, pad=8)
    for spine in ax.spines.values(): spine.set_visible(False)
    sm = mpl.cm.ScalarMappable(cmap=blue, norm=norm); sm.set_array([]); return sm


def make_figure(projection: pd.DataFrame, matrix: pd.DataFrame) -> mpl.figure.Figure:
    configure_style(); fig = plt.figure(figsize=(7.40, 4.35), constrained_layout=False); grid = fig.add_gridspec(1, 2, width_ratios=[1, 1], left=.070, right=.975, bottom=.185, top=.805, wspace=.30); ax_a, ax_b = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]); ax_a.set_box_aspect(1); ax_b.set_box_aspect(1); draw_projection(ax_a, projection); sm = draw_matrix(ax_b, matrix)
    apos, bpos = ax_a.get_position(), ax_b.get_position(); scale=.88; ax_b.set_position([bpos.x0 + bpos.width*(1-scale)/2, apos.y1-bpos.height*scale, bpos.width*scale, bpos.height*scale]); bpos=ax_b.get_position(); cax=fig.add_axes([bpos.x0, bpos.y0-.076, bpos.width, .022]); cbar=fig.colorbar(sm, cax=cax, orientation="horizontal"); cbar.set_ticks([0,50,100,150]); cbar.set_label("Pairwise co-membership (works)", fontsize=7, labelpad=7); cbar.ax.tick_params(labelsize=6.6, length=2.2, width=.45)
    title_y, sub_y = apos.y1+.130, apos.y1+.090; fig.text(apos.x0, title_y, "(a)", fontsize=9.2, fontweight="bold"); fig.text(apos.x0+.040, title_y, "Phrase-level semantic projection", fontsize=9.2, fontweight="semibold"); fig.text(apos.x0+.040, sub_y, "t-SNE projection of 256 recurrent phrases (df ≥ 3)", fontsize=7.1); fig.text(bpos.x0, title_y, "(b)", fontsize=9.2, fontweight="bold"); fig.text(bpos.x0+.040, title_y, "Family co-membership", fontsize=9.2, fontweight="semibold"); fig.text(bpos.x0+.040, sub_y, "Work level; n = 1,071; memberships are non-exclusive", fontsize=7.1)
    return fig


def export(fig: mpl.figure.Figure) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True); base=OUT_DIR / "Figure2_public"; fig.savefig(base.with_suffix(".svg"), bbox_inches="tight"); fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight"); fig.savefig(base.with_suffix(".png"), dpi=600, bbox_inches="tight"); buffer=BytesIO(); fig.savefig(buffer, format="tiff", dpi=600, bbox_inches="tight"); buffer.seek(0)
    with Image.open(buffer) as image: image.convert("RGB").save(base.with_suffix(".tif"), format="TIFF", compression="tiff_lzw", dpi=(600,600))


def main() -> None:
    projection=load_projection(); matrix=co_membership_matrix(); fig=make_figure(projection, matrix); export(fig); plt.close(fig); print(f"Fig. 2 written to {OUT_DIR}")


if __name__ == "__main__": main()
