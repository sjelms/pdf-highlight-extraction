"""
Handles BibTeX parsing and metadata matching.
"""
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author, convert_to_unicode
from thefuzz import fuzz
from typing import List, Optional, Dict, Any

def load_bibtex(bibtex_path: str) -> bibtexparser.bibdatabase.BibDatabase:
    """
    Loads and parses a BibTeX file.

    Args:
        bibtex_path: The path to the BibTeX file.

    Returns:
        A BibTexDatabase object.
    """
    with open(bibtex_path, 'r', encoding='utf-8') as bibtex_file:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    return bib_database

def get_authors_from_entry(entry: Dict[str, Any]) -> List[str]:
    """Extracts a list of author full names from a BibTeX entry."""
    authors = []
    if 'author' in entry:
        for author_name in entry['author'].split(' and '):
            parts = [p.strip() for p in author_name.split(',')]
            if len(parts) == 2:
                authors.append(f"{parts[1]} {parts[0]}")
            else:
                authors.append(parts[0])
    return authors

def get_editors_from_entry(entry: Dict[str, Any]) -> List[str]:
    """Extracts a list of editor full names from a BibTeX entry."""
    editors = []
    if 'editor' in entry:
        for editor_name in entry['editor'].split(' and '):
            parts = [p.strip() for p in editor_name.split(',')]
            if len(parts) == 2:
                editors.append(f"{parts[1]} {parts[0]}")
            else:
                editors.append(parts[0])
    return editors

def find_bibtex_entry(
    pdf_title: str,
    pdf_authors: List[str],
    bib_database: bibtexparser.bibdatabase.BibDatabase,
    title_threshold: int = 80,
    author_threshold: int = 80
) -> Optional[Dict[str, Any]]:
    """
    Finds the best matching BibTeX entry for a given PDF.

    Args:
        pdf_title: The title of the PDF.
        pdf_authors: A list of author last names from the PDF.
        bib_database: The BibTeX database to search.
        title_threshold: The minimum similarity score for a title match.
        author_threshold: The minimum similarity score for an author match.

    Returns:
        The best matching BibTeX entry, or None if no good match is found.
    """
    best_match = None
    best_score = 0

    for entry in bib_database.entries:
        bib_title = entry.get('title', '')
        bib_authors = get_authors_from_entry(entry)

        title_score = fuzz.token_set_ratio(pdf_title, bib_title)

        if title_score > title_threshold:
            # Compare authors
            author_score = 0
            if pdf_authors and bib_authors:
                pdf_author_str = " ".join(sorted(pdf_authors))
                bib_author_str = " ".join(sorted(bib_authors))
                author_score = fuzz.token_set_ratio(pdf_author_str, bib_author_str)

            total_score = title_score + author_score

            if total_score > best_score:
                best_score = total_score
                best_match = entry

    return best_match
