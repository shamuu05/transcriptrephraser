# streamlit_app.py
import streamlit as st
import os
from main import split_transcript, rephrase_each_paragraph, combine_rephrased_text

st.set_page_config(page_title="AI Transcript Rewriter", layout="wide")

# Move controls to sidebar for cleaner layout
with st.sidebar:
    st.title("⚙️ Controls")
    
    # API Key
    api_key = st.text_input("🔑 OpenAI API Key:", type="password")
    
    # User Profiles & Settings
    profile = st.selectbox("👤 Select Profile", ["Default", "My Writing Style", "Client A", "Client B"])
    user_settings = {
        "My Writing Style": {"tone": "Casual", "style": "Meme-style"},
        "Client A": {"tone": "Professional", "style": "Narrative"},
        "Client B": {"tone": "Formal", "style": "Bullet points"},
    }
    
    # Tone & Style Selection
    if profile in user_settings:
        tone = user_settings[profile]["tone"]
        style = user_settings[profile]["style"]
    else:
        tone = st.selectbox("🎨 Choose Tone (optional)", [
            "Default", "Formal", "Casual", "Humorous", "Motivational", 
            "Empathetic", "Assertive", "Professional", "Poetic", "Neutral"
        ])
        style = st.selectbox("✍️ Choose Script Style (optional)", [
            "Default", "Meme-style", "Storytelling", "Inspirational", "Socratic",
            "Bullet points", "Explanatory", "Twitter-thread", "Narrative", "Educational"
        ])
    
    
    # Multi-Persona / Voice Options
    persona = st.selectbox("🗣️ Choose Writing Persona (optional)", [
        "Default", "Motivational Coach", "Corporate Executive", 
        "Cool Teenager", "Old Monk", "YouTube Vlogger", 
        "Friendly Teacher", "Meme Lord", "Sci-Fi Narrator", "Reddit Commenter"
    ])
    
    # Language Selector
    lang = st.selectbox("🌐 Output Language", ["English", "Spanish", "French", "Hindi", "Arabic"])
    
    # Check if the storytelling style should be preserved
    preserve_story = st.checkbox("📚 Keep storytelling format/style")
    
    # Control paragraph splitting and rephrasing length
    para_len = st.slider("🧱 Paragraph word count (split input)", min_value=50, max_value=500, value=200, step=50)
    extend_limit = st.slider("📏 Rephrasing length multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    
    # Auto Save / Resume with Session State
    if 'last_text' not in st.session_state:
        st.session_state['last_text'] = ""
    
    if st.button("🔁 Resume Last Session"):
        input_text = st.session_state.get('last_text', "")
        st.session_state['current_text'] = input_text

    # Buttons
    start_button = st.button("🚀 Start Rephrasing")
    stop_button = st.button("🛑 Stop")

# Main area
st.title("📄 Transcript Rewriter (ChatGPT + Style Control)")

# File Upload for transcript
uploaded_file = st.file_uploader("📤 Upload a transcript file (.txt)", type=["txt"])
if uploaded_file:
    input_text = uploaded_file.read().decode("utf-8")
    st.session_state['current_text'] = input_text
else:
    # Main text input
    input_text = st.text_area("📝 Paste full transcript:", 
                             value=st.session_state.get('current_text', ""), 
                             height=300)

# Save current text to session state
if input_text and input_text != st.session_state.get('last_text', ""):
    st.session_state['last_text'] = input_text
    st.success("🧠 Session Saved!")

# Advanced Prompt Engineering
with st.expander("🛠️ Advanced Prompt Engineering (optional)"):
    custom_prompt = st.text_area("🔧 Enter your custom rewrite prompt (overrides tone/style):")

# Experimental Features
with st.expander("🧪 Experimental AI Features"):
    enable_qna = st.checkbox("🔍 Generate Q&A from transcript")
    summarize = st.checkbox("📝 Create summary first")
    turn_into_blog = st.checkbox("📚 Turn into blog post")

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
            
            # Build the prompt based on settings
            keyword_prompt = f"Write in a {tone} tone, using {style} style."
            
            if preserve_story:
                keyword_prompt += " Keep the storytelling structure."
                
            if humanize:
                keyword_prompt = ("Make this sound 100% human-written. Avoid any signs of AI-generated language. "
                                 "Use natural sentence variation, idioms, and tone shifts. Be engaging, yet authentic.\n\n"
                                 + keyword_prompt)
                
            if persona != "Default":
                keyword_prompt = f"Write this as if you are a {persona}.\n\n" + keyword_prompt
                
            if lang != "English":
                keyword_prompt = f"Translate and rephrase into {lang}.\n\n" + keyword_prompt
                
            if summarize:
                keyword_prompt = "First summarize, then rephrase:\n\n" + keyword_prompt
                
            if turn_into_blog:
                keyword_prompt = "Turn this into a high-quality blog post:\n\n" + keyword_prompt
            
            with st.spinner("Rephrasing..."):
                rephrased = []
                for para in paragraphs:
                    if custom_prompt.strip():
                        final_prompt = custom_prompt + "\n\n" + para
                    else:
                        final_prompt = (
                            f"{keyword_prompt}\n\nRephrase this paragraph. "
                            f"Adjust length by a factor of {extend_limit:.1f}:\n\n{para}"
                        )
                    response = rephrase_each_paragraph([para], keywords=final_prompt)
                    rephrased.extend(response)
                    
            final_output = combine_rephrased_text(rephrased)
            
            # Generate Q&A if enabled
            if enable_qna:
                with st.spinner("Generating Q&A from transcript..."):
                    qna_prompt = "Generate a Q&A section based on this content:\n\n" + input_text
                    qna_response = rephrase_each_paragraph([input_text], keywords=qna_prompt)
                    qna_output = combine_rephrased_text(qna_response)
                
                st.subheader("📋 Generated Q&A")
                st.text_area("Q&A Content:", value=qna_output, height=300)
                st.download_button("📥 Download Q&A", data=qna_output, file_name="transcript_qa.txt")
            
            # Display stats & metrics
            original_words = len(input_text.split())
            rephrased_words = len(final_output.split())
            read_time = round(original_words / 200)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Original Word Count", original_words)
            with col2:
                st.metric("✍️ Rephrased Word Count", rephrased_words)
            with col3:
                st.metric("⏱️ Estimated Read Time", f"{read_time} min")
            
            # Output section
            st.subheader("✅ Rephrased Output")
            st.text_area("📜 Rephrased Transcript:", value=final_output, height=500)
            st.download_button("📥 Download Transcript", data=final_output, file_name="rephrased_transcript.txt")
            
            # Original vs Rephrased Viewer
            with st.expander("🔍 Compare Original vs Rephrased"):
                original_chunks = split_transcript(input_text)
                for orig, rew in zip(original_chunks, rephrased):
                    st.markdown("**Original:**")
                    st.code(orig)
                    st.markdown("**Rephrased:**")
                    st.code(rew)
    
    if stop_button:
        st.warning("🚫 Process stopped manually.")
else:
    st.info("🔐 Enter your OpenAI API key to start.")
