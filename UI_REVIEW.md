# BookWise UI review and next steps

## Changes in this pass
- Consolidated the visual refresh into a single final override layer so the existing editorial look behaves more consistently.
- Removed the Google Fonts import. BookWise now falls back to system serif and sans-serif fonts and keeps its UI styling offline.
- Improved responsive spacing and legibility for narrow screens, with clearer focus states for keyboard users and reduced-motion support.
- Updated the sidebar footer copy to describe the product instead of calling out the classroom edition.
- Added a Book Insights route from each book card, with whole-book statistics for the bundled Project Gutenberg text of *Pride and Prejudice* and synopsis-based analysis for the other titles.

## Best next improvements
1. **Persist personal data.** Shelf, notes, progress, and goals currently live in the Streamlit session. Add SQLite for a single-user local demo, then use authenticated storage for a deployed multi-user version.
2. **Strengthen the catalogue.** The 30-title demo set limits discovery. Add a larger importable catalogue, genre normalization, cover attribution, and clear source/freshness labels.
3. **Make reading state easier to manage.** Add a shelf status filter, sorting, progress at a glance, and a one-click resume action from the shelf.
4. **Improve recommendation explanations.** Show a short “matched because” reason based on overlapping themes/genres and let readers tune results with feedback.
5. **Add quality safeguards.** Validate empty text and page ranges, handle export edge cases, and introduce UI checks for small screens and keyboard navigation before release.

## Product limitations to communicate
The current recommendations compare catalogue text and do not learn from reader behavior. Catalogue ratings are curated demo values, and session state is not durable storage. Keeping these labels visible will prevent the demo from implying a live commercial catalogue or account system.
