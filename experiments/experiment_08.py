"""Experiment 8: Named entity recognition using NLTK."""
def run(text):
    try:
        import nltk
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        tree = nltk.ne_chunk(tagged)
        entities = []
        for node in tree:
            if hasattr(node, "label"):
                entities.append({"entity": " ".join(w for w, tag in node.leaves()), "label": node.label()})
        return {"tree": str(tree), "entities": entities}
    except LookupError:
        return {"tree": "NLTK NER resources unavailable. Install/download NLTK resources to enable NER.", "entities": []}
