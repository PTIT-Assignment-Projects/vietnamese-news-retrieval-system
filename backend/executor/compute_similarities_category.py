import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyze_keyword import vietnamese_stopwords
from constant import CATEGORY_TEXT_PICKLE_FILE, MAX_FEATURES, SVD_FEATURES, RANDOM_STATE, TOP_K_SIMILARITY, \
    CATEGORY_COLUMN, CATEGORIES_SIMILARITY_PICKLE_FILE


def load_pickle_file(file_path):
    try:
        category_texts = pd.read_pickle(file_path)
        print(f"Loaded {len(category_texts)} categories from pickle.")
        return category_texts
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Pickle file not found: {CATEGORY_TEXT_PICKLE_FILE}") from e
def vectorizer_with_svd(data: pd.DataFrame):
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        stop_words=list(vietnamese_stopwords),
    )

    X = vectorizer.fit_transform(data.values)
    svd = TruncatedSVD(n_components=SVD_FEATURES, random_state=RANDOM_STATE)
    X = svd.fit_transform(X)
    return X

def top_result_similarity(data: pd.DataFrame, similarity_matrix):
    categories = data.index.tolist()
    pairs = []
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            sim = similarity_matrix[i, j]
            pairs.append((categories[i], categories[j], sim))

    # Sort by similarity (highest first)
    top_k_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)[:TOP_K_SIMILARITY]

    # Display top results
    print(f"\n🏆 Top-{TOP_K_SIMILARITY} most similar pairs of members:")
    for a, b, s in top_k_pairs:
        print(f"{a} — {b}: {s:.3f}")
    return top_k_pairs

def main():
    category_texts = load_pickle_file(CATEGORY_TEXT_PICKLE_FILE)
    X = vectorizer_with_svd(category_texts)
    similarity_matrix = cosine_similarity(X)
    top_k_pairs = top_result_similarity(category_texts, similarity_matrix)
    pd.DataFrame(top_k_pairs, columns=[f"{CATEGORY_COLUMN}1", f"{CATEGORY_COLUMN}2", "similarity"]).to_pickle(CATEGORIES_SIMILARITY_PICKLE_FILE)
    print(f"\n💾 Results saved to {CATEGORIES_SIMILARITY_PICKLE_FILE}")
if __name__ == "__main__":
    main()