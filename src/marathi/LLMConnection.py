import google.generativeai as genai
import os
# import streamlit as st
from dotenv import load_dotenv

load_dotenv() 
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


if os.getenv("GEMINI_API_KEY") is None:
    print("❌ Gemini API key not loaded")
else:
    print("✅ Gemini API key loaded")



def llm_explain(query, results, search_type):
    """
    query: user query
    results: list of ES hits
    search_type: Lexical / Semantic / Hybrid
    """

    context = ""
    for i, r in enumerate(results[:3]):
        src = r["_source"]
        score = round(r.get("_score", 0), 3)
        context += f"""
Result {i+1}:
Scheme Name: {src['scheme_name']}
Description: {src['description']}
Score: {score}
"""

    prompt = f"""
You are an assistant helping explain search results for a government scheme discovery platform.

User Query: "{query}"
Search Type: {search_type}

Below are retrieved schemes.

{context}

Tasks:
1. Generate a short, query-specific title for each scheme.
2. Generate a 2–3 line summary relevant to the query.
Respond in Marathi. Use simple marathi language that a general user can understand. Avoid technical jargon.
Keep answers factual. Do NOT invent new schemes.
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text
