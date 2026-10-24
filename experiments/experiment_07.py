"""Experiment 7: Chunking with a simple NP/PP/VP grammar."""
def run(text):
    try:
        import nltk
        tokens = nltk.word_tokenize(text)
        tags = nltk.pos_tag(tokens)
        grammar = r"""
            NP: {<DT>?<JJ.*>*<NN.*>+}
            PP: {<IN><NP>}
            VP: {<VB.*><NP|PP>*}
        """
        tree = nltk.RegexpParser(grammar).parse(tags)
        chunks = []
        for subtree in tree.subtrees():
            if subtree.label() in ["NP", "VP", "PP"]:
                phrase = " ".join(word for word, tag in subtree.leaves())
                chunks.append({"type": subtree.label(), "phrase": phrase})
        return {"tree": str(tree), "chunks": chunks}
    except LookupError:
        return {"tree": "NLTK model resources unavailable.", "chunks": []}
