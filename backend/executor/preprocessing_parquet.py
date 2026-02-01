import os
from constant import DATA_PATH, CHUNK_SIZE
from preprocessing import read_in_batches

for root, dirs, files in os.walk(DATA_PATH):
    for filename in files:
        full_path = os.path.join(root, filename)
        batches = read_in_batches(full_path, batch_size=CHUNK_SIZE)
        try:
            first_batch = next(batches)
            if not first_batch.empty:
                content = first_batch.iloc[0, 0]
                category = first_batch.iloc[0, 2]
            else:
                print("The file is empty.")
        except StopIteration:
            print("No data found.")
        except Exception as e:
            print(f"Failed to read: {e}")