# streamlit_app.py

import streamlit as st
import os
from main import extract_keywords, format_paragraphs, rephrase_with_openai

st.set_page_config(page_title="Transcript Rewriter with OpenAI", layout="wide")
st.title("📝 Transcript Rewriter (OpenAI-powered)")

api_key = st.text_input("Enter your OpenAI API Key:", type="password")
input_text = st.text_area("Paste your transcript text here:", height=300)

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if input_text:
        with st.spinner("Analyzing and rewriting..."):
            keywords = extract_keywords(input_text)
            paragraphs = format_paragraphs(input_text, max_paragraphs=15)
            final_output = rephrase_with_openai(paragraphs, keywords)

            st.subheader("🔑 Detected Keywords")
            st.write(", ".join(keywords))

            st.subheader("📝 Rewritten Transcript")
            st.write(final_output)
else:
    st.info("Please enter your OpenAI API key to continue.")
