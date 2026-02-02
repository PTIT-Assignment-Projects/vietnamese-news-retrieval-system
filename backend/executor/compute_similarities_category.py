import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyze_keyword import vietnamese_stopwords
from constant import CATEGORY_TEXT_PICKLE_FILE, MAX_FEATURES, SVD_FEATURES, RANDOM_STATE, TOP_K_SIMILARITY, \
    CATEGORY_COLUMN, CATEGORIES_SIMILARITY_JSON_FILE
from util import save_json_file


class CategorySimilarity:
    def __init__(self, first_column: str, second_column: str, similarity: float):
        self.first_column = first_column
        self.second_column = second_column
        self.similarity = similarity

    def __str__(self) -> str:
        return f"{self.first_column} — {self.second_column}: {self.similarity:.3f}"

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
    top_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
    result = []
    for a, b, s in top_pairs:
        cat_sim = CategorySimilarity(a, b, s)
        result.append(cat_sim)
        print(str(result))
    return result

def main():
    category_texts = load_pickle_file(CATEGORY_TEXT_PICKLE_FILE)
    X = vectorizer_with_svd(category_texts)
    similarity_matrix = cosine_similarity(X)
    top_pairs = top_result_similarity(category_texts, similarity_matrix)
    save_json_file(top_pairs, CATEGORIES_SIMILARITY_JSON_FILE)
if __name__ == "__main__":
    main()