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

import re

def _normalize_initials(name: str) -> str:
    """
    Removes periods from initials in a name, e.g., "H." -> "H".
    """
    # Replace any single uppercase letter followed by a period with just the letter
    return re.sub(r'\b([A-Z])\.\b', r'\1', name)


def _strip_braces(text: str) -> str:
    """Remove surrounding braces often present in BibTeX fields."""
    return text.replace('{', '').replace('}', '')


def _parse_names(field_value: str) -> List[str]:
    """Parse a BibTeX author/editor field into normalized full names.

    - Robustly split on 'and' with any whitespace around it (including newlines).
    - Support "Last, First" -> "First Last" conversion.
    - Keep multi-part last names (e.g., "LaScola Needy").
    - Normalize initials by removing trailing periods in single-letter initials.
    """
    if not field_value:
        return []

    raw = _strip_braces(field_value.strip())
    parts = re.split(r"\s+and\s+", raw)
    people: List[str] = []

    for p in parts:
        name = p.strip()
        if not name:
            continue
        # Split on first comma only to preserve commas within names
        last_first = [s.strip() for s in name.split(',', 1)]
        if len(last_first) == 2:
            last, first = last_first[0], last_first[1]
            full_name = f"{first} {last}".strip()
        else:
            # Already in First Last order or single token
            full_name = last_first[0]

        # Collapse internal whitespace and normalize initials
        full_name = re.sub(r"\s+", " ", full_name)
        full_name = _normalize_initials(full_name)
        people.append(full_name)

    return people

def get_authors_from_entry(entry: Dict[str, Any]) -> List[str]:
    """Extracts a list of author full names from a BibTeX entry, normalized."""
    return _parse_names(entry.get('author', ''))

def get_editors_from_entry(entry: Dict[str, Any]) -> List[str]:
    """Extracts a list of editor full names from a BibTeX entry, normalized."""
    return _parse_names(entry.get('editor', ''))

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


def _sanitize_basename(name: str) -> str:
    """Normalize a filename-like string for fuzzy matching.

    - Lowercase
    - Replace separators (underscore, hyphen, dot) with spaces
    - Remove file-extension-like suffixes
    - Collapse whitespace
    """
    import re as _re
    n = name.strip().lower()
    # strip a trailing extension if present
    n = _re.sub(r"\.[a-z0-9]{1,5}$", "", n)
    n = n.replace("_", " ").replace("-", " ").replace(".", " ")
    n = _re.sub(r"\s+", " ", n)
    return n


def find_bibtex_entry_by_basename(
    base_filename: str,
    bib_database: bibtexparser.bibdatabase.BibDatabase,
    id_threshold: int = 75,
    title_threshold: int = 80,
) -> Optional[Dict[str, Any]]:
    """Find a BibTeX entry by comparing the file's base name to entry ID and title.

    Useful when embedded PDF metadata is sparse or blank but the file name
    contains author/year or the BibTeX key.
    """
    target = _sanitize_basename(base_filename)
    if not target:
        return None

    best: Optional[Dict[str, Any]] = None
    best_score = 0
    for entry in bib_database.entries:
        entry_id = str(entry.get("ID", "")).strip()
        entry_title = str(entry.get("title", "")).strip()

        id_score = fuzz.token_set_ratio(target, entry_id)
        title_score = fuzz.token_set_ratio(target, entry_title)

        # Prefer ID matches slightly over title for filenames
        combined = max(int(id_score * 1.05), title_score)

        if (id_score >= id_threshold or title_score >= title_threshold) and combined > best_score:
            best = entry
            best_score = combined

    return best

def normalize_meta(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and normalizes metadata from a BibTeX entry.

    Normalizations:
    - title: replace colons with en dashes, collapse whitespace, strip trailing punctuation
    - short_title: first segment before colon or dash
    - year: only 4-digit year retained
    - entry_type: lowercase of ENTRYTYPE
    - citation_key: ID from BibTeX entry
    - authors: list of normalized authors
    - editors: list of normalized editors
    - doi: The DOI of the entry
    - url: The URL of the entry

    Args:
        entry: A BibTeX entry dictionary.

    Returns:
        A dictionary with normalized metadata.
    """
    raw_title = entry.get('title', '').strip()
    # Normalize separators to an en dash surrounded by spaces
    title = raw_title.replace(':', ' – ')
    title = re.sub(r"\s+[-–—]\s+", " – ", title)
    # Collapse multiple whitespace into single space
    title = re.sub(r'\s+', ' ', title)
    # Strip trailing punctuation (e.g., periods, commas, colons, semicolons)
    title = title.rstrip('.,:; ')

    # Derive short_title by splitting on colon or dash and taking first segment
    short_title_split = re.split(r'[:–-]', raw_title)
    short_title = short_title_split[0].strip() if short_title_split else title

    # Extract year: keep only 4-digit year if present
    year = entry.get('year', '')
    match_year = re.search(r'\b(\d{4})\b', year)
    year_clean = match_year.group(1) if match_year else year

    entry_type = entry.get('ENTRYTYPE', '').lower()
    citation_key = entry.get('ID', '')

    authors = get_authors_from_entry(entry)
    editors = get_editors_from_entry(entry)
    doi = entry.get('doi', '')
    url = entry.get('url', '')

    return {
        'title': title,
        'short_title': short_title,
        'year': year_clean,
        'entry_type': entry_type,
        'citation_key': citation_key,
        'authors': authors,
        'editors': editors,
        'doi': doi,
        'url': url,
    }
