"""Note S1 sensitivity analysis.

Removes the 51 work-phrase pairs added after first-pass extraction for five works,
recalculates document frequency, retains phrases with df >= 3 and repeats the primary
kNN graph construction and Leiden community detection with the stored embeddings.
Writes note_s1_sensitivity_results.json and note_s1_added_pairs.csv to
outputs/note_s1/ and does not overwrite existing files. Run from the repository root.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import igraph as ig
import leidenalg as la
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    adjusted_mutual_info_score,
    adjusted_rand_score,
    cohen_kappa_score,
)
from sklearn.neighbors import NearestNeighbors


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUT = Path(os.environ.get("SOFTPOWER_OUTPUT_DIR", str(Path(__file__).resolve().parents[1] / "outputs" / "note_s1"))).expanduser().resolve()

PAIRS = DATA_DIR / "s1_corrected_work_phrase_pairs.csv"
VOCAB = DATA_DIR / "s1_corrected_phrase_vocabulary.csv"
CLUSTERS = DATA_DIR / "s1_primary_clusters_df3.csv"
EMBEDDINGS = DATA_DIR / "corrected_embeddings_df3.npy"
CORPUS_MANIFEST = DATA_DIR / "corpus_manifest.csv"

RESULTS_PATH = OUT / "note_s1_sensitivity_results.json"
ADDED_PAIRS_PATH = OUT / "note_s1_added_pairs.csv"

K = 15
RESOLUTION = 1.0
SEED = 42
FAMILIES = ["F1", "F2", "F3", "F4", "F5"]

# This is the final primary-analysis correspondence, keyed by raw Leiden ID.
PRIMARY_CLUSTER_TO_FAMILY = {
    0: "F2",  # C1
    1: "F1",  # C2
    2: "F1",  # C3
    3: "F3",  # C4
    4: "F4",  # C5
    5: "F3",  # C6
    6: "F5",  # C7
}

ADDED_PAIR_WORK_IDS = {
    "work:62d677666340f5e4",  # First Lady
    "work:1f6b89334311917b",  # Digital Diplomacy
    "work:6fc2fbe23bfda768",  # Foreign Media Coverage
    "work:b6359c524c761d66",  # Evolution of China's foreign policy
    "work:96701c08928fc2ec",  # The Soft-Power Fallacy
}

# Categories are the prior literal metadata-field comparison: (a) phrase
# appears verbatim; (b) all content words appear; (c) only some content words
# appear; (d) no content words appear.
MATCH_CATEGORY = {
    ("work:1f6b89334311917b", "strategic communication"): "c",
    ("work:62d677666340f5e4", "comparative analysis of soft power"): "b",
    ("work:62d677666340f5e4", "comparative study"): "c",
    ("work:62d677666340f5e4", "media discourse analysis"): "b",
    ("work:6fc2fbe23bfda768", "corpus assisted analysis"): "b",
    ("work:96701c08928fc2ec", "concept definitions"): "c",
    ("work:96701c08928fc2ec", "conceptual evolution of soft power"): "c",
    ("work:96701c08928fc2ec", "conceptualization of soft power"): "c",
    ("work:96701c08928fc2ec", "contestation of concept"): "c",
    ("work:96701c08928fc2ec", "critique of soft power"): "c",
    ("work:96701c08928fc2ec", "soft power as international relations concept"): "c",
    ("work:96701c08928fc2ec", "soft power fallacy"): "b",
    ("work:b6359c524c761d66", "belt and road initiative"): "c",
    ("work:b6359c524c761d66", "chinese foreign policy"): "b",
    ("work:b6359c524c761d66", "foreign policy goals"): "c",
    ("work:b6359c524c761d66", "foreign policy strategy"): "b",
    ("work:b6359c524c761d66", "peaceful diplomacy"): "b",
    ("work:b6359c524c761d66", "peaceful rise policy"): "b",
    ("work:b6359c524c761d66", "soft power strategies"): "c",
    ("work:b6359c524c761d66", "solidarity with developing countries"): "c",
}


def write_new_csv(frame: pd.DataFrame, path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def write_new_json(payload: dict, path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_leiden(embeddings: np.ndarray) -> tuple[np.ndarray, int]:
    """Cosine kNN graph: undirected duplicate edges retain maximum weight."""
    nn = NearestNeighbors(n_neighbors=min(K + 1, len(embeddings)), metric="cosine")
    distances, indices = nn.fit(embeddings).kneighbors(embeddings, return_distance=True)
    edge_weights: dict[tuple[int, int], float] = {}
    for source in range(len(embeddings)):
        for target, distance in zip(indices[source, 1:], distances[source, 1:]):
            edge = tuple(sorted((source, int(target))))
            edge_weights[edge] = max(edge_weights.get(edge, -1.0), 1.0 - float(distance))
    edges = sorted(edge_weights)
    graph = ig.Graph(n=len(embeddings), edges=edges, directed=False)
    graph.es["weight"] = [edge_weights[edge] for edge in edges]
    partition = la.find_partition(
        graph,
        la.RBConfigurationVertexPartition,
        weights=graph.es["weight"],
        resolution_parameter=RESOLUTION,
        seed=SEED,
    )
    return np.asarray(partition.membership, dtype=int), len(edges)


def dominant_family(labels: np.ndarray, reference_families: list[str]) -> list[str]:
    """Map each re-clustered community to its primary-analysis dominant family."""
    mapping: dict[int, str] = {}
    for cluster in sorted(set(labels.tolist())):
        counts = Counter(
            family for label, family in zip(labels, reference_families) if label == cluster
        )
        mapping[cluster] = sorted(FAMILIES, key=lambda family: (-counts[family], family))[0]
    return [mapping[int(label)] for label in labels]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if RESULTS_PATH.exists() or ADDED_PAIRS_PATH.exists():
        raise FileExistsError("Output file already exists; this script will not overwrite prior results.")

    pairs = pd.read_csv(PAIRS, encoding="utf-8-sig", dtype=str).rename(
        columns={"corrected_canonical": "phrase"}
    )
    vocab = pd.read_csv(VOCAB, encoding="utf-8-sig")
    clusters = pd.read_csv(CLUSTERS, encoding="utf-8-sig")
    core = pd.read_csv(CORPUS_MANIFEST, encoding="utf-8-sig", dtype=str)
    embeddings = np.load(EMBEDDINGS)

    if len(clusters) != 256 or embeddings.shape != (256, 384):
        raise RuntimeError("The df>=3 phrase table or embeddings do not have the expected dimensions.")
    if clusters.node_index.nunique() != 256 or set(clusters.node_index) != set(range(256)):
        raise RuntimeError("Embedding row indices are not a complete 0..255 sequence.")
    if len(core) != 2055:
        raise RuntimeError("The final core corpus does not contain 2,055 works.")

    added = pairs.loc[pairs.work_id.isin(ADDED_PAIR_WORK_IDS)].copy()
    if len(added) != 51 or added.duplicated(["work_id", "phrase"]).any():
        raise RuntimeError("Expected exactly 51 distinct phrase-work pairs from the five specified works.")
    if core.work_id.duplicated().any():
        raise RuntimeError("The public corpus manifest has duplicate work_id values.")
    metadata = core[["work_id", "doi"]]
    df_lookup = vocab.set_index("phrase")["df"]
    added = added.merge(metadata, on="work_id", how="left", validate="many_to_one")
    if not added.phrase.isin(df_lookup.index).all():
        raise RuntimeError("Cannot recover the original df for every removed pair.")
    added["df"] = added.phrase.map(df_lookup).astype(int)
    added["df_ge_3"] = added["df"].ge(3)
    added["text_match_category"] = [
        MATCH_CATEGORY.get((row.work_id, row.phrase), "a") for row in added.itertuples(index=False)
    ]
    if added.text_match_category.value_counts().to_dict() != {"a": 31, "c": 12, "b": 8}:
        raise RuntimeError("The pre-specified 51-pair text-match category map is incomplete or inconsistent.")
    added["author_judgement"] = ""
    added_export = added[
        ["work_id", "doi", "phrase", "df", "df_ge_3", "text_match_category", "author_judgement"]
    ].sort_values(["work_id", "phrase"], kind="mergesort")
    write_new_csv(added_export, ADDED_PAIRS_PATH)

    retained_pairs = pairs.loc[~pairs.work_id.isin(ADDED_PAIR_WORK_IDS)].copy()
    new_df = retained_pairs.groupby("phrase", sort=False).work_id.nunique()
    retained_phrases = set(new_df.index[new_df.ge(3)])
    retained = clusters.loc[clusters.phrase.isin(retained_phrases)].copy().sort_values("node_index")
    if len(retained) != 249:
        raise RuntimeError(f"Expected 249 retained df>=3 phrases, found {len(retained)}.")
    common = retained.phrase.tolist()
    retained_embeddings = embeddings[retained.node_index.to_numpy(dtype=int)]
    new_labels, edge_n = run_leiden(retained_embeddings)
    reference_labels = retained.cluster_id_raw.to_numpy(dtype=int)
    reference_families = [PRIMARY_CLUSTER_TO_FAMILY[int(label)] for label in reference_labels]
    mapped_families = dominant_family(new_labels, reference_families)

    covered_works = retained_pairs.loc[retained_pairs.phrase.isin(retained_phrases), "work_id"].nunique()
    community_sizes = Counter(new_labels.tolist())
    results = {
        "analysis": "Exclude the 51 phrase-work pairs added for five works, recalculate df, retain df>=3 phrases, then re-cluster using the stored embeddings.",
        "removed_work_count": len(ADDED_PAIR_WORK_IDS),
        "removed_phrase_work_pair_count": int(len(added)),
        "common_phrase_count": int(len(common)),
        "retained_df_ge_3_phrase_count": int(len(retained)),
        "community_count": int(len(community_sizes)),
        "community_sizes_desc": sorted((int(size) for size in community_sizes.values()), reverse=True),
        "community_sizes_by_leiden_id": {str(cluster): int(community_sizes[cluster]) for cluster in sorted(community_sizes)},
        "structural_coverage": {
            "covered_works": int(covered_works),
            "core_works": int(len(core)),
            "fraction": float(covered_works / len(core)),
            "display": f"{covered_works}/{len(core)} = {covered_works / len(core):.4%}",
        },
        "agreement_on_249_common_phrases": {
            "ARI": float(adjusted_rand_score(reference_labels, new_labels)),
            "AMI": float(adjusted_mutual_info_score(reference_labels, new_labels)),
            "family_level_cohens_kappa": float(
                cohen_kappa_score(reference_families, mapped_families, labels=FAMILIES)
            ),
            "family_mapping_rule": "Each new Leiden community is assigned the plurality family among its member phrases under the primary-analysis family mapping; ties resolve by F1–F5 order.",
        },
        "clustering": {
            "metric": "cosine",
            "k": K,
            "graph": "undirected kNN; duplicate edges retain maximum 1 - cosine_distance weight",
            "undirected_edge_count": int(edge_n),
            "partition": "Leiden RBConfigurationVertexPartition",
            "resolution": RESOLUTION,
            "seed": SEED,
        },
        "source_paths": {
            "pairs": "data/s1_corrected_work_phrase_pairs.csv",
            "vocabulary": "data/s1_corrected_phrase_vocabulary.csv",
            "primary_clusters": "data/s1_primary_clusters_df3.csv",
            "embeddings": "data/corrected_embeddings_df3.npy",
            "corpus_manifest": "data/corpus_manifest.csv",
        },
        "runtime": {
            "python": sys.version.replace("\n", " "),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "igraph": ig.__version__,
            "leidenalg": getattr(la, "version", getattr(la, "__version__", "unknown")),
        },
    }
    write_new_json(results, RESULTS_PATH)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
