"""
Orchestrates the extraction, enrichment, and export of annotations to an enriched JSON file.
"""
import json
import os
import fitz
from typing import List, Dict, Any

from annotations import extract_annotations, Annotation
from bib import load_bibtex, find_bibtex_entry, get_authors_from_entry, get_editors_from_entry

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
    
    # For matching, we'll use the PDF's title and author metadata if available
    # As a fallback, we can parse the filename
    doc = fitz.open(pdf_path)
    pdf_metadata = doc.metadata
    doc.close()

    pdf_title = pdf_metadata.get('title', os.path.basename(pdf_path))
    pdf_author_list = pdf_metadata.get('author', '').split(', ')

    bib_entry = find_bibtex_entry(pdf_title, pdf_author_list, bib_database)

    # 3. Combine into a single structured dictionary
    if bib_entry:
        meta = {
            "citation_key": bib_entry.get('ID', ''),
            "title": bib_entry.get('title', pdf_title),
            "authors": get_authors_from_entry(bib_entry),
            "editors": get_editors_from_entry(bib_entry),
            "year": bib_entry.get('year', ''),
            "doi": bib_entry.get('doi', ''),
            "url": bib_entry.get('url', ''),
            "entry_type": bib_entry.get('ENTRYTYPE', ''),
            "short_title": bib_entry.get('shorttitle', ''),
        }
    else:
        # Fallback to PDF metadata if no BibTeX match
        meta = {
            "citation_key": "",
            "title": pdf_title,
            "authors": pdf_author_list,
            "editors": [],
            "year": "",
            "doi": "",
            "url": "",
            "entry_type": "",
            "short_title": "",
        }

    enriched_data = {
        "meta": meta,
        "data": [annot.dict() for annot in annotations]
    }

    # 4. Export to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_data, f, indent=4)

    print(f"Successfully exported enriched JSON to {output_path}")
