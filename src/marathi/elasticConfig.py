from elasticsearch import Elasticsearch

INDEX_NAME = "schemes_mapping"

def get_es_client():

    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=("elasticsearch", "e3TKzHmKRFWBP4gY--cjeQ")
    )

    return es