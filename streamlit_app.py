# streamlit_app.py

import streamlit as st
import os
from main import extract_keywords_with_gpt, split_into_paragraphs, rephrase_paragraphs_with_gpt, combine_and_trim

st.set_page_config(page_title="Transcript Rewriter with ChatGPT", layout="wide")
st.title("📝 Transcript Rewriter (ChatGPT + Local Merge)")

api_key = st.text_input("Enter your OpenAI API Key:", type="password")
input_text = st.text_area("Paste your transcript text here:", height=300)

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if input_text:
        with st.spinner("Extracting keywords..."):
            keywords = extract_keywords_with_gpt(input_text)

        with st.spinner("Splitting and rephrasing..."):
            paragraphs = split_into_paragraphs(input_text, max_paragraphs=15)
            rephrased_paragraphs = rephrase_paragraphs_with_gpt(paragraphs, keywords)

        with st.spinner("Combining into final output..."):
            final_output = combine_and_trim(rephrased_paragraphs, original_length=len(input_text))

        st.subheader("🔑 Extracted Keywords")
        st.write(", ".join(keywords))

        st.subheader("📄 Final Rephrased Transcript")
        st.write(final_output)
else:
    st.info("Please enter your OpenAI API key to continue.")
