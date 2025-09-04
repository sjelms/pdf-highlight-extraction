# TECHNICAL SPECIFICATION for pdf-highlight-extraction

## Project Overview

The `pdf-highlight-extraction` project automates the extraction, enrichment, and export of PDF annotations into two primary output formats:

- **Readwise-ready CSV**: A structured CSV file optimized for import into Readwise, containing highlights and enriched bibliographic metadata.
- **Markdown**: A human-readable Markdown file summarizing annotations with contextual metadata, suitable for note-taking apps like Obsidian.

The tool parses PDF highlights, enriches them with bibliographic metadata via BibTeX files, and exports well-structured outputs to streamline knowledge management workflows.

---

## Directory Structure

```
/project-root
│
├── main.py                # Entry point coordinating the pipeline
├── annotations.py         # Extract and process PDF annotations
├── bib.py                 # BibTeX parsing and metadata matching
├── export_csv.py          # Generate Readwise-ready CSV exports
├── export_md.py           # Generate Markdown exports of annotations
├── utils.py               # Utility functions (logging, parsing helpers)
├── config.yaml            # Configuration file for paths and options
├── tests/                 # Unit and integration tests
│   ├── test_annotations.py
│   ├── test_bib.py
│   ├── test_export.py
│   └── fixtures/
│       ├── sample.pdf
│       ├── sample.bib
│       └── expected.csv
└── README.md
```

---

## Setup Instructions

### 1. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Paths

- Edit `config.yaml` to specify:
  - Path to PDFs folder
  - Path to BibTeX file(s)
  - Output directories for CSV and Markdown
  - Any optional parameters (e.g., similarity thresholds)

---

## Workflow

The pipeline proceeds as follows:

1. **PDF Annotation Extraction**  
   Parse each PDF to extract highlight annotations, including text, page numbers, colors, and notes.

2. **Metadata Enrichment via BibTeX**  
   Parse BibTeX files and attempt to match PDF metadata (e.g., filename-derived info) against BibTeX entries using a heuristic matching strategy.

3. **Export Generation**  
   Produce two outputs per PDF:
   - A Readwise CSV file containing highlights and enriched metadata fields.
   - A Markdown summary file with formatted annotations, page numbers, and notes.

---

## Core Functions

### `extract_annotations(pdf_path: str) -> List[Annotation]`  
Extracts highlight annotations from a PDF file, returning a list of `Annotation` objects containing text, page number, color, and notes.

### `resolve_highlight_text(page: PdfPage, annot: PdfAnnotation) -> str`  
Given a PDF page and an annotation object, extracts and cleans the highlighted text content.

### `parse_filename_metadata(filename: str) -> ParsedName`  
Parses a PDF filename to extract metadata such as author(s), year, and title components for matching.

### `load_bibtex(bibtex_path: str) -> BibDB`  
Loads and parses a BibTeX file into an internal database structure for efficient lookup.

### `find_bibtex_entry_by_title_and_authors(title: str, authors: List[str], bibtex_path: str) -> dict | None`  
Searches the BibTeX database for an entry matching the given title and author list; returns the matching entry or None.

### `parse_bibtex_entry(citation_key: str, bibtex_path: str) -> Optional[Dict[str, Any]]`  
Extracts detailed metadata fields from a BibTeX entry identified by its citation key.

### `bibtex_to_yaml_names(bibtex_authors: str) -> List[str]`  
Converts BibTeX author strings into a list of standardized author names suitable for YAML or other structured formats.

### `match_pdf_to_bib(pdf_meta: ParsedName, parsed_name: ParsedName, bibdb: BibDB) -> MatchResult`  
Performs heuristic matching between extracted PDF metadata and BibTeX entries, returning a `MatchResult` with matching status and matched entry.

### `build_readwise_rows(annotations: List[Annotation], match: MatchResult) -> List[Dict[str, str]]`  
Constructs a list of dictionaries representing rows for the Readwise CSV export, mapping annotation and metadata fields.

### `write_readwise_csv(rows: List[Dict[str, str]], out_path: str)`  
Writes the Readwise CSV rows to the specified output file with appropriate headers.

### `write_markdown(annotations: List[Annotation], match: MatchResult, out_path: str)`  
Generates a Markdown file summarizing annotations with enriched metadata and writes it to the specified path.

---

## Matching Strategy

The matching between PDF metadata and BibTeX entries uses a stepwise heuristic:

1. **Filename Parsing**  
   Extract author(s), year, and title fragments from the PDF filename.

2. **Title Similarity**  
   Compute string similarity (e.g., Levenshtein or fuzzy matching) between extracted title and BibTeX titles.

3. **Author Overlap**  
   Compare parsed authors with BibTeX author lists for overlap and ordering.

4. **Year Check**  
   Confirm that the publication year matches or is within a small tolerance.

5. **DOI Matching**  
   If available, compare DOI fields for exact matches.

6. **Fallbacks**  
   Use partial title matches or truncated author lists for ambiguous cases.

7. **Truncation Handling**  
   Handle incomplete or abbreviated filenames gracefully.

The goal is to maximize precision while allowing for minor inconsistencies in naming conventions.

---

## Data Models

```python
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

class Annotation(BaseModel):
    text: str
    page: int
    color: Optional[str] = None
    note: Optional[str] = None

class ParsedName(BaseModel):
    authors: List[str]
    year: Optional[int]
    title: Optional[str]

class MatchResult(BaseModel):
    matched: bool
    bib_entry: Optional[dict] = None
    confidence: float = 0.0
```

---

## CSV Export Details

The Readwise CSV export contains exactly seven columns:

| CSV Column | Source Field / Description                    |
|------------|----------------------------------------------|
| Highlight  | Annotation text                              |
| Title      | Matched BibTeX entry title                   |
| Author     | Concatenated author names from BibTeX       |
| URL        | URL or DOI from BibTeX entry                  |
| Note       | Annotation note, if any                        |
| Location   | Page number or PDF location                    |
| Date       | Publication year or date from BibTeX          |

Each row corresponds to one annotation, enriched with metadata for seamless import into Readwise.

---

## Markdown Export Notes

- Output includes a header with bibliographic metadata (title, authors, year, DOI).
- Each annotation is listed with:
  - Highlight text
  - Page number
  - Highlight color (if available)
  - User notes
- Formatting placeholders allow for future styling and linking.
- Markdown is compatible with note-taking apps such as Obsidian.

### YAML Header Variants

The exported Markdown files include YAML front matter that can specify authors, editors, or both, using standardized keys such as `author`, `authors`, `editor`, or `editors`. This facilitates integration with note-taking systems that parse YAML metadata.

**Authors only:**
```yaml
---
title: "Title of the Work"
year: 2023
author-1: "[[Author One]]"
author-2: "[[Author Two]]"
citation-key: "CitationKey2023"
highlights:
---
```

**Editors only:**
```yaml
---
title: "Title of the Work"
year: 2023
editor-1: "[[Editor One]]"
editor-2: "[[Editor Two]]"
citation-key: "CitationKey2023"
highlights:
---
```

**Both authors and editors:**
```yaml
---
title: "Title of the Work"
year: 2023
author-1: "[[Author One]]"
editor-1: "[[Editor One]]"
citation-key: "CitationKey2023"
highlights:
---
```

**Notes:**
- The `citation-key` field corresponds to the BibTeX entry key matched during processing and must be preserved in the format `[[@CitationKey]]` within the text when referenced.
- The `author-n` and `editor-n` fields are numbered sequentially and use double square brackets for linking (e.g., `[[Author Name]]`), supporting Obsidian's linking syntax.

### Highlight Formatting Rules

- Highlights are formatted to preserve line breaks and whitespace as closely as possible to the original PDF.
- Annotations with user notes are displayed beneath the highlight text, indented or styled for clarity.
- Each highlight begins with a list item marker `- ` followed by the highlighted text.
- Immediately following the highlight text is a blockquote `>` containing metadata:
  - `page: \`00\`` indicating the page number where the highlight appears.
  - `tags: #color-tag` where the color tag corresponds to the highlight's color.
- If the annotation includes a user comment (the `Text` field in the JSON annotation), add a blank line after the metadata block and then:
  ```
  >[!memo]
  > Comment text
  ```

### Color-to-Tag Mapping

Highlight colors are mapped to tags or labels within the Markdown, allowing users to filter or categorize highlights by color. This mapping is configurable and reflected in the Markdown output.

- `#b9e8b9 → #important-pdf`
- `#c3e1f8 → #reference-note-pdf`
- `#f0bbcd → #secondary-pdf`
- `#f9e196 → #general-pdf`

### Whitespace & Callout Requirements

- Proper whitespace around highlights and notes is maintained to ensure readability and compatibility with Markdown parsers.
- Leading and trailing spaces are preserved where meaningful.
- Blank lines separate annotations for visual clarity.
- A mandatory blank line **must** precede the `>[!memo]` callout block to ensure correct rendering.
- Backticks used in page numbers or metadata (e.g., ``page: `00` ``) are preserved exactly as shown.

### Exact Example

```
- This is a highlight
> page: `00`
> tags: #general-pdf

>[!memo]
> This is a comment on the highlight
```

## Error Handling & Logging

- **No-annotation PDFs:** Logs a warning and skips export.
- **Partial Matches:** Logs confidence scores and flags uncertain matches.
- **Malformed BibTeX:** Catches parsing exceptions, logs errors, and continues gracefully.
- **Diagnostics:** Writes detailed logs including file paths, matching attempts, and errors.
- Verbose logging option available for debugging.

---

## Testing & Validation

- Unit tests cover:
  - Annotation extraction correctness
  - BibTeX parsing and matching logic
  - CSV and Markdown export formatting
- Integration tests use fixtures with sample PDFs and BibTeX files.
- Golden files (`expected.csv`, `expected.md`) used to verify output consistency.
- Edge cases tested:
  - PDFs with no highlights
  - BibTeX entries with missing fields
  - Filename irregularities
  - Multiple authors and ambiguous matches

---

## Future Enhancements

- Consolidate multiple PDFs into a single CSV export.
- Incorporate DOI lookup APIs for enhanced metadata fetching.
- Implement color mapping for highlight types.
- Add deduplication logic for repeated highlights.
- Support additional export formats (e.g., JSON, HTML).
- Improve fuzzy matching with machine learning techniques.

---

## Author & Contact

- **Author**: Stephen Elms  
- **GitHub**: [https://github.com/sjelms/pdf-highlight-extraction](https://github.com/sjelms/pdf-highlight-extraction)