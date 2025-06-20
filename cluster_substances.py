import os
from itertools import combinations
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import numpy as np


DEF_NUMERIC_COLS = [
    "MolecularWeight",
    "BoilingPoint",
    "MeltingPoint",
    "log_kow",
]


def load_and_prepare(path: str) -> pd.DataFrame:
    """Load CSV and ensure numeric columns are parsed."""
    df = pd.read_csv(path)
    for col in DEF_NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def find_best_k(data, k_range):
    """Return the k with the highest silhouette score."""
    best_k = k_range[0]
    best_score = -1
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=0)
        labels = km.fit_predict(data)
        score = silhouette_score(data, labels)
        if score > best_score:
            best_score = score
            best_k = k
    return best_k, best_score


def export_cluster_table(
    df: pd.DataFrame,
    features: Iterable[str],
    labels: np.ndarray,
    scaled: np.ndarray,
    model: KMeans,
    filename: str,
) -> None:
    """Save cluster assignments and identify the CAS closest to each centroid."""

    result = df[["CAS", *features]].copy()
    result["Cluster"] = labels + 1
    result["IsCenter"] = False
    result["CenterCAS"] = ""

    for cl in range(model.n_clusters):
        idxs = np.where(labels == cl)[0]
        if not len(idxs):
            continue
        center = model.cluster_centers_[cl]
        # compute distances in scaled space
        distances = np.linalg.norm(scaled[idxs] - center, axis=1)
        center_idx = idxs[np.argmin(distances)]
        center_cas = result.iloc[center_idx]["CAS"]
        result.loc[result.index[idxs], "CenterCAS"] = center_cas
        result.loc[result.index[center_idx], "IsCenter"] = True

    os.makedirs("results", exist_ok=True)
    result.to_csv(os.path.join("results", filename), index=False)


def cluster_feature_pairs(df: pd.DataFrame, features: list[str], k_range=range(2, 7)) -> None:
    os.makedirs("results", exist_ok=True)
    for f1, f2 in combinations(features, 2):
        pair_df = df[["CAS", f1, f2]].dropna(subset=[f1, f2])
        if len(pair_df) < 2:
            continue
        pair_data = pair_df[[f1, f2]]
        scaled = StandardScaler().fit_transform(pair_data)
        best_k, score = find_best_k(scaled, k_range)
        km = KMeans(n_clusters=best_k, random_state=0)
        labels = km.fit_predict(scaled)

        plt.figure(figsize=(6, 4))
        for label in sorted(set(labels)):
            idx = labels == label
            plt.scatter(pair_data.loc[idx, f1], pair_data.loc[idx, f2], label=f"Cluster {label + 1}")
            for x, y, cas in zip(pair_data.loc[idx, f1], pair_data.loc[idx, f2], pair_df.loc[idx, "CAS"].astype(str)):
                plt.text(x, y, cas, fontsize=6)

        plt.xlabel(f1)
        plt.ylabel(f2)
        plt.legend()
        plt.title(f"{f1} vs {f2} (k={best_k})")
        plt.figtext(0.5, 0.01, f"Silhouette Score: {score:.2f}", ha="center")
        plt.tight_layout()
        out_file = f"results/pair_{f1}_{f2}_k{best_k}.png"
        plt.savefig(out_file)
        plt.close()

        export_cluster_table(
            pair_df,
            [f1, f2],
            labels,
            scaled,
            km,
            f"pair_{f1}_{f2}_k{best_k}.csv",
        )


def cluster_all_features(df: pd.DataFrame, features: list[str], k_range=range(2, 7)) -> None:
    """Cluster using all features together and visualize with PCA."""
    os.makedirs("results", exist_ok=True)
    all_df = df[["CAS", *features]].dropna(subset=features)
    if len(all_df) < 2:
        return
    data = all_df[features]
    scaled = StandardScaler().fit_transform(data)
    best_k, score = find_best_k(scaled, k_range)
    km = KMeans(n_clusters=best_k, random_state=0)
    labels = km.fit_predict(scaled)
    components = PCA(n_components=2, random_state=0).fit_transform(scaled)

    plt.figure(figsize=(6, 4))
    for label in sorted(set(labels)):
        idx = labels == label
        plt.scatter(components[idx, 0], components[idx, 1], label=f"Cluster {label + 1}")
        for x, y, cas in zip(components[idx, 0], components[idx, 1], all_df.loc[idx, "CAS"].astype(str)):
            plt.text(x, y, cas, fontsize=6)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend()
    plt.title(f"All features (k={best_k})")
    plt.figtext(0.5, 0.01, f"Silhouette Score: {score:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig(f"results/all_features_k{best_k}.png")
    plt.close()

    export_cluster_table(
        all_df,
        features,
        labels,
        scaled,
        km,
        f"all_features_k{best_k}.csv",
    )


def cluster_pca(df: pd.DataFrame, features: list[str], k_range=range(2, 7)) -> None:
    data_df = df[["CAS", *features]].dropna(subset=features)
    if len(data_df) < 2:
        return
    data = data_df[features]
    scaled = StandardScaler().fit_transform(data)
    components = PCA(n_components=2, random_state=0).fit_transform(scaled)
    best_k, score = find_best_k(components, k_range)
    km = KMeans(n_clusters=best_k, random_state=0)
    labels = km.fit_predict(components)

    plt.figure(figsize=(6, 4))
    for label in sorted(set(labels)):
        idx = labels == label
        plt.scatter(components[idx, 0], components[idx, 1], label=f"Cluster {label + 1}")
        for x, y, cas in zip(components[idx, 0], components[idx, 1], data_df.loc[idx, "CAS"].astype(str)):
            plt.text(x, y, cas, fontsize=6)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend()
    plt.title(f"PCA of {', '.join(features)} (k={best_k})")
    plt.figtext(0.5, 0.01, f"Silhouette Score: {score:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig(f"results/pca_k{best_k}.png")
    plt.close()

    pca_df = pd.DataFrame({
        "CAS": data_df["CAS"],
        "PC1": components[:, 0],
        "PC2": components[:, 1],
    })
    export_cluster_table(
        pca_df,
        ["PC1", "PC2"],
        labels,
        components,
        km,
        f"pca_k{best_k}.csv",
    )


def main() -> None:
    df = load_and_prepare("cas_numbers_property_table_clean.csv")
    features = ["MolecularWeight", "BoilingPoint", "MeltingPoint", "log_kow"]
    cluster_feature_pairs(df, features)
    cluster_all_features(df, features)
    cluster_pca(df, features)


if __name__ == "__main__":
    main()
