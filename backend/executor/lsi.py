import pickle

import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from constant import ALL_NEWS_FETCHED_FILEPATH, NUM_TOPICS, TOPIC_SUMMARIZATION_JSON_FILE, LSI_DATA_PICKLE_FILE
from util import save_json_file


def perform_lsi(df: pd.DataFrame):
    print(f"\nVectorizing {len(df)} content (TF-IDF)...")
    tfidf_vectorizer = TfidfVectorizer()
    X_tfidf = tfidf_vectorizer.fit_transform(df["content"])
    lsi_model = TruncatedSVD(n_components=NUM_TOPICS, random_state=42)
    lsi_matrix = lsi_model.fit_transform(X_tfidf)
    return lsi_model, tfidf_vectorizer, lsi_matrix

def save_topic_summarization(lsi_model, vectorizer):
    terms = vectorizer.get_feature_names_out()

    topics = []
    for i, comp in enumerate(lsi_model.components_, start=1):
        terms_comp = list(zip(terms, comp))
        sorted_terms = sorted(terms_comp, key=lambda x: x[1], reverse=True)[:10]
        topic_keywords = [t[0] for t in sorted_terms]
        topics.append({"topic_id": i, "keywords": topic_keywords})

    save_json_file(topics, TOPIC_SUMMARIZATION_JSON_FILE)

def main():
    df = pd.read_csv(ALL_NEWS_FETCHED_FILEPATH)
    df = df.dropna(subset=['content'])
    lsi_model, vectorizer, vectors = perform_lsi(df)
    save_topic_summarization(lsi_model, vectorizer)
    with open(LSI_DATA_PICKLE_FILE, "wb") as f:
        pickle.dump({
            "vectors": vectors,           # The mathematical vectors of content
            "ids": df["id"].tolist(),     # The content IDs
            "model": lsi_model            # The trained model
        }, f)
if __name__ == "__main__":
    main()