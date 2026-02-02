import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from elasticsearch import Elasticsearch
from tqdm import tqdm
import pickle
import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from analyze_keyword import clean_text, vietnamese_stopwords
    from constant import INDEX_NAME, ELASTIC_HOST, CONTENT_COLUMN, CATEGORY_COLUMN, ID_COLUMN
except ImportError:
    print("⚠️ Could not import 'analyze_keyword' or 'constant'. Make sure you are running this from the backend/executor directory.")
    sys.exit(1)

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
SAMPLE_SIZE = 10000   # Number of news to sample for LSI
NUM_TOPICS = 10       # How many "Thematic Areas" you want to discover
TOP_WORDS = 15         # How many words to display per topic
OUTPUT_FILE = "data/lsi_data.pkl"

# -----------------------------------------------------------
# 1. Fetch Data from Elasticsearch
# -----------------------------------------------------------
def fetch_news_sample(size=10000):
    print(f"🔌 Connecting to Elasticsearch at {ELASTIC_HOST}...")
    es = Elasticsearch(ELASTIC_HOST)

    # Check if index exists
    if not es.indices.exists(index=INDEX_NAME):
        print(f"❌ Index '{INDEX_NAME}' not found.")
        return pd.DataFrame()

    print(f"📥 Fetching {size} random news for LSI analysis...")
    
    # We use a random_score query to get a random sample of the data
    query = {
        "function_score": {
            "query": {"match_all": {}},
            "random_score": {}
        }
    }

    try:
        resp = es.search(index=INDEX_NAME, body={"query": query, "size": size})
    except Exception as e:
        print(f"\n❌ Error fetching data: {e}")
        return pd.DataFrame()

    hits = resp["hits"]["hits"]

    data = []
    print("🧹 Cleaning text...")
    for hit in tqdm(hits, desc="Processing"):
        source = hit["_source"]
        text = source.get(CONTENT_COLUMN, "")
        
        # Only keep news that have actual text (filter out very short ones)
        if text and len(text) > 50: 
            data.append({
                "id": hit["_id"],
                "category": source.get(CATEGORY_COLUMN, "Unknown"),
                "original_text": text,
                "cleaned_text": clean_text(text) 
            })

    return pd.DataFrame(data)

# -----------------------------------------------------------
# 2. Apply LSI (TF-IDF + SVD)
# -----------------------------------------------------------
def perform_lsi(df):
    print(f"\n🧮 Vectorizing {len(df)} news items (TF-IDF)...")
    
    # 1. TF-IDF Vectorization
    tfidf_vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words=list(vietnamese_stopwords),
        tokenizer=str.split, # Already cleaned and tokenized
        token_pattern=None,
        min_df=5,
        max_df=0.90
    )
    
    X_tfidf = tfidf_vectorizer.fit_transform(df["cleaned_text"])

    print(f"📉 Applying TruncatedSVD (LSI) to reduce to {NUM_TOPICS} dimensions...")
    # 2. LSI (Dimensionality Reduction)
    lsi_model = TruncatedSVD(n_components=NUM_TOPICS, random_state=42)
    lsi_matrix = lsi_model.fit_transform(X_tfidf)

    return lsi_model, tfidf_vectorizer, lsi_matrix

# -----------------------------------------------------------
# 3. Display Results
# -----------------------------------------------------------
def print_topics(model, vectorizer):
    print("\n" + "="*60)
    print(f"🔎 FOUND {NUM_TOPICS} THEMATIC AREAS (TOPICS)")
    print("="*60)
    
    terms = vectorizer.get_feature_names_out()
    
    for i, comp in enumerate(model.components_):
        terms_comp = zip(terms, comp)
        # Sort by weight to find most important words in this topic
        sorted_terms = sorted(terms_comp, key=lambda x: x[1], reverse=True)[:TOP_WORDS]
        
        topic_keywords = [t[0] for t in sorted_terms]
        print(f"Topic {i+1}: {', '.join(topic_keywords)}")
        print("-" * 150)

# -----------------------------------------------------------
# Main Execution
# -----------------------------------------------------------
if __name__ == "__main__":
    # Create data directory if not exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 1. Get Data
    df = fetch_news_sample(size=SAMPLE_SIZE)
    
    if df.empty:
        print("❌ No data found or search failed!")
        sys.exit(1)

    # 2. Run LSI
    lsi_model, vectorizer, vectors = perform_lsi(df)

    # 3. Show Human Readable Topics
    print_topics(lsi_model, vectorizer)

    # 4. Save for Clustering
    print(f"\n💾 Saving LSI vectors to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump({
            "vectors": vectors,           
            "ids": df["id"].tolist(),     
            "categories": df["category"].tolist(),
            "model": lsi_model            
        }, f)
    
    print(f"✅ Done! File saved as '{OUTPUT_FILE}'")
