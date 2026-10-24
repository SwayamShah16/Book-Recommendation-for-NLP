"""Experiment 5: N-gram model, next-word prediction, and text generation."""
from src.experiment_tools import build_ngram_model, predict_next_word, generate_text
def run(text, n=2, context="", seed=None, num_words=10):
    model = build_ngram_model(text, n)
    prediction = predict_next_word(model, context) if context else None
    generated = generate_text(model, seed or context or text.split()[0], num_words) if text.split() else ""
    return {"model": {str(k): dict(v) for k,v in model.items()}, "prediction": prediction, "generated_text": generated}
