"""
Handles the export of enriched annotations to a Markdown file.
"""
import json


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

        # Aliases (quote items; they can contain special chars)
        full_title = meta.get('title', '')
        short_title = meta.get('short_title', '')
        if full_title or short_title:
            md_file.write("aliases:\n")
            if full_title:
                md_file.write(f'  - "{full_title}"\n')
            if short_title:
                md_file.write(f'  - "{short_title}"\n')

        md_file.write("---\n\n")

        # Simple color to tag mapping (can be expanded in config)
        color_map = {
            '#b9e8b9': '#important-pdf',
            '#c3e1f8': '#reference-note-pdf',
            '#f0bbcd': '#secondary-pdf',
            '#f9e196': '#general-pdf',
        }

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
            if note:
                md_file.write("\n")
                md_file.write(">[!memo]\n")
                for line in note.strip().split('\n'):
                    md_file.write(f"> {line}\n")

            md_file.write("\n")

    print(f"Successfully exported {len(annotations)} highlights to {output_path}")
