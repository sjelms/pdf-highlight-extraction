"""
Handles the export of enriched annotations to a Readwise-ready CSV file.
"""
import csv
import json
from typing import List, Dict, Any

def create_readwise_csv(
    json_path: str,
    output_path: str,
):
    """
    Creates a Readwise-ready CSV file from an enriched JSON file.

    Args:
        json_path: Path to the enriched JSON file.
        output_path: Path to write the output CSV file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)

    meta = enriched_data.get("meta", {})
    annotations = enriched_data.get("data", [])

    if not annotations:
        print(f"No annotations found in {json_path}. Skipping CSV export.")
        return

    # Readwise required headers
    headers = ["Title", "Author", "Category", "Source URL", "Highlight", "Note", "Location"]

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for annot in annotations:
            writer.writerow({
                "Title": meta.get("title", ""),
                "Author": ", ".join(meta.get("authors", [])),
                "Category": "articles",  # Defaulting to articles
                "Source URL": meta.get("url", ""),
                "Highlight": annot.get("text", ""),
                "Note": annot.get("note", ""),
                "Location": f'Page {annot.get("page_number")}',
            })

    print(f"Successfully exported {len(annotations)} highlights to {output_path}")
