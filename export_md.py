"""
Handles the export of enriched annotations to a Markdown file.
"""
import json
import re


def create_markdown_export(
    json_path: str,
    output_path: str,
):
    """
    Creates a Markdown file from an enriched JSON file.

    Args:
        json_path: Path to the enriched JSON file.
        output_path: Path to write the output Markdown file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)

    meta = enriched_data.get("meta", {}) or {}
    annotations = enriched_data.get("data", []) or []

    if not annotations:
        print(f"No annotations found in {json_path}. Skipping Markdown export.")
        return

    with open(output_path, 'w', encoding='utf-8') as md_file:
    # Write YAML front matter
        md_file.write("---\n")
        _title = meta.get('title', '')
        md_file.write(f'title: "{_title}"\n')
        md_file.write(f"year: {meta.get('year', '')}\n")

        # Authors
        for i, author in enumerate(meta.get('authors', []), start=1):
            md_file.write(f'author-{i}: "[[{author}]]"\n')

        # Editors
        for i, editor in enumerate(meta.get('editors', []), start=1):
            md_file.write(f'editor-{i}: "[[{editor}]]"\n')

        # Citation key
        citation_key = meta.get('citation_key', '')
        if citation_key:
            md_file.write(f'citation-key: "[[@{citation_key}]]"\n')

        # Highlights count
        md_file.write(f"highlights: {len(annotations)}\n")

        # Type (quote the value to avoid YAML treating it as a comment)
        entry_type = str(meta.get('entry_type', '') or '').lower()
        if entry_type:
            md_file.write(f'type: "#{entry_type}-pdf"\n')

        # Aliases (full title + optional short title). Avoid duplicates.
        full_title = meta.get('title', '') or ''
        short_title = meta.get('short_title', '') or ''

        aliases: list[str] = []
        if full_title:
            aliases.append(full_title)

        # Derive a short title if not provided: take text before a dash/colon
        if not short_title and full_title:
            parts = re.split(r"\s*[–—-:]\s*", full_title, maxsplit=1)
            if len(parts) > 1 and parts[0].strip():
                short_title = parts[0].strip()

        if short_title:
            aliases.append(short_title)

        # Deduplicate while preserving order
        seen = set()
        unique_aliases = []
        for a in aliases:
            key = a.strip()
            if key and key not in seen:
                seen.add(key)
                unique_aliases.append(a)

        if unique_aliases:
            md_file.write("aliases:\n")
            for a in unique_aliases:
                md_file.write(f'  - "{a}"\n')

        md_file.write("---\n\n")

        # Add H1 header with citation key after YAML front matter
        if citation_key:
            md_file.write(f"# Highlights for [[@{citation_key}]]\n\n")
        else:
            md_file.write("# Highlights\n\n")

        # Simple color to tag mapping (can be expanded in config)
        color_map = {
            '#b9e8b9': '#important-pdf',
            '#c3e1f8': '#reference-note-pdf',
            '#f0bbcd': '#secondary-pdf',
            '#f9e196': '#general-pdf',
        }

        # Helper: check whether an annotation note is meaningful (not just a copy of the text)
        def _normalize_for_compare(s: str) -> str:
            # Compare notes to text verbatim aside from whitespace differences
            s = (s or "")
            s = s.replace("\r\n", "\n").replace("\r", "\n")
            s = s.replace("\n", " ")
            s = re.sub(r"\s+", " ", s)
            return s.strip()

        def _is_meaningful_note(note: str, text: str) -> bool:
            if not note or not note.strip():
                return False
            nn = _normalize_for_compare(note)
            nt = _normalize_for_compare(text)
            if not nn:
                return False
            # Skip only if verbatim (modulo whitespace) duplicate of the text
            if nn == nt:
                return False
            return True

        # Write annotations
        for annot in annotations:
            text = annot.get('text', '') or ''
            page_number = annot.get('page_number')

            md_file.write(f"- {text}\n")
            md_file.write(f"> page: `{page_number}`\n")

            color = annot.get('color')
            tag = color_map.get(color, '') if color else ''
            if tag:
                md_file.write(f"> tags: {tag}\n")

            note = annot.get('note')
            if _is_meaningful_note(note, text):
                md_file.write("\n")
                md_file.write(">[!memo]\n")
                _note_text = note.replace("\r\n", "\n").replace("\r", "\n").strip()
                for line in _note_text.split('\n'):
                    md_file.write(f"> {line}\n")

            md_file.write("\n")

    print(f"Successfully exported {len(annotations)} highlights to {output_path}")
