from elasticsearch import Elasticsearch, helpers
import os
import numpy as np
from constant import INDEX_NAME, DATA_PATH, CHUNK_SIZE
from preprocessing import read_in_batches
try:
    from semantic_analysis import SemanticAnalyzer
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False

# Initialize Elasticsearch
es = Elasticsearch(
    [{"host": "localhost", "port": 9200, "scheme": "http"}],
    verify_certs=False,
    ssl_show_warn=False
)

def create_index(vector_dim=384):
    """Delete existing index and create a new one with hybrid mapping."""
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

    # Hybrid Mapping: BM25 + Vector Search
    mapping = {
        "mappings": {
            "properties": {
                "category": {"type": "keyword"},
                "content": {
                    "type": "text",
                    "analyzer": "standard", 
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "content_vector": {
                    "type": "dense_vector",
                    "dims": vector_dim,
                    "index": True,
                    "similarity": "cosine"
                },
                "tags": {"type": "keyword"} # For NER/Entities later
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"🆕 Created index '{INDEX_NAME}' with hybrid mapping (Vector Dim: {vector_dim}).")
    return True

def generate_actions(df_chunk, analyzer=None):
    """Generator for bulk indexing actions. Processes text and creates embeddings."""
    texts = df_chunk['text'].tolist()
    
    embeddings = []
    if analyzer:
        try:
            embeddings = analyzer.create_embeddings(texts)
        except Exception as e:
            print(f"   ⚠️ Embedding generation failed: {e}")
            embeddings = []

    for i, (_, row) in enumerate(df_chunk.iterrows()):
        action = {
            "_index": INDEX_NAME,
            "_id": str(row.get("id", "")),
            "_source": {
                "category": str(row.get("domain", "")),
                "content": str(row.get("text", "")), # This is already segmented if preprocess=True
            }
        }
        
        if len(embeddings) > i:
            action["_source"]["content_vector"] = embeddings[i].tolist()
            
        yield action

def main(use_semantic=True, preprocess=True):
    # Initialize analyzer if requested
    analyzer = None
    if use_semantic and HAS_SEMANTIC:
        try:
            analyzer = SemanticAnalyzer()
            # Dim depends on the model (paraphrase-multilingual-MiniLM-L12-v2 is 384)
            vector_dim = 384 
        except Exception as e:
            print(f"⚠️ Could not load SemanticAnalyzer: {e}")
            analyzer = None
            vector_dim = 384 # Default placeholder
    else:
        vector_dim = 384

    if not create_index(vector_dim=vector_dim):
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
        print(f"❌ No parquet files found at path: {DATA_PATH}")
        return

    print(f"📂 Found {len(parquet_files)} parquet files to ingest.")

    total_success = 0
    for file_path in parquet_files:
        print(f"📦 Processing file: {os.path.basename(file_path)}")
        try:
            # Note: preprocess=True here will use word_tokenize from preprocessing.py
            batches = read_in_batches(file_path, batch_size=CHUNK_SIZE, preprocess=preprocess)
            for i, chunk_df in enumerate(batches):
                success, failed = helpers.bulk(es, generate_actions(chunk_df, analyzer))
                total_success += success
                print(f"   ✅ Chunk {i + 1}: {success} documents indexed.")
                if failed:
                    print(f"   ⚠️ {len(failed)} documents failed in this chunk.")
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")

    print(f"\n🎉 Hybrid Ingestion completed!")
    print(f"📊 Total documents successfully indexed: {total_success}")

if __name__ == "__main__":
    # You can toggle semantic search and preprocessing here
    main(use_semantic=True, preprocess=True)
