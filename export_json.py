"""
Orchestrates the extraction, enrichment, and export of annotations to an enriched JSON file.
"""
import json
import os
import re
import fitz
import html
from typing import List, Dict, Any

from annotations import extract_annotations, Annotation
from bib import (
    load_bibtex,
    find_bibtex_entry,
    normalize_meta,
    find_bibtex_entry_by_basename,
)

def create_enriched_json(
    pdf_path: str,
    bib_path: str,
    output_path: str,
):
    """
    Creates an enriched JSON file containing PDF annotations and BibTeX metadata.

    Args:
        pdf_path: Path to the PDF file.
        bib_path: Path to the BibTeX file.
        output_path: Path to write the output JSON file.
    """
    # 1. Extract raw annotations
    annotations = extract_annotations(pdf_path)

    if not annotations:
        print(f"No highlights found in {pdf_path}. Skipping.")
        return

    # 2. Enrich with BibTeX metadata
    bib_database = load_bibtex(bib_path)

    doc = fitz.open(pdf_path)
    pdf_metadata = doc.metadata
    doc.close()

    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # Prefer embedded PDF title, but fall back if missing/blank
    pdf_title = pdf_metadata.get('title') or base_filename
    
    # Normalize author names from PDF metadata for better matching
    pdf_author_str = pdf_metadata.get('author', '') or ''
    # Split on common separators: commas, semicolons, or the word 'and'
    pdf_author_list = [
        a.strip() for a in re.split(r"\s*(?:,|;|\band\b)\s*", pdf_author_str)
        if a.strip()
    ]

    # Prefer filename-based lookup first (reference manager schema Title_Authors_Year)
    bib_entry = find_bibtex_entry_by_basename(base_filename, bib_database)
    # Fallback: try title+author fuzzy match from embedded PDF metadata
    if not bib_entry:
        bib_entry = find_bibtex_entry(pdf_title, pdf_author_list, bib_database)

    # 3. Combine into a single structured dictionary
    if bib_entry:
        meta = normalize_meta(bib_entry)
    else:
        # Fallback to PDF metadata if no BibTeX match
        meta = {
            "citation_key": "",
            "title": pdf_title or base_filename,
            "authors": pdf_author_list,
            "editors": [],
            "year": "",
            "doi": "",
            "url": "",
            "entry_type": "",
            "short_title": "",
        }

        # Emit a warning so the UI can surface an issue in the summary
        print(f"Warning: No BibTeX match found for '{base_filename}'. Metadata may be incomplete.")

    # 3b. Sanitize annotation text and notes for consistent JSON/MD export
    def _sanitize_text(s: str) -> str:
        if s is None:
            return ""
        # HTML entities → characters (e.g., &amp; → &)
        s = html.unescape(str(s))
        # Normalize newlines and remove carriage returns
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        # Normalize spaces
        s = s.replace("\xa0", " ")  # non-breaking space
        s = s.replace("\u200b", "")  # zero-width space
        s = s.replace("\ufeff", "")  # BOM
        s = s.replace("\u00ad", "")  # soft hyphen
        # Trim each line and collapse intra-line runs of spaces/tabs, then join with a single space
        lines = [re.sub(r"[\t ]+", " ", ln.strip()) for ln in s.split("\n")]
        s = " ".join([ln for ln in lines if ln])
        return s.strip()

    cleaned_annots = []
    for a in annotations:
        d = a.dict()
        d["text"] = _sanitize_text(d.get("text", ""))
        d["note"] = _sanitize_text(d.get("note", ""))
        cleaned_annots.append(d)

    enriched_data = {
        "meta": meta,
        "data": cleaned_annots,
    }

    # 4. Export to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        # Keep Unicode characters as-is for readability (no \uXXXX escapes)
        json.dump(enriched_data, f, indent=4, ensure_ascii=False)

    print(f"Successfully exported enriched JSON to {output_path}")
