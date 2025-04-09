# main.py

import openai
import os
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_chatgpt(prompt, model="gpt-3.5-turbo"):
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=512
    )
    return response.choices[0].message.content.strip()

def extract_keywords_with_gpt(text):
    prompt = f"Extract the 10 most important keywords from the following transcript:\n\n{text}"
    response = call_chatgpt(prompt)
    keywords = re.findall(r'\\b\\w+\\b', response) if ',' not in response else [k.strip() for k in response.split(',')]
    return keywords[:10]

def split_into_paragraphs(text, max_paragraphs=15):
    sentences = re.split(r'(?<=[.!?]) +', text)
    total_sentences = len(sentences)
    sentences_per_paragraph = max(1, total_sentences // max_paragraphs)
    
    paragraphs = []
    for i in range(0, total_sentences, sentences_per_paragraph):
        paragraphs.append(" ".join(sentences[i:i+sentences_per_paragraph]))
    return paragraphs[:max_paragraphs]

def rephrase_paragraphs_with_gpt(paragraphs, keywords):
    rephrased = []
    keyword_string = ", ".join(keywords)
    for para in paragraphs:
        prompt = (
            f"Rephrase the following paragraph. Keep the meaning the same and retain these keywords: {keyword_string}.\n\n"
            f"Paragraph: {para}"
        )
        reply = call_chatgpt(prompt)
        rephrased.append(reply)
    return rephrased

def combine_and_trim(rephrased_paragraphs, original_length):
    combined = " ".join(rephrased_paragraphs)
    if len(combined) > original_length + 100:
        combined = combined[:original_length + 100]
        last_period = combined.rfind(".")
        if last_period != -1:
            combined = combined[:last_period+1]
    elif len(combined) < original_length - 100:
        combined += " [Note: Rephrased output is shorter than original.]"
    return combined

