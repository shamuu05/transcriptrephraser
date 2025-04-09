from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import re
import openai
import os

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize KeyBERT with a lightweight model
embedding_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
kw_model = KeyBERT(model=embedding_model)

def extract_keywords(text, num_keywords=10):
    keywords = kw_model.extract_keywords(text, top_n=num_keywords, stop_words='english')
    return [kw[0] for kw in keywords]

def format_paragraphs(text, sentences_per_paragraph=4):
    sentences = re.split(r'(?<=[.!?]) +', text)
    paragraphs = []
    for i in range(0, len(sentences), sentences_per_paragraph):
        paragraphs.append(" ".join(sentences[i:i+sentences_per_paragraph]))
    return paragraphs

def rephrase_with_openai(paragraphs, keywords):
    rephrased = []
    for para in paragraphs:
        prompt = (
            f"Rephrase the following paragraph while keeping the meaning the same. "
            f"Make sure to retain these keywords exactly as they are: {', '.join(keywords)}.\n\n"
            f"Paragraph: {para}"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that rewrites text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.7
            )
            reply = response['choices'][0]['message']['content'].strip()
            rephrased.append(reply)
        except Exception as e:
            rephrased.append(f"Error: {e}")
    return rephrased
