from elasticsearch import Elasticsearch, helpers
import os
from constant import INDEX_NAME, DATA_PATH, CHUNK_SIZE
from preprocessing import read_in_batches

# Initialize Elasticsearch
es = Elasticsearch(
    [{"host": "localhost", "port": 9200, "scheme": "http"}],
    verify_certs=False,
    ssl_show_warn=False
)

def create_index():
    """Delete existing index and create a new one with proper mapping."""
    print("🔍 Checking connection to Elasticsearch...")
    try:
        info = es.info()
        print(f"✅ Connected to Elasticsearch version: {info['version']['number']}")
    except Exception as e:
        print(f"❌ Error connecting to Elasticsearch: {e}")
        return False

    if es.indices.exists(index=INDEX_NAME):
        print(f"🗑️ Deleting existing index '{INDEX_NAME}'...")
        es.indices.delete(index=INDEX_NAME)

    # Robust mapping for news retrieval
    # 'id' is mapped to _id for document idempotency
    # 'category' (domain) is mapped to keyword for filtering
    # 'content' (text) is mapped to text for full-text search
    mapping = {
        "mappings": {
            "properties": {
                "category": {"type": "keyword"},
                "content": {
                    "type": "text",
                    "analyzer": "standard", # Suggestion: use 'vietnamese' if plugin is installed
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                }
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Created index '{INDEX_NAME}' with mapping.")
    return True

def generate_actions(df_chunk):
    """Generator for bulk indexing actions. Maps parquet columns to ES document."""
    for _, row in df_chunk.iterrows():
        # Mapping parquet columns:
        # 'id' -> _id (ES document ID)
        # 'domain' -> category
        # 'text' -> content
        yield {
            "_index": INDEX_NAME,
            "_id": str(row.get("id", "")),
            "_source": {
                "category": str(row.get("domain", "")),
                "content": str(row.get("text", "")),
            }
        }

def main():
    if not create_index():
        return

    # Gather all parquet files
    parquet_files = []
    if os.path.isfile(DATA_PATH):
        parquet_files = [DATA_PATH]
    elif os.path.isdir(DATA_PATH):
        for root, _, files in os.walk(DATA_PATH):
            for file in files:
                if file.endswith(".parquet"):
                    parquet_files.append(os.path.join(root, file))
    else:
        # Handle cases where DATA_PATH might be relative to the script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_data_path = os.path.join(base_dir, DATA_PATH)
        if os.path.isdir(abs_data_path):
            for root, _, files in os.walk(abs_data_path):
                for file in files:
                    if file.endswith(".parquet"):
                        parquet_files.append(os.path.join(root, file))

    if not parquet_files:
        print(f"No parquet files found at path: {DATA_PATH}")
        return

    print(f"Found {len(parquet_files)} parquet files to ingest.")

    total_success = 0
    for file_path in parquet_files:
        print(f"Processing file: {os.path.basename(file_path)}")
        try:
            batches = read_in_batches(file_path, batch_size=CHUNK_SIZE)
            for i, chunk_df in enumerate(batches):
                success, failed = helpers.bulk(es, generate_actions(chunk_df))
                total_success += success
                print(f"Chunk {i + 1}: {success} documents indexed.")
                if failed:
                    print(f"{len(failed)} documents failed in this chunk.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Ingestion completed!")
    print(f"Total documents successfully indexed: {total_success}")

if __name__ == "__main__":
    main()
