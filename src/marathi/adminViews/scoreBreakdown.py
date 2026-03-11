import streamlit as st

def render_score_breakdown(lex_score, sem_score):

    alpha = 0.5
    beta = 0.5

    hybrid_score = alpha * lex_score + beta * sem_score

    st.metric("Lexical Score", round(lex_score,3))
    st.metric("Semantic Score", round(sem_score,3))
    st.metric("Hybrid Score", round(hybrid_score,3))

    winner = "Lexical" if lex_score > sem_score else "Semantic"

    st.success(f"Highest Score: {winner}")