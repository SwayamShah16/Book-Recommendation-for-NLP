"""Small, dependency-light Text Insights helpers for the classroom experiments."""
from collections import defaultdict, Counter
import re


def _words(text):
    return re.findall(r"[a-zA-Z0-9']+", str(text).lower())


def build_ngram_model(text, n=2):
    words = _words(text)
    model = defaultdict(Counter)
    if n < 2: n = 2
    for i in range(len(words)-n+1):
        context = tuple(words[i:i+n-1])
        model[context][words[i+n-1]] += 1
    return dict(model)


def predict_next_word(model, context):
    words = tuple(_words(context))
    if not words: return None
    for size in range(len(words), 0, -1):
        key = words[-size:]
        if key in model and model[key]: return model[key].most_common(1)[0][0]
    return None


def generate_text(model, seed, num_words=10):
    output = _words(seed)
    if not output: return ''
    for _ in range(max(0, num_words)):
        nxt = predict_next_word(model, ' '.join(output))
        if not nxt: break
        output.append(nxt)
    return ' '.join(output)


def compare_texts(doc1, doc2):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        matrix = TfidfVectorizer(stop_words='english').fit_transform([str(doc1), str(doc2)])
        score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0,0])
    except ValueError:
        score = 0.0
    level = 'High' if score >= .5 else ('Moderate' if score >= .2 else 'Low')
    return score, level
