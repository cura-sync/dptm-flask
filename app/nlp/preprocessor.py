import re
from typing import List
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from difflib import SequenceMatcher

# Optional: If not downloaded, run once
import nltk
nltk.download('punkt')
nltk.download('stopwords')

EN_STOPWORDS = set(stopwords.words('english'))

def clean_text(text: str) -> str:
    """Remove unwanted artifacts like extra spaces, OCR junk, non-ascii."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
    text = re.sub(r'[^\w\s\.\,\-\/]', '', text)  # remove special chars except . , - /
    return text.strip()

def remove_stopwords(sentence: str) -> str:
    """Remove stopwords from a sentence."""
    words = word_tokenize(sentence)
    filtered_words = [word for word in words if word.lower() not in EN_STOPWORDS]
    return " ".join(filtered_words)

def deduplicate(sentences: List[str]) -> List[str]:
    """Remove near-duplicate sentences."""
    seen = []
    for s in sentences:
        if not any(SequenceMatcher(None, s, seen_s).ratio() > 0.9 for seen_s in seen):
            seen.append(s)
    return seen

def process_extracted_text(text: str) -> str:
    """
    Main function to process extracted OCR/Whisper text.
    Cleans, deduplicates, removes stopwords to optimize tokens.
    """
    print(f"Input text length: {len(text)}")
    
    if not text or len(text.strip()) == 0:
        return ""

    cleaned = clean_text(text)
    sentences = sent_tokenize(cleaned)
    deduped = deduplicate(sentences)
    stopword_removed = [remove_stopwords(sentence) for sentence in deduped]
    final_result = "\n".join(stopword_removed)

    return final_result