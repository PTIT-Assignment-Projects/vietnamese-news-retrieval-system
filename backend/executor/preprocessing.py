import os

import pyarrow.parquet as pq

from constant import *

if not os.path.exists(DATA_PATH):
    print(f"Warning: {DATA_PATH} not found. Using dummy path for demonstration.")
    file_path = 'data/data.parquet'

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

if __name__ == "__main__":
    # Get the first batch and print the text column of the first item
    print(f"Loading first item from: {DATA_PATH}")
    batches = read_in_batches(DATA_PATH, batch_size=1)
    try:
        first_batch = next(batches)
        if not first_batch.empty:
            print("\n--- First Item (Row 0) ---")
            
            # Access the second column (index 1) - typically 'text' in these datasets
            if len(first_batch.columns) > 1:
                col_name = first_batch.columns[1]
                value = first_batch.iloc[0, 1]
                print(f"Second Column Name: {col_name}")
                print(f"Value:\n{value}")
            else:
                print("Note: File only has one column.")
                print(f"First Column Name: {first_batch.columns[0]}")
                print(f"Value:\n{first_batch.iloc[0, 0]}")
                
            print("--------------------------\n")
        else:
            print("The file is empty.")
    except StopIteration:
        print("No data found.")
    except Exception as e:
        print(f"Failed to read: {e}")