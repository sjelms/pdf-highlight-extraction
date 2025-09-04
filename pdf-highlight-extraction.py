"""
Main entry point for the PDF highlight extraction and export pipeline.
"""
import argparse
import os
import yaml

from export_json import create_enriched_json
from export_csv import create_readwise_csv
from export_md import create_markdown_export

def main():
    """Main function to run the pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", help="The path to the PDF file to process.")
    parser.add_argument("--project-dir", default=".", help="The root directory of the project.")
    args = parser.parse_args()

    project_dir = args.project_dir

    if not os.path.exists(args.pdf_path):
        print(f"Error: The file '{args.pdf_path}' was not found.")
        return

    # Load configuration
    with open(os.path.join(project_dir, "config.yaml"), 'r') as f:
        config = yaml.safe_load(f)

    bibtex_path = os.path.join(project_dir, config.get("bibtex_path"))
    json_output_dir = os.path.join(project_dir, config.get("json_output_dir"))
    csv_output_dir = os.path.join(project_dir, config.get("csv_output_dir"))
    md_output_dir = os.path.join(project_dir, config.get("md_output_dir"))

    # Create output directories if they don't exist
    os.makedirs(json_output_dir, exist_ok=True)
    os.makedirs(csv_output_dir, exist_ok=True)
    os.makedirs(md_output_dir, exist_ok=True)

    # Define output file paths
    base_filename = os.path.splitext(os.path.basename(args.pdf_path))[0]
    json_path = os.path.join(json_output_dir, f"{base_filename}.json")
    csv_path = os.path.join(csv_output_dir, f"{base_filename}.csv")
    md_path = os.path.join(md_output_dir, f"{base_filename}.md")

    # --- Run the pipeline ---

    # 1. Create enriched JSON
    create_enriched_json(args.pdf_path, bibtex_path, json_path)

    # 2. Create CSV and Markdown from the enriched JSON
    if os.path.exists(json_path):
        create_readwise_csv(json_path, csv_path)
        create_markdown_export(json_path, md_path)

if __name__ == "__main__":
    main()
