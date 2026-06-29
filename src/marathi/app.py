import streamlit as st
from elasticConfig import get_es_client, INDEX_NAME
from adminViews.metricsDashboard import render_metrics_dashboard
from modelLoader import load_model

from searchFunctions.lexicalSearch import lexical_search
from searchFunctions.semanticSearch import semantic_search
from searchFunctions.hybridSearch import hybrid_search

from adminViews.searchComparison import render_results
from adminViews.scoreBreakdown import render_score_breakdown
from adminViews.llmView import render_llm
from adminViews.comparisionGraph import render_comparison_graph

st.set_page_config(
    page_title="Marathi Govt Scheme Search",
    page_icon="🔍",
    layout="wide"
)

es = get_es_client()
model = load_model()

mode = st.sidebar.radio("Select Panel", ["User","Admin"])

# USER PANEL

if mode == "User":

    st.title("🔍 महाराष्ट्र शासन योजना शोध")

    query = st.text_input("Enter Search Query")

    if st.button("Search"):

        hyb_results = hybrid_search(es, INDEX_NAME, query, model)
        
        results = hyb_results
        if not hyb_results:
            sem_results = semantic_search(es, INDEX_NAME, query, model)
            results = sem_results
        else:
            lex_results = lexical_search(es, INDEX_NAME, query)
            results = lex_results 


        for r in results:

            src = r["_source"]

            st.subheader(src["scheme_name"])

            with st.expander("अधिक माहिती"):
                st.write(src["description"])

            st.markdown(
                f"[Link]({src['scheme_link']})"
            )

# ADMIN PANEL

if mode == "Admin":

    query = st.text_input("Admin Test Query")

    if st.button("Run Analysis"):

        lex = lexical_search(es, INDEX_NAME, query)
        sem = semantic_search(es, INDEX_NAME, query, model)
        hyb = hybrid_search(es, INDEX_NAME, query, model)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Search Comparison",
            "Score Breakdown",
            "Metrics Dashboard",
            "Comparison Graph",
            "LLM Explanation"
        ])

        with tab1:

            col1, col2, col3 = st.columns(3)

            with col1:
                render_results("Lexical", lex)

            with col2:
                render_results("Semantic", sem)

            with col3:
                render_results("Hybrid", hyb)

        with tab2:

            lex_score = lex[0]["_score"] if lex else 0
            sem_score = sem[0]["_score"] if sem else 0

            render_score_breakdown(lex_score, sem_score)
            
        results_df = None

        with tab3:
            results_df = render_metrics_dashboard(es, INDEX_NAME, model)
        
        with tab4:
            render_comparison_graph(results_df)
    
        with tab5:
            render_llm(query, hyb)