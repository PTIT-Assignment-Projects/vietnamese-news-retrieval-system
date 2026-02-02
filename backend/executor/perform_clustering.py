import pickle
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import sys
import os
from sklearn.preprocessing import normalize
from elasticsearch import Elasticsearch

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from constant import INDEX_NAME, ELASTIC_HOST, ID_COLUMN, CATEGORY_COLUMN, CONTENT_COLUMN
except ImportError:
    INDEX_NAME = "vietnamese_curated_data"
    ELASTIC_HOST = "http://localhost:9200"
    ID_COLUMN = "id"
    CATEGORY_COLUMN = "category"
    CONTENT_COLUMN = "content"

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
LSI_DATA_FILE = "data/lsi_data.pkl"
OUTPUT_FILE = "data/news_clusters.pkl"

# Clustering parameters
N_CLUSTERS = 8  
MIN_SAMPLES = 5  
EPS = 0.5  

# -----------------------------------------------------------
# 1. Load LSI Data
# -----------------------------------------------------------
def load_lsi_data():
    if not os.path.exists(LSI_DATA_FILE):
        print(f"❌ Error: {LSI_DATA_FILE} not found!")
        print("Please run perform_lsi.py first.")
        sys.exit(1)
    
    print(f"📂 Loading LSI data from {LSI_DATA_FILE}...")
    with open(LSI_DATA_FILE, "rb") as f:
        data = pickle.load(f)
    
    vectors = data["vectors"]
    ids = data["ids"]

    # Normalize Vectors for better clustering
    print(f"⚖️  Normalizing vectors to unit length...")
    vectors = normalize(vectors, norm='l2')
    
    print(f"✅ Loaded {len(ids)} news vectors (Shape: {vectors.shape})")
    return vectors, ids

# -----------------------------------------------------------
# 2. Fetch Metadata from Elasticsearch
# -----------------------------------------------------------
def fetch_news_metadata(news_ids):
    print(f"🔌 Connecting to Elasticsearch at {ELASTIC_HOST}...")
    es = Elasticsearch(ELASTIC_HOST)
    
    metadata = {}
    batch_size = 100
    
    for i in tqdm(range(0, len(news_ids), batch_size), desc="Fetching metadata"):
        batch_ids = news_ids[i:i+batch_size]
        
        try:
            response = es.mget(index=INDEX_NAME, body={"ids": batch_ids})
            
            for doc in response["docs"]:
                if doc["found"]:
                    metadata[doc["_id"]] = {
                        "category": doc["_source"].get(CATEGORY_COLUMN, "Unknown"),
                        "title": doc["_source"].get("title", "No Title")
                    }
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch batch {i}: {e}")
            continue
    
    print(f"✅ Fetched metadata for {len(metadata)} news items")
    return metadata

# -----------------------------------------------------------
# 3. Clustering Methods
# -----------------------------------------------------------
def perform_kmeans(vectors, n_clusters=N_CLUSTERS):
    print(f"\n🔵 Running K-Means with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(vectors)
    
    silhouette = silhouette_score(vectors, labels)
    calinski = calinski_harabasz_score(vectors, labels)
    
    print(f"📊 Silhouette Score: {silhouette:.3f}")
    print(f"📊 Calinski-Harabasz Score: {calinski:.3f}")
    
    return labels, kmeans

def perform_dbscan(vectors, eps=EPS, min_samples=MIN_SAMPLES):
    print(f"\n🟣 Running DBSCAN (eps={eps}, min_samples={min_samples})...")
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
    labels = dbscan.fit_predict(vectors)
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    
    print(f"📊 Found {n_clusters} clusters")
    print(f"📊 Noise points: {n_noise}")
    
    return labels, dbscan

# -----------------------------------------------------------
# 4. Cluster Analysis
# -----------------------------------------------------------
def analyze_clusters(labels, news_ids, metadata):
    print("\n📈 Analyzing clusters...")
    
    df = pd.DataFrame({
        'news_id': news_ids,
        'cluster': labels
    })
    
    df['category'] = df['news_id'].map(lambda x: metadata.get(x, {}).get('category', 'Unknown'))
    df['title'] = df['news_id'].map(lambda x: metadata.get(x, {}).get('title', 'No Title'))
    
    cluster_stats = []
    unique_clusters = sorted([c for c in df['cluster'].unique() if c != -1])
    
    for cluster_id in unique_clusters:
        cluster_data = df[df['cluster'] == cluster_id]
        stats = {
            'cluster_id': cluster_id,
            'size': len(cluster_data),
            'top_categories': Counter(cluster_data['category']).most_common(3),
            'sample_titles': cluster_data['title'].head(5).tolist()
        }
        cluster_stats.append(stats)
    
    return df, cluster_stats

def print_cluster_summary(cluster_stats):
    print("\n" + "="*80)
    print("📊 CLUSTER SUMMARY")
    print("="*80)
    
    for stats in cluster_stats:
        print(f"\n🔹 Cluster {stats['cluster_id']} (Size: {stats['size']} items)")
        print("-" * 80)
        print("Top Categories:")
        for cat, count in stats['top_categories']:
            print(f"  • {cat}: {count} items ({100*count/stats['size']:.1f}%)")
        print("Sample Titles:")
        for title in stats['sample_titles']:
            print(f"  • {title}")

# -----------------------------------------------------------
# 5. Visualization
# -----------------------------------------------------------
def visualize_clusters(vectors, labels, method_name="clustering"):
    print(f"\n📊 Creating visualizations for {method_name}...")
    
    os.makedirs("visualizations", exist_ok=True)

    # 1. Cluster size distribution
    plt.figure(figsize=(10, 6))
    unique, counts = np.unique(labels[labels != -1], return_counts=True)
    plt.bar(unique, counts)
    plt.xlabel('Cluster ID')
    plt.ylabel('Number of News Items')
    plt.title(f'Cluster Size Distribution - {method_name}')
    plt.tight_layout()
    plt.savefig(f'visualizations/cluster_distribution_{method_name}.png')
    plt.close()
    
    # 2. 2D projection using first 2 components
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(vectors[:, 0], vectors[:, 1], c=labels, cmap='tab10', alpha=0.6, s=10)
    plt.colorbar(scatter, label='Cluster')
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.title(f'News Items in LSI Space - {method_name}')
    plt.tight_layout()
    plt.savefig(f'visualizations/cluster_visualization_{method_name}.png')
    plt.close()

# -----------------------------------------------------------
# Main Execution
# -----------------------------------------------------------
def main():
    print("🎯 STARTING NEWS CLUSTERING")
    
    vectors, news_ids = load_lsi_data()
    metadata = fetch_news_metadata(news_ids)
    
    # Run K-Means as default
    labels_km, model_km = perform_kmeans(vectors, N_CLUSTERS)
    df_km, stats_km = analyze_clusters(labels_km, news_ids, metadata)
    print_cluster_summary(stats_km)
    visualize_clusters(vectors, labels_km, "kmeans")
    
    # Save results
    print(f"\n💾 Saving results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump({
            'results': {'kmeans': {'labels': labels_km, 'stats': stats_km, 'df': df_km}},
            'vectors': vectors,
            'news_ids': news_ids,
            'metadata': metadata
        }, f)
    
    print("\n✅ CLUSTERING COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
