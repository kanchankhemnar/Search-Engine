import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

indexName = "marathi_schemes"

try:
    es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=('elasticsearch', 'e3TKzHmKRFWBP4gY--cjeQ')
    )
except ConnectionError as e:
    print("Connection Error:", e)
    
if es.ping():
    print("Succesfully connected to ElasticSearch!!")
else:
    print("Oops!! Can not connect to Elasticsearch!")




def search(input_keyword):
    model = SentenceTransformer('l3cube-pune/marathi-sentence-similarity-sbert')
    vector = model.encode(input_keyword)

    query = {
        "size": 2,
        "knn": {
            "field": "description_vector",
            "query_vector": vector.tolist(),
            "k": 2,
            "num_candidates": 10
        }
    }

    result = es.search(index="marathi_schemes", body=query, source=["scheme_name", "description","deadline"])
    result = result['hits']['hits']

    return result

def main():
    st.title("Search marathi gov schemes")

    # Input: User enters search query
    search_query = st.text_input("Enter your search query")

    # Button: User triggers the search
    if st.button("Search"):
        if search_query:
            # Perform the search and get results
            results = search(search_query)

            # Display search results
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    if '_source' in result:
                        try:
                            st.header(f"{result['_source']['scheme_name']}")
                        except Exception as e:
                            print(e)
                        
                        try:
                            st.write(f"वर्णन : {result['_source']['description']}")
                        except Exception as e:
                            print(e)

                        try:
                            st.write(f"कालमर्यादा :  {result['_source']['deadline']}")
                        except Exception as e:
                            print(e)

                        st.divider()

                    
if __name__ == "__main__":
    main()