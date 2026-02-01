import json
import os

import pandas as pd
from underthesea import text_normalize, word_tokenize
from elasticsearch import Elasticsearch

from constant import STOPWORD_FILENAME, INDEX_NAME, ELASTIC_HOST

es = Elasticsearch(ELASTIC_HOST)
def load_stopwords(path):
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

stopword_path = os.path.join(os.path.dirname(__file__), "data", STOPWORD_FILENAME)
vietnamese_stopwords = load_stopwords(stopword_path)

def clean_text(text: str) -> str:
    text = text_normalize(text)
    text = text.lower()
    tokens = word_tokenize(text, format="text", use_token_normalize = True).split()
    tokens = [t.replace("_", " ") for t in tokens]
    tokens = [t for t in tokens if len(t) > 1 and t not in vietnamese_stopwords]
    return " ".join(tokens)

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

    data = []
    res = es.search(
        index=INDEX_NAME,
        body={"query": {"match_all": {}}},
        scroll="5m",
        size=batch_size
    )
    scroll_id = res["_scroll_id"]
    total_hits = res["hits"]["total"]["value"]
    print(f"Total hits: {total_hits}")

    fetched = 0
    hits = res["hits"]["hits"]
    batch_idx = 0
    batch_buf = []

    # If already_processed > 0 we will skip collecting until we've advanced past that count.
    while hits:
        for hit in hits:
            fetched += 1
            if fetched <= already_processed:
                continue  # skip already-processed docs

            src = hit["_source"]
            rec = {
                "id": hit["_id"],
                "category": src.get("category", "").strip(),
                "speech": clean_text(src.get("content", "")),
            }
            batch_buf.append(rec)

            # flush buffer to disk when it reaches save_batch_size
            if len(batch_buf) >= save_batch_size:
                save_batch(batch_idx, batch_buf)
                batch_idx += 1
                already_processed += len(batch_buf)
                save_progress(already_processed)
                batch_buf = []

        print(f"Retrieved {min(fetched,total_hits)}/{total_hits} news (processed {already_processed})")
        res = es.scroll(scroll_id=scroll_id, scroll="5m")
        scroll_id = res["_scroll_id"]
        hits = res["hits"]["hits"]

    # flush any remaining records
    if batch_buf:
        save_batch(batch_idx, batch_buf)
        already_processed += len(batch_buf)
        save_progress(already_processed)

    # Optionally load all batches into a single DataFrame
    df = pd.concat([pd.read_json(os.path.join(BATCH_SAVE_DIR, f), lines=True) for f in sorted(os.listdir(BATCH_SAVE_DIR)) if f.endswith(".jsonl")], ignore_index=True)
    return df


def main():
    df = fetch_all_speeches()
    print(df.head())
if __name__ == "__main__":
    main()