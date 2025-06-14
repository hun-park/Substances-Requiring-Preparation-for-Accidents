import os
import re
from itertools import combinations

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DEF_NUMERIC_COLS = [
    "MolecularWeight",
    "BoilingPoint",
    "MeltingPoint",
    "Density",
    "log_kow",
]


def load_and_prepare(path: str) -> pd.DataFrame:
    """Load CSV and clean numeric columns."""
    df = pd.read_csv(path)

    def parse_density(x: str) -> float:
        if pd.isna(x):
            return float("nan")
        m = re.search(r"^\s*([0-9]+\.?[0-9]*)", str(x))
        return float(m.group(1)) if m else float("nan")

    if "Density" in df.columns:
        df["Density"] = df["Density"].apply(parse_density)
    for col in DEF_NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=DEF_NUMERIC_COLS)
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


def cluster_feature_pairs(df: pd.DataFrame, features: list[str], k_range=range(2, 7)) -> None:
    os.makedirs("results", exist_ok=True)
    for f1, f2 in combinations(features, 2):
        pair_data = df[[f1, f2]]
        scaled = StandardScaler().fit_transform(pair_data)
        best_k, score = find_best_k(scaled, k_range)
        km = KMeans(n_clusters=best_k, random_state=0)
        labels = km.fit_predict(scaled)

        plt.figure(figsize=(6, 4))
        for label in sorted(set(labels)):
            idx = labels == label
            plt.scatter(pair_data.loc[idx, f1], pair_data.loc[idx, f2], label=f"Cluster {label + 1}")
            for x, y, cas in zip(pair_data.loc[idx, f1], pair_data.loc[idx, f2], df.loc[idx, "CAS"].astype(str)):
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


def cluster_pca(df: pd.DataFrame, features: list[str], k_range=range(2, 7)) -> None:
    data = df[features]
    scaled = StandardScaler().fit_transform(data)
    components = PCA(n_components=2, random_state=0).fit_transform(scaled)
    best_k, score = find_best_k(components, k_range)
    km = KMeans(n_clusters=best_k, random_state=0)
    labels = km.fit_predict(components)

    plt.figure(figsize=(6, 4))
    for label in sorted(set(labels)):
        idx = labels == label
        plt.scatter(components[idx, 0], components[idx, 1], label=f"Cluster {label + 1}")
        for x, y, cas in zip(components[idx, 0], components[idx, 1], df.loc[idx, "CAS"].astype(str)):
            plt.text(x, y, cas, fontsize=6)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend()
    plt.title(f"PCA of {', '.join(features)} (k={best_k})")
    plt.figtext(0.5, 0.01, f"Silhouette Score: {score:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig(f"results/pca_k{best_k}.png")
    plt.close()


def main() -> None:
    df = load_and_prepare("cas_numbers_property_table_v2.csv")
    features = ["MolecularWeight", "BoilingPoint", "MeltingPoint", "log_kow"]
    cluster_feature_pairs(df, features)
    cluster_pca(df, features)


if __name__ == "__main__":
    main()
