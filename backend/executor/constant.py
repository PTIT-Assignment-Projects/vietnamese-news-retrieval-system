from dotenv import load_dotenv
import os
load_dotenv()

# NUMBER

CHUNK_SIZE = 5000
TOP_N_FEATURE = 10
MAX_FEATURES = 5000
RANDOM_STATE = 42
SVD_FEATURES = 100
TOP_K_SIMILARITY = 10
NUM_TOPICS = 10
NUM_WORDS_PER_TOPICS = 15

# Elasticsearch
INDEX_NAME = "vietnamese_curated_data"
ELASTIC_HOST = os.getenv("ELASTIC_HOST")


# DATASET

CATEGORY_COLUMN = "category"
CONTENT_COLUMN = "content"
ID_COLUMN = "id"



# FILEPATH

# # # ####################
#                         #
# ########################
DATA_PATH = "data"
STOPWORD_FILENAME = "vietnamese-stopwords.txt"
ALL_NEWS_FETCHED_FILEPATH = "batches/all_news.csv"
CATEGORY_KEYWORDS_PICKLE_FILE = "data/category_keywords.pkl"
CATEGORY_KEYWORDS_JSON_FILE = "file/category_keywords.json"
KEYWORDS_PER_NEWS_PICKLE_FILE = "data/keyword_per_news.pkl"
KEYWORDS_PER_NEWS_JSON_FILE = "file/keyword_per_news.json"
CATEGORY_TEXT_PICKLE_FILE = "data/category_texts.pkl"
CATEGORIES_SIMILARITY_JSON_FILE = "file/categories_similarities.json"
TOPIC_SUMMARIZATION_JSON_FILE = "file/topic_summary.json"
LSI_DATA_PICKLE_FILE = "file/lsi_data.pkl"