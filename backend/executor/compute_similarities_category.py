import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyze_keyword import vietnamese_stopwords
from constant import CATEGORY_TEXT_PICKLE_FILE, MAX_FEATURES, SVD_FEATURES, RANDOM_STATE, CATEGORY_COLUMN, CATEGORIES_SIMILARITY_JSON_FILE
from util import save_json_file


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
            sim = float(similarity_matrix[i, j])
            pairs.append((categories[i], categories[j], sim))

    top_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
    result = []
    for a, b, s in top_pairs:
        result.append({
            f"{CATEGORY_COLUMN}1": a,
            f"{CATEGORY_COLUMN}2": b,
            "similarity": s
        })
        print(f"{a} — {b}: {s:.3f}")
    return result

def main():
    category_texts = load_pickle_file(CATEGORY_TEXT_PICKLE_FILE)
    X = vectorizer_with_svd(category_texts)
    similarity_matrix = cosine_similarity(X)
    top_pairs = top_result_similarity(category_texts, similarity_matrix)
    save_json_file(top_pairs, CATEGORIES_SIMILARITY_JSON_FILE)
if __name__ == "__main__":
    main()