def semantic_search(es, index_name, query_text, model):

    vector = model.encode(query_text)

    query = {
        "size": 10,
        "knn": {
            "field": "description_vector",
            "query_vector": vector.tolist(),
            "k": 5,
            "num_candidates": 20
        }
    }

    res = es.search(index=index_name, body=query)

    return res["hits"]["hits"]