import streamlit as st
from LLMConnection import llm_explain

def render_llm(query, results):

    with st.spinner("LLM generating explanation..."):

        explanation = llm_explain(
            query,
            results,
            "Hybrid"
        )

    st.markdown(explanation)