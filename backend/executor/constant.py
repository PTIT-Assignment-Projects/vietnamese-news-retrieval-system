from dotenv import load_dotenv
import os
load_dotenv()
DATA_PATH = "data"
CHUNK_SIZE = 5000
INDEX_NAME = "vietnamese_curated_data"
STOPWORD_FILENAME = "vietnamese-stopwords.txt"
ELASTIC_HOST = os.getenv("ELASTIC_HOST")