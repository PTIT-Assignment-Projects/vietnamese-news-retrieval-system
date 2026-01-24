# https://huggingface.co/datasets/bkai-foundation-models/BKAINewsCorpus/blob/main/data/train-00000-of-00029-64c4b5d20df8ef78.parquet
import pyarrow.parquet as pq

from constant import *

# read file as Table
table = pq.read_table(DOWNLOADED_DATA_PATH)

# drop columns if present
cols_to_drop = [c for c in ("link", "publish") if c in table.column_names]
if cols_to_drop:
    table = table.drop(cols_to_drop)

# inspect schema / first rows
print(table.schema)
print(table.slice(0, 3).to_pydict())

# optionally write back to parquet without those columns
pq.write_table(table, DATA_PATH)
