import os
from underthesea import
from elasticsearch import Elasticsearch

es = Elasticsearch(
    [{"host": "localhost", "port": 9200, "scheme": "http"}],
    verify_certs=False,
    ssl_show_warn=False
)
def load_stopwords(path):
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

stopword_path = os.path.join(os.path.dirname(__file__), "data", "stopwords-el.txt")
vietnamese_stopwords = load_stopwords(stopword_path)

def clean_text(text: str) -> str: