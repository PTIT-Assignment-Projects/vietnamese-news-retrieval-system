import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle
import numpy as np
import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from constant import ALL_NEWS_FETCHED_FILEPATH, CONTENT_COLUMN, CATEGORY_COLUMN, ID_COLUMN
except ImportError:
    from constant import CONTENT_COLUMN, CATEGORY_COLUMN, ID_COLUMN
    ALL_NEWS_FETCHED_FILEPATH = "batches/all_news.csv"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BATCH_SIZE = 32
OUTPUT_FILE = "data/embeddings.pkl"
SAMPLE_SIZE = 5000  # Limit to 5000 for demonstration, set to None for all

def load_dataset():
    if not os.path.exists(ALL_NEWS_FETCHED_FILEPATH):
        print(f"❌ {ALL_NEWS_FETCHED_FILEPATH} not found. Please run analyze_keyword.py first.")
        return None
    
    print(f"📂 Loading dataset from {ALL_NEWS_FETCHED_FILEPATH}...")
    df = pd.read_csv(ALL_NEWS_FETCHED_FILEPATH)
    df = df.dropna(subset=[CONTENT_COLUMN])
    
    if SAMPLE_SIZE and len(df) > SAMPLE_SIZE:
        print(f"🕒 Sampling {SAMPLE_SIZE} news items...")
        df = df.sample(SAMPLE_SIZE, random_state=42)
        
    return df

def main():
    os.makedirs("data", exist_ok=True)
    
    df = load_dataset()
    if df is None:
        return

    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model.to(device)

    texts = df[CONTENT_COLUMN].tolist()
    ids = df[ID_COLUMN].tolist()
    categories = df[CATEGORY_COLUMN].tolist()

    print(f"Encoding {len(texts)} news items...")

    embeddings = []
    for i in tqdm(range(0, len(texts), BATCH_SIZE)):
        batch = texts[i:i+BATCH_SIZE]
        batch_emb = model.encode(
            batch, 
            show_progress_bar=False, 
            device=device, 
            convert_to_numpy=True
        )
        embeddings.extend(batch_emb)

    embeddings = np.array(embeddings)

    print(f"Saving embeddings to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump({
            "embeddings": embeddings,
            "ids": ids,
            "categories": categories
        }, f)

    print("✅ Done! Saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
