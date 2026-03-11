import streamlit as st

def render_results(title, results):

    st.markdown(f"### {title}")

    if not results:
        st.write("No results")
        return

    for i, r in enumerate(results):

        src = r["_source"]
        score = r.get("_score")

        st.markdown(f"**Rank {i+1} — {src['scheme_name']}**")
        st.caption(f"Score: {score}")

        with st.expander("Description"):
            st.write(src["description"])

        st.write("---")