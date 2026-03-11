from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def load_model():
    return SentenceTransformer(
        "l3cube-pune/marathi-sentence-similarity-sbert"
    )