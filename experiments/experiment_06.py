"""Experiment 6: Part-of-speech tagging."""
def run(text):
    try:
        import nltk
        tokens = nltk.word_tokenize(text)
        return nltk.pos_tag(tokens)
    except LookupError:
        # Keep the app usable offline; basic fallback is clearly labeled.
        import re
        tokens = re.findall(r"\b[\w']+\b|[^\w\s]", text)
        return [(t, "NN (fallback)") for t in tokens]
