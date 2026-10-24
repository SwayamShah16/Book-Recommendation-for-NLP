"""Experiment 9: TF-IDF text similarity recognizer."""
from src.experiment_tools import compare_texts
def run(doc1, doc2):
    score, level = compare_texts(doc1, doc2)
    return {"cosine_similarity": score, "percentage": score*100, "level": level}
