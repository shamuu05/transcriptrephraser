import os
import zipfile

# Create the project folder
project_name = "ai_transcript_rewriter_pro"
os.makedirs(f"{project_name}", exist_ok=True)

# ======================
# main.py
# ======================
main_py = '''
import openai
import os
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_chatgpt(prompt, model="gpt-3.5-turbo"):
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that rewrites text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def split_transcript(text, max_words_per_paragraph=200):
    words = text.split()
    paragraphs = []
    for i in range(0, len(words), max_words_per_paragraph):
        chunk = " ".join(words[i:i+max_words_per_paragraph])
        paragraphs.append(chunk)
    return paragraphs

def rephrase_each_paragraph(paragraphs, custom_prompt=None):
    rephrased = []
    for i, para in enumerate(paragraphs):
        prompt = f"{custom_prompt}\\n\\n{para}" if custom_prompt else f"Rephrase this paragraph:\\n\\n{para}"
        try:
            response = call_chatgpt(prompt)
            rephrased.append(response)
        except Exception as e:
            rephrased.append(f"[Error rephrasing paragraph {i+1}: {e}]")
    return rephrased

def combine_rephrased_text(paragraphs):
    return "\\n\\n".join(paragraphs)
'''

# ======================
# streamlit_app.py
# ======================
streamlit_py = '''
import streamlit as st
import os
from main import split_transcript, rephrase_each_paragraph, combine_rephrased_text
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Transcript Rewriter Pro", layout="wide")
st.title("📄 AI Transcript Rewriter Pro")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Rewriting Controls")

    api_key = st.text_input("🔑 OpenAI API Key:", type="password")
    humanize = st.checkbox("🤖 Human Style Writing (Bypass AI Detectors)")
    custom_prompt = st.text_area("✏️ Advanced Prompt (Optional)")

    tone = st.selectbox("🎨 Tone", ["Default", "Formal", "Casual", "Humorous", "Motivational", "Empathetic", "Assertive", "Professional", "Poetic", "Neutral"])
    style = st.selectbox("🖋️ Script Style", ["Default", "Meme-style", "Storytelling", "Inspirational", "Socratic", "Bullet points", "Explanatory", "Twitter-thread", "Narrative", "Educational"])
    persona = st.selectbox("🎭 Persona", ["Default", "Motivational Coach", "Corporate Executive", "Cool Teenager", "Old Monk", "YouTube Vlogger", "Friendly Teacher", "Meme Lord", "Sci-Fi Narrator", "Reddit Commenter"])
    lang = st.selectbox("🌍 Output Language", ["English", "Spanish", "French", "Hindi", "Arabic"])
    preserve_story = st.checkbox("📚 Preserve Storytelling Style")
    para_len = st.slider("📏 Paragraph Word Length", min_value=50, max_value=500, value=200, step=50)
    length_factor = st.slider("📐 Rephrased Length Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    profile = st.selectbox("👤 User Profile", ["Default", "My Writing Style", "Client A", "Client B"])
    profile_presets = {
        "My Writing Style": {"tone": "Casual", "style": "Meme-style"},
        "Client A": {"tone": "Professional", "style": "Narrative"},
        "Client B": {"tone": "Formal", "style": "Bullet points"},
    }

    if profile != "Default":
        tone = profile_presets[profile]["tone"]
        style = profile_presets[profile]["style"]

    with st.expander("🧪 Experimental Features"):
        enable_qna = st.checkbox("Generate Q&A")
        summarize = st.checkbox("Create Summary First")
        turn_into_blog = st.checkbox("Turn into Blog Post")

# Transcript Input
uploaded_file = st.file_uploader("📤 Upload transcript (.txt)", type=["txt"])
input_text = ""

if uploaded_file:
    input_text = uploaded_file.read().decode("utf-8")
else:
    input_text = st.text_area("📝 Paste full transcript:", height=300)

# Auto Save/Resume
if 'last_text' not in st.session_state:
    st.session_state['last_text'] = ""

if input_text and input_text != st.session_state['last_text']:
    st.session_state['last_text'] = input_text
    st.success("🧠 Session Saved!")

if st.button("🔁 Resume Last Session"):
    input_text = st.session_state['last_text']
    st.text_area("📝 Restored Transcript", input_text, height=300)

# Start Processing
if st.button("🚀 Start Rephrasing") and api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if not input_text.strip():
        st.warning("Please upload or paste a transcript first.")
    else:
        st.info("Preparing advanced prompt...")
        paragraphs = split_transcript(input_text, max_words_per_paragraph=para_len)

        # Prompt Engineering
        base_prompt = ""
        if tone != "Default":
            base_prompt += f"Use a {tone} tone. "
        if style != "Default":
            base_prompt += f"Write in {style} style. "
        if persona != "Default":
            base_prompt += f"Act as a {persona}. "
        if preserve_story:
            base_prompt += "Preserve storytelling format. "
        if humanize:
            base_prompt += "Make it 100% human-written and undetectable by AI detectors. "
        if lang != "English":
            base_prompt += f"Translate and rephrase in {lang}. "
        if summarize:
            base_prompt = "First summarize, then " + base_prompt
        if turn_into_blog:
            base_prompt = "Rewrite this as a compelling blog post. " + base_prompt

        final_prompt = custom_prompt if custom_prompt.strip() else base_prompt

        st.info(f"📃 Splitting into {len(paragraphs)} paragraphs (~{para_len} words each)...")
        with st.spinner("Rephrasing with ChatGPT..."):
            rephrased = rephrase_each_paragraph(paragraphs, custom_prompt=final_prompt)

        final_output = combine_rephrased_text(rephrased)

        # Stats
        st.subheader("📊 Stats & Visuals")
        orig_wc = len(input_text.split())
        new_wc = len(final_output.split())
        st.metric("Original Words", orig_wc)
        st.metric("Rephrased Words", new_wc)
        st.metric("Read Time (min)", round(new_wc / 200))

        # Output Display
        st.subheader("📄 Final Rephrased Transcript")
        st.text_area("📜 Output", value=final_output, height=500)
        st.download_button("📥 Download Rephrased Transcript", data=final_output, file_name="rephrased_transcript.txt")

        # Original vs Rephrased Comparison
        with st.expander("🔍 Compare Original vs Rephrased"):
            for orig, rew in zip(paragraphs, rephrased):
                st.write("**Original:**")
                st.code(orig)
                st.write("**Rephrased:**")
                st.code(rew)

        # Q&A Experimental Feature
        if enable_qna:
            st.subheader("❓ Q&A Generation (Experimental)")
            qna_prompt = "Generate 5 insightful Q&A pairs based on this transcript:\\n\\n" + input_text
            qna_response = rephrase_each_paragraph([input_text], custom_prompt=qna_prompt)
            st.write(qna_response[0])
else:
    st.info("Please enter your OpenAI API key to begin.")
'''

# ======================
# requirements.txt
# ======================
requirements_txt = '''
streamlit
openai>=1.0.0
matplotlib
'''

# Write files
files = {
    f"{project_name}/main.py": main_py,
    f"{project_name}/streamlit_app.py": streamlit_py,
    f"{project_name}/requirements.txt": requirements_txt
}

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# Create zip
zip_path = f"/mnt/data/{project_name}.zip"
with zipfile.ZipFile(zip_path, 'w') as zipf:
    for folder_name, subfolders, filenames in os.walk(project_name):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            arcname = os.path.relpath(file_path, project_name)
            zipf.write(file_path, arcname)

zip_path
