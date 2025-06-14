import pandas as pd
import re
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def load_and_prepare(path: str) -> pd.DataFrame:
    """Load CSV and return dataframe with numeric columns cleaned."""
    df = pd.read_csv(path)

    def parse_density(x: str) -> float:
        if pd.isna(x):
            return float('nan')
        m = re.search(r'^\s*([0-9]+\.?[0-9]*)', str(x))
        return float(m.group(1)) if m else float('nan')

    df['Density'] = df['Density'].apply(parse_density)
    numeric_cols = ['MolecularWeight', 'BoilingPoint', 'MeltingPoint', 'Density', 'log_kow']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=numeric_cols)
    return df


def perform_clustering(df: pd.DataFrame, k_range=range(2, 7)) -> None:
    """Perform k-means clustering for each k and save scatter plots."""
    features = df[['MolecularWeight', 'BoilingPoint', 'MeltingPoint', 'Density', 'log_kow']]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    pca = PCA(n_components=2, random_state=0)
    components = pca.fit_transform(scaled)
    cas_numbers = df['CAS'].astype(str).values

    inertia = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=0)
        labels = km.fit_predict(scaled)
        inertia.append(km.inertia_)
        plt.figure(figsize=(6, 4))
        for label in sorted(set(labels)):
            idx = labels == label
            plt.scatter(components[idx, 0], components[idx, 1], label=f"Cluster {label+1}")
            for x, y, cas in zip(components[idx, 0], components[idx, 1], cas_numbers[idx]):
                plt.text(x, y, cas, fontsize=6)
        plt.legend()
        plt.xlabel('PC1')
        plt.ylabel('PC2')
        plt.title(f'KMeans Clustering (k={k})')
        plt.tight_layout()
        plt.savefig(f'clusters_k{k}.png')
        plt.close()

    # elbow plot
    plt.figure(figsize=(6, 4))
    plt.plot(list(k_range), inertia, marker='o')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method for Optimal k')
    plt.tight_layout()
    plt.savefig('elbow.png')
    plt.close()


def main() -> None:
    df = load_and_prepare('cas_numbers_property_table_v2.csv')
    perform_clustering(df)


if __name__ == '__main__':
    main()
