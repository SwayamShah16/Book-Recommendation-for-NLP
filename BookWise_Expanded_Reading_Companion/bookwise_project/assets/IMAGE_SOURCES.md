# BookWise image assets

The `covers/` folder contains original, locally generated typographic cover illustrations for the demo catalogue. They are bundled with the project, so book images load offline and do not depend on third-party servers. They are illustrative designs, not official publisher cover art.

`cover_links.csv` contains an Open Library search link for each title. If you later choose to use official cover images, verify the matching edition on Open Library and use its cover ID/ISBN. Open Library cover API documentation: https://openlibrary.org/dev/docs/api/covers

The Open Library cover URL pattern is `https://covers.openlibrary.org/b/$key/$value-$size.jpg`. Missing covers may return a blank image; keep the bundled artwork as a fallback.
