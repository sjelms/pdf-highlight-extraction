# PDF Highlight Extraction Script

Extract, enrich, and export PDF highlights to Readwise-ready CSV and Markdown with BibTeX/BibLaTeX-powered metadata.

## Overview

This tool parses highlight annotations from PDFs, matches them to entries in a BibTeX file, and generates:
- Readwise-ready CSV files
- Rich Markdown notes with YAML front matter

The pipeline’s single source of truth is an enriched JSON file per PDF that combines raw annotations with normalized bibliographic metadata.

## Features

- Quad-based highlight extraction using PyMuPDF (reliable text capture from highlighted quadpoints)
- BibTeX/BibLaTeX integration with filename-first matching, fuzzy fallbacks, and normalization
- Robust author/editor parsing (supports “Last, First” format, multiline `and` separators, initials, and multi-part surnames like “LaScola Needy”)
- Markdown export with Obsidian-friendly YAML front matter, H1 header, aliases, and color tags
- Readwise CSV export following the official template
- Deterministic output naming using citation key and type (e.g., `Assaad2022-zl article-pdf.md`)
- JSON sanitization for clean text/notes (normalized whitespace, single-line fields, readable Unicode)

## Requirements

- Python 3.9+
- Packages in `requirements.txt`
    - PyMuPDF
    - pydantic
    - bibtexparser
    - thefuzz[speedup]
    - PyYAML
    - latexcodec

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configure

Edit `config.yaml` to set paths relative to the project root:
- `bibtex_path`: path to your BibTeX/BibLaTeX file (e.g., `paperpile.bib`)
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
  - Matching prefers the PDF filename schema `Title_Authors_Year` against BibTeX IDs/titles; falls back to embedded PDF metadata.

## Output Details

### Enriched JSON
- `meta` includes: `title`, `short_title`, `year`, `entry_type`, `citation_key`, `authors`, `editors`, `doi`, `url`.
- `data` is a list of annotations: `text`, `page_number`, `color`, `note`.
  - Text and notes are sanitized: HTML entities unescaped, CR/LF normalized, zero‑width/soft hyphen removed, intra-line whitespace collapsed, and newlines joined into single spaces.

### Markdown
- YAML front matter: title, year, `author-n` / `editor-n`, `citation-key`, `highlights`, `type`, and `aliases` (full and optionally short title).
- Adds `# Highlights for [[@{citation_key}]]` after YAML (falls back to `# Highlights` if no key).
- Each highlight renders as a bullet with page and optional color tag.
- Memos: a memo block is included only when the note is present and not a verbatim duplicate of the highlight text (whitespace-insensitive).
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
- The run summary dialog reports "warning" when metadata is incomplete (e.g., BibTeX key not found) so you can review issues even if exports succeed.

## What’s New

- Support BibLaTeX entries and decode LaTeX accents/macros via latexcodec
- Derive publication year from BibLaTeX `date` when `year` is missing
- Prefer filename-based BibTeX matching; fallback to PDF metadata fuzzy match
- Add H1 header in Markdown: `# Highlights for [[@{citation_key}]]`
- Improve `aliases`: include full title and optional short title (derived before dash/colon); de-duplicate
- Sanitize JSON text/notes and write Unicode without `\uXXXX`
- Suppress memos that are exact duplicates of the highlight text
- Surface incomplete metadata as "warning" in the summary dialog

## Related Docs

- See `TECHNICAL.md` for a detailed specification and changelog.
