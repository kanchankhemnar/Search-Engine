import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def render_comparison_graph(results_df):

    st.subheader("📊 Model Comparison Graph")

    if results_df is None or results_df.empty:
        st.warning("No data available for plotting")
        return

    # Set index
    df = results_df.set_index("Search Type")

    # Select metrics
    metrics = ["Top-1 Accuracy", "Top-3 Accuracy", "MRR", "Precision@3"]

    # 🔥 TRANSPOSE → metrics become x-axis groups
    plot_df = df[metrics].T

    # 🎨 Bigger figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot grouped bars
    plot_df.plot(kind="bar", ax=ax)

    # Labels
    ax.set_title("Search Model Performance Comparison", fontsize=16)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_xlabel("Evaluation Metrics", fontsize=12)

    # Scale properly
    ax.set_ylim(0, 1)

    # Grid
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    # Clean x labels
    plt.xticks(rotation=0)

    # Legend (models)
    plt.legend(title="Search Type", loc='upper right')

    # Space fix
    plt.tight_layout()

    st.pyplot(fig)