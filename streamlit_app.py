# streamlit_app.py

import streamlit as st
import os
from main import split_transcript, rephrase_each_paragraph, combine_rephrased_text

st.set_page_config(page_title="AI Transcript Rewriter", layout="wide")
st.title("📄 Transcript Rewriter (ChatGPT + Style Control)")

# API Key
api_key = st.text_input("🔑 OpenAI API Key:", type="password")

# Tone & Style Selection
tone = st.selectbox("🎨 Choose Tone (optional)", [
    "Default", "Formal", "Casual", "Humorous", "Motivational", 
    "Empathetic", "Assertive", "Professional", "Poetic", "Neutral"
])
humanize = st.checkbox("🤖 Write in 100% Human-Like Style (AI Undetectable)")
if humanize:
    full_prompt = (
        "Make this sound 100% human-written. Avoid any signs of AI-generated language. "
        "Use natural sentence variation, idioms, and tone shifts. Be engaging, yet authentic.\n\n"
        + full_prompt
    )

style = st.selectbox("✍️ Choose Script Style (optional)", [
    "Default", "Meme-style", "Storytelling", "Inspirational", "Socratic",
    "Bullet points", "Explanatory", "Twitter-thread", "Narrative", "Educational"
])
lang = st.selectbox("🌐 Output Language", ["English", "Spanish", "French", "Hindi", "Arabic"])
if lang != "English":
    full_prompt = f"Translate and rephrase into {lang}.\n\n" + full_prompt

# Check if the storytelling style should be preserved
preserve_story = st.checkbox("📚 Keep storytelling format/style")

# Control paragraph splitting and rephrasing length
para_len = st.slider("🧱 Paragraph word count (split input)", min_value=50, max_value=500, value=200, step=50)
extend_limit = st.slider("📏 Rephrasing length multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# Main text input
input_text = st.text_area("📝 Paste full transcript:", height=300)
uploaded_file = st.file_uploader("📤 Upload a transcript file (.txt)", type=["txt"])
if uploaded_file:
    input_text = uploaded_file.read().decode("utf-8")

# Buttons
start_button = st.button("🚀 Start Rephrasing")
stop_button = st.button("🛑 Stop")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if start_button:
        if not input_text.strip():
            st.warning("Please paste a transcript first.")
        else:
            st.success("Starting rephrasing process...")

            with st.spinner("Splitting transcript..."):
                paragraphs = split_transcript(input_text, max_words_per_paragraph=para_len)

            st.info(f"✅ Split into {len(paragraphs)} paragraphs (~{para_len} words each)")

            # Rephrasing Prompt Modifier
            keyword_prompt = f"Write in a {tone} tone, using {style} style."
            if preserve_story:
                keyword_prompt += " Keep the storytelling structure."

            with st.spinner("Rephrasing..."):
                rephrased = []
                for para in paragraphs:
                    full_prompt = (
                        f"{keyword_prompt}\n\nRephrase this paragraph. "
                        f"Adjust length by a factor of {extend_limit:.1f}:\n\n{para}"
                    )
                    response = rephrase_each_paragraph([para], keywords=None)  # you can pass prompt here if needed
                    rephrased.extend(response)

            final_output = combine_rephrased_text(rephrased)

            st.subheader("✅ Rephrased Output")
            st.text_area("📜 Rephrased Transcript:", value=final_output, height=500)

            st.download_button("📥 Download Transcript", data=final_output, file_name="rephrased_transcript.txt")

    if stop_button:
        st.warning("🚫 Process stopped manually.")
else:
    st.info("🔐 Enter your OpenAI API key to start.")
original_words = len(input_text.split())
rephrased_words = len(final_output.split())
read_time = round(original_words / 200)

st.metric("📄 Original Word Count", original_words)
st.metric("✍️ Rephrased Word Count", rephrased_words)
st.metric("⏱️ Estimated Read Time", f"{read_time} min")
