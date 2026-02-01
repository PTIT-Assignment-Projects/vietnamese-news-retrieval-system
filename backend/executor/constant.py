from dotenv import load_dotenv
import os
load_dotenv()
DATA_PATH = "data"
CHUNK_SIZE = 5000
INDEX_NAME = "vietnamese_curated_data"
STOPWORD_FILENAME = "vietnamese-stopwords.txt"
ELASTIC_HOST = os.getenv("ELASTIC_HOST")
TOP_N_FEATURE = 10
MAX_FEATURES = 5000
ALL_NEWS_FETCHED_FILEPATH = "batches/all_news.csv"
CATEGORY_KEYWORDS_PICKLE_FILE = "data/category_keywords.pkl"