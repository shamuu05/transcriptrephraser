# main.py

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
        max_tokens=1000  # max safe output for GPT-3.5
    )
    return response.choices[0].message.content.strip()

def split_transcript(text, max_words_per_paragraph=200):
    words = text.split()
    paragraphs = []
    for i in range(0, len(words), max_words_per_paragraph):
        chunk = " ".join(words[i:i+max_words_per_paragraph])
        paragraphs.append(chunk)
    return paragraphs

def rephrase_each_paragraph(paragraphs, keywords=None):
    rephrased = []
    for i, para in enumerate(paragraphs):
        prompt = f"Rephrase the following paragraph, keeping the meaning and keywords (if any):\n\n{para}"
        if keywords:
            prompt = f"Rephrase this while keeping these keywords intact: {', '.join(keywords)}.\n\n{para}"
        try:
            response = call_chatgpt(prompt)
            rephrased.append(response)
        except Exception as e:
            rephrased.append(f"[Error rephrasing paragraph {i+1}: {e}]")
    return rephrased

def combine_rephrased_text(paragraphs):
    return "\n\n".join(paragraphs)
