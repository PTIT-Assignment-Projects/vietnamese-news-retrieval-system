
import pyarrow.parquet as pq

def read_in_batches(path, batch_size=10000):
    """
    Reads a large Parquet file in batches of rows using pyarrow.
    This is memory efficient as it only loads one batch at a time.
    """
    try:
        parquet_file = pq.ParquetFile(path)
        print(f"Total rows in file: {parquet_file.metadata.num_rows}")
        
        # Iterating over batches
        for batch in parquet_file.iter_batches(batch_size=batch_size):
            # Convert the record batch to a pandas DataFrame
            chunk_df = batch.to_pandas()
            yield chunk_df
            
    except Exception as e:
        print(f"Error reading parquet file: {e}")
