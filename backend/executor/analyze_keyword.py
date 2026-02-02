import json
import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from underthesea import text_normalize, word_tokenize
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError
from constant import CATEGORY_KEYWORDS_JSON_FILE, CATEGORY_KEYWORDS_PICKLE_FILE, KEYWORDS_PER_NEWS_JSON_FILE, KEYWORDS_PER_NEWS_PICKLE_FILE, STOPWORD_FILENAME, INDEX_NAME, ELASTIC_HOST, TOP_N_FEATURE, MAX_FEATURES, \
    ALL_NEWS_FETCHED_FILEPATH

es = Elasticsearch(ELASTIC_HOST)
def load_stopwords(path):
    with open(path, "r", encoding="utf-8") as f:
        return {
            line.strip().replace(" ", "_").lower()
            for line in f
            if line.strip()
        }

stopword_path = os.path.join(os.path.dirname(__file__), "file", STOPWORD_FILENAME)
vietnamese_stopwords = load_stopwords(stopword_path)

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text_normalize(text)
    text = text.lower()
    # Remove noise characters like replacement character
    text = text.replace("\ufffd", " ")
    
    tokens = word_tokenize(text, format="text", use_token_normalize=True).split()
    
    # Regex for valid Vietnamese/Latin alphanumeric tokens (including compound word underscores)
    # This excludes Thaana script, emoji, and other non-standard symbols.
    valid_pattern = re.compile(r'^[a-z0-9_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\.\-]+$')
    
    cleaned_tokens = []
    for t in tokens:
        # Only keep tokens that match our valid character set
        if not valid_pattern.match(t):
            continue
        
        # Finally, check for stopwords and length
        if t not in vietnamese_stopwords and len(t) > 1:
            cleaned_tokens.append(t)
            
    return " ".join(cleaned_tokens)

BATCH_SAVE_DIR = "batches"
PROGRESS_FILE = os.path.join(BATCH_SAVE_DIR, "progress.json")

os.makedirs(BATCH_SAVE_DIR, exist_ok=True)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed": 0}

def save_progress(processed):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"processed": processed}, f)

def save_batch(batch_idx, records):
    path = os.path.join(BATCH_SAVE_DIR, f"batch_{batch_idx:05d}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def fetch_all_speeches(batch_size=5000, save_batch_size=1000):
    prog = load_progress()
    already_processed = int(prog.get("processed", 0))

    res = es.search(
        index=INDEX_NAME,
        body={"query": {"match_all": {}}},
        scroll="5m",
        size=batch_size
    )
    scroll_id = res.get("_scroll_id")
    total_hits = res["hits"]["total"]["value"]
    print(f"Total hits: {total_hits}")

    fetched = 0
    hits = res["hits"]["hits"]
    batch_idx = 0
    batch_buf = []

    try:
        while hits:
            for hit in hits:
                fetched += 1
                if fetched <= already_processed:
                    continue  # skip already-processed docs

                src = hit["_source"]
                rec = {
                    "id": hit["_id"],
                    "category": src.get("category", "").strip(),
                    "content": clean_text(src.get("content", "")),
                }
                batch_buf.append(rec)

                if len(batch_buf) >= save_batch_size:
                    save_batch(batch_idx, batch_buf)
                    batch_idx += 1
                    already_processed += len(batch_buf)
                    save_progress(already_processed)
                    batch_buf = []

            print(f"Retrieved {min(fetched, total_hits)}/{total_hits} news (processed {already_processed})")

            try:
                res = es.scroll(scroll_id=scroll_id, scroll="5h")
            except NotFoundError:
                print("Scroll context expired; stopping early and saving progress.")
                break

            scroll_id = res.get("_scroll_id")
            hits = res["hits"]["hits"]
    finally:
        # flush remaining buffer and save progress
        if batch_buf:
            save_batch(batch_idx, batch_buf)
            already_processed += len(batch_buf)
            save_progress(already_processed)

        # attempt to clear scroll
        try:
            if scroll_id:
                es.clear_scroll(scroll_id=scroll_id)
        except Exception:
            pass

    # load saved batches into DataFrame
    df = pd.concat(
        [pd.read_json(os.path.join(BATCH_SAVE_DIR, f), lines=True)
         for f in sorted(os.listdir(BATCH_SAVE_DIR)) if f.endswith(".jsonl")],
        ignore_index=True
    )

    return df

def compute_keywords(df: pd.DataFrame, group_col, top_n=TOP_N_FEATURE) -> dict:
    results = {}
    
    print(f"Grouping data by {group_col}...")
    # Group content by category and join them. 
    # To save memory, we ensure content is string and handled efficiently.
    grouped = df.groupby(group_col)["content"].apply(lambda x: " ".join(x.astype(str)))
    
    print(f"Initializing TfidfVectorizer for {len(grouped)} groups...")
    # the text is already cleaned and tokenized in clean_text,
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        stop_words=None,
        tokenizer=str.split,
        token_pattern=None
    )

    print("Fitting and transforming TF-IDF matrix...")
    tfidf_matrix = vectorizer.fit_transform(grouped.values)
    feature_names = vectorizer.get_feature_names_out()
    
    print("Extracting top keywords...")
    for idx, name in enumerate(grouped.index):
        # Get the sparse row and convert only it to dense to save RAM
        row = tfidf_matrix[idx]
        scores = row.toarray()[0]
        top_idx = scores.argsort()[-top_n:][::-1]
        results[name] = [(feature_names[i], round(scores[i], 3)) for i in top_idx if scores[i] > 0]
        
    return results

def compute_keywords_per_news(df: pd.DataFrame, top_n=TOP_N_FEATURE, batch_size=5000) -> dict:
    results = {}
    print(f"Computing keywords for {len(df)} news items in batches of {batch_size}...")

    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        stop_words=list(vietnamese_stopwords),
        tokenizer=str.split,
        token_pattern=None
    )

    contents = df["content"].astype(str).tolist()
    # Use 'id' column if available, otherwise fallback to index
    indices = df["id"].tolist() if "id" in df.columns else df.index.tolist()

    for start in range(0, len(contents), batch_size):
        end = start + batch_size
        batch_texts = contents[start:end]
        batch_ids = indices[start:end]

        # Filter for valid non-empty content
        valid_batch = [(i, t) for i, t in zip(batch_ids, batch_texts) if t.strip()]
        if not valid_batch:
            continue

        idxs, texts = zip(*valid_batch)

        # Fit and transform on the current batch (local IDF)
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()

        # Convert to array for score extraction
        dense_matrix = tfidf_matrix.toarray()
        for local_idx, news_id in enumerate(idxs):
            row = dense_matrix[local_idx]
            top_idx = row.argsort()[-top_n:][::-1]
            results[news_id] = [(feature_names[j], round(row[j], 3)) for j in top_idx if row[j] > 0]

        print(f"  > Processed {min(end, len(contents))}/{len(contents)} news items")

    return results

def main():
    if not os.path.exists(ALL_NEWS_FETCHED_FILEPATH):
        print(f"File {ALL_NEWS_FETCHED_FILEPATH} not found. Fetching from Elasticsearch...")
        df = fetch_all_speeches()
        df.to_csv(ALL_NEWS_FETCHED_FILEPATH, index=False, encoding="utf-8")
    else:
        print(f"Loading data from {ALL_NEWS_FETCHED_FILEPATH}...")
        # Include 'id' in usecols to allow mapping keywords back to documents
        df = pd.read_csv(ALL_NEWS_FETCHED_FILEPATH, usecols=["id", "category", "content"])
        df = df.dropna(subset=["content"])

    print(f"Data loaded. Shape: {df.shape}")
    keywords = compute_keywords(df, "category")
    pd.to_pickle(keywords, CATEGORY_KEYWORDS_PICKLE_FILE)
    # Print some results
    for cat, kws in list(keywords.items())[:5]:
        print(f"\nCategory: {cat}")
        print(f"Keywords: {kws}")

    print("\nComputing per-news keywords (sample)...")
    # Compute for a small sample or full dataset if needed
    news_keywords = compute_keywords_per_news(df.iloc[:1000]) # Sample for demonstration
    pd.to_pickle(news_keywords, KEYWORDS_PER_NEWS_PICKLE_FILE)
    for nid, kws in list(news_keywords.items())[:3]:
        print(f"\nNews ID: {nid}")
        print(f"Keywords: {kws}")

    # Optionally save keywords to file
    with open(CATEGORY_KEYWORDS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False, indent=4)
    print(f"\nKeywords saved to {CATEGORY_KEYWORDS_JSON_FILE}")

    with open(KEYWORDS_PER_NEWS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(news_keywords, f, ensure_ascii=False, indent=4)
    print(f"\nKeywords saved to {KEYWORDS_PER_NEWS_JSON_FILE}")

if __name__ == "__main__":
    main()