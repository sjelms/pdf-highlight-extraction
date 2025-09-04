"""
Handles the export of enriched annotations to a Markdown file.
"""
import json
from typing import List, Dict, Any

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

    meta = enriched_data.get("meta", {})
    annotations = enriched_data.get("data", [])

    if not annotations:
        print(f"No annotations found in {json_path}. Skipping Markdown export.")
        return

    with open(output_path, 'w', encoding='utf-8') as md_file:
        # Write YAML front matter
        md_file.write("---\
")
        md_file.write(f"title: \"{meta.get('title', '')}\"\n")
        md_file.write(f"year: {meta.get('year', '')}\n")
        for i, author in enumerate(meta.get('authors', [])):
            md_file.write(f"author-{i+1}: \"[[{author}]]\"\n")
        md_file.write(f"citation-key: \"{meta.get('citation_key', '')}\"\n")
        md_file.write("highlights:\n")
        md_file.write("---\
\n")

        # Write annotations
        for annot in annotations:
            md_file.write(f"- {annot.get('text', '')}\n")
            md_file.write(f"> page: `{annot.get('page_number')}`\n")
            if annot.get('color'):
                # Simple color to tag mapping (can be expanded in config)
                color_map = {
                    '#b9e8b9': '#important-pdf',
                    '#c3e1f8': '#reference-note-pdf',
                    '#f0bbcd': '#secondary-pdf',
                    '#f9e196': '#general-pdf'
                }
                tag = color_map.get(annot.get('color'), '')
                if tag:
                    md_file.write(f"> tags: {tag}\n")
            
            if annot.get('note'):
                md_file.write("\n")
                md_file.write(f">[!memo]\n")
                md_file.write(f"> {annot.get('note')}\n")
            
            md_file.write("\n")

    print(f"Successfully exported {len(annotations)} highlights to {output_path}")
