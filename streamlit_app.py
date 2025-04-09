import streamlit as st
from main import extract_keywords, format_paragraphs, rephrase_with_keywords

st.set_page_config(page_title="Manual Transcript Rewriter", layout="wide")
st.title("📝 Manual Transcript Rewriter Bot")

input_text = st.text_area("Paste your transcript text here:", height=300)

if input_text:
    with st.spinner("Processing transcript..."):
        keywords = extract_keywords(input_text)
        paragraphs = format_paragraphs(input_text)
        new_transcript = rephrase_with_keywords(paragraphs, keywords)

        st.subheader("🔑 Detected Keywords")
        st.write(", ".join(keywords))

        st.subheader("📝 Rewritten Transcript")
        for para in new_transcript:
            st.write(para)