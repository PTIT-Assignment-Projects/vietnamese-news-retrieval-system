import numpy as np
import torch
import pickle
import os
import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class CategoryMatcher:
    def __init__(
        self, 
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        embeddings_path="data/embeddings.pkl"
    ):
        print(f"Loading model {model_name}... (this might take a few seconds)")
        self.model = SentenceTransformer(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        if not os.path.exists(embeddings_path):
            raise FileNotFoundError(f"Embeddings file not found at {embeddings_path}. Please run create_embeddings.py first.")

        print(f"Loading embeddings database from {embeddings_path}...")
        with open(embeddings_path, "rb") as f:
            data = pickle.load(f)

        self.embeddings = data["embeddings"]  
        self.categories = data["categories"]
        self.ids = data["ids"]

        if isinstance(self.embeddings, torch.Tensor):
            self.embeddings = self.embeddings.numpy()

        print("Ready!")

    def _embed(self, texts):
        emb = self.model.encode(texts, convert_to_numpy=True, device=self.device)
        return emb

    def _top_k(self, emb, k=5):
        sims = cosine_similarity(emb, self.embeddings)[0]
        idxs = np.argsort(sims)[-k:][::-1]
        return idxs, sims[idxs]

    def match_category(self, texts, k=10):
        """Find the most likely category based on top-k similar news items"""
        results = []
        for text in texts:
            emb = self._embed([text])
            idxs, sims = self._top_k(emb, k)

            # Weighted voting by cosine similarity
            cat_scores = {}
            for i, sim in zip(idxs, sims):
                cat = self.categories[i]
                cat_scores[cat] = cat_scores.get(cat, 0) + float(sim)

            if not cat_scores:
                results.append({"category": "Unknown", "score": 0.0})
                continue

            # Best category
            best_cat = max(cat_scores, key=cat_scores.get)
            score = cat_scores[best_cat]

            results.append({
                "category": best_cat,
                "score": float(score),
            })

        return results

    def find_similar_news(self, texts, k=5):
        """Find the top-k most similar news items"""
        results = []
        for text in texts:
            emb = self._embed([text])
            idxs, sims = self._top_k(emb, k)

            matches = []
            for i, sim in zip(idxs, sims):
                matches.append({
                    "news_id": self.ids[i],
                    "category": self.categories[i],
                    "similarity": float(sim)
                })
            results.append(matches)

        return results

if __name__ == "__main__":
    # Quick test
    try:
        matcher = CategoryMatcher()
        test_query = "tình hình kinh tế thế giới đang có nhiều biến động"
        print(f"\nQuery: {test_query}")
        
        cat_match = matcher.match_category([test_query])
        print(f"Matched Category: {cat_match[0]['category']} (Score: {cat_match[0]['score']:.4f})")
        
        sim_news = matcher.find_similar_news([test_query], k=3)
        print("\nTop 3 Similar News Items:")
        for i, match in enumerate(sim_news[0], 1):
            print(f"{i}. ID: {match['news_id']} | Category: {match['category']} | Similarity: {match['similarity']:.4f}")
            
    except Exception as e:
        print(f"Error: {e}")
