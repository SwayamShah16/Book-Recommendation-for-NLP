"""Experiment 2: Tokenization, filtration, and script validation."""
from src.preprocessing import tokenize, filter_tokens, validate_script
def run(text):
    tokens = tokenize(text)
    return {"original_text": text, "tokens": tokens, "filtered_tokens": filter_tokens(tokens), "script_validation": validate_script(text)}
