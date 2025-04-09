from youtube_transcript_api import YouTubeTranscriptApi
from keybert import KeyBERT
from transformers import pipeline
import re

def fetch_transcript(video_url):
    match = re.search(r"v=([a-zA-Z0-9_-]+)", video_url)
    if not match:
        return None
    video_id = match.group(1)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    full_text = " ".join([entry['text'] for entry in transcript])
    return full_text

def extract_keywords(text, num_keywords=10):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, top_n=num_keywords, stop_words='english')
    return [kw[0] for kw in keywords]

def format_paragraphs(text, sentences_per_paragraph=4):
    sentences = re.split(r'(?<=[.!?]) +', text)
    paragraphs = []
    for i in range(0, len(sentences), sentences_per_paragraph):
        paragraphs.append(" ".join(sentences[i:i+sentences_per_paragraph]))
    return paragraphs

rephraser = pipeline("text2text-generation", model="ramsrigouthamg/t5_paraphraser")

def rephrase_with_keywords(paragraphs, keywords):
    rephrased = []
    for para in paragraphs:
        prompt = f"Paraphrase this while keeping keywords: {', '.join(keywords)}. Text: {para}"
        result = rephraser(prompt, max_length=512, do_sample=True, top_k=50)[0]['generated_text']
        rephrased.append(result)
    return rephrased
