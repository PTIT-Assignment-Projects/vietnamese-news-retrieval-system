from elasticsearch import Elasticsearch

from constant import INDEX_NAME

es = Elasticsearch(
    [{"host": "localhost", "port": 9200, "scheme": "http"}],
    verify_certs=False,
    ssl_show_warn=False
)
print("Connected to Elasticsearch:", es.info()['version']['number'])
if es.indices.exists(index=INDEX_NAME):
    print(f"Deleting existing index '{INDEX_NAME}'...")
    es.indices.delete(index=INDEX_NAME)