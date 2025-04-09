import streamlit as st
from app.main import fetch_transcript, extract_keywords, format_paragraphs, rephrase_with_keywords

st.set_page_config(page_title="YouTube Transcript Rewriter", layout="wide")
st.title("🎥 YouTube Transcript Rewriter Bot")

video_url = st.text_input("Paste the YouTube video link here:")

if video_url:
    with st.spinner("Fetching and processing transcript..."):
        transcript = fetch_transcript(video_url)
        if transcript:
            keywords = extract_keywords(transcript)
            paragraphs = format_paragraphs(transcript)
            new_transcript = rephrase_with_keywords(paragraphs, keywords)

            st.subheader("🔑 Detected Keywords")
            st.write(", ".join(keywords))

            st.subheader("📝 Rewritten Transcript")
            for para in new_transcript:
                st.write(para)
        else:
            st.error("Failed to fetch transcript. Make sure the video has captions and the link is valid.")