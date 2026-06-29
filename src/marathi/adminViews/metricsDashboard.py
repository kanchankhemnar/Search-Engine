import streamlit as st
import pandas as pd
from evaluation.metric import evaluate_system
from searchFunctions.lexicalSearch import lexical_search
from searchFunctions.semanticSearch import semantic_search
from searchFunctions.hybridSearch import hybrid_search
# Removed invalid import for CSV file


TEST_FILE = "./testSet.csv"    # your dataset path


def render_metrics_dashboard(es, index_name, model):

    st.subheader("View 3 — Performance Metrics Dashboard")

    # Load dataset
    try:
        test_df = pd.read_csv(TEST_FILE)
        st.success("Test dataset loaded successfully")
    except:
        st.error("❌ testSet.csv not found.")
        print("❌ testSet.csv not found. Please ensure the file exists at the specified path.")
        test_df = None

    if test_df is None:
        return

    # Wrapper functions (because evaluate_system expects only query input)
    def lexical(q):
        return lexical_search(es, index_name, q)

    def semantic(q):
        return semantic_search(es, index_name, q, model)

    def hybrid(q):
        return hybrid_search(es, index_name, q, model)

    # Run evaluation
    with st.spinner("Evaluating test dataset..."):

        lexical_metrics = evaluate_system(test_df, lexical)
        semantic_metrics = evaluate_system(test_df, semantic)
        hybrid_metrics = evaluate_system(test_df, hybrid)

    # Create results table
    results_df = pd.DataFrame([
        {"Search Type": "Lexical", **lexical_metrics},
        {"Search Type": "Semantic", **semantic_metrics},
        {"Search Type": "Hybrid", **hybrid_metrics}
    ])

    st.dataframe(results_df, use_container_width=True)

    # Best model
    best = results_df.sort_values(
        "Top-1 Accuracy",
        ascending=False
    ).iloc[0]["Search Type"]

    st.success(f"Best Performing Method: {best}")
    return results_df  