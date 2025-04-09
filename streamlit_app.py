# streamlit_app.py

import streamlit as st
import os
from main import split_transcript, rephrase_each_paragraph, combine_rephrased_text

st.set_page_config(page_title="Long Transcript Rewriter", layout="wide")
st.title("📄 Transcript Rewriter (Token-Limit Safe)")

api_key = st.text_input("Enter your OpenAI API Key:", type="password")
input_text = st.text_area("Paste your full transcript (up to 3000+ words):", height=300)

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if input_text:
        st.info("Splitting transcript into manageable parts...")
        paragraphs = split_transcript(input_text, max_words_per_paragraph=200)

        st.info(f"✅ Split into {len(paragraphs)} paragraphs (max ~200 words each)")

        with st.spinner("Rephrasing paragraphs one by one with ChatGPT..."):
            rephrased = rephrase_each_paragraph(paragraphs)

        final_text = combine_rephrased_text(rephrased)

        st.subheader("📝 Rephrased Transcript (Full Length)")
        st.text_area("Rephrased Output:", value=final_text, height=500)

        st.download_button("📥 Download Rephrased Transcript", data=final_text, file_name="rephrased_transcript.txt")
else:
    st.info("Please enter your OpenAI API key to start.")
