import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import MiniBatchKMeans

class SemanticAnalyzer:
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initializes the semantic analyzer.
        Using a multilingual model that supports Vietnamese by default.
        """
        print(f"📡 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
    def create_embeddings(self, texts):
        """
        Generates dense vector embeddings for a list of texts.
        """
        if not texts:
            return np.array([])
        
        print(f"📊 Generating embeddings for {len(texts)} documents...")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings

    def perform_clustering(self, embeddings, n_clusters=5):
        """
        Groups documents into clusters using K-Means.
        Useful for 'Related News' or 'Top Trending Topics'.
        """
        if len(embeddings) < n_clusters:
            n_clusters = len(embeddings)
            
        if n_clusters == 0:
            return []

        kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        return clusters

if __name__ == "__main__":
    # Quick test
    texts = [
        "Thủ tướng Phạm Minh Chính thăm và làm việc tại Mỹ",
        "Đoàn đại biểu Việt Nam thảo luận về kinh tế bền vững",
        "Công nghệ AI đang thay đổi cách chúng ta làm việc",
        "Trí tuệ nhân tạo và ứng dụng trong y tế",
        "Bóng đá Việt Nam chuẩn bị cho vòng loại World Cup"
    ]
    
    analyzer = SemanticAnalyzer()
    embeddings = analyzer.create_embeddings(texts)
    clusters = analyzer.perform_clustering(embeddings, n_clusters=3)
    
    for i, text in enumerate(texts):
        print(f"Cluster {clusters[i]}: {text}")
