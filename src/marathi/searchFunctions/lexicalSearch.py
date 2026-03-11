def lexical_search(es, index_name, query_text):

    query = {
        "size": 10,
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["scheme_name^2", "description"],
                "fuzziness": "AUTO"
            }
        }
    }

    res = es.search(index=index_name, body=query)

    return res["hits"]["hits"]