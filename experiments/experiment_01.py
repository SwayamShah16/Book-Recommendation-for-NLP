"""Experiment 1: Study of Text Insights applications and formulate a mini-project use case."""
def get_project_use_case():
    return {
        "project": "Smart Book Recommendation System",
        "problem_statement": "Readers face difficulty finding books matching their interests across large catalogs.",
        "text_applications": {
            "Text categorization": "Use genre and category metadata to filter books.",
            "Text similarity": "Compare book descriptions using TF-IDF and cosine similarity.",
            "Information retrieval": "Search title, author, genre, and description.",
            "Text preprocessing": "Normalize and filter book text before feature extraction."
        },
        "techniques": ["text preprocessing", "tokenization", "TF-IDF", "cosine similarity", "word frequency analysis"]
    }
