# streamlit_app.py
import streamlit as st
import os
import re
from main import split_transcript, rephrase_each_paragraph, combine_rephrased_text

st.set_page_config(page_title="AI Transcript Rewriter", layout="wide")

# Initialize session state variables
if 'last_text' not in st.session_state:
    st.session_state['last_text'] = ""
if 'current_text' not in st.session_state:
    st.session_state['current_text'] = ""
if 'humanize' not in st.session_state:
    st.session_state['humanize'] = False
if 'persona' not in st.session_state:
    st.session_state['persona'] = "Default"
if 'lang' not in st.session_state:
    st.session_state['lang'] = "English"
if 'keywords' not in st.session_state:
    st.session_state['keywords'] = ""

# Move controls to sidebar for cleaner layout
with st.sidebar:
    st.title("⚙️ Controls")
    
    # API Key
    api_key = st.text_input("🔑 OpenAI API Key:", type="password")
    
    # Tone & Style Selection
    tone = st.selectbox("🎨 Choose Tone (optional)", [
        "Default", "Formal", "Casual", "Conversational", "Humorous", "Motivational", 
        "Empathetic", "Assertive", "Professional", "Poetic", "Neutral", "Enthusiastic",
        "Technical", "Friendly", "Authoritative", "Educational", "Inspirational", 
        "Critical", "Analytical", "Persuasive", "Satirical"
    ])
    
    style = st.selectbox("✍️ Choose Script Style (optional)", [
        "Default", "Meme-style", "Storytelling", "Inspirational", "Socratic",
        "Bullet points", "Explanatory", "Twitter-thread", "Narrative", "Educational",
        "Dialog", "Interview", "Academic", "News article", "Blog post", "Tutorial"
    ])
    
    # Human Style Writing (Bypass AI Detectors)
    st.session_state['humanize'] = st.checkbox("🤖 Write in 100% Human-Like Style (AI Undetectable)")
    
    # Multi-Persona / Voice Options
    st.session_state['persona'] = st.selectbox("🗣️ Choose Writing Persona (optional)", [
        "Default", "Motivational Coach", "Corporate Executive", "Cool Teenager", 
        "Old Monk", "YouTube Vlogger", "Friendly Teacher", "Meme Lord", 
        "Sci-Fi Narrator", "Reddit Commenter", "College Professor", "Marketing Expert",
        "Tech Enthusiast", "Life Coach", "Fitness Trainer", "Travel Blogger",
        "Food Critic", "Data Scientist", "Historian", "Comedian", "Business Analyst",
        "Sports Commentator", "Political Analyst", "Fashion Expert", "Journalist"
    ])
    
    # Language Selector
    st.session_state['lang'] = st.selectbox("🌐 Output Language", [
        "English", "Spanish", "French", "German", "Italian", "Portuguese", 
        "Russian", "Japanese", "Chinese", "Korean", "Hindi", "Arabic", 
        "Dutch", "Swedish", "Norwegian", "Finnish", "Danish", "Polish", 
        "Turkish", "Greek", "Thai", "Vietnamese", "Indonesian", "Malay"
    ])
    
    # Check if the storytelling style should be preserved
    preserve_story = st.checkbox("📚 Keep storytelling format/style")
    
    # Control paragraph splitting and rephrasing length
    para_len = st.slider("🧱 Paragraph word count (split input)", min_value=50, max_value=500, value=200, step=50)
    extend_limit = st.slider("📏 Rephrasing length multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    
    # Keyword management
    st.session_state['keywords'] = st.text_area("🔑 Keywords to include (comma separated):", 
                                               value=st.session_state.get('keywords', ""))
    
    keywords_to_remove = st.text_area("❌ Keywords to remove (comma separated):")
    
    # Auto Save / Resume with Session State
    if st.button("🔁 Resume Last Session"):
        st.session_state['current_text'] = st.session_state['last_text']

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
                             value=st.session_state['current_text'], 
                             height=300)

# Save current text to session state
if input_text and input_text != st.session_state['last_text']:
    st.session_state['last_text'] = input_text
    st.success("🧠 Session Saved!")

# Advanced Prompt Engineering
with st.expander("🛠️ Advanced Prompt Engineering (optional)"):
    custom_prompt = st.text_area("🔧 Enter your custom rewrite prompt (overrides tone/style):")

# Highlight keywords in the input text
if st.session_state['keywords'] and input_text:
    keywords_list = [k.strip() for k in st.session_state['keywords'].split(',') if k.strip()]
    if keywords_list:
        st.subheader("📌 Input Text with Highlighted Keywords:")
        highlighted_text = input_text
        for keyword in keywords_list:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            highlighted_text = pattern.sub(f"**{keyword}**", highlighted_text)
        st.markdown(highlighted_text)

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
            
            # Process keywords
            include_keywords = [k.strip() for k in st.session_state['keywords'].split(',') if k.strip()]
            exclude_keywords = [k.strip() for k in keywords_to_remove.split(',') if k.strip()]
            
            # Build the prompt based on settings
            keyword_prompt = f"Write in a {tone} tone, using {style} style."
            
            if preserve_story:
                keyword_prompt += " Keep the storytelling structure."
                
            if st.session_state['humanize']:
                keyword_prompt = ("Make this sound 100% human-written. Avoid any signs of AI-generated language. "
                                 "Use natural sentence variation, idioms, and tone shifts. Be engaging, yet authentic.\n\n"
                                 + keyword_prompt)
                
            if st.session_state['persona'] != "Default":
                keyword_prompt = f"Write this as if you are a {st.session_state['persona']}.\n\n" + keyword_prompt
                
            if st.session_state['lang'] != "English":
                keyword_prompt = f"Translate and rephrase into {st.session_state['lang']}.\n\n" + keyword_prompt
            
            # Add strict word count instruction
            target_word_count = int(para_len * extend_limit)
            keyword_prompt += f"\n\nIMPORTANT: Each paragraph MUST be approximately {target_word_count} words long."
            
            # Add keyword instructions
            if include_keywords:
                keyword_prompt += f"\n\nMake sure to include these keywords: {', '.join(include_keywords)}."
            
            if exclude_keywords:
                keyword_prompt += f"\n\nAvoid using these words: {', '.join(exclude_keywords)}."
            
            with st.spinner("Rephrasing..."):
                rephrased = []
                for para in paragraphs:
                    if custom_prompt.strip():
                        final_prompt = custom_prompt + "\n\n" + para
                    else:
                        final_prompt = (
                            f"{keyword_prompt}\n\nRephrase this paragraph and strictly adhere to the target word count "
                            f"of {target_word_count} words (±10%):\n\n{para}"
                        )
                    response = rephrase_each_paragraph([para], keywords=final_prompt)
                    rephrased.extend(response)
                    
            final_output = combine_rephrased_text(rephrased)
            
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
            
            # Original vs Rephrased Viewer with highlighted keywords
            with st.expander("🔍 Compare Original vs Rephrased"):
                original_chunks = split_transcript(input_text)
                for i, (orig, rew) in enumerate(zip(original_chunks, rephrased)):
                    st.markdown(f"**Paragraph {i+1}**")
                    col1, col2 = st.columns(2)
                    
                    # Highlight keywords in original text
                    highlighted_orig = orig
                    if include_keywords:
                        for keyword in include_keywords:
                            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                            highlighted_orig = pattern.sub(f"**{keyword}**", highlighted_orig)
                    
                    # Highlight keywords in rephrased text
                    highlighted_rew = rew
                    if include_keywords:
                        for keyword in include_keywords:
                            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                            highlighted_rew = pattern.sub(f"**{keyword}**", highlighted_rew)
                    
                    with col1:
                        st.markdown("**Original:**")
                        st.markdown(highlighted_orig)
                    with col2:
                        st.markdown("**Rephrased:**")
                        st.markdown(highlighted_rew)
                        
                    # Word count comparison
                    orig_wc = len(orig.split())
                    rew_wc = len(rew.split())
                    
                    st.markdown(f"Word count: Original ({orig_wc}) → Rephrased ({rew_wc})")
                    st.divider()
    
    if stop_button:
        st.warning("🚫 Process stopped manually.")
else:
    st.info("🔐 Enter your OpenAI API key to start.")
