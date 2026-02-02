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
CATEGORY_KEYWORDS_JSON_FILE = "file/category_keywords.json"
KEYWORDS_PER_NEWS_PICKLE_FILE = "data/keyword_per_news.pkl"
KEYWORDS_PER_NEWS_JSON_FILE = "file/keyword_per_news.json"
CATEGORY_COLUMN = "category"
CONTENT_COLUMN = "content"
CATEGORY_TEXT_PICKLE_FILE = "data/cateogory_texts.pkl"