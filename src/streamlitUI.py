import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="Marathi Govt Scheme Search", page_icon="🔍", layout="wide")

# --- Elasticsearch Config ---
index_name = "schemes_mapping"

try:
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=('elasticsearch', 'e3TKzHmKRFWBP4gY--cjeQ')
    )
    es_status = es.ping()
except:
    st.error("❌ Could not connect to Elasticsearch.")
    es_status = False


# --- Load Model ---
@st.cache_resource
def load_model():
    return SentenceTransformer("l3cube-pune/marathi-sentence-similarity-sbert")

model = load_model()


# -----------------------------------------
# SEARCH FUNCTIONS
# -----------------------------------------

def lexical_search(query_text):
    query = {
        "size": 5,
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["scheme_name^2", "description"],
                "fuzziness": "AUTO"
            }
        }
    }
    res = es.search(index=index_name, body=query, source=["scheme_name", "description", "scheme_link"])
    return res.get("hits", {}).get("hits", [])


def semantic_search(query_text):
    vector = model.encode(query_text)

    query = {
        "size": 5,
        "knn": {
            "field": "description_vector",
            "query_vector": vector.tolist(),
            "k": 5,
            "num_candidates": 20
        }
    }

    res = es.search(index=index_name, body=query, source=["scheme_name", "description", "scheme_link"])
    return res.get("hits", {}).get("hits", [])


def hybrid_search(query_text):
    vector = model.encode(query_text)

    query = {
        "size": 5,
        "query": {
            "bool": {
                "should": [
                    {"multi_match": {"query": query_text, "fields": ["scheme_name^2", "description"]}},
                    {"knn": {
                        "field": "description_vector",
                        "query_vector": vector.tolist(),
                        "k": 5,
                        "num_candidates": 20
                    }},
                ]
            }
        }
    }

    res = es.search(index=index_name, body=query, source=["scheme_name", "description", "scheme_link"])
    return res.get("hits", {}).get("hits", [])



# -----------------------------------------
# PAGE HEADER
# -----------------------------------------

st.markdown("<h1 style='text-align:center; color:#D32F2F;'>🔍 महाराष्ट्र शासन योजना शोध</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>तुमच्या गरजेनुसार योग्य योजना शोधा.</p>", unsafe_allow_html=True)
st.write("---")

search_query = st.text_input("🔎 तुमचा शोध येथे लिहा", placeholder="उदा. विद्यार्थ्यांसाठी योजना, शेतकऱ्यांसाठी मदत योजना...")


# ----------------------------------------------------
# TABLE STYLE
# ----------------------------------------------------

st.markdown("""
    <style>
        div[data-testid="column"] > div {
            border: 2px solid white;
            border-radius: 5px;
            padding: 10px;
            background-color: #00000020;
            min-height: 650px;
        }
    </style>
""", unsafe_allow_html=True)




# ====================================================
# SEARCH BUTTON PRESSED
# ====================================================

if st.button("Search"):
    if not search_query.strip():
        st.warning("कृपया शोध शब्द प्रविष्ट करा.")
    else:
        with st.spinner("शोध सुरू आहे..."):

            lex_results = lexical_search(search_query)
            sem_results = semantic_search(search_query)
            hyb_results = hybrid_search(search_query)

        # ----------------------------
        # Columns with table borders
        # ----------------------------
        col1, col2, col3 = st.columns(3)

        # ----------------------------
        # COLUMN 1 - LEXICAL
        # ----------------------------
        with col1:
            st.markdown("<div class='border-col'>", unsafe_allow_html=True)
            st.subheader("Lexical results")

            if not lex_results:
                st.write("❌ कोणतेही परिणाम नाहीत")
            else:
                for r in lex_results:
                    src = r["_source"]
                    st.markdown(f"**{src['scheme_name']}**")
                    exp = st.expander("expand")
                    exp.write(src["description"])
                    st.markdown(f"[🔗 अधिक माहितीसाठी क्लिक करा]({src['scheme_link']})")
                    st.write("---")

            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------
        # COLUMN 2 - SEMANTIC
        # ----------------------------
        with col2:
            st.markdown("<div class='border-col'>", unsafe_allow_html=True)
            st.subheader("Semantic results")

            if not sem_results:
                st.write("❌ कोणतेही परिणाम नाहीत")
            else:
                for r in sem_results:
                    src = r["_source"]
                    st.markdown(f"**{src['scheme_name']}**")
                    exp = st.expander("expand")
                    exp.write(src["description"])
                    st.markdown(f"[🔗 अधिक माहितीसाठी क्लिक करा]({src['scheme_link']})")
                    st.write("---")

            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------
        # COLUMN 3 - HYBRID
        # ----------------------------
        with col3:
            st.markdown("<div class='border-col'>", unsafe_allow_html=True)
            st.subheader("Hybrid results")

            if not hyb_results:
                st.write("❌ कोणतेही परिणाम नाहीत")
            else:
                for r in hyb_results:
                    src = r["_source"]
                    st.markdown(f"**{src['scheme_name']}**")
                    exp = st.expander("expand")
                    exp.write(src["description"])
                    st.markdown(f"[🔗 अधिक माहितीसाठी क्लिक करा]({src['scheme_link']})")
                    st.write("---")

            st.markdown("</div>", unsafe_allow_html=True)
