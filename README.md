# BookWise — Smart Book Discovery & Reading Companion

BookWise is a Python and Streamlit web application for discovering books, receiving content-based suggestions, organizing a personal shelf, tracking reading progress, and exploring catalogue and text insights.

## Features

- **Discover:** search by title, author, genre, topic, mood, or description; filter by genre and minimum rating.
- **For You:** personalize suggestions by preferred genres, mood, and book length.
- **Content-based matching:** TF-IDF and cosine similarity rank descriptions against a search idea.
- **My Shelf:** save books, remove saved titles, and export your shelf to CSV.
- **Reading Tracker:** track Want to Read / Currently Reading / Finished status, page progress, personal ratings, notes, yearly goal, and export a reading log.
- **Explore Insights:** view catalogue statistics, genre counts, rating distribution, reading lengths, and top-rated titles.
- **Similarity Matcher:** compare two catalogue descriptions or your own text.
- **Text Insights:** ten interactive tools for keyword cleaning, word refinement, word forms, next-word ideas, sentence roles, key phrases, names and places, text comparison, and popular words.
- **Data export:** download the full book catalogue and personal lists as CSV files.
- **30 curated demo titles** across multiple genres. The app does not require an API key or internet access for core recommendations.

## Run locally

1. Install Python 3.10 or newer.
2. Extract the ZIP and open a terminal in the project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Launch the app:

   ```bash
   streamlit run app.py
   ```

5. Open the local address printed in the terminal, usually `http://localhost:8501`.

## Project structure

- `app.py` — interface, catalogue, recommendations, reading tracker, and insights
- `src/preprocessing.py` — text cleanup, word forms, and script validation
- `src/experiment_tools.py` — text comparison and next-word helper functions
- `experiments/` — ten standalone classroom experiment modules retained for traceability
- `assets/ui_design_preview.png` — interface concept preview
- `assets/covers/` — 30 locally bundled book-cover illustrations that load offline
- `assets/cover_links.csv` — Open Library search links and cover URL reference
- `assets/IMAGE_SOURCES.md` — image asset notes and cover API guidance

## Technology

Python, Streamlit, Pandas, scikit-learn, and optional NLTK resources for sentence tagging, phrase chunking, and name recognition.

## Notes and limitations

The catalogue is a curated demonstration dataset, not a live commercial book service. Book covers are locally styled cover concepts rather than official cover images. Recommendations are content-based and do not yet learn from a community of users. Reading state is held in the current Streamlit session; it is not a secure multi-user account system or permanent database. Optional sentence-analysis features may show a setup message if their NLTK resources are unavailable.


## Sidebar and responsive layout
The desktop sidebar uses a fixed 272px width and the resize handle is hidden. On narrow screens it remains collapsible and adapts to the viewport. Book cover illustrations are stored locally in `assets/covers/`, so they do not rely on an internet connection.
