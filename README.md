# pdf-highlight-extraction

Extract, enrich, and export PDF highlights to Readwise-ready CSV and Markdown with BibTeX-powered metadata.

## Overview

This tool parses highlight annotations from PDFs, matches them to entries in a BibTeX file, and generates:
- Readwise-ready CSV files
- Rich Markdown notes with YAML front matter

The pipeline’s single source of truth is an enriched JSON file per PDF that combines raw annotations with normalized bibliographic metadata.

## Features

- Quad-based highlight extraction using PyMuPDF (reliable text capture from highlighted quadpoints)
- BibTeX integration with fuzzy title/author matching and normalization
- Robust author/editor parsing (supports “Last, First” format, multiline `and` separators, initials, and multi-part surnames like “LaScola Needy”)
- Markdown export with Obsidian-friendly YAML front matter, aliases, and color tags
- Readwise CSV export following the official template
- Deterministic output naming using citation key and type (e.g., `Assaad2022-zl article-pdf.md`)

## Requirements

- Python 3.9+
- Packages in `requirements.txt`

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configure

Edit `config.yaml` to set paths relative to the project root:
- `bibtex_path`: path to your BibTeX file (e.g., `paperpile.bib`)
- `json_output_dir`: directory for enriched JSON
- `csv_output_dir`: directory for Readwise CSV
- `md_output_dir`: directory for Markdown

## Usage

```bash
python pdf-highlight-extraction.py \
  "/absolute/path/to/your.pdf" \
  [--output-dir /tmp/exports] [--no-csv] [--no-md]
```

- Provide an absolute path to the PDF.
- If `--output-dir` is omitted, outputs go to folders specified in `config.yaml`.
- Filenames use: `"<citation-key> <entry-type>-pdf.<ext>"`; when no BibTeX match, fall back to the PDF base name.

## Output Details

### Enriched JSON
- `meta` includes: `title`, `short_title`, `year`, `entry_type`, `citation_key`, `authors`, `editors`, `doi`, `url`.
- `data` is a list of annotations: `text`, `page_number`, `color`, `note`.

### Markdown
- YAML front matter: title, year, `author-n` / `editor-n`, `citation-key`, `highlights`, `type`, and `aliases` (full and short title).
- Each highlight renders as a bullet with page and optional color tag.
- Color→tag mapping (default):
  - `#b9e8b9` → `#important-pdf`
  - `#c3e1f8` → `#reference-note-pdf`
  - `#f0bbcd` → `#secondary-pdf`
  - `#f9e196` → `#general-pdf`

### CSV (Readwise)

Columns (in order): `Title, Author, Category, Source URL, Highlight, Note, Location`

- `Title`: BibTeX title → PDF metadata title → filename fragment
- `Author`: BibTeX authors joined with comma
- `Category`: defaults to `articles`
- `Source URL`: `https://doi.org/<doi>` → BibTeX `url` → blank
- `Highlight`: annotation text (single-line; internal newlines collapsed)
- `Note`: annotation comment
- `Location`: `Page <n>`

## Notes & Troubleshooting

- If highlight text is empty, ensure annotations are highlight-type and the PDF isn’t scanned; quad-based extraction is used by default.
- Author parsing relies on BibTeX `author` / `editor` fields. For mismatches, confirm the BibTeX entry and citation key.
- Outputs require the PDF path to be absolute when invoking the script.

## Related Docs

- See `TECHNICAL.md` for a detailed specification and changelog.
