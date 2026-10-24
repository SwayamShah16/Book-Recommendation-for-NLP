"""Experiment 10: Text exploratory analysis and word cloud."""
import re
from collections import Counter
def run(text):
    cleaned = re.sub(r"[^a-zA-Z\s]", "", str(text).lower())
    words = cleaned.split()
    stopwords = {"a","an","the","and","or","is","are","of","to","in","for","on","with","it","this","that"}
    frequencies = Counter(w for w in words if w not in stopwords)
    return {"cleaned_text": cleaned, "frequencies": dict(frequencies)}
