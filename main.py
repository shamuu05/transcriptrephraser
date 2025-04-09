from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import re

# Load a lightweight embedding model for keyword extraction
embedding_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # very small and fast
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

def rephrase_with_keywords(paragraphs, keywords):
    rephraser = pipeline("text2text-generation", model="ramsrigouthamg/t5_paraphraser")
    rephrased = []
    for para in paragraphs:
        prompt = f"paraphrase: {para}"
        result = rephraser(prompt, max_length=512, do_sample=True, top_k=50)[0]['generated_text']
        rephrased.append(result)
    return rephrased
