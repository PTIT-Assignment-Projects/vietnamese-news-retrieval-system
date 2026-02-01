
import os
import pyarrow.parquet as pq
from underthesea import word_tokenize

def preprocess_vietnamese(text):
    """
    Cleans and segments Vietnamese text.
    Standardizes whitespace and uses underthesea for word segmentation.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Basic cleaning: remove extra whitespace
    text = " ".join(text.split())
    
    # Word segmentation (essential for Vietnamese IR)
    # format="text" replaces spaces with underscores (e.g., "trọng_tâm")
    try:
        segmented_text = word_tokenize(text, format="text")
        return segmented_text
    except Exception as e:
        print(f"Warning: Tokenization failed: {e}")
        return text

def read_in_batches(path, batch_size=10000, preprocess=False):
    """
    Reads a large Parquet file in batches.
    Optionally applies Vietnamese preprocessing to the 'text' column.
    """
    try:
        parquet_file = pq.ParquetFile(path)
        print(f"Total rows in file: {parquet_file.metadata.num_rows}")
        
        for batch in parquet_file.iter_batches(batch_size=batch_size):
            chunk_df = batch.to_pandas()
            
            if preprocess and 'text' in chunk_df.columns:
                print(f"   ⚙️  Preprocessing {len(chunk_df)} rows...")
                chunk_df['text'] = chunk_df['text'].apply(preprocess_vietnamese)
                
            yield chunk_df
            
    except Exception as e:
        print(f"Error reading parquet file: {e}")

if __name__ == "__main__":
    from constant import DATA_PATH
    # Test on a single file if exists
    test_path = 'data/train-00000-of-00132.parquet'
    if os.path.exists(test_path):
        print(f"Testing preprocessing on: {test_path}")
        batches = read_in_batches(test_path, batch_size=5, preprocess=True)
        try:
            first_batch = next(batches)
            print("\n--- Preprocessed Sample ---")
            print(first_batch['text'].iloc[0][:200] + "...")
            print("--------------------------\n")
        except StopIteration:
            print("No data.")
