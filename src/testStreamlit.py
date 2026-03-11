import streamlit as st
import numpy as np
import pandas as pd
import ast
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from LLMConnection import llm_explain

st.set_page_config(page_title="Marathi Govt Scheme Search", page_icon="🔍", layout="wide")

# ------------------------------
# ELASTICSEARCH CONFIG
# ------------------------------
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


# ------------------------------
# LOAD MODEL
# ------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("l3cube-pune/marathi-sentence-similarity-sbert")

model = load_model()


# ------------------------------
# SEARCH FUNCTIONS
# ------------------------------

def lexical_search(query_text):
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
    res = es.search(index=index_name, body=query, source=["scheme_id","scheme_name", "description", "scheme_link"])
    return res.get("hits", {}).get("hits", [])


def semantic_search(query_text):
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

    res = es.search(index=index_name, body=query, source=["scheme_id","scheme_name", "description", "scheme_link"])
    return res.get("hits", {}).get("hits", [])


def hybrid_search(query_text):
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

    res = es.search(index=index_name, body=query,
                    source=["scheme_id","scheme_name","description","scheme_link"])
    return res.get("hits", {}).get("hits", [])


# ------------------------------
# UI MODE SWITCH (USER / ADMIN)
# ------------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "User"

mode = st.sidebar.radio("Select Panel", ["User", "Admin"])


# ==================================================
# USER PANEL — CLEAN HYBRID SEARCH
# ==================================================
if mode == "User":

    st.markdown("<h1 style='text-align:center; color:#D32F2F;'>🔍 महाराष्ट्र शासन योजना शोध</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>तुमच्या गरजेनुसार योग्य योजना शोधा.</p>", unsafe_allow_html=True)

    search_query = st.text_input("🔎 तुमचा शोध येथे लिहा", placeholder="उदा. विद्यार्थ्यांसाठी योजना, शेतकऱ्यांसाठी मदत योजना...")

    if st.button("Search"):
        if not search_query.strip():
            st.warning("कृपया शोध शब्द प्रविष्ट करा.")
        else:
            with st.spinner("शोध सुरू आहे..."):
                hyb_results = hybrid_search(search_query)

            if not hyb_results:
                st.write("❌ कोणतेही परिणाम नाहीत")
            else:
                for r in hyb_results:
                    src = r["_source"]
                    st.markdown(f"### {src['scheme_name']}")
                    exp = st.expander("वर्णन पाहा")
                    exp.write(src["description"])
                    st.markdown(f"[🔗 अधिक माहितीसाठी क्लिक करा]({src['scheme_link']})")
                    st.write("---")


# ==================================================
# ADMIN PANEL — EXPLAINABILITY DASHBOARD
# ==================================================
if mode == "Admin":

    st.markdown("##  Admin Panel")

    admin_query = st.text_input("🔎 Enter test query for analysis")

    if st.button("Run Analysis"):
        if not admin_query.strip():
            st.warning("Enter a valid query")
        else:
            lex_results = lexical_search(admin_query)
            sem_results = semantic_search(admin_query)
            hyb_results = hybrid_search(admin_query)

            # -----------------------------------------
            # VIEW 1 — SEARCH COMPARISON DASHBOARD
            # -----------------------------------------





            st.subheader("View 1 — Search Comparison")
            col1, col2, col3 = st.columns(3)

            lexical_scores = []


            def render_results(title, results):
                st.markdown(f"### {title}")
                if not results:
                    st.write("❌ No results")
                else:
                    
                    for i, r in enumerate(results):
                        src = r["_source"]
                        score = r.get("_score", "N/A")
                        if title == "Lexical":
                            lexical_scores.insert(i,score)
                        st.markdown(f"**Rank {i+1} — {src['scheme_name']}**")
                        st.caption(f"Score: {score}")
                        exp = st.expander("Expand")
                        exp.write(src["description"])
                        st.write("---")

            with col1:
                render_results("Lexical", lex_results)

            with col2:
                render_results("Semantic", sem_results)

            with col3:
                render_results("Hybrid", hyb_results)


            # -----------------------------------------
            # VIEW 2 — SCORE BREAKDOWN (EXPLAINABILITY)
            # -----------------------------------------
            st.subheader("View 2 — Score Breakdown")

            # alpha = st.slider("Lexical Weight (α)", 0.0, 1.0, 0.5)
            # beta = st.slider("Semantic Weight (β)", 0.0, 1.0, 0.5)
            alpha = 0.5
            beta = 0.5

            # calculating normalized scores for lexical scores

            

            def normalize_scores(scores):
                if not scores:
                    return []
                
                max_score = max(scores)
                
                if max_score == 0:
                    return [0.0 for _ in scores]
                
                normalized = [score / max_score for score in scores]
                return normalized

            if  sem_results:
                sem_score = sem_results[0].get("_score", 0)
                lex_score = lex_results[0].get("_score", 0)
                print("\n\n\n\lex_score:", lex_score)
                print("max lexical score:", max(lexical_scores) if lexical_scores else 0)
                lex_score = lex_score/max(lexical_scores) if lexical_scores else 0
                

                # avg_lex_score = sum(lexical_scores) / len(lexical_scores) if lexical_scores else 0
                # print("avg_lex_score:", avg_lex_score)
                # avg_lex_score = (avg_lex_score/lex_score) if lex_score else 0
                # normalized_lex_scores = normalize_scores(lexical_scores)
                # lex_score = sum(normalized_lex_scores) / len(normalized_lex_scores) if normalized_lex_scores else 0
                hybrid_score = alpha * lex_score + beta * sem_score
                
                print("\n\n\n\lex_score:", lex_score)

                st.metric("Lexical Score",lex_score)
                st.metric("Semantic Score", round(sem_score, 3))
                st.metric("Hybrid Score", round(hybrid_score, 3))

                winner = "Lexical" if lex_score > sem_score else "Semantic"
                st.success(f"Highest Score: {winner} Model")
                
                # print("Lexical Scores:", lexical_scores)
                # print("lex_score:", lex_score)
                # print("avg_lex_score:", avg_lex_score)


            
            # -----------------------------------------
            # VIEW 3 — PERFORMANCE METRICS DASHBOARD
            # -----------------------------------------
            st.subheader("View 3 — Performance Metrics Dashboard")

            TEST_FILE = "./marathi/testSet.csv"  # Format: query,correct_scheme_id

            # Load test dataset
            try:
                test_df = pd.read_csv(TEST_FILE)
                print("Test dataset loaded successfully.")
            except:
                st.error("❌ test_set.csv not found. Upload file in project folder.")
                test_df = None


            # --------- METRIC FUNCTIONS ---------
            def top_k_accuracy(pred_ids, correct_id, k):
                return int(correct_id in pred_ids[:k])

            def reciprocal_rank(pred_ids, correct_id):
                for i, pid in enumerate(pred_ids):
                    if pid == correct_id:
                        return 1 / (i + 1)
                return 0

            def precision_at_k(pred_ids, correct_id, k):
                return int(correct_id in pred_ids[:k]) / k


            # --------- EXTRACT IDS FROM SEARCH RESULTS ---------
            def extract_scheme_ids(results):
                return [r["_source"]["scheme_id"] for r in results]


            # --------- EVALUATION FUNCTION ---------
            def evaluate_system(df, search_function):
                top1, top3, top5, top10, mrr, precision = [], [], [], [],[], []

                for _, row in df.iterrows():
                    query = row["query"]

                    # Convert string "[14,34,43]" → actual list
                    correct_ids = ast.literal_eval(row["relevant_scheme_ids"])
                    # print("\n\nCorrect IDs:", correct_ids)

                    results = search_function(query)
                    pred_ids = extract_scheme_ids(results)
                    # print("\n\nPredicted IDs:", pred_ids)

                    # Now check if ANY correct id is in top-k
                    top1.append(any(cid in pred_ids[:1] for cid in correct_ids))
                    top3.append(any(cid in pred_ids[:3] for cid in correct_ids))
                    top5.append(any(cid in pred_ids[:5] for cid in correct_ids))
                    top10.append(any(cid in pred_ids[:10] for cid in correct_ids))


                    # MRR
                    rr = 0
                    for i, pid in enumerate(pred_ids):
                        if pid in correct_ids:
                            rr = 1 / (i + 1)
                            break
                    mrr.append(rr)

                    precision.append(
                        sum(1 for pid in pred_ids[:3] if pid in correct_ids) / 3
                    )


                # print("Top-1 Accuracy:", np.mean(top1))
                # print("Top-3 Accuracy:", np.mean(top3))
                return {
                    "Top-1 Accuracy": np.mean(top1),
                    "Top-3 Accuracy": np.mean(top3),
                    "Top-5 Accuracy": np.mean(top5),
                    "Top-10 Accuracy": np.mean(top10),
                    "MRR": np.mean(mrr),
                    "Precision@3": np.mean(precision)
                }


            # --------- RUN EVALUATION ---------
            if test_df is not None:

                with st.spinner("Evaluating real test data..."):
                    lexical_metrics = evaluate_system(test_df, lexical_search)
                    semantic_metrics = evaluate_system(test_df, semantic_search)
                    hybrid_metrics = evaluate_system(test_df, hybrid_search)

                # --------- RESULTS TABLE ---------
                results_df = pd.DataFrame([
                    {"Search Type": "Lexical", **lexical_metrics},
                    {"Search Type": "Semantic", **semantic_metrics},
                    {"Search Type": "Hybrid", **hybrid_metrics}
                ])

                print("\n\nEvaluation Results:\n", results_df)
                st.dataframe(results_df, use_container_width=True)

                # --------- BEST MODEL ---------
                best = results_df.sort_values("Top-1 Accuracy", ascending=False).iloc[0]["Search Type"]
                st.success(f"Best Performing Method: {best}")





                    
            st.subheader("LLM-based Explanation")

            with st.spinner("LLM generating explanations..."):
                explanation = llm_explain(
                    admin_query,
                    hyb_results,
                    "Hybrid"
                )

            st.markdown("### Output")
            st.markdown(explanation)