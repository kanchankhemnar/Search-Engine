def hybrid_search(es, index_name, query_text, model):

    vector = model.encode(query_text)

    query = {
        "size": 10,
        "query": {
            "script_score": {
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["scheme_name^2", "description"]
                    }
                },
                "script": {
                    "source": """
                        double bm25 = _score;
                        double cosine = cosineSimilarity(params.query_vector, 'description_vector');
                        return 0.4 * bm25 + 0.6 * cosine;
                    """,
                    "params": {
                        "query_vector": vector.tolist()
                    }
                }
            }
        }
    }

    res = es.search(index=index_name, body=query)

    return res["hits"]["hits"]